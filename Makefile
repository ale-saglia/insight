.PHONY: help setup build preview rebuild clean

PELICAN := $(shell command -v .venv/bin/pelican 2>/dev/null || command -v pelican 2>/dev/null || echo "")

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  setup    Create .venv and install Python dependencies"
	@echo "  build    Build the site (includes frontmatter check and OG images)"
	@echo "  serve    Build then serve on port 4000 (no OG regen)"
	@echo "  rebuild  Clean and rebuild"
	@echo "  clean    Remove _site/"

setup:
	python3 -m venv .venv
	.venv/bin/pip install -q -r requirements.txt
	@echo "Setup complete. Run 'make build' or 'make serve'."

build:
	./scripts/build-local.sh

serve:
	@if [ -z "$(PELICAN)" ]; then echo "pelican not found — run: make setup"; exit 1; fi
	$(PELICAN) --settings pelicanconf.py
	@echo "Serving at http://127.0.0.1:4000/"
	@cd _site && python3 -m http.server 4000

rebuild:
	rm -rf _site
	./scripts/build-local.sh

clean:
	rm -rf _site
