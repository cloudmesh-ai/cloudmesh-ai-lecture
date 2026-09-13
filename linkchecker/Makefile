# ------------------------------------------------------------
# Makefile – cloudmesh‑ai‑lecture linkchecker
# ------------------------------------------------------------
# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
# Name of the Docker image that will be built locally
DOCKER_IMAGE ?= cloudmesh-linkinator

# Flags you want to pass to linkinator by default.
LINKINATOR_FLAGS ?= --markdown --verbosity info

# Current directory (absolute) – required for the volume mount
PWD_ABS := $(shell pwd)/..

# ------------------------------------------------------------------
# Build the Docker image (cached automatically by Docker)
# ------------------------------------------------------------------
.PHONY: docker-build
docker-build:
	@echo "🚧 Building Docker image '$(DOCKER_IMAGE)' …"
	@docker build -t $(DOCKER_IMAGE) .

# ------------------------------------------------------------------
# Run Linkinator on the repository – *friendly* (never fails make)
# ------------------------------------------------------------------
.PHONY: linkcheck
linkcheck: docker-build
	@echo "🔎 Running Linkinator (local dev mode)…"
	@docker run --rm \
		-v "$(PWD_ABS)":/app \
		-w /app \
		$(DOCKER_IMAGE) . $(LINKINATOR_FLAGS) || true
	@echo "✅ Done – broken links (if any) are printed above."

# ------------------------------------------------------------------
# CI‑ready: abort make (non‑zero exit) if any broken link is found
# ------------------------------------------------------------------
.PHONY: linkcheck-ci
linkcheck-ci: docker-build
	@echo "🔎 Running Linkinator (CI mode – fail on broken links)…"
	@docker run --rm \
		-v "$(PWD_ABS)":/app \
		-w /app \
		$(DOCKER_IMAGE) . $(LINKINATOR_FLAGS) --verbose --ignore-redirects false
	@echo "✅ CI check completed."

# ------------------------------------------------------------------
# Produce a JSON report that can be archived as an artifact
# ------------------------------------------------------------------
.PHONY: linkcheck-report
linkcheck-report: docker-build
	@echo "📊 Generating JSON report → link-report.json …"
	@docker run --rm \
		-v "$(PWD_ABS)":/app \
		-w /app \
		$(DOCKER_IMAGE) . $(LINKINATOR_FLAGS) --json > link-report.json
	@echo "✅ Report written to link-report.json"

# ------------------------------------------------------------------
# Clean up the locally‑built image (useful for a fresh rebuild)
# ------------------------------------------------------------------
.PHONY: docker-clean
docker-clean:
	@docker rmi -f $(DOCKER_IMAGE) || true
	@echo "🗑️  Image $(DOCKER_IMAGE) removed."
