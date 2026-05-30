PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
VENV_DIR ?= .venv

.PHONY: help bootstrap doctor extract build verify test check refresh status catalog hub-list hub-summary clean-publishable

help:
	@printf "Targets disponibles:\n"
	@printf "  make bootstrap        Crea .venv e instala dependencias\n"
	@printf "  make doctor           Muestra el Python efectivo y dependencias clave\n"
	@printf "  make extract          Ejecuta extractores\n"
	@printf "  make build            Compila outputs del hub\n"
	@printf "  make verify           Verifica artefactos generados\n"
	@printf "  make test             Corre smoke tests\n"
	@printf "  make check            Ejecuta build + verify + test\n"
	@printf "  make refresh          Ejecuta extract + build + verify + test\n"
	@printf "  make status           Imprime resumen humano del pipeline\n"
	@printf "  make catalog          Muestra dataset_catalog.json\n"
	@printf "  make hub-list         Lista datasets via CLI\n"
	@printf "  make hub-summary      Resume datasets via CLI\n"
	@printf "  make clean-publishable Elimina artefactos livianos versionables\n"

bootstrap:
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/python -m pip install --upgrade pip
	$(VENV_DIR)/bin/python -m pip install -r requirements.txt

doctor:
	@printf "PYTHON=%s\n" "$(PYTHON)"
	@$(PYTHON) -c "import sys; print(sys.executable)"
	@$(PYTHON) -c "import duckdb, polars; print('duckdb=' + duckdb.__version__); print('polars=' + polars.__version__)"

extract:
	$(PYTHON) src/extractors/subdere_extractor.py
	$(PYTHON) src/extractors/bcentral_extractor.py

build:
	$(PYTHON) src/build_dev_db.py

verify:
	$(PYTHON) scripts/verify_pipeline.py

test:
	$(PYTHON) -m unittest discover -s tests

check: build verify test

refresh: extract build verify test

status:
	$(PYTHON) scripts/pipeline_status.py

catalog:
	@cat data/normalized/dataset_catalog.json

hub-list:
	$(PYTHON) -m src.chile_hub list

hub-summary:
	$(PYTHON) -m src.chile_hub summary

clean-publishable:
	rm -f data/normalized/*.json data/normalized/*.md data/normalized/*.parquet
