#!/usr/bin/env python3
"""Augment concert YAML with setlists and performance video links.

Sources (in priority order):
  1. scripts/research/concert_augmentation_catalog.yaml (curated)
  2. setlist.fm HTML (recent reunion shows)
  3. Internet Archive advanced search (date-matched live footage)

Run: python scripts/research/augment_concerts.py [--dry-run] [--limit N]
Then: make build
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "concerts"
CATALOG = Path(__file__).resolve().parent / "concert_augmentation_catalog.yaml"
TODAY = datetime.now().strftime("%Y-%m-%d")
USER_AGENT = "MaliceMizerArchive/1.0 (research; contact via malice-mizer-print-archive)"

sys.path.insert(0, str(ROOT / "scripts"))
from common import iter_yaml_files, load_songs, song_slugs  # noqa: E402

# Manual aliases for setlist.fm / fan-setlist spellings → v1 song slug.
SONG_ALIASES: dict[str, str] = {
    "de memoire": "de-memoire",
    "apres midi": "apres-midi",
    "apr s midi aru paris no gogo de": "apres-midi-paris",
    "n p s n g s": "nps-ngs",
    "n ps n gs": "nps-ngs",
    "ma ch rie itoshii kimi e": "ma-cherie",
    "ma ch rie": "ma-cherie",
    "aegen": "aege-sugisarishi-kaze",
    "aegean sugisarishi kaze to tomo ni": "aege-sugisarishi-kaze",
    "je te veux": "ju-te-veux",
    "ju te veux": "ju-te-veux",
    "s conscious": "s-conscious",
    "syunikiss": "syunikiss",
    "syunikiss nidome no aitou": "syunikiss",
    "tsuioku no kakera": "tsuioku-no-hahen",
    "tsuioku no hahen": "tsuioku-no-hahen",
    "shi no butou": "shi-no-butou",
    "hamon kyousoukyoku": "hamon-kyousoukyoku",
    "hamon kyoso kyoku": "hamon-kyousoukyoku",
    "mezame no rasen": "mezame-no-rasen",
    "gekka no yasoukyoku": "gekka-no-yasoukyoku",
    "gekka no yasoukyoku de l image": "gekka-de-limage",
    "bel air kuuhaku no toki no naka de": "bel-air",
    "bel air": "bel-air",
    "le ciel": "le-ciel",
    "au revoir": "au-revoir",
    "illuminati": "illuminati",
    "madrigal": "madrigal",
    "brise": "brise",
    "saikai no chi to bara": "saikai-no-chi-to-bara",
    "kyomu no naka de no yuugi": "kyomu-no-naka-de-no-yugi",
    "kioku to sora": "kioku-to-sora",
    "unmei no deai": "unmei-no-deai",
    "zencho": "zencho",
    "saikai": "saikai",
    "beast of blood": "beast-of-blood",
    "intro des congratulations": "intro-des-congratulations",
    "8": "8",
}


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_song_index() -> dict[str, str]:
    index: dict[str, str] = dict(SONG_ALIASES)
    valid = song_slugs()
    for song in load_songs():
        slug = song["id"]
        if slug not in valid:
            continue
        index[normalize(slug.replace("-", " "))] = slug
        index[normalize(slug)] = slug
        for field in ("title_en", "title_ja"):
            value = song.get(field)
            if value:
                index[normalize(value)] = slug
    return index


def match_song(name: str, index: dict[str, str]) -> str | None:
    key = normalize(name)
    if key in index:
        return index[key]
    # Strip parenthetical / subtitle tails
    short = re.sub(r"\s~.*$", "", key).strip()
    if short in index:
        return index[short]
    # Prefix match on longest keys
    best: tuple[int, str] | None = None
    for alias, slug in index.items():
        if key.startswith(alias) or alias.startswith(key):
            score = min(len(key), len(alias))
            if best is None or score > best[0]:
                best = (score, slug)
    return best[1] if best and best[0] >= 4 else None


def fetch(url: str, timeout: int = 20) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_setlist_fm_date(html: str) -> str | None:
    match = re.search(r"on ([A-Za-z]+ \d{1,2}, \d{4})", html)
    if not match:
        return None
    try:
        parsed = datetime.strptime(match.group(1), "%B %d, %Y")
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return None


def parse_setlist_fm_songs(html: str) -> list[str]:
    match = re.search(r"YouTubeSearch\.setPlaylist\((\[.*?\]), false\)", html)
    if not match:
        return []
    try:
        entries = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []
    return [entry.get("song", "") for entry in entries if entry.get("song")]


def load_setlist_fm_index() -> dict[str, list[str]]:
    """Return {YYYY-MM-DD: [song names]} from setlist.fm search results."""
    by_date: dict[str, list[str]] = {}
    search_url = "https://www.setlist.fm/search?query=Malice+Mizer"
    try:
        html = fetch(search_url)
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"  setlist.fm search unavailable: {exc}", file=sys.stderr)
        return by_date

    paths = sorted(set(re.findall(r"(setlist/malice-mizer/[^\"']+\.html)", html)))
    for path in paths:
        url = f"https://www.setlist.fm/{path}"
        try:
            page = fetch(url)
            time.sleep(0.5)
        except (urllib.error.URLError, TimeoutError):
            continue
        date = parse_setlist_fm_date(page)
        songs = parse_setlist_fm_songs(page)
        if date and songs:
            by_date[date] = songs
            print(f"  setlist.fm: {date} ({len(songs)} songs)")
    return by_date


def load_ia_by_date(catalog: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Merge catalog IA mappings with live API search for malice mizer movies."""
    by_date: dict[str, list[dict[str, Any]]] = {}
    for date, items in catalog.get("internet_archive_by_date", {}).items():
        by_date.setdefault(date, []).extend(items)

    query = urllib.parse.urlencode(
        {
            "q": 'creator:"MALICE MIZER" AND mediatype:movies',
            "fl[]": ["identifier", "title", "date"],
            "rows": 100,
            "output": "json",
        }
    )
    url = f"https://archive.org/advancedsearch.php?{query}"
    try:
        payload = json.loads(fetch(url))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"  Internet Archive search unavailable: {exc}", file=sys.stderr)
        return by_date

    live_keywords = ("live", "concert", "final", "merveilles", "memoire", "deep sanct", "tetsu")
    for doc in payload.get("response", {}).get("docs", []):
        title = (doc.get("title") or "").lower()
        if not any(word in title for word in live_keywords):
            continue
        raw_date = doc.get("date")
        if not raw_date:
            continue
        date = str(raw_date)[:10]
        if not re.match(r"\d{4}-\d{2}-\d{2}", date):
            continue
        entry = {
            "identifier": doc["identifier"],
            "title": doc.get("title", doc["identifier"]),
            "quality": "unknown",
        }
        existing_ids = {item["identifier"] for item in by_date.get(date, [])}
        if doc["identifier"] not in existing_ids:
            by_date.setdefault(date, []).append(entry)
    return by_date


