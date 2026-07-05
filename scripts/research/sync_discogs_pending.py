#!/usr/bin/env python3
"""Sync only catalog entries missing a YAML file (for rate-limit recovery)."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sync_discogs import (  # noqa: E402
    IMAGES,
    RATE_LIMIT_SEC,
    download_cover,
    ensure_public_symlink,
    fetch_entry,
    load_catalog,
    primary_image_url,
    update_yaml,
    yaml_dir_for_kind,
)
import time
import urllib.error


def main() -> int:
    catalog = load_catalog()
    pending = []
    for entry in catalog:
        path = yaml_dir_for_kind(entry["kind"]) / f"{entry['slug']}.yaml"
        if not path.exists():
            pending.append(entry)
    if not pending:
        print("All catalog entries have YAML files.")
        return 0
    print(f"Syncing {len(pending)} pending releases...")
    ok = 0
    for entry in pending:
        slug = entry["slug"]
        try:
            meta = fetch_entry(entry["discogs"])
            time.sleep(max(RATE_LIMIT_SEC, 2.5))
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                print(f"  rate limited at {slug}, waiting 60s...", file=sys.stderr)
                time.sleep(60)
                try:
                    meta = fetch_entry(entry["discogs"])
                    time.sleep(2.5)
                except urllib.error.HTTPError as exc2:
                    print(f"  FAIL {slug}: HTTP {exc2.code}", file=sys.stderr)
                    continue
            else:
                print(f"  FAIL {slug}: HTTP {exc.code}", file=sys.stderr)
                continue
        except urllib.error.URLError as exc:
            print(f"  FAIL {slug}: {exc}", file=sys.stderr)
            continue

        cover_rel = None
        image_url = primary_image_url(meta.get("images") or [])
        if image_url:
            dest = IMAGES / f"{slug}.jpg"
            try:
                if not dest.exists():
                    download_cover(image_url, dest)
                    time.sleep(0.5)
                cover_rel = f"images/covers/{slug}.jpg"
            except urllib.error.URLError as exc:
                print(f"  skip cover {slug}: {exc}", file=sys.stderr)

        update_yaml(entry, meta, cover_rel)
        print(f"  ok: {slug} ({meta.get('released')})")
        ok += 1

    ensure_public_symlink()
    print(f"Done: {ok}/{len(pending)} pending releases synced.")
    return 0 if ok == len(pending) else 1


if __name__ == "__main__":
    raise SystemExit(main())
