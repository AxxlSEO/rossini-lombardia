#!/usr/bin/env python3
"""
Étape 2 : Enrichir les données des villes avec :
- Wikidata : description, image, site web officiel, altitude
- Open-Meteo : climat annuel (température moyenne, précipitations)
- Overpass (OSM) : POIs pertinents (stations-service, parkings, centres commerciaux, supermarchés)
"""

import json
import os
import sys
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import *


def enrich_wikidata(city):
    """Récupère description, image et infos complémentaires depuis Wikidata."""
    wikidata_id = city.get("wikidata_id")
    if not wikidata_id:
        return city

    url = "https://query.wikidata.org/sparql"
    query = f"""
    SELECT ?description ?image ?website ?altitude ?inception WHERE {{
      OPTIONAL {{ wd:{wikidata_id} schema:description ?description . FILTER(LANG(?description) = "it") }}
      OPTIONAL {{ wd:{wikidata_id} wdt:P18 ?image . }}
      OPTIONAL {{ wd:{wikidata_id} wdt:P856 ?website . }}
      OPTIONAL {{ wd:{wikidata_id} wdt:P2044 ?altitude . }}
      OPTIONAL {{ wd:{wikidata_id} wdt:P571 ?inception . }}
    }}
    LIMIT 1
    """

    headers = {
        "Accept": "application/json",
        "User-Agent": "RossiniEnergySEO/1.0"
    }

    try:
        resp = requests.get(url, params={"query": query}, headers=headers, timeout=30)
        resp.raise_for_status()
        results = resp.json()["results"]["bindings"]

        if results:
            r = results[0]
            city["description_it"] = r.get("description", {}).get("value", "")
            city["image_url"] = r.get("image", {}).get("value", "")
            city["official_website"] = r.get("website", {}).get("value", "")
            city["altitude_m"] = float(r["altitude"]["value"]) if "altitude" in r else None

    except Exception as e:
        print(f"  ⚠️ Wikidata erreur pour {city['name']}: {e}")

    return city


def enrich_climate(city):
    """Récupère les données climatiques annuelles via Open-Meteo."""
    lat, lng = city.get("latitude"), city.get("longitude")
    if not lat or not lng:
        return city

    url = "https://climate-api.open-meteo.com/v1/climate"
    params = {
        "latitude": lat,
        "longitude": lng,
        "start_date": "2020-01-01",
        "end_date": "2024-12-31",
        "models": "EC_Earth3P_HR",
        "monthly": "temperature_2m_mean,precipitation_sum",
    }

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        monthly = data.get("monthly", {})
        temps = monthly.get("temperature_2m_mean", [])
        precip = monthly.get("precipitation_sum", [])

        if temps:
            city["climate"] = {
                "temp_avg_annual": round(sum(temps) / len(temps), 1),
                "temp_min_month": round(min(temps), 1),
                "temp_max_month": round(max(temps), 1),
                "precipitation_annual_mm": round(sum(precip)) if precip else None
            }

    except Exception as e:
        print(f"  ⚠️ Open-Meteo erreur pour {city['name']}: {e}")

    return city


def enrich_pois(city):
    """
    Récupère les POIs pertinents via Overpass API (OpenStreetMap).
    POIs liés à l'activité de Rossini Energy :
    - Parkings (pour carports solaires)
    - Stations-service (transition énergétique)
    - Centres commerciaux / supermarchés (clients potentiels)
    - Bornes de recharge existantes (concurrence / densité)
    """
    lat, lng = city.get("latitude"), city.get("longitude")
    if not lat or not lng:
        return city

    # Rayon de recherche autour du centre-ville (en mètres)
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

        total = data.get("elements", [{}])[0].get("tags", {}).get("total", 0)
        # On fait une 2ème requête plus détaillée pour les counts par type
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


def get_wikipedia_extract(city_name):
    """Récupère un extrait Wikipedia en italien pour la ville."""
    url = "https://it.wikipedia.org/api/rest_v1/page/summary/" + city_name.replace(" ", "_")
    headers = {"User-Agent": "RossiniEnergySEO/1.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.ok:
            data = resp.json()
            return data.get("extract", "")
    except Exception:
        pass
    return ""


def main():
    input_path = os.path.join(DATA_DIR, "cities_lombardia.json")
    output_path = os.path.join(DATA_DIR, "cities_enriched.json")

    if not os.path.exists(input_path):
        print(f"❌ Fichier {input_path} introuvable. Lance d'abord 01_fetch_cities.py")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        cities = json.load(f)

    print(f"📊 Enrichissement de {len(cities)} villes...\n")

    for i, city in enumerate(cities):
        print(f"[{i+1}/{len(cities)}] {city['name']}...")

        # 1. Wikidata
        city = enrich_wikidata(city)
        time.sleep(0.5)

        # 2. Wikipedia extract
        city["wikipedia_extract"] = get_wikipedia_extract(city["name"])
        time.sleep(0.3)

        # 3. Climat
        city = enrich_climate(city)
        time.sleep(0.3)

        # 4. POIs (attention au rate limit Overpass)
        city = enrich_pois(city)
        time.sleep(2)  # Overpass demande du fair-use

        cities[i] = city

    # Sauvegarder
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Enrichissement terminé !")
    print(f"📄 Sauvegardé dans {output_path}")

    # Stats
    with_desc = sum(1 for c in cities if c.get("wikipedia_extract"))
    with_climate = sum(1 for c in cities if c.get("climate"))
    with_pois = sum(1 for c in cities if c.get("pois"))
    print(f"   📝 {with_desc}/{len(cities)} avec description Wikipedia")
    print(f"   🌡️ {with_climate}/{len(cities)} avec données climat")
    print(f"   📍 {with_pois}/{len(cities)} avec POIs")


if __name__ == "__main__":
    main()
