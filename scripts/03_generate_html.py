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
from scripts import variants as V

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("❌ Jinja2 requis: pip install jinja2")
    sys.exit(1)


def normalize_province(province_raw):
    """
    Normalise le nom de province pour éviter duplication de 'provincia di'.
    Si la province contient déjà 'provincia di', la retourne telle quelle.
    Sinon, retourne juste le nom sans préfixe.
    """
    if not province_raw or not province_raw.strip():
        return ""

    province = province_raw.strip()

    # Si déjà préfixé avec "provincia di", retourner tel quel
    if province.startswith("provincia di ") or province.startswith("Provincia di "):
        return province

    # Sinon, retourner sans préfixe (sera ajouté dans le template si nécessaire)
    return province


def fix_image_url(image_url):
    """
    Convertit les URLs Wikimedia Commons en URLs HTTPS directes.
    commons.wikimedia.org/wiki/Special:FilePath/ → upload.wikimedia.org
    """
    if not image_url:
        return ""

    # Convertir HTTP en HTTPS
    image_url = image_url.replace("http://", "https://")

    # Convertir les URLs Special:FilePath en URLs directes
    if "commons.wikimedia.org/wiki/Special:FilePath/" in image_url:
        # Extraire le nom du fichier
        filename = image_url.split("/Special:FilePath/")[-1]
        # Retourner l'URL directe (upload.wikimedia.org nécessite un hash MD5,
        # mais on peut garder l'URL FilePath en HTTPS qui redirige correctement)
        return f"https://commons.wikimedia.org/wiki/Special:FilePath/{filename}"

    return image_url


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


def get_seo_title(city_name):
    """Title unique, aligné sur le H1 (pas de rotation)."""
    return f"Pensilina Fotovoltaica a {city_name}: Parcheggi Aziendali | Rossini Energy"


def get_seo_description(city_name, solar_annual_str):
    """Meta description unique, différenciée par le chiffre PVGIS local."""
    if solar_annual_str:
        return (f"Rossini Energy installa pensiline fotovoltaiche per parcheggi aziendali a {city_name}: "
                f"un impianto da 30 kWp produce fino a {solar_annual_str} kWh/anno. Preventivo gratuito.")
    return (f"Rossini Energy installa pensiline fotovoltaiche per parcheggi aziendali a {city_name}. "
            f"Sopralluogo e preventivo gratuiti, installazione chiavi in mano.")


def get_h1_text(city_name):
    """H1 unique, aligné sur le title."""
    return f"Pensilina Fotovoltaica a <strong>{city_name}</strong>"


def get_city_profile(city):
    """
    Classifie les villes en 6 profils basés sur leurs caractéristiques.

    Profils:
    A - Metropoli: grandes villes > 100k habitants
    B - Polo industriale: forte présence industrielle
    C - Centro commerciale: forte présence commerciale
    D - Residenziale: principalement résidentiel
    E - Turistico: indicateurs touristiques
    F - Capoluogo: chef-lieu de province
    """
    population = city.get("population", 0)
    province = city.get("province", "")
    name = city.get("name", "")

    # Données industrielles
    industry = city.get("industry", {})
    industrial_zones = industry.get("industrial_zones_count", 0)
    industrial_area = industry.get("industrial_area_hectares", 0)
    commercial_zones = industry.get("commercial_zones_count", 0)
    malls = industry.get("malls_count", 0)

    # POIs
    pois = city.get("pois", {})
    hotels = pois.get("hotels_count", 0)

    # Liste des chefs-lieux de province lombards
    capoluoghi = [
        "Milano", "Brescia", "Bergamo", "Como", "Cremona", "Lecco",
        "Lodi", "Mantova", "Monza", "Pavia", "Sondrio", "Varese"
    ]

    # Villes touristiques connues (Lac de Garde, Lac de Côme, etc.)
    tourist_cities = [
        "Desenzano del Garda", "Salò", "Lonato del Garda",
        "Sirmione", "Limone sul Garda", "Gardone Riviera",
        "Bellagio", "Menaggio", "Varenna", "Tremezzina"
    ]

    # Profil A - Metropoli
    if population > 100000:
        return "A", "Metropoli"

    # Profil E - Turistico (vérifier avant industriel/commercial)
    if name in tourist_cities or hotels > 10:
        return "E", "Turistico"

    # Profil B - Polo industriale
    if industrial_zones > 100 or industrial_area > 300:
        return "B", "Polo industriale"

    # Profil C - Centro commerciale
    if commercial_zones > 30 or malls > 3:
        return "C", "Centro commerciale"

    # Profil F - Capoluogo
    if name in capoluoghi:
        return "F", "Capoluogo"

    # Profil D - Residenziale (par défaut)
    return "D", "Residenziale"


