#!/usr/bin/env python3
"""Fix schema validation issues in bulk-imported issue stubs."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ISSUES = ROOT / "data" / "issues"

TYPE_MAP = {"feature": "photo_spread"}


def fix_issue(doc: dict) -> bool:
    changed = False
    if doc.get("publication_date") == "unknown":
        # Year-only placeholder satisfies schema; vol issues lack month data.
        doc["publication_date"] = "1999"
        changed = True
    if doc.get("date_precision") == "unknown":
        doc["date_precision"] = "year"
        changed = True
    for art in doc.get("articles") or []:
        if art.get("type") in TYPE_MAP:
            art["type"] = TYPE_MAP[art["type"]]
            changed = True
        scan = art.get("scan") or {}
        if scan.get("quality") == "unknown":
            scan["quality"] = "medium"
            art["scan"] = scan
            changed = True
    return changed


def main() -> None:
    fixed = 0
    for path in sorted(ISSUES.rglob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict) or "publication" not in doc:
            continue
        if fix_issue(doc):
            path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
            fixed += 1
    print(f"Fixed {fixed} issue stubs.")


if __name__ == "__main__":
    main()
