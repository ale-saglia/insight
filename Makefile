VENV_BIN	?= .venv/bin
PYTHON   	?= $(VENV_BIN)/python
PELICAN  	?= $(VENV_BIN)/pelican
LINKCHECKER ?= $(VENV_BIN)/linkchecker
PORT     	?= 4000
CHECK_PORT  ?= 4567

.DEFAULT_GOAL := help
.PHONY: help setup setup-dev compile build serve preview rebuild clean check-links

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  setup      Create .venv and install Python dependencies"
	@echo "  setup-dev  Like setup, but also install test dependencies"
	@echo "  compile    Recompile *.txt from *.in (run after editing a .in file)"
	@echo "  build      Check front matter and build with Pelican"
	@echo "  serve      Build then start Pelican live-reload on port $(PORT)"
	@echo "  preview    Build then serve _site/ statically on port $(PORT)"
	@echo "  rebuild    Clean and rebuild"
	@echo "  check-links Check internal links in _site/ on port $(CHECK_PORT) (override: CHECK_PORT=NNNN)"
	@echo "  clean      Remove _site/"

compile:
	uv pip compile requirements.in     --generate-hashes -o requirements.txt
	uv pip compile requirements-dev.in --generate-hashes -o requirements-dev.txt
	@echo "Requirements compiled. Run 'make setup' or 'make setup-dev' to reinstall."

setup:
	uv venv --clear .venv
	uv pip install --require-hashes -r requirements.txt
	@echo "Setup complete. Run 'make build' or 'make serve'."

setup-dev:
	uv venv --clear .venv
	uv pip install --require-hashes -r requirements-dev.txt
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

check-links:
	@test -d _site || { echo "_site/ not found — run: make build"; exit 1; }
	@test -x $(LINKCHECKER) || { echo "linkchecker not found — run: make setup-dev"; exit 1; }
	@echo "Starting check server on port $(CHECK_PORT)..."
	@$(PYTHON) -m http.server $(CHECK_PORT) --directory _site --bind 127.0.0.1 > /dev/null 2>&1 & \
	  SERVER_PID=$$!; \
	  trap "kill $$SERVER_PID 2>/dev/null" EXIT INT TERM; \
	  sleep 1; \
	  $(LINKCHECKER) \
	    --no-warnings \
	    --ignore-url='^https?://(?!127\.0\.0\.1)' \
	    --ignore-url='^mailto:' \
	    http://127.0.0.1:$(CHECK_PORT)/; \
	  RESULT=$$?; \
	  kill $$SERVER_PID 2>/dev/null; \
	  exit $$RESULT

clean:
	rm -rf _site
