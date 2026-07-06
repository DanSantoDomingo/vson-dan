#!/usr/bin/env python3
"""Manually roll back to the last known-good image, or to a specific tag:
    python3 scripts/rollback.py            # last good
    python3 scripts/rollback.py <git-sha>  # a specific build
"""
import os
import subprocess
import sys

IMAGE = os.environ.get("IMAGE", "ghcr.io/dansantodomingo/vson-dan")
DEPLOY_DIR = "/opt/vson"

if len(sys.argv) > 1:
    tag = sys.argv[1]
else:
    with open(f"{DEPLOY_DIR}/last_good_tag") as f:
        tag = f.read().strip()

subprocess.run(["docker", "pull", f"{IMAGE}:{tag}"], check=True)
env = dict(os.environ, IMAGE=IMAGE, IMAGE_TAG=tag)
subprocess.run(["docker", "compose", "-p", "vson", "-f", f"{DEPLOY_DIR}/docker-compose.yml",
                "--env-file", f"{DEPLOY_DIR}/.env", "up", "-d"], env=env, check=True)
print(f"rolled back to {tag}")
