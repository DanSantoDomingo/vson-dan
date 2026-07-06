#!/usr/bin/env python3
"""Pull the freshly-built image, start it, health-check it, and roll back to the
last known-good image if the new one doesn't come up."""
import os
import shutil
import subprocess
import sys
import time
import urllib.request

IMAGE = os.environ.get("IMAGE", "ghcr.io/dansantodomingo/vson-dan")
IMAGE_TAG = os.environ.get("IMAGE_TAG")
if not IMAGE_TAG:
    sys.exit("IMAGE_TAG is required")

DEPLOY_DIR = "/opt/vson"
ENV_FILE = f"{DEPLOY_DIR}/.env"
COMPOSE_FILE = f"{DEPLOY_DIR}/docker-compose.yml"
LAST_GOOD_FILE = f"{DEPLOY_DIR}/last_good_tag"
HEALTH_URL = "http://localhost:3000/api/ping"
PROJECT = "vson"


def run(cmd, **kw):
    print(f"==> {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, **kw)


def compose(args, tag=None):
    env = dict(os.environ, IMAGE=IMAGE)
    if tag:
        env["IMAGE_TAG"] = tag
    run(["docker", "compose", "-p", PROJECT, "-f", COMPOSE_FILE,
         "--env-file", ENV_FILE, *args], env=env)


def deploy_tag(tag):
    run(["docker", "pull", f"{IMAGE}:{tag}"])
    compose(["up", "-d"], tag=tag)


def health_ok():
    print(f"==> health check {HEALTH_URL}")
    for attempt in range(1, 16):
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=3) as r:
                if r.status == 200:
                    print(f"    healthy (attempt {attempt})")
                    return True
        except Exception:
            pass
        time.sleep(2)
    print("    unhealthy after ~30s")
    return False


def sync(src, dst, mode):
    shutil.copy(src, dst)
    os.chmod(dst, mode)


def main():
    os.makedirs(DEPLOY_DIR, exist_ok=True)
    # Keep server config in sync with the repo.
    sync("docker-compose.yml", COMPOSE_FILE, 0o644)
    sync("Caddyfile", f"{DEPLOY_DIR}/Caddyfile", 0o644)
    sync("db/setup.sql", f"{DEPLOY_DIR}/setup.sql", 0o644)
    sync("scripts/backup.py", f"{DEPLOY_DIR}/backup.py", 0o755)

    token = os.environ.get("GHCR_TOKEN")
    if token:
        user = os.environ.get("GHCR_USER", "x")
        print("==> docker login ghcr.io")
        subprocess.run(["docker", "login", "ghcr.io", "-u", user, "--password-stdin"],
                       input=token.encode(), check=True)

    deploy_tag(IMAGE_TAG)

    if health_ok():
        with open(LAST_GOOD_FILE, "w") as f:
            f.write(IMAGE_TAG)
        subprocess.run(["docker", "image", "prune", "-f"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"==> deploy OK ({IMAGE_TAG})")
        return

    print("!! new build unhealthy — rolling back")
    if os.path.exists(LAST_GOOD_FILE):
        with open(LAST_GOOD_FILE) as f:
            prev = f.read().strip()
        print(f"==> rolling back to {prev}")
        deploy_tag(prev)
        if health_ok():
            print(f"==> rolled back; site is up on {prev}")
        else:
            print("!! rollback also unhealthy — manual attention needed")
    else:
        print("!! no previous good build recorded — cannot roll back")
    sys.exit(1)


if __name__ == "__main__":
    main()
