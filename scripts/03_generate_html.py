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


def get_seo_title(city_name, province, city_index):
    """Génère un title SEO avec rotation (5 variantes)."""
    titles = [
        f"Tettoia Fotovoltaica per Parcheggio a {city_name} | Rossini Energy",
        f"Pensilina Fotovoltaica a {city_name}, {province} - Preventivo Gratuito | Rossini Energy",
        f"Parcheggio Fotovoltaico a {city_name} | Installazione Chiavi in Mano | Rossini Energy",
        f"Installatore Pensiline Fotovoltaiche a {city_name} | Rossini Energy",
        f"Tettoia Solare per Parcheggio Aziendale a {city_name} | Rossini Energy"
    ]
    return titles[city_index % 5]


def get_seo_description(city_name, province, city_index):
    """Génère une meta description SEO avec rotation (5 variantes)."""
    descriptions = [
        f"Rossini Energy installa tettoie fotovoltaiche per parcheggi aziendali a {city_name}. Struttura in legno, pannelli bifacciali. Preventivo gratuito.",
        f"Pensilina fotovoltaica a {city_name}: trasforma il parcheggio della tua azienda in una fonte di energia rinnovabile. Installazione chiavi in mano.",
        f"Parcheggio fotovoltaico a {city_name}, {province}. Riduci i costi energetici della tua azienda con le pensiline solari TOSSO® di Rossini Energy.",
        f"Installazione tettoie fotovoltaiche per aziende e PMI a {city_name}. Legno Douglas, pannelli bifacciali. Contattaci per un sopralluogo gratuito.",
        f"Copri il parcheggio della tua azienda a {city_name} con una pensilina fotovoltaica. Energia solare + protezione veicoli. Rossini Energy."
    ]
    return descriptions[city_index % 5]


def get_h1_text(city_name, city_index):
    """Génère un H1 avec rotation (3 variantes)."""
    h1_variants = [
        f"Tettoia Fotovoltaica per Parcheggio a <strong>{city_name}</strong>",
        f"Pensilina Fotovoltaica a <strong>{city_name}</strong>",
        f"Parcheggio Fotovoltaico a <strong>{city_name}</strong>"
    ]
    return h1_variants[city_index % 3]


def generate_unique_city_content(city):
    """Génère un contenu unique pour chaque ville basé sur ses données."""
    city_name = city.get("name", "")
    province = city.get("province", "")
    population = city.get("population", 0)
    has_pois = bool(city.get("pois"))
    parking_count = city.get("pois", {}).get("parking_count", 0) if has_pois else 0
    ev_stations = city.get("pois", {}).get("ev_charging_stations", 0) if has_pois else 0

    # Titre H2 unique basé sur les caractéristiques de la ville
    if population > 100000:
        h2 = f"Pensiline Fotovoltaiche per Grandi Aziende a {city_name}"
        intro = f"{city_name}, con oltre {population:,} abitanti, è un polo industriale importante della provincia di {province}. "
        intro += "Le grandi aziende locali possono ridurre significativamente i costi energetici installando tettoie fotovoltaiche sui parcheggi dipendenti. "
    elif population > 50000:
        h2 = f"Installazione Tettoie Fotovoltaiche per PMI a {city_name}"
        intro = f"A {city_name} ({province}), molte PMI stanno investendo in soluzioni di energia rinnovabile. "
        intro += "Le pensiline fotovoltaiche TOSSO® rappresentano un investimento intelligente per ridurre le bollette energetiche e valorizzare gli spazi esterni. "
    else:
        h2 = f"Parcheggi Fotovoltaici per Aziende a {city_name}"
        intro = f"Anche le aziende di {city_name} possono beneficiare dell'energia solare. "
        intro += "Installare una tettoia fotovoltaica sul parcheggio aziendale significa produrre energia pulita e proteggere i veicoli dalle intemperie. "

    # Contenu basé sur les POIs disponibles
    if has_pois and parking_count > 0:
        intro += f"La città conta {parking_count} parcheggi censiti, molti dei quali potrebbero essere convertiti in impianti di produzione solare. "

    if has_pois and ev_stations > 0:
        intro += f"Con {ev_stations} punti di ricarica già presenti, {city_name} mostra una crescente attenzione alla mobilità elettrica. "
        intro += "Le nostre tettoie fotovoltaiche integrano colonnine di ricarica EV direttamente nella struttura. "
    else:
        intro += "Rossini Energy può installare pensiline fotovoltaiche con colonnine di ricarica integrate, preparando la tua azienda al futuro della mobilità elettrica. "

    # Avantages spécifiques
    benefits = "I vantaggi per la tua azienda: produzione di energia solare autoconsumata, riduzione dei costi energetici fino al 70%, "
    benefits += "protezione dei veicoli dipendenti, valorizzazione dell'immagine aziendale green, "
    benefits += "e possibilità di ricarica veicoli elettrici direttamente sul posto di lavoro."

    return {
        "h2": h2,
        "intro": intro,
        "benefits": benefits
    }


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

        # SEO dynamique avec rotation
        seo_title = get_seo_title(city["name"], city.get("province", ""), i)
        seo_description = get_seo_description(city["name"], city.get("province", ""), i)
        h1_text = get_h1_text(city["name"], i)

        # Contenu unique généré
        unique_content = generate_unique_city_content(city)

        html = city_template.render(
            city=city,
            company=COMPANY,
            domain=DOMAIN,
            year=year,
            nearby_cities=nearby,
            seo_title=seo_title,
            seo_description=seo_description,
            h1_text=h1_text,
            unique_content=unique_content
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
