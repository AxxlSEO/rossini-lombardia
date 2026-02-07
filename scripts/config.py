# === Configuration ===

# Domaine de production (modifier pour le déploiement)
DOMAIN = "https://lombardia.rossinienergy.it"

# GeoNames username (créer un compte gratuit sur geonames.org)
GEONAMES_USERNAME = "YOUR_USERNAME"

# Infos Rossini Energy
COMPANY = {
    "name": "Rossini Energy",
    "legal_name": "Rossini Energy SAS",
    "url": "https://rossinienergy.it",
    "phone": "+39 351 591 0020",
    "email": "commerciale@rossinienergy.com",
    "logo": "https://rossinienergy.it/wp-content/uploads/2022/01/cropped-logo.png",
    "logo_mobile": "https://rossinienergy.it/wp-content/uploads/2020/09/Logo_Mobile-02.png",
    "rdv_url": "https://meetings.hubspot.com/arata-lorenzo",
    "address_it": {
        "street": "Via Dante Alighieri 10",
        "city": "Corvino San Quirico",
        "province": "PV",
        "postal_code": "27050",
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
