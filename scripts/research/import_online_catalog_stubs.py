#!/usr/bin/env python3
"""Import missing entries from magazine_references_online.yaml into data/issues/ stubs."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ISSUES = ROOT / "data" / "issues"
CATALOG = ROOT / "scripts" / "research" / "magazine_references_online.yaml"
SCAN_CATALOG = ROOT / "scripts" / "research" / "scan_sources_catalog.yaml"
VKGY_DIR = ROOT / "scripts" / "research"
ARTIST_TIMELINE_URL = "https://vk.gy/artists/malice-mizer/"
TODAY = "2026-07-06"

NDL_PUB_NAMES = {
    "fools-mate": "FOOL'S MATE",
    "shoxx": "SHOXX",
    "arena37": "Arena37",
    "cure": "Cure",
    "gigs": "GiGS",
    "pati-pati": "PATi PATi",
    "b-pass": "B-PASS",
    "vicious": "Vicious",
    "m-gazette": "M GAZETTE",
    "cd-skit": "CD SKiT",
    "band-yarouze": "Band Yarouze",
    "artist-fan": "Artist Fan",
    "j-rock-magazine": "J-Rock Magazine",
    "apres-guerre": "Après Guerre",
    "pop-beat": "POP BEAT",
    "uv": "uv",
    "friday": "Friday",
    "cutie": "Cutie",
    "cd-data": "CD Data",
    "myojo": "Myojo",
    "quick-japan": "Quick Japan",
    "luck-das": "Luck-das",
    "zy": "Zy",
    "gb": "GB",
    "astan": "Astan",
    "band-style": "Band Style",
    "band-x-artist": "Band x Artist",
    "band-collection": "Band Collection",
    "bidan": "Bidan",
    "creation": "Creation",
    "clap": "Clap!",
    "da-vinchi": "Da Vinchi",
    "fruige": "Fruige",
    "dears": "Dears",
    "newsmaker": "Newsmaker",
    "ongaku-to-hito": "Ongaku to Hito",
}


def load_existing_keys() -> set[tuple[str, str | None, str | None]]:
    keys: set[tuple[str, str | None, str | None]] = set()
    for path in ISSUES.rglob("*.yaml"):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        pub = doc.get("publication")
        date = doc.get("publication_date")
        num = doc.get("issue_number")
        if pub:
            keys.add((pub, date, str(num) if num else None))
    return keys


def issue_file_path(pub: str, issue_date: str | None, issue_number: str | None) -> Path:
    if issue_date:
        # normalize YYYY-MM or YYYY-MM-DD
        if len(issue_date) >= 7:
            stem = issue_date[:7]
        else:
            stem = issue_date
        return ISSUES / pub / f"{stem}.yaml"
    if issue_number:
        safe = re.sub(r"[^\w.-]", "", str(issue_number))
        return ISSUES / pub / f"vol-{safe}.yaml"
    return ISSUES / pub / "unknown.yaml"


def make_issue_id(pub: str, issue_date: str | None, issue_number: str | None) -> str:
    if issue_date and len(issue_date) >= 7:
        return f"{pub}-{issue_date[:7]}"
    if issue_number:
        return f"{pub}-vol-{issue_number}"
    return f"{pub}-unknown"


def infer_article_type(entry: dict) -> str:
    notes = (entry.get("coverage_notes") or "").lower()
    if "表紙" in notes or "cover" in notes:
        return "cover"
    if "インタビュー" in notes or "interview" in notes:
        return "interview"
    if "レポ" in notes or "report" in notes:
        return "live_report"
    if "フォト" in notes or "photo" in notes:
        return "photo_spread"
    roles = entry.get("roles") or []
    if "cover" in roles:
        return "cover"
    if "large_feature" in roles:
        return "photo_spread"
    return "mention"


def infer_status(entry: dict) -> str:
    sources = entry.get("sources") or []
    if entry.get("coverage_notes") and len(sources) >= 2:
        return "possible"
    if entry.get("coverage_notes") or len(sources) >= 2:
        return "possible"
    if entry.get("scan", {}).get("available"):
        return "possible"
    return "mention_only"


def build_source_notes(entry: dict) -> str:
    parts: list[str] = []
    if entry.get("coverage_notes"):
        parts.append(entry["coverage_notes"])
    for s in entry.get("sources") or []:
        sid = s.get("id", "")
        url = s.get("url", "")
        if url:
            parts.append(f"[{sid}] {url}")
    if entry.get("notes"):
        parts.append(entry["notes"])
    if entry.get("url"):
        parts.append(f"vkgy: {entry['url']}")
    return "\n".join(parts).strip()


def article_stub(issue_id: str, entry: dict) -> dict:
    scan = entry.get("scan") or {}
    scan_url = scan.get("url")
    atype = infer_article_type(entry)
    return {
        "id": f"{issue_id}-001",
        "title_ja": None,
        "title_en": entry.get("title"),
        "type": atype,
        "pages": None,
        "members": [],
        "photographer": None,
        "writer": None,
        "cover": atype == "cover" or "cover" in (entry.get("roles") or []),
        "poster": False,
        "foldout": False,
        "scan": {
            "available": bool(scan_url),
            "quality": "medium" if scan_url else None,
            "url": scan_url,
        },
        "translation": {"available": False, "url": None},
        "purchase_links": [],
        "notes": entry.get("coverage_notes") or "",
    }


def entry_from_vkgy(vkgy_entry: dict, publication: str) -> dict:
    scan_url = None
    return {
        "publication": publication,
        "issue_number": vkgy_entry.get("issue_number"),
        "issue_date": vkgy_entry.get("publication_date"),
        "coverage_notes": None,
        "roles": vkgy_entry.get("roles"),
        "url": vkgy_entry.get("url"),
        "sources": [{"id": "vkgy", "url": vkgy_entry.get("url") or f"https://vk.gy/magazines/{publication}/"}],
        "scan": {"available": bool(scan_url), "url": scan_url},
    }


def load_vkgy_entries() -> list[dict]:
    entries: list[dict] = []
    for path in sorted(VKGY_DIR.glob("vkgy_*_malice_mizer.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        pub = doc.get("publication")
        if not pub and "fools-mate" in path.name:
            pub = "fools-mate"
        if not pub:
            m = re.search(r"vkgy_([a-z0-9_]+)_malice", path.name)
            pub = m.group(1).replace("_", "-") if m else None
        for e in doc.get("entries") or []:
            entries.append(entry_from_vkgy(e, pub))

    timeline_path = VKGY_DIR / "vkgy_timeline_magazines.yaml"
    if timeline_path.exists():
        doc = yaml.safe_load(timeline_path.read_text(encoding="utf-8"))
        for e in doc.get("entries") or []:
            entries.append(
                {
                    "publication": e["publication"],
                    "issue_number": e.get("issue_number"),
                    "issue_date": e.get("issue_date"),
                    "coverage_notes": e.get("notes"),
                    "url": ARTIST_TIMELINE_URL,
                    "sources": e.get("sources") or [{"id": "vkgy-timeline", "url": ARTIST_TIMELINE_URL}],
                    "scan": {"available": False, "url": None},
                }
            )
    return entries


def merge_catalog_entries(online: list[dict], vkgy: list[dict]) -> list[dict]:
    merged: dict[tuple, dict] = {}

    def key(e: dict) -> tuple:
        num = e.get("issue_number")
        if num is not None:
            num = str(num).lstrip("0") or str(num)
        date = e.get("issue_date")
        if date and len(date) >= 7:
            date = date[:7]
        return (e["publication"], num, date)

    for e in online:
        merged[key(e)] = dict(e)
    for e in vkgy:
        k = key(e)
        if k not in merged:
            merged[k] = e
        else:
            m = merged[k]
            for s in e.get("sources", []):
                if s not in m.get("sources", []):
                    m.setdefault("sources", []).append(s)
            if e.get("url") and not m.get("url"):
                m["url"] = e["url"]
            if e.get("roles"):
                m["roles"] = e["roles"]
    return list(merged.values())


def load_scan_url_index() -> dict[tuple[str, str | None, str | None], str]:
    """Map (publication, date, issue_number) -> scan_url from scan_sources_catalog."""
    if not SCAN_CATALOG.exists():
        return {}
    doc = yaml.safe_load(SCAN_CATALOG.read_text(encoding="utf-8"))
    index: dict[tuple[str, str | None, str | None], str] = {}
    for item in doc.get("items") or []:
        pub = item.get("publication")
        url = item.get("scan_url")
        if not pub or not url:
            continue
        date = item.get("issue_date")
        if date and len(str(date)) >= 7:
            date = str(date)[:7]
        num = item.get("issue_number")
        if num is not None:
            num = str(num).lstrip("0") or str(num)
        index[(pub, date, num)] = url
        if date:
            index[(pub, date, None)] = url
        if num:
            index[(pub, None, num)] = url
    return index


def lookup_scan(entry: dict, scan_index: dict) -> str | None:
    pub = entry.get("publication")
    date = entry.get("issue_date")
    if date and len(str(date)) >= 7:
        date = str(date)[:7]
    num = entry.get("issue_number")
    if num is not None:
        num = str(num).lstrip("0") or str(num)
    for key in ((pub, date, num), (pub, date, None), (pub, None, num)):
        if key in scan_index:
            return scan_index[key]
    scan = entry.get("scan") or {}
    return scan.get("url")


def main() -> None:
    catalog = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    online_entries = catalog.get("entries") or []
    vkgy_entries = load_vkgy_entries()
    all_entries = merge_catalog_entries(online_entries, vkgy_entries)
    scan_index = load_scan_url_index()

    existing = load_existing_keys()
    created = 0
    skipped = 0

    for entry in all_entries:
        pub = entry.get("publication")
        if not pub:
            continue
        issue_date = entry.get("issue_date")
        if issue_date and len(str(issue_date)) >= 7:
            issue_date = str(issue_date)[:7]
        issue_number = entry.get("issue_number")
        if issue_number is not None:
            issue_number = str(issue_number).lstrip("0") or str(issue_number)

        ek = (pub, issue_date, issue_number)
        if ek in existing:
            skipped += 1
            continue
        # also skip if same pub+date exists with different issue number
        if issue_date and any(k[0] == pub and k[1] == issue_date for k in existing):
            skipped += 1
            continue

        issue_id = make_issue_id(pub, issue_date, issue_number)
        path = issue_file_path(pub, issue_date, issue_number)
        if path.exists():
            skipped += 1
            continue

        scan_url = lookup_scan(entry, scan_index)
        if scan_url:
            entry = dict(entry)
            entry["scan"] = {"available": True, "url": scan_url}

        data = {
            "id": issue_id,
            "publication": pub,
            "issue_number": issue_number,
            "volume": None,
            "publication_date": issue_date or "1999",
            "date_precision": "month" if issue_date else "year",
            "verification_status": infer_status(entry),
            "source_notes": build_source_notes(entry),
            "research_targets": [
                "exact issue numbers",
                "page numbers",
                "scan availability",
            ],
            "articles": [article_stub(issue_id, entry)],
            "changelog": [
                {
                    "date": TODAY,
                    "action": "created",
                    "source": "online_catalog_import",
                    "notes": "Imported from merged online bibliography catalog.",
                }
            ],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        existing.add(ek)
        created += 1

    print(f"Created {created} issue stubs, skipped {skipped} existing.")


if __name__ == "__main__":
    main()
