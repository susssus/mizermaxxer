#!/usr/bin/env python3
"""Fetch Discogs track titles and emit a language audit YAML for songs.

Read-only against Discogs; writes scripts/research/song_title_language_audit.yaml
(and a raw cache under scripts/research/.discogs_cache/).

Priority when the same slug appears on multiple releases:
  single > album/ep > compilation > video/misc
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sync_discogs import (  # noqa: E402
    DISCOGS_SECTION_HEADERS,
    RATE_LIMIT_SEC,
    fetch_entry,
    load_catalog,
    slugify,
)

OUT_PATH = Path(__file__).resolve().parent / "song_title_language_audit.yaml"
CACHE_DIR = Path(__file__).resolve().parent / ".discogs_cache"

CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
LATIN = re.compile(r"[A-Za-zÀ-ÿ]")

KIND_PRIORITY = {
    "single": 0,
    "album": 1,
    "compilation": 2,
    "video": 3,
    "misc": 4,
}

FR_HINTS = re.compile(
    r"\b("
    r"au revoir|le ciel|bel air|merveilles|bois|brise|ju te veux|"
    r"ma ch[eé]rie|apr[eè]s|de l['’]?image|de memoire|premier amour|"
    r"seraph|baroque|transylvania|madrigal|claire|bossa|jardin|"
    r"illuminati|conscious"  # illuminati often English; overridden below
    r")\b|"
    r"\b(de|du|des|la|le|les|sans|retour|merveilles)\b",
    re.I,
)
EN_HINTS = re.compile(
    r"\b("
    r"color me|blood|beast of|illuminati|conscious|despair|temptation|"
    r"float|gardenia|garnet|interview|night walk|last train|democracy|"
    r"colors|ashes|baptism|breath|bluster|speed of|no pains|no gains|"
    r"piece of broken|romance of|vault of heaven|hidden track|"
    r"band history|tv documentary|instrumental"
    r")\b",
    re.I,
)


def classify(title: str) -> str:
    t = title.strip()
    has_cjk = bool(CJK.search(t))
    has_latin = bool(LATIN.search(t))
    if has_cjk and has_latin:
        return "mixed"
    if has_cjk:
        return "japanese"
    # Pure Latin: distinguish French vs English vs other
    if EN_HINTS.search(t) and not FR_HINTS.search(t):
        return "english"
    # Known French MM titles / particles
    if FR_HINTS.search(t) or "～" in t or "~" in t and re.search(r"[A-Za-z].*~", t):
        # S-Conscious / Illuminati handled as english via EN_HINTS
        if re.search(r"\b(illuminati|s-conscious|conscious)\b", t, re.I):
            return "english"
        if re.search(r"\b(color me|beast of|blood|gardenia|garnet)\b", t, re.I):
            return "english"
        return "french"
    if EN_HINTS.search(t):
        return "english"
    if has_latin:
        return "other"
    return "other"


def cached_fetch(entry: dict[str, Any]) -> dict[str, Any]:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    d = entry["discogs"]
    key = f"{d['type']}_{d['id']}.json"
    path = CACHE_DIR / key
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    delay = max(RATE_LIMIT_SEC, 3.0)
    last_err: Exception | None = None
    for attempt in range(6):
        time.sleep(delay)
        try:
            meta = fetch_entry(d)
            # masters call twice internally; pause after success
            time.sleep(delay)
            path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            return meta
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            msg = str(exc)
            if "429" in msg or "Too Many" in msg:
                delay = min(delay * 2, 60)
                print(f"  429 backoff {delay:.0f}s (attempt {attempt + 1})", flush=True)
                continue
            raise
    assert last_err is not None
    raise last_err


def strip_variant_suffix(title: str) -> str:
    """Normalize light punctuation for slug matching."""
    t = title.strip()
    t = t.replace("〜", "～").replace("~", "～")
    t = re.sub(r"\s+", " ", t)
    return t


def main() -> None:
    catalog = load_catalog()
    # slug -> best observation
    best: dict[str, dict[str, Any]] = {}
    observations: dict[str, list[dict[str, Any]]] = {}

    for entry in catalog:
        slug_release = entry["slug"]
        kind = entry["kind"]
        print(f"Fetching {slug_release} ({kind})...", flush=True)
        try:
            meta = cached_fetch(entry)
        except Exception as exc:  # noqa: BLE001
            print(f"  FAIL: {exc}", flush=True)
            continue
        uri = meta.get("uri") or ""
        for track in meta.get("tracklist") or []:
            title = (track.get("title") or "").strip()
            if not title or title.lower() in DISCOGS_SECTION_HEADERS:
                continue
            if track.get("type_") == "heading":
                continue
            song_slug = slugify(title)
            obs = {
                "discogs_title": title,
                "language": classify(title),
                "source_release": slug_release,
                "source_kind": kind,
                "source_uri": uri,
                "position": track.get("position"),
            }
            observations.setdefault(song_slug, []).append(obs)
            cur = best.get(song_slug)
            pri = KIND_PRIORITY.get(kind, 9)
            if cur is None or pri < cur["_priority"]:
                best[song_slug] = {**obs, "_priority": pri}

    songs_dir = ROOT / "data" / "songs"
    existing = {
        p.stem
        for p in songs_dir.glob("*.yaml")
        if not p.name.endswith(".entity.yaml")
    }

    audit: dict[str, Any] = {
        "_meta": {
            "description": (
                "Discogs-first language audit for song titles. "
                "proposed_title_en uses Romanization (Meaning) only for japanese/mixed; "
                "french/english/other keep Discogs Latin form."
            ),
            "priority": "single > album > compilation > video/misc",
        },
        "songs": {},
    }

    for song_slug, obs in sorted(best.items()):
        if song_slug not in existing and song_slug == "unknown-track":
            continue
        lang = obs["language"]
        discogs_title = obs["discogs_title"]
        # Defaults; human fill step / mapping will refine proposed_title_en
        proposed_ja = discogs_title
        proposed_en = discogs_title  # placeholder for non-JA; filled below or left
        audit["songs"][song_slug] = {
            "discogs_title": discogs_title,
            "language": lang,
            "proposed_title_ja": proposed_ja,
            "proposed_title_en": proposed_en,
            "source_release": obs["source_release"],
            "source_kind": obs["source_kind"],
            "source_uri": obs["source_uri"],
            "in_catalog": song_slug in existing,
            "also_seen_as": sorted(
                {
                    o["discogs_title"]
                    for o in observations.get(song_slug, [])
                    if o["discogs_title"] != discogs_title
                }
            ),
        }

    OUT_PATH.write_text(
        yaml.dump(audit, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    print(f"Wrote {OUT_PATH} ({len(audit['songs'])} songs)", flush=True)


if __name__ == "__main__":
    main()
