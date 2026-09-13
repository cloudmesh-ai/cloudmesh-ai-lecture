# ------------------------------------------------------------
# Dockerfile – linkinator for cloudmesh‑ai‑lecture
# ------------------------------------------------------------
# Use the lightweight Node LTS image
FROM node:20-alpine AS builder

# Create a non‑root user (safer for CI)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app

# ------------------------------------------------------------
# Install linkinator
# ------------------------------------------------------------
# Copy package files if they exist
COPY package*.json ./

# Use npm ci only if package-lock.json exists, otherwise use npm install
RUN if [ -f package-lock.json ]; then \
        npm ci; \
    else \
        npm install --save-dev linkinator@latest; \
    fi

# ------------------------------------------------------------
# Set the entrypoint so we can simply write:
#   docker run … linkinator <args>
# ------------------------------------------------------------
ENTRYPOINT ["npx","linkinator"]
USER appuser
