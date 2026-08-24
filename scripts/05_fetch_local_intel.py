#!/usr/bin/env python3
"""
Étape 5 : Collecter les données locales à forte valeur pour les 41 pages gardées.
Sources (gratuites, throttlées) :
  - ISTAT SDMX  : unità locali attive + addetti par commune (registre ASIA, 2023)
  - Overpass/OSM: NOMS des zones industrielles et centres commerciaux
  - Wikipedia IT: texte de la section « Economia » (matière première rédactionnelle)
  - Wikidata    : entreprises ayant leur siège dans la commune (filtrées)
GSE (impianti FV par commune) : abandonné — site bot-protégé, viewer Atlaimpianti hors ligne.

Sortie : data/local_intel.json (versionné — fetch one-shot, ne pas relancer sans raison).
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.config import DATA_DIR, keeps_page

UA = {"User-Agent": "RossiniLombardia/1.0 (axel@prosition0.fr)"}
ISTAT_FLOW = "183_285_DF_DICA_ASIAULP_7"
# Préfixes provincia des codes ISTAT communaux lombards (évite les homonymes hors région)
LOMBARDIA_PREFIXES = ("012", "013", "014", "015", "016", "017", "018", "019", "020", "097", "098", "108")


def get(url, timeout=60, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")
        except Exception as e:
            if attempt == retries - 1:
                print(f"    ⚠️ échec: {e}")
                return ""
            time.sleep(5 * (attempt + 1))


def istat_city_codes():
    """Nom → code ISTAT 6 chiffres, depuis le codelist du DSD (fichier local si déjà téléchargé)."""
    path = "/tmp/istat_dsd2.xml"
    if not os.path.exists(path):
        raw = get("https://esploradati.istat.it/SDMXWS/rest/datastructure/IT1/DICA_ASIAULP?references=children", 120)
        open(path, "w").write(raw)
    raw = open(path, encoding="utf-8", errors="replace").read()
    codes = {}
    for m in re.finditer(r'<structure:Code id="([0-9]{6})">(.*?)</structure:Code>', raw, re.S):
        code = m.group(1)
        if not code.startswith(LOMBARDIA_PREFIXES):
            continue
        name = re.search(r'<common:Name xml:lang="it">([^<]+)</common:Name>', m.group(2))
        if name:
            codes.setdefault(name.group(1), code)
    return codes


def fetch_istat(code):
    url = (f"https://esploradati.istat.it/SDMXWS/rest/data/{ISTAT_FLOW}/"
           f"A.{code}..0010.TOTAL?lastNObservations=1")
    raw = get(url)
    out = {}
    for s in re.findall(r"<generic:Series>(.*?)</generic:Series>", raw, re.S):
        key = dict(re.findall(r'<generic:Value id="([^"]+)" value="([^"]+)"', s))
        obs = re.search(r'<generic:ObsValue value="([^"]+)"', s)
        year = re.search(r'<generic:ObsDimension id="TIME_PERIOD" value="([^"]+)"', s)
        if obs and key.get("DATA_TYPE") == "LU":
            out["unita_locali"] = int(float(obs.group(1)))
        elif obs and key.get("DATA_TYPE") == "LUEMPDAA":
            out["addetti"] = int(float(obs.group(1)))
        if year:
            out["anno"] = year.group(1)
    return out


def fetch_overpass(city):
    """Noms des zones industrielles et centres commerciaux dans la commune (par zone admin)."""
    q = f"""[out:json][timeout:60];
