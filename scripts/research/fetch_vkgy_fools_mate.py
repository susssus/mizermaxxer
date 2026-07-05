#!/usr/bin/env python3
"""Fetch vk.gy FOOL'S MATE issue pages and catalog MALICE MIZER appearances.

Index: https://vk.gy/magazines/fools-mate/
Issue URL pattern: https://vk.gy/magazines/fools-mate/{vkgy_id}/no{issue_number}/

Output: scripts/research/vkgy_fools_mate_malice_mizer.yaml
"""

from __future__ import annotations

import json
import re
import time
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "scripts/research/vkgy_fools_mate_malice_mizer.yaml"
INDEX_URL = "https://vk.gy/magazines/fools-mate/"
USER_AGENT = "Mozilla/5.0 (compatible; malice-mizer-print-archive/1.0)"

# MM-active era on vkgy timeline (1992–2001 band period).
ISSUE_RANGE = range(133, 243)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_issue_index(html: str) -> dict[str, dict]:
    """Map issue_number -> {vkgy_id, url, date}."""
    by_issue: dict[str, dict] = {}
    for m in re.finditer(r'href="(/magazines/fools-mate/(\d+)/no(\d+)/)"', html):
        path, vkgy_id, issue = m.group(1), m.group(2), m.group(3)
        start = max(0, m.start() - 100)
        ctx = html[start : m.start()]
        dm = re.search(r"(\d{4}-\d{2})", ctx)
        by_issue[issue] = {
            "issue_number": issue,
            "vkgy_id": vkgy_id,
            "url": f"https://vk.gy{path}",
            "publication_date": dm.group(1) if dm else None,
        }
    return by_issue


def parse_issue_page(html: str) -> dict:
    """Extract date and content sections mentioning bands."""
    out: dict = {
        "cover_artists": [],
        "large_features": [],
        "other_appearances": [],
        "flyers": [],
    }

    dm = re.search(r"Date公開日[^0-9]*(\d{4}-\d{2})", html)
    if dm:
        out["publication_date"] = dm.group(1)

    def artists_in_section(header: str) -> list[str]:
        m = re.search(rf"{header}\s*</h4>(.*?)(?:<h4|</section>|<!-- Flyers|$)", html, re.S | re.I)
        if not m:
            return []
        block = m.group(1)
        names = re.findall(
            r'class="volume__artist[^"]*"[^>]*>.*?<span>([^<]+)</span>',
            block,
            re.S,
        )
        return [re.sub(r"&#39;", "'", n.strip()) for n in names if n.strip()]

    out["cover_artists"] = artists_in_section("Cover artists")
    out["large_features"] = artists_in_section("Large features")
    out["other_appearances"] = artists_in_section("Other appearances")
    out["flyers"] = artists_in_section("Flyers")

    if "malice mizer" not in html.lower():
        return out

    out["has_malice_mizer"] = True
    roles = []
    if any("malice mizer" in x.lower() for x in out["cover_artists"]):
        roles.append("cover")
    if any("malice mizer" in x.lower() for x in out["large_features"]):
        roles.append("large_feature")
    if any("malice mizer" in x.lower() for x in out["other_appearances"]):
        roles.append("other_appearance")
    if any("malice mizer" in x.lower() for x in out["flyers"]):
        roles.append("flyer")
    out["roles"] = roles or ["mention"]
    return out


def main() -> None:
    print("Fetching index…")
    index_html = fetch(INDEX_URL)
    index = parse_issue_index(index_html)
    print(f"Index: {len(index)} issues")

    entries = []
    checked = 0
    for num in ISSUE_RANGE:
        meta = index.get(str(num))
        if not meta:
            continue
        checked += 1
        url = meta["url"]
        print(f"  no.{num} …", end="", flush=True)
        try:
            html = fetch(url)
            parsed = parse_issue_page(html)
        except Exception as exc:  # noqa: BLE001
            print(f" error: {exc}")
            continue
        if parsed.get("has_malice_mizer"):
            entry = {
                "issue_number": str(num),
                "publication_date": parsed.get("publication_date") or meta.get("publication_date"),
                "url": url,
                "roles": parsed.get("roles", []),
                "cover_artists": parsed.get("cover_artists") or None,
                "large_features": parsed.get("large_features") or None,
                "other_appearances": parsed.get("other_appearances") or None,
            }
            entries.append(entry)
            print(" MM ✓", parsed.get("roles"))
        else:
            print(" —")
        time.sleep(0.4)

    doc = {
        "generated": "2026-07-06",
        "source_index": INDEX_URL,
        "source_notes": "vkgy (ブイケージ) per-issue TOC; MM entries only.",
        "issues_checked": checked,
        "issues_with_malice_mizer": len(entries),
        "entries": sorted(entries, key=lambda e: int(e["issue_number"])),
    }
    OUT.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    print(f"\nWrote {len(entries)} MM entries ({checked} checked) → {OUT}")


if __name__ == "__main__":
    main()
