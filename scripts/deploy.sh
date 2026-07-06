#!/usr/bin/env bash
# Pull the freshly-built image, start it, health-check it, and roll back to the
# last known-good image if the new one doesn't come up.
set -euo pipefail

IMAGE="${IMAGE:-ghcr.io/dansantodomingo/vson-dan}"
IMAGE_TAG="${IMAGE_TAG:?IMAGE_TAG is required}"
DEPLOY_DIR="/opt/vson"
ENV_FILE="$DEPLOY_DIR/.env"
LAST_GOOD_FILE="$DEPLOY_DIR/last_good_tag"
HEALTH_URL="http://localhost:3000/api/ping"
PROJECT="vson"

export IMAGE

compose() {
  docker compose -p "$PROJECT" -f docker-compose.yml --env-file "$ENV_FILE" "$@"
}

deploy_tag() {
  local tag="$1"
  echo "==> docker pull $IMAGE:$tag"
  docker pull "$IMAGE:$tag"
  echo "==> starting $tag"
  export IMAGE_TAG="$tag"
  compose up -d
}

health_ok() {
  echo "==> health check $HEALTH_URL"
  for i in $(seq 1 15); do
    if curl -fsS -o /dev/null "$HEALTH_URL"; then
      echo "    healthy (attempt $i)"
      return 0
    fi
    sleep 2
  done
  echo "    unhealthy after ~30s"
  return 1
}

# Keep the Caddy config, DB schema, and backup script on the box in sync with the repo.
install -D -m 644 Caddyfile "$DEPLOY_DIR/Caddyfile"
install -D -m 644 db/setup.sql "$DEPLOY_DIR/setup.sql"
install -D -m 755 scripts/backup.sh "$DEPLOY_DIR/backup.sh"

# Authenticate to GHCR so private images can be pulled (harmless for public).
if [ -n "${GHCR_TOKEN:-}" ]; then
  echo "$GHCR_TOKEN" | docker login ghcr.io -u "${GHCR_USER:-x}" --password-stdin
fi

deploy_tag "$IMAGE_TAG"

if health_ok; then
  echo "$IMAGE_TAG" > "$LAST_GOOD_FILE"
  docker image prune -f >/dev/null 2>&1 || true
  echo "==> deploy OK ($IMAGE_TAG)"
  exit 0
fi

echo "!! new build unhealthy — rolling back"
if [ -f "$LAST_GOOD_FILE" ]; then
  prev="$(cat "$LAST_GOOD_FILE")"
  echo "==> rolling back to $prev"
  deploy_tag "$prev"
  if health_ok; then
    echo "==> rolled back; site is up on $prev"
  else
    echo "!! rollback also unhealthy — manual attention needed"
  fi
else
  echo "!! no previous good build recorded — cannot roll back"
fi
exit 1