def songs_to_slugs(names: list[str], index: dict[str, str]) -> list[str]:
    slugs: list[str] = []
    valid = song_slugs()
    for name in names:
        slug = match_song(name, index)
        if slug and slug in valid and slug not in slugs:
            slugs.append(slug)
    return slugs


def performance_url_exists(performances: list[dict[str, Any]], url: str) -> bool:
    return any(p.get("url") == url for p in performances)


def ia_performance(item: dict[str, Any]) -> dict[str, Any]:
    identifier = item["identifier"]
    return {
        "url": f"https://archive.org/details/{identifier}",
        "platform": "archive_org",
        "quality": item.get("quality", "unknown"),
        "title": item.get("title", identifier),
        "notes": item.get("notes", "Matched via Internet Archive search."),
    }


def setlist_fm_performance(url: str, date: str) -> dict[str, Any]:
    return {
        "url": url,
        "platform": "other",
        "quality": "unknown",
        "title": f"Setlist.fm ({date})",
        "notes": "Community-submitted setlist reference.",
    }


def append_changelog(doc: dict[str, Any], notes: str) -> None:
    doc.setdefault("changelog", []).append(
        {
            "date": TODAY,
            "action": "augmented",
            "source": "augment_concerts",
            "notes": notes,
        }
    )


def merge_setlist(doc: dict[str, Any], slugs: list[str], source: str) -> bool:
    if not slugs or doc.get("setlist"):
        return False
    doc["setlist"] = slugs
    append_changelog(doc, f"Setlist added from {source} ({len(slugs)} songs)")
    return True


def merge_performances(doc: dict[str, Any], new_items: list[dict[str, Any]], source: str) -> bool:
    if not new_items:
        return False
    performances = list(doc.get("performances") or [])
    added = 0
    for item in new_items:
        if not performance_url_exists(performances, item["url"]):
            performances.append(item)
            added += 1
    if not added:
        return False
    doc["performances"] = performances
    append_changelog(doc, f"Added {added} performance link(s) from {source}")
    return True


