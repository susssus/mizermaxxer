#!/usr/bin/env python3
"""Generate a printable PDF catalogue from the SQLite archive."""

from __future__ import annotations

import sqlite3
import sys
from collections import defaultdict

from fpdf import FPDF

from common import DB_PATH, EXPORTS_DIR, ensure_dirs


def pdf_safe(text: str | None) -> str:
    if not text:
        return ""
    return (
        text.replace("℃", "C")
        .replace("'", "'")
        .replace(""", '"')
        .replace(""", '"')
        .encode("latin-1", errors="replace")
        .decode("latin-1")
    )


class CataloguePDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "Malice Mizer Print Archive", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def fetch_data() -> tuple[list[dict], list[dict]]:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        issues = [dict(row) for row in connection.execute(
            """
            SELECT i.*, p.name_en AS publication_name
            FROM issues i
            JOIN publications p ON p.slug = i.publication
            ORDER BY i.publication_date, p.priority, i.id
            """
        )]
        articles = [dict(row) for row in connection.execute("SELECT * FROM articles ORDER BY issue_id, id")]
    finally:
        connection.close()
    return issues, articles


def status_badge(status: str) -> str:
    return status.replace("_", " ").upper()


def main() -> int:
    if not DB_PATH.exists():
        print("Database not found. Run build_db.py first.", file=sys.stderr)
        return 1

    ensure_dirs()
    issues, articles = fetch_data()
    articles_by_issue: dict[str, list[dict]] = defaultdict(list)
    for article in articles:
        articles_by_issue[article["issue_id"]].append(article)

    pdf = CataloguePDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0,
        6,
        "Bibliography of known and suspected Malice Mizer print appearances. "
        "Verification statuses reflect current research confidence.",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(4)

    current_year = None
    for issue in issues:
        year = issue["publication_date"][:4]
        if year != current_year:
            current_year = year
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 8, year, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)

        issue_label = pdf_safe(issue["publication_name"])
        if issue.get("issue_number"):
            issue_label += f" #{issue['issue_number']}"
        issue_label += f" ({issue['publication_date']})"
        issue_label = pdf_safe(issue_label)

        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 6, issue_label, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(
            0,
            5,
            f"Status: {status_badge(issue['verification_status'])}",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        if issue.get("source_notes"):
            pdf.multi_cell(0, 5, pdf_safe(issue["source_notes"]), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)

        for article in articles_by_issue.get(issue["id"], []):
            title = pdf_safe(article["title_en"] or article["title_ja"] or "(untitled)")
            line = f"  - [{article['type']}] {title}"
            if article.get("pages"):
                line += f" (p. {pdf_safe(article['pages'])})"
            pdf.multi_cell(0, 5, pdf_safe(line), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    output = EXPORTS_DIR / "catalogue.pdf"
    pdf.output(str(output))
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
