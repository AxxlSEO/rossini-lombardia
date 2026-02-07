#!/usr/bin/env python3
"""
Script pour récupérer les images des villes depuis Wikipedia IT.
"""

import json
import os
import sys
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import DATA_DIR


def fetch_city_image(city_name):
    """
    Récupère l'image d'une ville depuis l'API Wikipedia IT.
    """
    try:
        # Encode le nom de la ville pour l'URL
        encoded_name = city_name.replace(" ", "_")
        url = f"https://it.wikipedia.org/api/rest_v1/page/summary/{encoded_name}"

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            # Essayer thumbnail d'abord, puis originalimage
            if "thumbnail" in data and "source" in data["thumbnail"]:
                return data["thumbnail"]["source"]
            elif "originalimage" in data and "source" in data["originalimage"]:
                return data["originalimage"]["source"]

        return None

    except Exception as e:
        print(f"  ⚠️ Erreur pour {city_name}: {e}")
        return None


def main():
    input_path = os.path.join(DATA_DIR, "cities_enriched.json")

    if not os.path.exists(input_path):
        print(f"❌ Fichier {input_path} introuvable.")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        cities = json.load(f)

    # Identifier les villes sans images
    cities_without_images = [c for c in cities if not c.get("image_url")]

    print(f"📊 Récupération d'images pour {len(cities_without_images)} villes...\n")

    if len(cities_without_images) == 0:
        print("✅ Toutes les villes ont déjà des images !")
        return

    success_count = 0

    for i, city in enumerate(cities_without_images):
        print(f"[{i+1}/{len(cities_without_images)}] {city['name']}...", end=" ")

        # Récupérer l'image
        image_url = fetch_city_image(city["name"])

        if image_url:
            print(f"✅ {image_url[:60]}...")
            success_count += 1

            # Mettre à jour dans la liste complète
            for j, c in enumerate(cities):
                if c["name"] == city["name"]:
                    cities[j]["image_url"] = image_url
                    break
        else:
            print("❌ Aucune image trouvée")

        # Pause pour respecter les limites de l'API
        time.sleep(0.5)

        # Sauvegarder progressivement tous les 20 villes
        if (i + 1) % 20 == 0:
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(cities, f, ensure_ascii=False, indent=2)
            print(f"  💾 Sauvegarde intermédiaire ({i+1}/{len(cities_without_images)})")

    # Sauvegarder final
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Récupération terminée !")
    print(f"📄 Sauvegardé dans {input_path}")

    # Stats finales
    with_images = sum(1 for c in cities if c.get("image_url"))
    print(f"   🖼️  {with_images}/{len(cities)} villes avec images ({success_count} nouvelles)")


if __name__ == "__main__":
    main()
