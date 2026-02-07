#!/usr/bin/env python3
"""
Script pour récupérer les données de qualité de l'air via Open-Meteo Air Quality API.
"""

import json
import os
import sys
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import DATA_DIR


def get_quality_label(aqi):
    """Retourne le label de qualité selon l'indice AQI européen."""
    if aqi < 50:
        return "Buona"
    elif aqi < 100:
        return "Discreta"
    elif aqi < 150:
        return "Scarsa"
    else:
        return "Cattiva"


def fetch_air_quality(lat, lon):
    """Récupère les données de qualité de l'air via Open-Meteo."""
    try:
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "european_aqi,pm10,pm2_5,nitrogen_dioxide"
        }

        response = requests.get(url, params=params, timeout=15)

        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})

            aqi = current.get("european_aqi")
            if aqi is None:
                return None

            return {
                "european_aqi": int(aqi),
                "pm10": round(current.get("pm10", 0), 1),
                "pm2_5": round(current.get("pm2_5", 0), 1),
                "nitrogen_dioxide": round(current.get("nitrogen_dioxide", 0), 1),
                "quality_label": get_quality_label(aqi)
            }

        return None

    except Exception as e:
        print(f"  ⚠️ Erreur Air Quality: {e}")
        return None


def main():
    input_path = os.path.join(DATA_DIR, "cities_enriched.json")

    if not os.path.exists(input_path):
        print(f"❌ Fichier {input_path} introuvable.")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        cities = json.load(f)

    # Villes sans données air
    cities_without_air = [c for c in cities if not c.get("air_quality")]

    print(f"📊 Récupération qualité de l'air pour {len(cities_without_air)} villes...\n")

    if len(cities_without_air) == 0:
        print("✅ Toutes les villes ont déjà des données de qualité de l'air !")
        return

    success_count = 0

    for i, city in enumerate(cities_without_air):
        if not city.get("latitude") or not city.get("longitude"):
            print(f"[{i+1}/{len(cities_without_air)}] {city['name']} ⏭️  Pas de coordonnées")
            continue

        print(f"[{i+1}/{len(cities_without_air)}] {city['name']}...", end=" ")

        air_data = fetch_air_quality(city["latitude"], city["longitude"])

        if air_data:
            print(f"✅ AQI: {air_data['european_aqi']} ({air_data['quality_label']})")
            success_count += 1

            # Mettre à jour dans la liste complète
            for j, c in enumerate(cities):
                if c["name"] == city["name"]:
                    cities[j]["air_quality"] = air_data
                    break
        else:
            print("❌ Échec")

        # Pause courte
        time.sleep(0.5)

        # Sauvegarder progressivement tous les 30 villes
        if (i + 1) % 30 == 0:
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(cities, f, ensure_ascii=False, indent=2)
            print(f"  💾 Sauvegarde intermédiaire ({i+1}/{len(cities_without_air)})")

    # Sauvegarder final
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Récupération terminée !")
    print(f"📄 Sauvegardé dans {input_path}")

    # Stats finales
    with_air = sum(1 for c in cities if c.get("air_quality"))
    print(f"   🌫️  {with_air}/{len(cities)} villes avec données qualité air ({success_count} nouvelles)")


if __name__ == "__main__":
    main()
