#!/usr/bin/env python3
"""Merge Malice Archive incomplete-mags Drive links into scan_sources_catalog.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
INCOMPLETE = ROOT / "scripts" / "research" / "malice_archive_incomplete_mags.yaml"
CATALOG = ROOT / "scripts" / "research" / "scan_sources_catalog.yaml"


def item_key(item: dict) -> tuple:
    pub = item.get("publication", "")
    date = item.get("issue_date")
    if date and len(str(date)) >= 7:
        date = str(date)[:7]
    num = item.get("issue_number")
    return (pub, date, str(num) if num else None)


def project_path(item: dict) -> str | None:
    pub = item["publication"]
    date = item.get("issue_date")
    if date:
        stem = str(date)[:7] if len(str(date)) >= 7 else str(date)
        return f"data/issues/{pub}/{stem}.yaml"
    if item.get("issue_number"):
        return f"data/issues/{pub}/vol-{item['issue_number']}.yaml"
    return None


def main() -> None:
    incomplete = yaml.safe_load(INCOMPLETE.read_text(encoding="utf-8"))
    source_meta = incomplete["source"]

    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    sources = catalog.setdefault("sources", [])
    items = catalog.setdefault("items", [])

    if not any(s.get("id") == source_meta["id"] for s in sources):
        sources.append(
            {
                "id": source_meta["id"],
                "name": source_meta["name"],
                "base_url": source_meta["url"],
                "license_notes": source_meta["license_notes"].strip(),
            }
        )

    existing_keys = {item_key(i) for i in items}
    added = 0
    for raw in incomplete.get("items") or []:
        key = item_key(raw)
        if key in existing_keys:
            continue
        entry = {
            "publication": raw["publication"],
            "title": raw.get("title"),
            "scan_url": raw["scan_url"],
            "source": source_meta["id"],
            "project_path": project_path(raw),
        }
        if raw.get("issue_date"):
            date = raw["issue_date"]
            entry["issue_date"] = str(date)[:7] if len(str(date)) >= 7 else date
        if raw.get("issue_number"):
            entry["issue_number"] = str(raw["issue_number"])
        items.append(entry)
        existing_keys.add(key)
        added += 1

    CATALOG.write_text(yaml.dump(catalog, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    print(f"Added {added} incomplete-mags scan entries to {CATALOG.name} (total items: {len(items)})")


if __name__ == "__main__":
    main()
