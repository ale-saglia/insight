.DEFAULT_GOAL := help
.PHONY: help setup build serve rebuild clean

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  setup    Create .venv and install Python dependencies"
	@echo "  build    Build the site (includes frontmatter check and OG images)"
	@echo "  serve    Build then serve on port 4000 with live reload"
	@echo "  rebuild  Clean and rebuild"
	@echo "  clean    Remove _site/"

setup:
	test -d .venv || python3 -m venv .venv
	.venv/bin/pip install -q -r requirements.txt
	@echo "Setup complete. Run 'make build' or 'make serve'."

build:
	./scripts/build-local.sh

serve: build
	@command -v .venv/bin/pelican >/dev/null 2>&1 || command -v pelican >/dev/null 2>&1 || \
		{ echo "pelican not found — run: make setup"; exit 1; }
	$$(command -v .venv/bin/pelican || command -v pelican) \
		--listen --port 4000 --settings pelicanconf.py

rebuild: clean build

clean:
	rm -rf _site
