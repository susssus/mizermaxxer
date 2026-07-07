#!/usr/bin/env python3
"""Validate and sync images/manifest.json coverage for catalog image paths."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from common import (
    DATA_DIR,
    ROOT,
    is_entity_stub,
    iter_issue_files,
    iter_yaml_files,
    load_yaml,
)

MANIFEST_PATH = ROOT / "images" / "manifest.json"

FLYER_BASE = "https://malice-mizer.info"

# Release flyers indexed at malice-mizer.info/flyers (mirrors import_web_sources.FLYERS).
RELEASE_FLYERS: list[tuple[str, str, str]] = [
    ("1994-07-24", "memoire", "94.7.24-memoire-flyer.webp"),
    ("1994-07-24", "memoire-ii", "94.7.24-memoire-flyer-II.webp"),
    ("1994-12-24", "memoire-dx", "94.12.24-memoire-DX-flyer.webp"),
    ("1995-12-10", "uruwashiki-kamen", "95.12.10-Uruwashiki-Kamen-no-Shoutaijou-flyer.webp"),
    ("1996-06-09", "voyage", "96.6.9Voyage~sans-retour~flyer-cropped.webp"),
    ("1996-10-10", "ma-cherie", "96.10.10-ma-cherie-flyer.webp"),
    ("1997-02-11", "gekka", "97.2.11-Gekka-no-Yasoukyoku-release-flyer.webp"),
    ("1997-06-30", "derniere-vhs", "97.6.30-sans-retour-Voyage-LIVE-VIDEO-6-30-RELEASE-flyer.webp"),
    ("1997-07-19", "vers-elle", "97.7.19-Debut-Single-Release-flyer-cropped.webp"),
    ("1998-04-01", "au-revoir", "98.4.1-au-revoir-flyer.webp"),
    ("1998-05-20", "illuminati", "98.5.20-ILLUMINATI-flyer-cropped.webp"),
    ("1998-09-30", "le-ciel", "98.9.30-Le-ciel-flyer.webp"),
    ("1998-10-28", "lespace", "98.10.28-lespace-release.webp"),
    ("1998-11-27", "itan-shinmon", "98.11.webp"),
    ("1999-11-03", "saikai-single", "99.11.3-再会の血と薔薇-flyer.webp"),
    ("1999-12-21", "saikai-de-limage", "99.12.21-再会の血と薔薇-flyer.webp"),
    ("2000-02-01", "shinwa-front", "00.2.1-神話-flyer-front.webp"),
    ("2000-02-01", "shinwa-back", "00.2.1-神話-flyer-back.webp"),
    ("2000-05-31", "kyomu", "00.5.31-虚無の中での遊戯-flyer.webp"),
    ("2000-08-03", "bara-no-seidou-front", "00.8.3-薔薇の聖堂-flyer-front.webp"),
    ("2000-08-03", "bara-no-seidou-back", "00.8.3-薔薇の聖堂-flyer-back.webp"),
    ("2000-11-22", "budokan-vhs", "00.11.22-薇に彩られた悪意と悲劇の幕開け-flyer.webp"),
    ("2001-04-18", "derniere-dvd-front", "01.4.18-sans-retour-Voyage-DVD-flyer-front.webp"),
    ("2001-05-30", "gardenia", "01.5.30-Gardenia-flyer.webp"),
    ("2001-10-30", "bara-no-konrei", "01.10.30-真夜中に交わした約束~薔薇の婚礼~flyer.webp"),
    ("2001-11-30", "garnet", "01.11.30-Garnet-flyer.webp"),
]

EARLY_FLYER_SOURCES: dict[str, str] = {
    "images/flyers/flyers-1992-08-debut-era.webp": "https://malicemeezer.neocities.org/tetsu/oldflyer5.jpg",
    "images/flyers/flyers-1993-06-live-1993.webp": "https://malicemeezer.neocities.org/tetsu/oldflyer2.jpg",
    "images/flyers/flyers-1993-08-artistic-expression.webp": "https://malicemeezer.neocities.org/tetsu/oldflyer3.jpg",
    "images/flyers/flyers-1993-12-upcoming-lives.webp": "https://malicemeezer.neocities.org/tetsu/oldflyer8.jpg",
    "images/flyers/flyers-1994-01-live-1994.webp": "https://malicemeezer.neocities.org/tetsu/oldflyer.jpg",
}


@dataclass(frozen=True)
class CatalogImageRef:
    yaml_path: str
    field: str
    path: str


def normalize_image_path(path: str) -> str:
    return path.lstrip("/")


def is_local_image_path(path: object) -> bool:
    if not path or not isinstance(path, str):
        return False
    normalized = normalize_image_path(path.strip())
    if not normalized:
        return False
    lowered = normalized.lower()
    if lowered.startswith(("http://", "https://", "data/")):
        return False
    return normalized.startswith("images/")


def flyer_source_map() -> dict[str, tuple[str, str]]:
    mapping: dict[str, tuple[str, str]] = {}
    for date, slug, filename in RELEASE_FLYERS:
        local = f"images/flyers/flyers-{date}-{slug}.webp"
        mapping[local] = (f"{FLYER_BASE}/{filename}", "malice-mizer.info")
    for local, source_url in EARLY_FLYER_SOURCES.items():
        mapping[local] = (source_url, "Malice Meezer / malicemeezer.neocities.org")
    return mapping


def discogs_url_from_doc(doc: dict) -> str | None:
    for entry in doc.get("changelog") or []:
        notes = str(entry.get("notes") or "")
        match = re.search(r"https?://(?:www\.)?discogs\.com/\S+", notes)
        if match:
            return match.group(0).rstrip(").,]")
    return None


def default_attribution(path: str, doc: dict | None = None) -> tuple[str, str]:
    flyers = flyer_source_map()
    if path in flyers:
        return flyers[path]
    if path.startswith("images/flyers/"):
        return f"{FLYER_BASE}/flyers", "malice-mizer.info"
    if path.startswith("images/scans/"):
        return "https://cantavanda.com/malice-mizer/", "Cantavanda (Butterfly Rose)"
    if path.startswith("images/covers/"):
        if doc:
            discogs = discogs_url_from_doc(doc)
            if discogs:
                return discogs, "Cover Art Archive / Discogs"
        return "https://coverartarchive.org/", "Cover Art Archive / Discogs"
    return "https://github.com/susssus/mizermaxxer", "Mizermaxxer archive"


def load_manifest_entries() -> list[dict]:
    if not MANIFEST_PATH.exists():
        return []
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def load_manifest_paths() -> set[str]:
    return {entry["path"] for entry in load_manifest_entries() if entry.get("path")}


def collect_catalog_image_refs() -> list[CatalogImageRef]:
    refs: list[CatalogImageRef] = []

    for issue_path in iter_issue_files():
        issue = load_yaml(issue_path)
        rel = str(issue_path.relative_to(DATA_DIR))
        for article in issue.get("articles", []):
            scan_url = (article.get("scan") or {}).get("url")
            if is_local_image_path(scan_url):
                refs.append(
                    CatalogImageRef(
                        yaml_path=rel,
                        field="scan.url",
                        path=normalize_image_path(scan_url),
                    )
                )

    for collection in ("albums", "singles"):
        directory = DATA_DIR / collection
        for path in iter_yaml_files(directory):
            doc = load_yaml(path)
            if is_entity_stub(doc):
                continue
            cover = doc.get("cover_image")
            if is_local_image_path(cover):
                refs.append(
                    CatalogImageRef(
                        yaml_path=f"{collection}/{path.name}",
                        field="cover_image",
                        path=normalize_image_path(cover),
                    )
                )

    return refs


def validate_manifest_coverage() -> list[str]:
    errors: list[str] = []
    manifest_paths = load_manifest_paths()
    if not MANIFEST_PATH.exists():
        errors.append("images/manifest.json: missing manifest file")
        return errors

    for ref in collect_catalog_image_refs():
        if ref.path not in manifest_paths:
            errors.append(
                f"{ref.yaml_path}: local {ref.field} '{ref.path}' missing from images/manifest.json"
            )
        image_file = ROOT / ref.path
        if not image_file.exists():
            errors.append(f"{ref.yaml_path}: local {ref.field} '{ref.path}' file not found on disk")

    return errors


def sync_manifest_coverage(dry_run: bool = False) -> int:
    entries = load_manifest_entries()
    index = {entry["path"]: entry for entry in entries if entry.get("path")}
    added = 0
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")

    doc_by_cover: dict[str, dict] = {}
    for collection in ("albums", "singles"):
        for path in iter_yaml_files(DATA_DIR / collection):
            doc = load_yaml(path)
            if is_entity_stub(doc):
                continue
            cover = doc.get("cover_image")
            if is_local_image_path(cover):
                doc_by_cover[normalize_image_path(cover)] = doc

    for ref in collect_catalog_image_refs():
        if ref.path in index:
            continue
        source_url, source_name = default_attribution(ref.path, doc_by_cover.get(ref.path))
        entry = {
            "path": ref.path,
            "source_url": source_url,
            "source_name": source_name,
            "fetched_at": now,
        }
        if dry_run:
            print(f"would add: {ref.path} ({source_name})")
        else:
            entries.append(entry)
            index[ref.path] = entry
        added += 1

    if added and not dry_run:
        entries.sort(key=lambda item: item["path"])
        MANIFEST_PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return added


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    if "--sync" in sys.argv:
        count = sync_manifest_coverage(dry_run=dry_run)
        action = "Would add" if dry_run else "Added"
        print(f"{action} {count} manifest entries.")
        return 0

    errors = validate_manifest_coverage()
    if errors:
        print("Manifest coverage check failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        print("Run: python scripts/manifest_coverage.py --sync", file=sys.stderr)
        return 1

    refs = collect_catalog_image_refs()
    print(f"Manifest coverage OK ({len(refs)} local scan/cover paths, {len(load_manifest_paths())} manifest entries).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
