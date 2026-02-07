#!/usr/bin/env python3
"""
Script pour enrichir les POIs des villes restantes (celles qui n'en ont pas encore).
"""

import json
import os
import sys
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import DATA_DIR


def enrich_pois(city):
    """
    Récupère les POIs pertinents via Overpass API (OpenStreetMap).
    """
    lat, lng = city.get("latitude"), city.get("longitude")
    if not lat or not lng:
        return city

    radius = 5000
    overpass_url = "https://overpass-api.de/api/interpreter"

    query = f"""
    [out:json][timeout:30];
    (
      node["amenity"="parking"](around:{radius},{lat},{lng});
      way["amenity"="parking"](around:{radius},{lat},{lng});
      node["amenity"="fuel"](around:{radius},{lat},{lng});
      node["shop"="supermarket"](around:{radius},{lat},{lng});
      node["shop"="mall"](around:{radius},{lat},{lng});
      node["amenity"="charging_station"](around:{radius},{lat},{lng});
    );
    out count;
    """

    try:
        resp = requests.post(overpass_url, data={"data": query}, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        # Requête détaillée pour les parkings
        query_detail = f"""
        [out:json][timeout:30];
        (
          node["amenity"="parking"](around:{radius},{lat},{lng});
          way["amenity"="parking"](around:{radius},{lat},{lng});
        );
        out count;
        """
        resp2 = requests.post(overpass_url, data={"data": query_detail}, timeout=60)
        parking_count = resp2.json().get("elements", [{}])[0].get("tags", {}).get("total", 0) if resp2.ok else 0

        # Requête pour les bornes de recharge
        query_ev = f"""
        [out:json][timeout:30];
        node["amenity"="charging_station"](around:{radius},{lat},{lng});
        out count;
        """
        resp3 = requests.post(overpass_url, data={"data": query_ev}, timeout=60)
        ev_count = resp3.json().get("elements", [{}])[0].get("tags", {}).get("total", 0) if resp3.ok else 0

        city["pois"] = {
            "parking_count": int(parking_count),
            "ev_charging_stations": int(ev_count),
        }

    except Exception as e:
        print(f"  ⚠️ Overpass erreur pour {city['name']}: {e}")

    return city


def main():
    input_path = os.path.join(DATA_DIR, "cities_enriched.json")

    if not os.path.exists(input_path):
        print(f"❌ Fichier {input_path} introuvable.")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        cities = json.load(f)

    # Identifier les villes sans POIs
    cities_without_pois = [c for c in cities if not c.get("pois")]

    print(f"📊 Enrichissement POIs pour {len(cities_without_pois)} villes restantes...\n")

    if len(cities_without_pois) == 0:
        print("✅ Toutes les villes ont déjà des POIs !")
        return

    for i, city in enumerate(cities_without_pois):
        print(f"[{i+1}/{len(cities_without_pois)}] {city['name']}...")

        # Enrichir les POIs
        city = enrich_pois(city)
        time.sleep(3)  # Respecter le fair-use d'Overpass

        # Mettre à jour dans la liste complète
        for j, c in enumerate(cities):
            if c["name"] == city["name"]:
                cities[j] = city
                break

        # Sauvegarder progressivement tous les 10 villes
        if (i + 1) % 10 == 0:
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(cities, f, ensure_ascii=False, indent=2)
            print(f"  💾 Sauvegarde intermédiaire ({i+1}/{len(cities_without_pois)})")

    # Sauvegarder final
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Enrichissement terminé !")
    print(f"📄 Sauvegardé dans {input_path}")

    # Stats finales
    with_pois = sum(1 for c in cities if c.get("pois"))
    print(f"   📍 {with_pois}/{len(cities)} villes avec POIs")


if __name__ == "__main__":
    main()