def augment_concert(
    doc: dict[str, Any],
    *,
    catalog_entry: dict[str, Any] | None,
    setlist_fm: dict[str, list[str]],
    ia_by_date: dict[str, list[dict[str, Any]]],
    song_index: dict[str, str],
    setlist_fm_urls: dict[str, str],
) -> tuple[bool, list[str]]:
    concert_id = doc["id"]
    date = doc.get("date", "")
    changes: list[str] = []
    changed = False

    # --- Setlist ---
    if not doc.get("setlist"):
        slugs: list[str] = []
        source = ""
        if catalog_entry and catalog_entry.get("setlist"):
            slugs = catalog_entry["setlist"]
            source = catalog_entry.get("setlist_source", "curated catalog")
        elif date in setlist_fm:
            slugs = songs_to_slugs(setlist_fm[date], song_index)
            source = "setlist.fm"
        if slugs:
            if merge_setlist(doc, slugs, source):
                changes.append(f"setlist ({len(slugs)} songs)")
                changed = True
            if catalog_entry and catalog_entry.get("verification_status"):
                doc["verification_status"] = catalog_entry["verification_status"]

    # --- Performances ---
    new_performances: list[dict[str, Any]] = []

    if catalog_entry:
        for perf in catalog_entry.get("performances") or []:
            new_performances.append(perf)

    for item in ia_by_date.get(date, []):
        new_performances.append(ia_performance(item))

    if date in setlist_fm_urls:
        url = setlist_fm_urls[date]
        new_performances.append(setlist_fm_performance(url, date))

    if merge_performances(doc, new_performances, "augment_concerts"):
        changes.append("performances")
        changed = True

    return changed, changes


def load_catalog() -> dict[str, Any]:
    if not CATALOG.exists():
        return {"concerts": {}, "internet_archive_by_date": {}}
    return yaml.safe_load(CATALOG.read_text(encoding="utf-8")) or {}


def build_setlist_fm_url_index() -> dict[str, str]:
    urls: dict[str, str] = {}
    try:
        html = fetch("https://www.setlist.fm/search?query=Malice+Mizer")
    except (urllib.error.URLError, TimeoutError):
        return urls
    for path in set(re.findall(r"(setlist/malice-mizer/[^\"']+\.html)", html)):
        url = f"https://www.setlist.fm/{path}"
        try:
            page = fetch(url)
            time.sleep(0.3)
        except (urllib.error.URLError, TimeoutError):
            continue
        date = parse_setlist_fm_date(page)
        if date:
            urls[date] = url
    return urls


def main() -> int:
    parser = argparse.ArgumentParser(description="Augment concert YAML with setlists and videos.")
    parser.add_argument("--dry-run", action="store_true", help="Report changes without writing files")
    parser.add_argument("--limit", type=int, default=0, help="Process at most N concerts (0 = all)")
    args = parser.parse_args()

    print("Loading song index…")
    song_index = build_song_index()
    catalog = load_catalog()
    catalog_concerts: dict[str, Any] = catalog.get("concerts") or {}

    print("Fetching setlist.fm…")
    setlist_fm = load_setlist_fm_index()
    setlist_fm_urls = build_setlist_fm_url_index()

    print("Fetching Internet Archive…")
    ia_by_date = load_ia_by_date(catalog)

    paths = iter_yaml_files(DATA)
    if args.limit:
        paths = paths[: args.limit]

    updated = 0
    skipped = 0
    for path in paths:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        concert_id = doc.get("id", path.stem)
        entry = catalog_concerts.get(concert_id)

        changed, notes = augment_concert(
            doc,
            catalog_entry=entry,
            setlist_fm=setlist_fm,
            ia_by_date=ia_by_date,
            song_index=song_index,
            setlist_fm_urls=setlist_fm_urls,
        )

        if changed:
            updated += 1
            print(f"{'[dry-run] ' if args.dry_run else ''}✓ {concert_id}: {', '.join(notes)}")
            if not args.dry_run:
                path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
        else:
            skipped += 1

    print(f"\nDone: {updated} updated, {skipped} unchanged ({len(paths)} total)")
    if updated and not args.dry_run:
        print("Run `make build` to refresh archive.json and the site.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
