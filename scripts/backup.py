#!/usr/bin/env python3
"""Dump the Postgres container's database to a gzipped file and prune old ones.
Runs daily from cron on the droplet."""
import gzip
import os
import subprocess
import time

BACKUP_DIR = "/opt/vson/backups"
DB = "vision_template"
KEEP_DAYS = 14

os.makedirs(BACKUP_DIR, exist_ok=True)
stamp = time.strftime("%Y%m%d-%H%M%S")
path = f"{BACKUP_DIR}/{DB}-{stamp}.sql.gz"

dump = subprocess.run(["docker", "exec", "vson-db", "pg_dump", "-U", "postgres", DB],
                      check=True, stdout=subprocess.PIPE)
with gzip.open(path, "wb") as f:
    f.write(dump.stdout)
print(f"backup written: {path}")

cutoff = time.time() - KEEP_DAYS * 86400
for name in os.listdir(BACKUP_DIR):
    if name.startswith(f"{DB}-") and name.endswith(".sql.gz"):
        p = os.path.join(BACKUP_DIR, name)
        if os.path.getmtime(p) < cutoff:
            os.remove(p)
            print(f"pruned {name}")
