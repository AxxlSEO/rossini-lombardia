.PHONY: install fetch enrich generate sitemap all serve clean

install:
	pip install requests jinja2

fetch:
	python scripts/01_fetch_cities.py

enrich:
	python scripts/02_fetch_enrichment.py

generate:
	python scripts/03_generate_html.py

sitemap:
	python scripts/04_generate_sitemap.py

all: fetch enrich generate sitemap
	@echo "🎉 Site complet généré dans output/"

serve:
	cd output && python -m http.server 8000

clean:
	rm -f data/*.json
	rm -f output/citta/*.html
	rm -f output/index.html
	rm -f output/sitemap.xml
	rm -f output/robots.txt
