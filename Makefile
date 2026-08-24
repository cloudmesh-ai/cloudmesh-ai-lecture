# Variables
MKDOCS_BIN = mkdocs

.PHONY: help serve build clean publish

help:
	@echo "Introduction to Python - Build System"
	@echo "  make serve    - Live preview in browser with auto-reload"
	@echo "  make build    - Generate static HTML site"
	@echo "  make clean    - Remove generated site directory"
	@echo "  make publish  - Deploy the site to GitHub Pages"

serve:
	$(MKDOCS_BIN) serve --dirtyreload

dev: serve

build:
	$(MKDOCS_BIN) build

html: build

clean:
	rm -rf site

publish:
	$(MKDOCS_BIN) gh-deploy
