.PHONY: venv validate build export site pdf all clean

PYTHON := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: bibliography-expand
bibliography-expand:
	$(PYTHON) scripts/research/patch_scan_sources_incomplete_mags.py
	$(PYTHON) scripts/research/fetch_vkgy_magazines.py
	$(PYTHON) scripts/research/build_magazine_references_online.py
	$(PYTHON) scripts/research/import_online_catalog_stubs.py
	$(PYTHON) scripts/research/fix_imported_stubs.py
	$(PYTHON) scripts/research/verify_ndl_placeholders.py
	$(PYTHON) scripts/build_db.py

venv:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt
	cd site && npm install

validate:
	$(PYTHON) scripts/validate.py
	$(PYTHON) scripts/validate_entities.py

entities-validate:
	$(PYTHON) scripts/validate_entities.py

links:
	$(PYTHON) scripts/build_links_index.py

entities: entities-validate links

build: validate links
	$(PYTHON) scripts/build_db.py

export: build
	$(PYTHON) scripts/export_csv.py

site: build
	cd site && npm run build

pdf: build
	$(PYTHON) scripts/build_pdf.py

all: export site pdf

clean:
	rm -rf db/archive.sqlite exports/archive.csv exports/archive.xlsx exports/catalogue.pdf site/dist site/src/data/archive.json

seed:
	$(PYTHON) scripts/generate_seed.py

music-seed:
	$(PYTHON) scripts/generate_music_seed.py

concert-seed:
	$(PYTHON) scripts/seed_concerts_catalog.py
	$(PYTHON) scripts/build_db.py

concert-augment:
	$(PYTHON) scripts/research/augment_concerts.py
	$(PYTHON) scripts/build_db.py

discogs-sync:
	$(PYTHON) scripts/research/sync_discogs.py
	$(PYTHON) scripts/research/sync_discogs_pending.py
	$(PYTHON) scripts/research/fix_discogs_slugs.py
