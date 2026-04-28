VENV_BIN  ?= .venv/bin
PYTHON    ?= $(VENV_BIN)/python
PIP       ?= $(VENV_BIN)/pip
PELICAN   ?= $(VENV_BIN)/pelican
PORT      ?= 4000

.DEFAULT_GOAL := help
.PHONY: help setup setup-dev build serve preview rebuild clean

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  setup      Create .venv and install Python dependencies"
	@echo "  setup-dev  Like setup, but also install test dependencies"
	@echo "  build      Check front matter and build with Pelican"
	@echo "  serve      Build then start Pelican live-reload on port $(PORT)"
	@echo "  preview    Build then serve _site/ statically on port $(PORT)"
	@echo "  rebuild    Clean and rebuild"
	@echo "  clean      Remove _site/"


# Internal function for venv creation and requirements install
define create_venv_and_install
  test -d .venv || python3 -m venv .venv
  @echo "Installing dependencies: $(1)"
  @if ! .venv/bin/pip install -q -r $(1); then \
    echo "[ERROR] Installation failed. Removing .venv and retrying..."; \
    rm -rf .venv; \
    python3 -m venv .venv; \
    if ! .venv/bin/pip install -q -r $(1); then \
      echo "[ERROR] Installation failed again. Check your Python setup and $(1)."; \
      exit 1; \
    fi; \
  fi
endef

setup:
	$(call create_venv_and_install,requirements.txt)
	@echo "Setup complete. Run 'make build' or 'make serve'."

setup-dev:
	$(call create_venv_and_install,requirements-dev.txt)
	@echo "Dev setup complete. Run 'make test' to run the test suite."

build:
	@test -x $(PYTHON) || { echo "python not found — run: make setup"; exit 1; }
	@test -x $(PELICAN) || { echo "pelican not found — run: make setup"; exit 1; }
	@echo "Checking and normalizing article front matter..."
	$(PYTHON) scripts/ensure_frontmatter.py
	@echo "Building with Pelican..."
	$(PELICAN) --settings pelicanconf.py
	@echo "Build complete → _site/"

serve: build
	$(PELICAN) --listen --port $(PORT) --settings pelicanconf.py

preview: build
	@echo "Preview at: http://127.0.0.1:$(PORT)/"
	$(PYTHON) -m http.server $(PORT) --directory _site

rebuild: clean build

clean:
	rm -rf _site
