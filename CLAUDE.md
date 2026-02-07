# CLAUDE.md — Instructions pour Claude Code

## Vue d'ensemble du projet
Site de référencement local pour **Rossini Energy** (bornes de recharge EV + carports solaires) ciblant les villes de Lombardie, Italie, avec +10.000 habitants.

## Stack technique
- Python 3 + Jinja2 pour la génération de pages statiques
- APIs gratuites : Wikidata SPARQL, Open-Meteo, Overpass (OSM), Wikipedia IT
- HTML/CSS statique (pas de framework JS)

## Comment exécuter
```bash
pip install requests jinja2
python scripts/01_fetch_cities.py       # Fetch villes Lombardie
python scripts/02_fetch_enrichment.py   # Enrichir données (API calls - ~2min)
python scripts/03_generate_html.py      # Générer HTML
python scripts/04_generate_sitemap.py   # Générer sitemap
```

## Structure des fichiers
- `scripts/config.py` — Configuration (domaine, infos entreprise, paramètres)
- `scripts/01_fetch_cities.py` — Récupère les villes via Wikidata SPARQL
- `scripts/02_fetch_enrichment.py` — Enrichit avec climat, POIs, descriptions
- `scripts/03_generate_html.py` — Génère les pages HTML via Jinja2
- `scripts/04_generate_sitemap.py` — Génère sitemap.xml
- `templates/` — Templates Jinja2 (city_template.html, index_template.html)
- `output/` — Site statique généré (à déployer)

## Conventions
- Les slugs de ville sont en minuscules ASCII sans accents
- Le contenu des pages est en italien
- Les données brutes sont dans `data/` au format JSON
- Le maillage interne entre villes utilise la distance haversine (rayon 50km)

## Commandes utiles
- Tester le site localement : `cd output && python -m http.server 8000`
- Compter les pages : `ls output/citta/*.html | wc -l`
- Vérifier le JSON-LD : chercher `<script type="application/ld+json">` dans les pages
