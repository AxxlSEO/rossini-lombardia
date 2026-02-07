#!/usr/bin/env python3
"""
Étape 4 : Générer le sitemap.xml pour le site.
"""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import *


def main():
    input_path = os.path.join(DATA_DIR, "cities_enriched.json")
    if not os.path.exists(input_path):
        input_path = os.path.join(DATA_DIR, "cities_lombardia.json")

    if not os.path.exists(input_path):
        print("❌ Aucun fichier de données trouvé.")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        cities = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")

    urls = []

    # Page d'accueil
    urls.append({
        "loc": f"{DOMAIN}/index.html",
        "lastmod": today,
        "changefreq": "weekly",
        "priority": "1.0"
    })

    # Pages ville
    for city in cities:
        # Priorité basée sur la population
        if city["population"] > 100000:
            priority = "0.9"
        elif city["population"] > 50000:
            priority = "0.8"
        else:
            priority = "0.7"

        urls.append({
            "loc": f"{DOMAIN}/citta/{city['slug']}.html",
            "lastmod": today,
            "changefreq": "monthly",
            "priority": priority
        })

    # Construire le XML
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url in urls:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{url['loc']}</loc>")
        xml_lines.append(f"    <lastmod>{url['lastmod']}</lastmod>")
        xml_lines.append(f"    <changefreq>{url['changefreq']}</changefreq>")
        xml_lines.append(f"    <priority>{url['priority']}</priority>")
        xml_lines.append("  </url>")

    xml_lines.append("</urlset>")

    output_path = os.path.join(OUTPUT_DIR, "sitemap.xml")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(xml_lines))

    print(f"✅ Sitemap généré : {output_path}")
    print(f"   📍 {len(urls)} URLs ({len(cities)} villes + index)")


if __name__ == "__main__":
    main()
