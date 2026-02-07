#!/usr/bin/env python3
"""
Script pour récupérer les données de production solaire via EU PVGIS API.
"""

import json
import os
import sys
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import DATA_DIR


def fetch_solar_data(lat, lon):
    """
    Récupère les données de production solaire via PVGIS.
    Paramètres : 30 kWp, pertes 14%, cristallin, angle 15°
    """
    try:
        url = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"
        params = {
            "lat": lat,
            "lon": lon,
            "peakpower": 30,
            "loss": 14,
            "outputformat": "json",
            "pvtechchoice": "crystSi",
            "mountingplace": "building",
            "angle": 15
        }

        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            outputs = data.get("outputs", {})
            totals = outputs.get("totals", {})
            monthly = outputs.get("monthly", {})

            return {
                "annual_production_kwh": round(totals.get("fixed", {}).get("E_y", 0), 0),
                "monthly_production": [m.get("E_m", 0) for m in monthly.get("fixed", [])] if monthly.get("fixed") else [],
                "irradiation_kwh_m2": round(totals.get("fixed", {}).get("H(i)_y", 0), 0),
                "optimal_angle": outputs.get("pv_module_output_params", {}).get("optimalInclination", 15)
            }

        return None

    except Exception as e:
        print(f"  ⚠️ Erreur PVGIS: {e}")
        return None


def main():
    input_path = os.path.join(DATA_DIR, "cities_enriched.json")

    if not os.path.exists(input_path):
        print(f"❌ Fichier {input_path} introuvable.")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        cities = json.load(f)

    # Villes sans données solaires
    cities_without_solar = [c for c in cities if not c.get("solar")]

    print(f"📊 Récupération données solaires PVGIS pour {len(cities_without_solar)} villes...\n")

    if len(cities_without_solar) == 0:
        print("✅ Toutes les villes ont déjà des données solaires !")
        return

    success_count = 0

    for i, city in enumerate(cities_without_solar):
        if not city.get("latitude") or not city.get("longitude"):
            print(f"[{i+1}/{len(cities_without_solar)}] {city['name']} ⏭️  Pas de coordonnées")
            continue

        print(f"[{i+1}/{len(cities_without_solar)}] {city['name']}...", end=" ")

        solar_data = fetch_solar_data(city["latitude"], city["longitude"])

        if solar_data and solar_data["annual_production_kwh"] > 0:
            print(f"✅ {int(solar_data['annual_production_kwh'])} kWh/an")
            success_count += 1

            # Mettre à jour dans la liste complète
            for j, c in enumerate(cities):
                if c["name"] == city["name"]:
                    cities[j]["solar"] = solar_data
                    break
        else:
            print("❌ Échec")

        # Pause pour respecter les limites de l'API
        time.sleep(1)

        # Sauvegarder progressivement tous les 20 villes
        if (i + 1) % 20 == 0:
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(cities, f, ensure_ascii=False, indent=2)
            print(f"  💾 Sauvegarde intermédiaire ({i+1}/{len(cities_without_solar)})")

    # Sauvegarder final
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Récupération terminée !")
    print(f"📄 Sauvegardé dans {input_path}")

    # Stats finales
    with_solar = sum(1 for c in cities if c.get("solar"))
    print(f"   ☀️  {with_solar}/{len(cities)} villes avec données solaires ({success_count} nouvelles)")


if __name__ == "__main__":
    main()
