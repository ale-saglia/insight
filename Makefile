.PHONY: help build preview rebuild clean

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "  build    Build the site"
	@echo "  preview  Build and serve locally on port 4000"
	@echo "  rebuild  Clean and rebuild the site"
	@echo "  clean    Remove _site/"

build:
	./scripts/build-local.sh

preview:
	./scripts/preview-local.sh

rebuild:
	rm -rf _site
	./scripts/build-local.sh

clean:
	rm -rf _site
