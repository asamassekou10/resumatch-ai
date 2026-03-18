#!/bin/bash
# =============================================================================
# Deployment script for AI Resume Analyzer on Hetzner VPS
# Usage: ./deploy.sh
# =============================================================================

set -euo pipefail

APP_DIR="$HOME/app"
COMPOSE_FILE="docker-compose.prod.yml"
LOG_FILE="$APP_DIR/deploy.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Starting deployment ==="

cd "$APP_DIR"

# Pull latest code
log "Pulling latest code from GitHub..."
git fetch origin main
git reset --hard origin/main

# Verify env file exists
if [ ! -f .env.production ]; then
    log "ERROR: .env.production not found! Create it before deploying."
    exit 1
fi

# Build and restart containers
log "Building and starting containers..."
docker compose -f "$COMPOSE_FILE" build --parallel
docker compose -f "$COMPOSE_FILE" up -d

# Wait for backend to be healthy
log "Waiting for backend health check..."
RETRIES=30
until docker compose -f "$COMPOSE_FILE" exec -T backend curl -sf http://localhost:5000/api/health > /dev/null 2>&1; do
    RETRIES=$((RETRIES - 1))
    if [ $RETRIES -le 0 ]; then
        log "ERROR: Backend failed health check after 30 attempts"
        log "Rolling back..."
        docker compose -f "$COMPOSE_FILE" logs --tail=50 backend
        exit 1
    fi
    sleep 2
done

log "Backend is healthy."

# Run database migrations
log "Running database migrations..."
docker compose -f "$COMPOSE_FILE" exec -T backend alembic upgrade head

# Clean up old Docker images
log "Cleaning up old images..."
docker image prune -f

log "=== Deployment complete ==="
log "Services status:"
docker compose -f "$COMPOSE_FILE" ps
