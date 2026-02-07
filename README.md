# 🇮🇹 Rossini Energy — SEO Local Lombardia

Site de référencement local pour **Rossini Energy** ciblant toutes les villes de Lombardie (Italie) avec +10.000 habitants.

**Objectif** : Générer des leads pour l'installation de bornes de recharge EV et carports solaires photovoltaïques (TOSSO®).

## 📁 Structure du projet

```
rossini-lombardia/
├── scripts/
│   ├── 01_fetch_cities.py        # Récupère les villes de Lombardie (+10k hab.)
│   ├── 02_fetch_enrichment.py    # Enrichit avec Wikidata, Open-Meteo, OSM
│   ├── 03_generate_html.py       # Génère les pages HTML statiques
│   └── 04_generate_sitemap.py    # Génère sitemap.xml
├── templates/
│   └── city_template.html        # Template HTML des pages ville
├── data/
│   ├── cities_lombardia.json     # Liste des villes (sortie étape 1)
│   └── cities_enriched.json      # Données enrichies (sortie étape 2)
├── output/                       # Site statique final
│   ├── index.html
│   ├── sitemap.xml
│   ├── robots.txt
│   ├── assets/
│   │   ├── css/style.css
│   │   ├── js/main.js
│   │   └── img/
│   └── citta/
│       ├── milano.html
│       ├── brescia.html
│       └── ...
└── README.md
```

## 🚀 Setup & Exécution

### Prérequis
```bash
pip install requests jinja2
```

### Étape par étape
```bash
# 1. Récupérer la liste des villes de Lombardie +10k habitants
python scripts/01_fetch_cities.py

# 2. Enrichir avec données APIs (Wikidata, climat, POIs)
python scripts/02_fetch_enrichment.py

# 3. Générer les pages HTML
python scripts/03_generate_html.py

# 4. Générer le sitemap
python scripts/04_generate_sitemap.py
```

## 🔌 APIs utilisées (toutes gratuites)

| API | Données | Limite |
|-----|---------|--------|
| **GeoNames** | Villes, population, coordonnées, codes postaux | 1000 req/h (compte gratuit) |
| **Wikidata SPARQL** | Descriptions, histoire, superficie, altitude | Illimité |
| **Open-Meteo** | Climat annuel (T° moy, précipitations) | Illimité |
| **Overpass (OSM)** | POIs : stations essence, parkings, centres commerciaux | Fair use |
| **Wikimedia Commons** | Images libres de droit des villes | Illimité |

## 📝 Configuration

### GeoNames
1. Créer un compte gratuit sur https://www.geonames.org/login
2. Activer le web service dans "Manage Account"
3. Mettre le username dans `scripts/config.py`

### Domaine cible
Modifier `DOMAIN` dans `scripts/config.py` pour le domaine de production.

## 🎯 SEO Features
- Pages statiques ultra-rapides
- JSON-LD Schema (LocalBusiness + City)
- Balises title/description optimisées par ville
- Sitemap XML auto-généré
- Structure URLs propre : `/citta/nome-citta.html`
- Maillage interne entre villes proches
- Données locales uniques par page (climat, POIs, stats)
