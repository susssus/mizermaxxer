#!/usr/bin/env python3
"""Write content_nature / promotional_subtype fields into issue YAML articles."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_issues
from content_taxonomy import enrich_article

ROOT = Path(__file__).resolve().parents[1]
ISSUES_DIR = ROOT / "data" / "issues"

CLASSIFICATION_FIELDS = (
    "content_nature",
    "promotional_subtype",
    "promotional_carrier",
    "promotional_subject",
    "vkgy_roles",
)


def dump_yaml(path: Path, data: dict) -> None:
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000),
        encoding="utf-8",
    )


def apply_to_issue(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        issue = yaml.safe_load(handle)
    if not isinstance(issue, dict) or "articles" not in issue:
        return 0

    publication = issue.get("publication")
    changed = 0
    for index, article in enumerate(issue["articles"]):
        enriched = enrich_article(article, publication)
        for field in CLASSIFICATION_FIELDS:
            new_value = enriched.get(field)
            old_value = article.get(field)
            if new_value and new_value != old_value:
                article[field] = new_value
                changed += 1
            elif field in article and not new_value:
                del article[field]
                changed += 1
        issue["articles"][index] = article

    if changed:
        dump_yaml(path, issue)
    return changed


def main() -> int:
    total = 0
    files = 0
    for path in sorted(ISSUES_DIR.rglob("*.yaml")):
        changed = apply_to_issue(path)
        if changed:
            files += 1
            total += changed
            print(f"  {path.relative_to(ROOT)}: {changed} field(s) updated")
    print(f"Updated {total} classification field(s) across {files} issue file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
