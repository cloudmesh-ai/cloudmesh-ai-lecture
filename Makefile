# Variables
MKDOCS_BIN = mkdocs

.PHONY: help serve build clean publish size local-size

help:
	@echo "Introduction to Python - Build System"
	@echo "  make serve    - Live preview in browser with auto-reload"
	@echo "  make build    - Generate static HTML site"
	@echo "  make clean    - Remove generated site directory"
	@echo "  make publish  - Deploy the site to GitHub Pages"
	@echo \"  make size     - Get repository size from GitHub API\"
	@echo \"  make local-size  - Get local repository size ignoring gitignore\"



serve:
	$(MKDOCS_BIN) serve --dirtyreload

dev: serve

build:
	$(MKDOCS_BIN) build

html: build

clean:
	rm -rf site

size:
	python3 bin/get_local_size.py


publish:
	$(MKDOCS_BIN) gh-deploy
