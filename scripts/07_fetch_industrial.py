#!/usr/bin/env python3
"""
Script pour récupérer les données industrielles et de parking via Overpass API.
"""

import json
import os
import sys
import time
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import DATA_DIR


def fetch_industrial_data(lat, lon, city_name):
    """Récupère les données industrielles et de parking via Overpass API."""
    try:
        # Rayon de 5km
        radius = 5000

        # Query Overpass complexe pour toutes les données en une seule requête
        overpass_query = f"""
        [out:json][timeout:25];
        (
          // Zones industrielles
          way["landuse"="industrial"](around:{radius},{lat},{lon});
          relation["landuse"="industrial"](around:{radius},{lat},{lon});

          // Parkings de surface
          node["amenity"="parking"]["parking"="surface"](around:{radius},{lat},{lon});
          way["amenity"="parking"]["parking"="surface"](around:{radius},{lat},{lon});

          // Parkings privés
          node["amenity"="parking"]["access"="private"](around:{radius},{lat},{lon});
          way["amenity"="parking"]["access"="private"](around:{radius},{lat},{lon});

          // Centres commerciaux
          node["shop"="mall"](around:{radius},{lat},{lon});
          way["shop"="mall"](around:{radius},{lat},{lon});
          node["shop"="supermarket"](around:{radius},{lat},{lon});
          way["shop"="supermarket"](around:{radius},{lat},{lon});

          // Zones commerciales
          way["landuse"="commercial"](around:{radius},{lat},{lon});
          relation["landuse"="commercial"](around:{radius},{lat},{lon});
        );
        out body;
        >;
        out skel qt;
        """

        response = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": overpass_query},
            timeout=30
        )

        if response.status_code != 200:
            return None

        data = response.json()
        elements = data.get("elements", [])

        # Analyser les résultats
        industrial_zones = []
        surface_parking = []
        private_parking = []
        malls = []
        commercial_zones = []

        # Map pour stocker les nodes des ways
        nodes_map = {}
        for elem in elements:
            if elem["type"] == "node":
                nodes_map[elem["id"]] = elem

        for elem in elements:
            tags = elem.get("tags", {})

            # Zones industrielles
            if tags.get("landuse") == "industrial":
                if elem["type"] in ["way", "relation"]:
                    industrial_zones.append(elem)

            # Parkings de surface
            if tags.get("amenity") == "parking" and tags.get("parking") == "surface":
                surface_parking.append(elem)

            # Parkings privés
            if tags.get("amenity") == "parking" and tags.get("access") == "private":
                private_parking.append(elem)

            # Centres commerciaux et supermarchés
            if tags.get("shop") in ["mall", "supermarket"]:
                malls.append(elem)

            # Zones commerciales
            if tags.get("landuse") == "commercial":
                if elem["type"] in ["way", "relation"]:
                    commercial_zones.append(elem)

        # Calculer la surface totale des zones industrielles (approximation)
        total_industrial_area = 0
        for zone in industrial_zones:
            if zone["type"] == "way" and "nodes" in zone:
                # Approximation simple : calculer l'aire du polygone
                coords = []
                for node_id in zone["nodes"]:
                    if node_id in nodes_map:
                        node = nodes_map[node_id]
                        coords.append((node["lat"], node["lon"]))

                if len(coords) >= 3:
                    # Formule de Shoelace pour calculer l'aire
                    area = calculate_polygon_area(coords)
                    total_industrial_area += area

        # Convertir en hectares (1 hectare = 10,000 m²)
        industrial_area_hectares = round(total_industrial_area / 10000, 1)

        return {
            "industrial_zones_count": len(industrial_zones),
            "industrial_area_hectares": industrial_area_hectares,
            "surface_parking_count": len(surface_parking),
            "private_parking_count": len(private_parking),
            "commercial_zones_count": len(commercial_zones),
            "malls_count": len(malls)
        }

    except Exception as e:
        print(f"  ⚠️ Erreur Overpass: {e}")
        return None


def calculate_polygon_area(coords):
    """
    Calcule l'aire d'un polygone en m² à partir de coordonnées lat/lon.
    Utilise la formule de Shoelace avec conversion en mètres.
    """
    if len(coords) < 3:
        return 0

    # Conversion approximative : 1° lat ≈ 111km, 1° lon ≈ 111km * cos(lat)
    # On prend la latitude moyenne
    avg_lat = sum(c[0] for c in coords) / len(coords)
    lat_to_m = 111000  # mètres par degré de latitude
    lon_to_m = 111000 * abs(cosine(avg_lat))  # mètres par degré de longitude

    # Convertir en coordonnées métriques
    coords_m = [(lat * lat_to_m, lon * lon_to_m) for lat, lon in coords]

    # Formule de Shoelace
    area = 0
    for i in range(len(coords_m)):
        j = (i + 1) % len(coords_m)
        area += coords_m[i][0] * coords_m[j][1]
        area -= coords_m[j][0] * coords_m[i][1]

    return abs(area) / 2


def cosine(degrees):
    """Calcule le cosinus d'un angle en degrés."""
    import math
    return math.cos(math.radians(degrees))


def main():
    input_path = os.path.join(DATA_DIR, "cities_enriched.json")

    if not os.path.exists(input_path):
        print(f"❌ Fichier {input_path} introuvable.")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        cities = json.load(f)

    # Villes sans données industrielles
    cities_without_industry = [c for c in cities if not c.get("industry")]

    print(f"📊 Récupération données industrielles pour {len(cities_without_industry)} villes...\n")

    if len(cities_without_industry) == 0:
        print("✅ Toutes les villes ont déjà des données industrielles !")
        return

    success_count = 0

    for i, city in enumerate(cities_without_industry):
        if not city.get("latitude") or not city.get("longitude"):
            print(f"[{i+1}/{len(cities_without_industry)}] {city['name']} ⏭️  Pas de coordonnées")
            continue

        print(f"[{i+1}/{len(cities_without_industry)}] {city['name']}...", end=" ")

        industry_data = fetch_industrial_data(
            city["latitude"],
            city["longitude"],
            city["name"]
        )

        if industry_data:
            zones = industry_data['industrial_zones_count']
            area = industry_data['industrial_area_hectares']
            parking = industry_data['surface_parking_count']
            print(f"✅ {zones} zones ind., {area}ha, {parking} parkings")
            success_count += 1

            # Mettre à jour dans la liste complète
            for j, c in enumerate(cities):
                if c["name"] == city["name"]:
                    cities[j]["industry"] = industry_data
                    break
        else:
            print("❌ Échec")

        # Pause pour respecter rate limit Overpass (3 secondes)
        time.sleep(3)

        # Sauvegarder progressivement tous les 10 villes
        if (i + 1) % 10 == 0:
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(cities, f, ensure_ascii=False, indent=2)
            print(f"  💾 Sauvegarde intermédiaire ({i+1}/{len(cities_without_industry)})")

    # Sauvegarder final
    with open(input_path, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Récupération terminée !")
    print(f"📄 Sauvegardé dans {input_path}")

    # Stats finales
    with_industry = sum(1 for c in cities if c.get("industry"))
    print(f"   🏭 {with_industry}/{len(cities)} villes avec données industrielles ({success_count} nouvelles)")


if __name__ == "__main__":
    main()