area["name"="{city['name']}"]["admin_level"="8"]["boundary"="administrative"]->.a;
(
  way["landuse"="industrial"]["name"](area.a);
  relation["landuse"="industrial"]["name"](area.a);
  way["shop"="mall"]["name"](area.a);
  node["shop"="mall"]["name"](area.a);
);
out tags;"""
    raw = get("https://overpass-api.de/api/interpreter?" + urllib.parse.urlencode({"data": q}), 90)
    zones, malls = [], []
    try:
        for el in json.loads(raw).get("elements", []):
            tags = el.get("tags", {})
            name = tags.get("name", "").strip()
            if not name:
                continue
            if tags.get("landuse") == "industrial" and name not in zones:
                zones.append(name)
            elif tags.get("shop") == "mall" and name not in malls:
                malls.append(name)
    except Exception:
        pass
    return {"zone_industriali_nomi": zones[:6], "centri_commerciali_nomi": malls[:4]}


def fetch_wikipedia_economia(city_name):
    """Texte nettoyé de la section Economia de l'article Wikipedia IT."""
    base = "https://it.wikipedia.org/w/api.php"
    raw = get(base + "?" + urllib.parse.urlencode(
        {"action": "parse", "page": city_name, "prop": "sections", "format": "json", "redirects": 1}))
    try:
        secs = json.loads(raw)["parse"]["sections"]
    except Exception:
        return ""
    idx = next((s["index"] for s in secs if s["line"].strip().lower() == "economia"), None)
    if not idx:
        return ""
    raw = get(base + "?" + urllib.parse.urlencode(
        {"action": "parse", "page": city_name, "section": idx, "prop": "wikitext", "format": "json", "redirects": 1}))
    try:
        w = json.loads(raw)["parse"]["wikitext"]["*"]
    except Exception:
        return ""
    w = re.sub(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", "", w, flags=re.S)
    w = re.sub(r"\{\{[^{}]*\}\}", "", w)
    w = re.sub(r"\[\[(?:[^]|]*\|)?([^]]*)\]\]", r"\1", w)
    w = re.sub(r"==+[^=]*==+|'''?|<[^>]+>", "", w)
    return re.sub(r"\s+", " ", w).strip()[:2500]


def fetch_wikidata_companies(qid):
    """Entreprises (P159 = siège) hors clubs sportifs/diocèses/entités dissoutes."""
    q = f"""SELECT DISTINCT ?aLabel WHERE {{
  ?a wdt:P159 wd:{qid} .
  FILTER NOT EXISTS {{ ?a wdt:P576 ?d }}
  FILTER NOT EXISTS {{ ?a wdt:P31/wdt:P279* wd:Q847017 }}
  FILTER NOT EXISTS {{ ?a wdt:P31/wdt:P279* wd:Q665487 }}
  ?a wdt:P31/wdt:P279* wd:Q4830453 .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "it,en". }}
}} LIMIT 8"""
    raw = get("https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": q, "format": "json"}))
    try:
        return [b["aLabel"]["value"] for b in json.loads(raw)["results"]["bindings"]
                if not b["aLabel"]["value"].startswith("Q")]
    except Exception:
        return []


def main():
    cities = [c for c in json.load(open(os.path.join(DATA_DIR, "cities_enriched.json"))) if keeps_page(c)]
    codes = istat_city_codes()
    out_path = os.path.join(DATA_DIR, "local_intel.json")
    intel = json.load(open(out_path)) if os.path.exists(out_path) else {}

    for i, c in enumerate(cities):
        slug, name = c["slug"], c["name"]
        if slug in intel and intel[slug].get("_complete"):
            continue
        print(f"[{i+1}/{len(cities)}] {name}")
        e = intel.setdefault(slug, {})
        code = codes.get(name)
        if code:
            e["istat"] = fetch_istat(code)
            e["istat"]["codice"] = code
            print(f"    ISTAT: {e['istat']}")
        time.sleep(1)
        e["osm"] = fetch_overpass(c)
        print(f"    OSM: {len(e['osm']['zone_industriali_nomi'])} zone ind., {len(e['osm']['centri_commerciali_nomi'])} malls")
        time.sleep(1)
        e["wikipedia_economia"] = fetch_wikipedia_economia(name)
        print(f"    Wikipedia Economia: {len(e['wikipedia_economia'])} car.")
        time.sleep(1)
        e["wikidata_aziende"] = fetch_wikidata_companies(c["wikidata_id"])
        print(f"    Wikidata: {e['wikidata_aziende'][:3]}")
        e["_complete"] = True
        json.dump(intel, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        time.sleep(3)

    print(f"\n✅ {len(intel)} villes → {out_path}")


if __name__ == "__main__":
    main()
