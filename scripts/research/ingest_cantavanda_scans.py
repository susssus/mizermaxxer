#!/usr/bin/env python3
"""Update issue YAML + manifest after Cantavanda scans are mirrored locally."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "scripts" / "research" / "scan_sources_catalog.yaml"
MANIFEST = ROOT / "images" / "manifest.json"

CANTAVANDA_SOURCES = {"cantavanda-magazine-appearances", "cantavanda-fan-club-mags"}
SOURCE_NAMES = {
    "cantavanda-magazine-appearances": "Cantavanda / Butterfly Rose",
    "cantavanda-fan-club-mags": "Cantavanda / Madame Tarantula",
}


def scan_path(pub: str, date: str, page: int) -> str:
    return f"images/scans/{pub}/{date}/{page:02d}.jpg"


def load_manifest() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    entries: list[dict[str, Any]] = []
    if MANIFEST.exists():
        entries = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return entries, {e["path"]: e for e in entries}


def add_manifest(
    entries: list[dict[str, Any]],
    index: dict[str, dict[str, Any]],
    path: str,
    source_url: str,
    source_name: str,
) -> None:
    if path in index:
        return
    entry = {
        "path": path,
        "source_url": source_url,
        "source_name": source_name,
        "fetched_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    entries.append(entry)
    index[path] = entry


def default_article(issue: dict[str, Any], item: dict[str, Any], page_count: int) -> dict[str, Any]:
    issue_id = issue["id"]
    return {
        "id": f"{issue_id}-001",
        "title_ja": None,
        "title_en": item.get("title"),
        "type": issue.get("articles", [{}])[0].get("type", "newsletter")
        if issue.get("articles")
        else "mention",
        "pages": str(page_count) if page_count else None,
        "members": ["gackt", "kami", "kozi", "mana", "yuki"],
        "photographer": None,
        "writer": None,
        "cover": False,
        "poster": False,
        "foldout": False,
        "scan": {
            "available": True,
            "quality": "high",
            "url": scan_path(
                issue["publication"],
                str(issue["publication_date"])[:7],
                1,
            ),
        },
        "translation": {"available": False, "url": None},
        "purchase_links": [],
        "notes": (
            f"{page_count} local scan pages. Gallery: {item.get('scan_url', '')}. "
            f"Source: {SOURCE_NAMES.get(item.get('source', ''), 'Cantavanda')}."
        ),
    }


def update_issue(issue: dict[str, Any], item: dict[str, Any]) -> bool:
    pub = issue["publication"]
    date = str(issue["publication_date"])[:7]
    page_count = len(item.get("image_urls") or [])
    gallery = item.get("scan_url", "")

    if not issue.get("articles"):
        issue["articles"] = [default_article(issue, item, page_count)]

    primary = issue["articles"][0]
    scan = primary.setdefault("scan", {})
    if scan.get("url", "").startswith("http") or not scan.get("url"):
        scan["url"] = scan_path(pub, date, 1)
        scan["available"] = True
        if not scan.get("quality"):
            scan["quality"] = "high"

    extra_pages = [
        scan_path(pub, date, n) for n in range(2, page_count + 1)
    ]
    if extra_pages:
        note = primary.get("notes", "")
        extra_note = f" Additional pages: {', '.join(extra_pages)}."
        if extra_note.strip() not in note:
            primary["notes"] = (note.rstrip() + extra_note).strip()

    issue["source_notes"] = (
        f"{item.get('title', 'Cantavanda scan')}. "
        f"{page_count} pages mirrored locally under images/scans/{pub}/{date}/. "
        f"Gallery: {gallery}\n"
    )

    changelog = issue.setdefault("changelog", [])
    if not any(e.get("action") == "updated" and e.get("source") == "cantavanda" for e in changelog):
        changelog.append(
            {
                "date": datetime.now(UTC).strftime("%Y-%m-%d"),
                "action": "updated",
                "source": "cantavanda",
                "notes": f"Mirrored {page_count} scan pages locally.",
            }
        )
    return True


def main() -> int:
    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    entries, index = load_manifest()
    updated = 0

    for item in catalog.get("items") or []:
        if item.get("source") not in CANTAVANDA_SOURCES:
            continue
        project_path = item.get("project_path")
        if not project_path or not project_path.startswith("data/issues/"):
            continue

        issue_path = ROOT / project_path
        if not issue_path.exists():
            print(f"skip missing {project_path}")
            continue

        issue = yaml.safe_load(issue_path.read_text(encoding="utf-8"))
        pub = issue["publication"]
        date = str(issue["publication_date"])[:7]
        source_name = SOURCE_NAMES.get(item["source"], "Cantavanda")

        for idx, url in enumerate(item.get("image_urls") or [], start=1):
            rel = scan_path(pub, date, idx)
            if (ROOT / rel).exists():
                add_manifest(entries, index, rel, url, source_name)

        if update_issue(issue, item):
            issue_path.write_text(
                yaml.dump(issue, allow_unicode=True, sort_keys=False, default_flow_style=False),
                encoding="utf-8",
            )
            updated += 1
            print(f"updated {project_path}")

    MANIFEST.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Done: {updated} issues, {len(entries)} manifest entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
