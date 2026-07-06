#!/usr/bin/env python3
"""Extract magazine mentions from vk.gy artist timeline into import catalog entries.

Used for publications without usable vk.gy index pages (e.g. POP BEAT) or to
supplement vol-only mentions (uv, M GAZETTE) with timeline dates.

Output: scripts/research/vkgy_timeline_magazines.yaml
"""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "scripts" / "research" / "vkgy_timeline_magazines.yaml"
ARTIST_URL = "https://vk.gy/artists/malice-mizer/"
USER_AGENT = "Mozilla/5.0 (compatible; malice-mizer-print-archive/1.0)"

# (publication slug, regex on history section lines)
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("pop-beat", re.compile(r"POP BEAT.*?(\d{4}-\d{2})\1")),
    ("uv", re.compile(r"UVUV Vol\.(\d+)Vol\.\1")),
    ("m-gazette", re.compile(r"M GAZETTE.*?Vol\.(\d+)Vol\.\1")),
    ("j-rock-magazine", re.compile(r"J-Rock Magazine.*?Vol\.(\d+)Vol\.\1")),
    ("newsmaker", re.compile(r"Newsmaker.*?Vol\.(\d+)Vol\.\1")),
    (
        "vicious",
        re.compile(r"ViciousVicious (\d{4}) (\d{1,2}) Vol\.(\d+)\1 \2 Vol\.\3"),
    ),
    ("ongaku-to-hito", re.compile(r"ONGAKU TO HITO.*?(\d{4}-\d{2})\1")),
    ("b-pass", re.compile(r"B-PASS.*?(\d{4}-\d{2})\1")),
    ("band-yarouze", re.compile(r"BAND YAROZE.*?(\d{4}-\d{2})\1")),
    ("gigs", re.compile(r"GiGS.*?No\.(\d+)No\.\1")),
    ("pati-pati", re.compile(r"PATi▶PATi.*?VOL\.(\d+)VOL\.\1")),
]


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_history_text(html: str) -> str:
    """Prefer HTML history block; fall back to markdown export."""
    m = re.search(r'id="history"|class="history[^"]*"', html, re.I)
    if m:
        chunk = html[m.start() : m.start() + 200_000]
        return re.sub(r"<[^>]+>", "\n", chunk)
    m = re.search(r"## History.*?(?=## Live history|## Comments)", html, re.S)
    if m:
        return m.group(0)
    return html


def parse_entries(text: str) -> list[dict]:
    entries: dict[tuple, dict] = {}

    def add(pub: str, *, issue_date: str | None = None, issue_number: str | None = None) -> None:
        if issue_date and len(issue_date) >= 7:
            issue_date = issue_date[:7]
        if issue_number is not None:
            issue_number = str(int(issue_number)) if str(issue_number).isdigit() else str(issue_number)
        key = (pub, issue_date, issue_number)
        if key in entries:
            return
        entry: dict = {
            "publication": pub,
            "issue_date": issue_date,
            "issue_number": issue_number,
            "sources": [{"id": "vkgy-timeline", "url": ARTIST_URL}],
            "notes": "vk.gy artist timeline mention",
        }
        if pub == "vicious" and issue_date:
            parts = issue_date.split("-")
            if len(parts) == 2:
                entry["issue_date"] = f"{parts[0]}-{int(parts[1]):02d}"
        entries[key] = entry

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        for pub, pat in PATTERNS:
            m = pat.search(line)
            if not m:
                continue
            if pub == "vicious":
                year, month, vol = m.group(1), m.group(2), m.group(3)
                add(pub, issue_date=f"{year}-{int(month):02d}", issue_number=vol)
            elif pub in ("pop-beat", "b-pass", "band-yarouze", "ongaku-to-hito"):
                add(pub, issue_date=m.group(1))
            else:
                add(pub, issue_number=m.group(1))

    return sorted(
        entries.values(),
        key=lambda e: (
            e["publication"],
            e.get("issue_date") or "",
            int(e["issue_number"]) if e.get("issue_number") and str(e["issue_number"]).isdigit() else 0,
        ),
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Parse vk.gy artist timeline for magazine mentions.")
    parser.add_argument("--input", type=Path, help="Local HTML/markdown file instead of fetching")
    args = parser.parse_args()

    if args.input:
        raw = args.input.read_text(encoding="utf-8")
    else:
        print(f"Fetching {ARTIST_URL} …")
        raw = fetch(ARTIST_URL)

    text = extract_history_text(raw)
    entries = parse_entries(text)

    doc = {
        "generated": "2026-07-06",
        "source": ARTIST_URL,
        "source_notes": "vk.gy artist profile history section; magazine mentions only.",
        "entry_count": len(entries),
        "entries": entries,
    }
    OUT.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    by_pub: dict[str, int] = {}
    for e in entries:
        by_pub[e["publication"]] = by_pub.get(e["publication"], 0) + 1
    print(f"Wrote {len(entries)} timeline entries → {OUT.name}")
    for pub, count in sorted(by_pub.items()):
        print(f"  {pub}: {count}")


if __name__ == "__main__":
    main()
