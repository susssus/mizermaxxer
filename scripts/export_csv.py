#!/usr/bin/env python3
"""Export SQLite archive to CSV and XLSX."""

from __future__ import annotations

import csv
import sqlite3
import sys

from openpyxl import Workbook

from common import DB_PATH, EXPORTS_DIR, ensure_dirs


COLUMNS = [
    "publication",
    "publication_name_en",
    "issue_id",
    "issue_number",
    "volume",
    "publication_date",
    "verification_status",
    "article_id",
    "article_type",
    "title_ja",
    "title_en",
    "pages",
    "members",
    "photographer",
    "writer",
    "cover",
    "poster",
    "foldout",
    "scan_available",
    "scan_quality",
    "scan_url",
    "translation_available",
    "translation_url",
    "purchase_links",
    "notes",
    "source_notes",
]


QUERY = """
SELECT
    i.publication,
    p.name_en AS publication_name_en,
    i.id AS issue_id,
    i.issue_number,
    i.volume,
    i.publication_date,
    i.verification_status,
    a.id AS article_id,
    a.type AS article_type,
    a.title_ja,
    a.title_en,
    a.pages,
    a.members_json AS members,
    a.photographer,
    a.writer,
    a.cover,
    a.poster,
    a.foldout,
    a.scan_available,
    a.scan_quality,
    a.scan_url,
    a.translation_available,
    a.translation_url,
    a.purchase_links_json AS purchase_links,
    a.notes,
    i.source_notes
FROM articles a
JOIN issues i ON i.id = a.issue_id
JOIN publications p ON p.slug = i.publication
ORDER BY i.publication_date, p.priority, a.id
"""


def fetch_rows() -> list[dict]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in connection.execute(QUERY)]
    finally:
        connection.close()


def write_csv(rows: list[dict]) -> None:
    csv_path = EXPORTS_DIR / "archive.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in COLUMNS})
    print(f"Wrote {csv_path}")


def write_xlsx(rows: list[dict]) -> None:
    xlsx_path = EXPORTS_DIR / "archive.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Archive"
    sheet.append(COLUMNS)
    for row in rows:
        sheet.append([row.get(column) for column in COLUMNS])
    workbook.save(xlsx_path)
    print(f"Wrote {xlsx_path}")


def main() -> int:
    if not DB_PATH.exists():
        print("Database not found. Run build_db.py first.", file=sys.stderr)
        return 1
    ensure_dirs()
    rows = fetch_rows()
    write_csv(rows)
    write_xlsx(rows)
    print(f"Exported {len(rows)} article rows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
