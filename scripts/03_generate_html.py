#!/usr/bin/env python3
"""
Étape 3 : Générer les pages HTML statiques à partir des données enrichies.
Utilise Jinja2 pour le templating.
"""

import json
import os
import sys
import math
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import *

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("❌ Jinja2 requis: pip install jinja2")
    sys.exit(1)


def haversine_distance(lat1, lon1, lat2, lon2):
    """Distance en km entre deux points GPS."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def find_nearby_cities(target, all_cities, max_count=8, max_distance_km=50):
    """Trouve les villes les plus proches pour le maillage interne."""
    if not target.get("latitude") or not target.get("longitude"):
        return []

    nearby = []
    for city in all_cities:
        if city["slug"] == target["slug"]:
            continue
        if not city.get("latitude") or not city.get("longitude"):
            continue
        dist = haversine_distance(
            target["latitude"], target["longitude"],
            city["latitude"], city["longitude"]
        )
        if dist <= max_distance_km:
            nearby.append((dist, city))

    nearby.sort(key=lambda x: x[0])
    return [c for _, c in nearby[:max_count]]


def main():
    input_path = os.path.join(DATA_DIR, "cities_enriched.json")
    if not os.path.exists(input_path):
        # Fallback sur le fichier non-enrichi
        input_path = os.path.join(DATA_DIR, "cities_lombardia.json")
        if not os.path.exists(input_path):
            print(f"❌ Aucun fichier de données trouvé. Lance d'abord les scripts 01 et 02.")
            sys.exit(1)
        print("⚠️ Utilisation des données non-enrichies (lance 02_fetch_enrichment.py pour plus de contenu)")

    with open(input_path, "r", encoding="utf-8") as f:
        cities = json.load(f)

    # Setup Jinja2
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=False
    )

    city_template = env.get_template("city_template.html")
    index_template = env.get_template("index_template.html")

    year = datetime.now().year
    os.makedirs(os.path.join(OUTPUT_DIR, "citta"), exist_ok=True)

    # === Générer les pages de chaque ville ===
    print(f"🏗️ Génération de {len(cities)} pages ville...\n")

    for i, city in enumerate(cities):
        nearby = find_nearby_cities(city, cities)

        html = city_template.render(
            city=city,
            company=COMPANY,
            domain=DOMAIN,
            year=year,
            nearby_cities=nearby
        )

        output_path = os.path.join(OUTPUT_DIR, "citta", f"{city['slug']}.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"  ✅ {city['name']} → citta/{city['slug']}.html")

    # === Générer la page index ===
    provinces = {}
    for c in cities:
        p = c.get("province", "Altro")
        provinces[p] = provinces.get(p, 0) + 1
    # Trier par nombre de villes
    provinces = dict(sorted(provinces.items(), key=lambda x: -x[1]))

    index_html = index_template.render(
        cities=cities,
        provinces=provinces,
        company=COMPANY,
        domain=DOMAIN,
        year=year
    )

    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"\n  ✅ index.html")

    # === Générer robots.txt ===
    robots = f"""User-agent: *
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
"""
    with open(os.path.join(OUTPUT_DIR, "robots.txt"), "w") as f:
        f.write(robots)
    print(f"  ✅ robots.txt")

    print(f"\n🎉 Site généré avec succès dans /{OUTPUT_DIR}/")
    print(f"   📄 {len(cities)} pages ville + index + robots.txt")


if __name__ == "__main__":
    main()
