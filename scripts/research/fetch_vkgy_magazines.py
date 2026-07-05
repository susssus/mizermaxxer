#!/usr/bin/env python3
"""Fetch vk.gy magazine index pages and catalog MALICE MIZER appearances.

Extends fetch_vkgy_fools_mate.py to SHOXX, Cure, GiGS, B-PASS, Arena37℃, Vicious, PATi PATi.

Output: scripts/research/vkgy_{slug}_malice_mizer.yaml per magazine.
"""

from __future__ import annotations

import re
import time
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
USER_AGENT = "Mozilla/5.0 (compatible; malice-mizer-print-archive/1.0)"

MAGAZINES = {
    "shoxx": {
        "index_url": "https://vk.gy/magazines/shoxx/",
        "link_pattern": r'href="(/magazines/shoxx/(\d+)/vol-(\d+)/)"',
        "issue_key": "vol",
    },
    "cure": {
        "index_url": "https://vk.gy/magazines/cure/",
        "link_pattern": r'href="(/magazines/cure/(\d+)/(\d{4}-\d{2})/)"',
        "issue_key": "date",
    },
    "gigs": {
        "index_url": "https://vk.gy/magazines/gigs/",
        "link_pattern": r'href="(/magazines/gigs/(\d+)/no-(\d+)/)"',
        "issue_key": "no",
    },
    "b-pass": {
        "index_url": "https://vk.gy/magazines/b-pass/",
        "link_pattern": r'href="(/magazines/b-pass/(\d+)/(\d{4}-\d{2})/)"',
        "issue_key": "date",
    },
    "arena37": {
        "index_url": "https://vk.gy/magazines/arena37/",
        "link_pattern": r'href="(/magazines/arena37/(\d+)/no-(\d+)/)"',
        "issue_key": "no",
    },
    "vicious": {
        "index_url": "https://vk.gy/magazines/vicious/",
        "link_pattern": r'href="(/magazines/vicious/(\d+)/(\d{4}-\d{2}(?:-vol-\d+)?)/)"',
        "issue_key": "date",
    },
    "pati-pati": {
        "index_url": "https://vk.gy/magazines/pati-pati/",
        "link_pattern": r'href="(/magazines/pati-pati/(\d+)/vol-(\d+)/)"',
        "issue_key": "vol",
    },
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_issue_page(html: str) -> dict:
    out: dict = {
        "cover_artists": [],
        "large_features": [],
        "other_appearances": [],
        "flyers": [],
    }

    for pat in (
        r"Date[^0-9]{0,40}((?:19|20)\d{2}-\d{2})",
        r">\s*((?:19|20)\d{2}-\d{2})\s*</div>",
    ):
        dm = re.search(pat, html)
        if dm:
            out["publication_date"] = dm.group(1)
            break

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


def parse_index(html: str, slug: str, config: dict) -> list[dict]:
    pattern = config["link_pattern"]
    seen: set[str] = set()
    issues: list[dict] = []
    for m in re.finditer(pattern, html):
        path, vkgy_id, key = m.group(1), m.group(2), m.group(3)
        if path in seen:
            continue
        seen.add(path)
        entry: dict = {
            "vkgy_id": vkgy_id,
            "url": f"https://vk.gy{path}",
        }
        if config["issue_key"] == "date":
            entry["publication_date"] = key[:7] if len(key) >= 7 else key
        else:
            entry["issue_number"] = key.lstrip("0") or key
        issues.append(entry)
    return issues


def harvest_magazine(slug: str, config: dict, delay: float = 0.35) -> Path:
    out_path = ROOT / "scripts" / "research" / f"vkgy_{slug.replace('-', '_')}_malice_mizer.yaml"
    print(f"\n=== {slug} ===")
    index_html = fetch(config["index_url"])
    index_issues = parse_index(index_html, slug, config)
    print(f"Index: {len(index_issues)} issues")

    entries = []
    checked = 0
    for meta in index_issues:
        checked += 1
        url = meta["url"]
        label = meta.get("issue_number") or meta.get("publication_date") or meta["vkgy_id"]
        print(f"  {label} …", end="", flush=True)
        try:
            html = fetch(url)
            parsed = parse_issue_page(html)
        except Exception as exc:  # noqa: BLE001
            print(f" error: {exc}")
            continue
        if parsed.get("has_malice_mizer"):
            entry = {
                "issue_number": meta.get("issue_number"),
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
        time.sleep(delay)

    doc = {
        "generated": "2026-07-06",
        "publication": slug,
        "source_index": config["index_url"],
        "source_notes": "vkgy (ブイケージ) per-issue TOC; MM entries only.",
        "issues_checked": checked,
        "issues_with_malice_mizer": len(entries),
        "entries": sorted(
            entries,
            key=lambda e: (
                e.get("publication_date") or "",
                int(e["issue_number"]) if e.get("issue_number") and str(e["issue_number"]).isdigit() else 0,
            ),
        ),
    }
    out_path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    print(f"Wrote {len(entries)} MM entries ({checked} checked) → {out_path.name}")
    return out_path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Harvest vk.gy magazine indexes for MM appearances.")
    parser.add_argument(
        "--magazines",
        nargs="*",
        default=list(MAGAZINES.keys()),
        choices=list(MAGAZINES.keys()),
        help="Magazines to harvest (default: all)",
    )
    parser.add_argument("--delay", type=float, default=0.35, help="Delay between issue page fetches")
    args = parser.parse_args()

    for slug in args.magazines:
        harvest_magazine(slug, MAGAZINES[slug], delay=args.delay)


if __name__ == "__main__":
    main()