MESI_IT = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
           "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]


def fmt_kwh(v):
    return "{:,.0f}".format(v).replace(",", ".")


def build_faqs(city, solar_annual_str):
    """4-5 FAQ par ville : socle (production locale + tempi) en variantes stables,
    + questions conditionnelles selon les données réelles, + compléments."""
    name = city["name"]
    slug = city["slug"]
    fmt = {"name": name, "annual": solar_annual_str}

    def take(section, options):
        q, a = V.pick(slug, section, options)
        return {"q": q.format(**fmt), "a": a.format(**fmt)}

    faqs = []
    if solar_annual_str:
        faqs.append(take("faq_prod", V.FAQ_PRODUZIONE))
    faqs.append(take("faq_tempi", V.FAQ_TEMPI))

    extra = []
    industry = city.get("industry", {}) or {}
    pois = city.get("pois", {}) or {}
    code, _ = get_city_profile(city)
    if code == "F":
        extra.append(take("faq_enti", V.FAQ_ENTI))
    if industry.get("industrial_zones_count", 0) > 50:
        extra.append(take("faq_ind", V.FAQ_INDUSTRIA))
    if industry.get("malls_count", 0) > 1 or industry.get("commercial_zones_count", 0) > 30:
        extra.append(take("faq_comm", V.FAQ_COMMERCIO))
    if pois.get("hotels_count", 0) > 10:
        extra.append(take("faq_tur", V.FAQ_TURISMO))
    for section, options in (("faq_inc", V.FAQ_INCENTIVI), ("faq_perm", V.FAQ_PERMESSI),
                             ("faq_pmi", V.FAQ_PMI), ("faq_spazio", V.FAQ_SPAZIO),
                             ("faq_manu", V.FAQ_MANUTENZIONE)):
        extra.append(take(section, options))

    total = 4 + (int(__import__("hashlib").md5(slug.encode()).hexdigest(), 16) % 2)
    return (faqs + extra)[:total]


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

    intel_path = os.path.join(DATA_DIR, "local_intel.json")
    intel = json.load(open(intel_path)) if os.path.exists(intel_path) else {}
    content_path = os.path.join(DATA_DIR, "local_content.json")
    local_content = json.load(open(content_path)) if os.path.exists(content_path) else {}

    year = datetime.now().year
    os.makedirs(os.path.join(OUTPUT_DIR, "citta"), exist_ok=True)

    # === Filtrer : pages complètes vs stubs de redirection ===
    kept = [c for c in cities if keeps_page(c)]
    kept_slugs = {c["slug"] for c in kept}
    dropped = [c for c in cities if c["slug"] not in kept_slugs]

    # === Générer les pages de chaque ville gardée ===
    # NB : on énumère la liste complète pour préserver l'index i (rotation des
    # titles/descriptions) et donc la stabilité des pages existantes.
    print(f"🏗️ Génération de {len(kept)} pages ville (sur {len(cities)})...\n")

    for i, city in enumerate(cities):
        if city["slug"] not in kept_slugs:
            continue
        nearby = find_nearby_cities(city, kept)

        # Normaliser la province
        province_normalized = normalize_province(city.get("province", ""))
        image_url_fixed = fix_image_url(city.get("image_url", ""))
        slug = city["slug"]

        # Données solaires locales (PVGIS) — différenciateur réel
        solar = city.get("solar") or {}
        solar_annual = fmt_kwh(solar["annual_production_kwh"]) if solar.get("annual_production_kwh") else ""
        solar_monthly = ""
        monthly = solar.get("monthly_production") or []
        if len(monthly) == 12:
            mn = min(range(12), key=lambda m: monthly[m])
            mx = max(range(12), key=lambda m: monthly[m])
            solar_monthly = V.pick(slug, "solar_monthly", V.SOLAR_MONTHLY).format(
                mmin=fmt_kwh(monthly[mn]), mmin_name=MESI_IT[mn],
                mmax=fmt_kwh(monthly[mx]), mmax_name=MESI_IT[mx])

        prov_virgola = f", {province_normalized}" if province_normalized else ""
        prov_parentesi = f" ({province_normalized})" if province_normalized else ""
        fmt = {"name": city["name"], "prov_virgola": prov_virgola,
               "prov_parentesi": prov_parentesi, "annual": solar_annual}

        pois = city.get("pois", {}) or {}
        ev = pois.get("ev_charging_stations", 0)
        pois_options = V.POIS_P1_FEW if ev < 10 else V.POIS_P1_MANY

        html = city_template.render(
            city=city, company=COMPANY, domain=DOMAIN, year=year,
            nearby_cities=nearby,
            seo_title=get_seo_title(city["name"]),
            seo_description=get_seo_description(city["name"], solar_annual),
            h1_text=get_h1_text(city["name"]),
            hero_subtitle=V.pick(slug, "hero", V.HERO_SUBTITLE).format(**fmt),
            intro_p1=V.pick(slug, "p1", V.INTRO_P1).format(**fmt),
            intro_p2=V.pick(slug, "p2", V.INTRO_P2).format(**fmt),
            benefits=V.pick(slug, "benefits", V.BENEFITS).format(**fmt),
            solar_p=V.pick(slug, "solar_p", V.SOLAR_P).format(**fmt),
            solar_monthly=solar_monthly,
            pois_p1=V.pick(slug, "pois1", pois_options).format(
                name=city["name"], ev=ev, parking=pois.get("parking_count", 0)),
            pois_p2=V.pick(slug, "pois2", V.POIS_P2).format(name=city["name"]),
            nearby_intro=V.pick(slug, "nearby", V.NEARBY_INTRO).format(name=city["name"]),
            cta_p=V.pick(slug, "cta", V.CTA_P).format(name=city["name"]),
            services=V.pick(slug, "services", V.SERVICES),
            section_order=V.pick(slug, "order", [
                ["local", "solar", "pois"], ["solar", "local", "pois"], ["solar", "pois", "local"]]),
            local_h2=V.pick(slug, "local_h2", [
                "Il tessuto economico di {name}",
                "{name}: il contesto per le imprese",
                "Un territorio pronto per il fotovoltaico aziendale"]).format(name=city["name"]),
            local_block=(local_content.get(slug) or "") if not isinstance(local_content.get(slug), dict)
                        else local_content[slug].get("html", ""),
            intel=intel.get(slug, {}),
            faqs=build_faqs(city, solar_annual),
            province_normalized=province_normalized,
            image_url_fixed=image_url_fixed,
        )

        output_path = os.path.join(OUTPUT_DIR, "citta", f"{city['slug']}.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"  ✅ {city['name']} → citta/{city['slug']}.html")

    # === Générer les stubs de redirection pour les villes retirées ===
    capoluoghi_cities = [c for c in cities if c["slug"] in CAPOLUOGHI_SLUGS]
    milano = next(c for c in capoluoghi_cities if c["slug"] == "milano")

    def nearest_capoluogo(city):
        if not city.get("latitude") or not city.get("longitude"):
            return milano
        return min(capoluoghi_cities, key=lambda c: haversine_distance(
            city["latitude"], city["longitude"], c["latitude"], c["longitude"]))

    print(f"\n↪️ Génération de {len(dropped)} stubs de redirection...")
    for city in dropped:
        target = nearest_capoluogo(city)
        target_url = f"{DOMAIN}/citta/{target['slug']}.html"
        stub = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="utf-8">
    <title>Pagina spostata — Pensiline Fotovoltaiche a {target['name']}</title>
    <meta http-equiv="refresh" content="0; url={target_url}">
    <link rel="canonical" href="{target_url}">
</head>
<body>
    <p>Questa pagina è stata spostata. <a href="{target_url}">Continua verso {target['name']}</a>.</p>
</body>
</html>
"""
        with open(os.path.join(OUTPUT_DIR, "citta", f"{city['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(stub)

    # === Générer la page index (villes gardées uniquement) ===
    provinces = {}
    for c in kept:
        p = c.get("province", "Altro")
        provinces[p] = provinces.get(p, 0) + 1
    # Trier par nombre de villes
    provinces = dict(sorted(provinces.items(), key=lambda x: -x[1]))

    index_html = index_template.render(
        cities=kept,
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
    print(f"   📄 {len(kept)} pages ville + {len(dropped)} stubs de redirection + index + robots.txt")


if __name__ == "__main__":
    main()
