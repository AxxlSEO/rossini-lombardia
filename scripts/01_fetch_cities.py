#!/usr/bin/env python3
"""
Étape 1 : Récupérer toutes les villes de Lombardie avec +10.000 habitants.
Source: GeoNames API (compte gratuit requis)
Fallback: Wikidata SPARQL (pas de compte requis)
"""

import json
import os
import sys
import time
import requests
import unicodedata
import re

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import *


def slugify(text):
    """Convertit un nom de ville en slug URL-friendly."""
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text


def fetch_from_wikidata():
    """
    Récupère les villes de Lombardie via Wikidata SPARQL.
    Pas besoin de compte — méthode recommandée.
    """
    print("📡 Récupération des villes via Wikidata SPARQL...")

    query = """
    SELECT ?city ?cityLabel ?population ?coordinates ?province ?provinceLabel ?postalCode ?area WHERE {
      ?city wdt:P31 wd:Q747074 .            # instance of: comune of Italy
      ?city wdt:P131* wd:Q1210 .             # located in: Lombardy (recursive)
      ?city wdt:P1082 ?population .          # population
      OPTIONAL { ?city wdt:P625 ?coordinates . }
      OPTIONAL { ?city wdt:P131 ?province . ?province wdt:P31 wd:Q15089 . }
      OPTIONAL { ?city wdt:P281 ?postalCode . }
      OPTIONAL { ?city wdt:P2046 ?area . }
      FILTER(?population >= 10000)
      SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en" . }
    }
    ORDER BY DESC(?population)
    """

    url = "https://query.wikidata.org/sparql"
    headers = {
        "Accept": "application/json",
        "User-Agent": "RossiniEnergySEO/1.0 (info@rossinienergy.com)"
    }

    response = requests.get(url, params={"query": query}, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()

    cities = []
    seen = set()

    for item in data["results"]["bindings"]:
        name = item["cityLabel"]["value"]
        if name in seen:
            continue
        seen.add(name)

        # Parse coordinates
        lat, lng = None, None
        if "coordinates" in item:
            coords = item["coordinates"]["value"]
            # Format: Point(lng lat)
            match = re.search(r'Point\(([-\d.]+)\s+([-\d.]+)\)', coords)
            if match:
                lng = float(match.group(1))
                lat = float(match.group(2))

        city = {
            "name": name,
            "slug": slugify(name),
            "population": int(float(item["population"]["value"])),
            "latitude": lat,
            "longitude": lng,
            "province": item.get("provinceLabel", {}).get("value", ""),
            "postal_code": item.get("postalCode", {}).get("value", ""),
            "area_km2": round(float(item["area"]["value"]), 1) if "area" in item else None,
            "wikidata_id": item["city"]["value"].split("/")[-1],
            "region": "Lombardia",
            "country": "IT"
        }
        cities.append(city)

    return cities


def fetch_from_geonames():
    """
    Récupère les villes via GeoNames API.
    Nécessite un compte gratuit (username dans config.py).
    """
    if GEONAMES_USERNAME == "YOUR_USERNAME":
        print("⚠️  GeoNames username non configuré, passage à Wikidata...")
        return None

    print("📡 Récupération des villes via GeoNames API...")

    # Code admin1 pour Lombardie dans GeoNames : 09
    url = "http://api.geonames.org/searchJSON"
    params = {
        "country": "IT",
        "adminCode1": "09",  # Lombardia
        "featureClass": "P",
        "featureCode": "PPL",
        "maxRows": 500,
        "orderby": "population",
        "username": GEONAMES_USERNAME
    }

    cities = []
    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    if "geonames" not in data:
        print(f"❌ Erreur GeoNames: {data}")
        return None

    for g in data["geonames"]:
        pop = g.get("population", 0)
        if pop < MIN_POPULATION:
            continue

        city = {
            "name": g["name"],
            "slug": slugify(g["name"]),
            "population": pop,
            "latitude": float(g["lat"]),
            "longitude": float(g["lng"]),
            "province": g.get("adminName2", ""),
            "postal_code": "",
            "area_km2": None,
            "geonames_id": g["geonameId"],
            "region": "Lombardia",
            "country": "IT"
        }
        cities.append(city)

    return cities


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Essayer GeoNames d'abord, sinon Wikidata
    cities = fetch_from_geonames()
    if not cities:
        cities = fetch_from_wikidata()

    if not cities:
        print("❌ Aucune ville récupérée !")
        sys.exit(1)

    # Dédupliquer par slug
    seen_slugs = set()
    unique_cities = []
    for c in cities:
        if c["slug"] not in seen_slugs:
            seen_slugs.add(c["slug"])
            unique_cities.append(c)
    cities = unique_cities

    # Trier par population décroissante
    cities.sort(key=lambda x: x["population"], reverse=True)

    # Sauvegarder
    output_path = os.path.join(DATA_DIR, "cities_lombardia.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(cities)} villes trouvées en Lombardie (+{MIN_POPULATION} habitants)")
    print(f"📄 Sauvegardé dans {output_path}")
    print(f"\n🏙️ Top 10 :")
    for i, c in enumerate(cities[:10], 1):
        print(f"   {i}. {c['name']} — {c['population']:,} hab. ({c['province']})")


if __name__ == "__main__":
    main()
