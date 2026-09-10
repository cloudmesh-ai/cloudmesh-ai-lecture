# Variables
MKDOCS_BIN = mkdocs
PORT=8000

.PHONY: help serve build clean publish size local-size marp marp-install slides slides-force

help:
	@echo "Introduction to Python - Build System"
	@echo "  make serve    - Live preview in browser with auto-reload"
	@echo "  make build    - Generate static HTML site"
	@echo "  make clean    - Remove generated site directory"
	@echo "  make publish  - Deploy the site to GitHub Pages"
	@echo "  make size     - Get repository size from GitHub API"
	@echo "  make local-size  - Get local repository size ignoring gitignore"
	@echo "  make slides    - Convert all *-talk.md slides to HTML"
	@echo "  make slides-force - Force convert all *-talk.md slides to HTML"
	@echo "  make marp     - (Legacy) Convert all *-talk.md slides to HTML"
	@echo "  make marp-install - Install Marp CLI globally"

view:
	open http://localhost:${PORT}

serve: slides
	-lsof -ti:$(PORT) | xargs -n 1 kill -9 2>/dev/null || true
	$(MKDOCS_BIN) serve --dirtyreload

dev: serve

build: slides
	$(MKDOCS_BIN) build

html: build

clean:
	rm -rf site

size:
	python3 bin/get_local_size.py

publish:
	$(MKDOCS_BIN) gh-deploy

install:
	pip install mkdocs-exclude-search
	pip install mkdocs-glightbox

marp-install:
	npm install -g @marp-team/marp-cli

slides:
	python3 bin/generate-talks.py

slides-force:
	python3 bin/generate-talks.py --force

marp: slides
