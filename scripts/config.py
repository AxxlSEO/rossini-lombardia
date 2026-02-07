# === Configuration ===

# Domaine de production (modifier pour le déploiement)
DOMAIN = "https://lombardia.rossinienergy.it"

# GeoNames username (créer un compte gratuit sur geonames.org)
GEONAMES_USERNAME = "YOUR_USERNAME"

# Infos Rossini Energy
COMPANY = {
    "name": "Rossini Energy",
    "legal_name": "Rossini Energy SAS",
    "url": "https://rossinienergy.com",
    "phone": "+33 (0)3 74 09 01 05",
    "email": "info@rossinienergy.com",
    "logo": "https://rossinienergy.com/logo.png",
    "address_it": {
        "street": "Piazza Torre Sacchetti, 73",
        "city": "Stradella",
        "province": "PV",
        "postal_code": "27049",
        "country": "IT"
    },
    "services": [
        {
            "name_it": "Installazione Colonnine di Ricarica EV",
            "name_fr": "Installation de bornes de recharge EV",
            "description_it": "Installazione di stazioni di ricarica per veicoli elettrici da 7kW a 22kW, in legno di Douglas o alluminio riciclato.",
            "keywords": ["colonnina di ricarica", "ricarica veicoli elettrici", "borne de recharge", "EV charging"]
        },
        {
            "name_it": "Pensiline Fotovoltaiche TOSSO®",
            "name_fr": "Carports solaires photovoltaïques TOSSO®",
            "description_it": "Pensiline per parcheggi con pannelli fotovoltaici bifacciali, struttura in legno sostenibile.",
            "keywords": ["pensilina fotovoltaica", "carport solare", "ombrière photovoltaïque", "TOSSO"]
        },
        {
            "name_it": "Software di Gestione Ricarica",
            "name_fr": "Logiciel de gestion de recharge",
            "description_it": "Piattaforma software per il pilotaggio dinamico della ricarica e gestione dell'energia solare.",
            "keywords": ["gestione ricarica", "pilotage dynamique", "software energia"]
        }
    ]
}

# Région cible
REGION = "Lombardia"
COUNTRY = "IT"
MIN_POPULATION = 10000

# Chemins
DATA_DIR = "data"
OUTPUT_DIR = "output"
TEMPLATES_DIR = "templates"
