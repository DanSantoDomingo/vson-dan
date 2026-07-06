#!/usr/bin/env bash
# Manually roll back to the last known-good image, or to a specific tag:
#   bash scripts/rollback.sh            # last good
#   bash scripts/rollback.sh <git-sha>  # a specific build
set -euo pipefail

IMAGE="${IMAGE:-ghcr.io/dansantodomingo/vson-dan}"
TAG="${1:-$(cat /opt/vson/last_good_tag)}"
export IMAGE

docker pull "$IMAGE:$TAG"
IMAGE_TAG="$TAG" docker compose -p vson -f docker-compose.yml --env-file /opt/vson/.env up -d
echo "rolled back to $TAG"
