#!/usr/bin/env python3
"""Sync release metadata and cover art from Discogs API.

Reads scripts/research/discogs_catalog.yaml, fetches each master/release,
downloads front cover to images/covers/{slug}.jpg, and updates data/albums/
or data/singles/ YAML (dates, label, catalog number, cover_image).

Discogs API: unauthenticated requests allowed with User-Agent (60 req/min).
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = Path(__file__).resolve().parent / "discogs_catalog.yaml"
IMAGES = ROOT / "images" / "covers"
USER_AGENT = "MaliceMizerArchive/1.0 +https://github.com/ (research; discogs sync)"
TODAY = datetime.now(UTC).strftime("%Y-%m-%d")
RATE_LIMIT_SEC = 1.5


def load_catalog() -> list[dict[str, Any]]:
    return yaml.safe_load(CATALOG_PATH.read_text(encoding="utf-8"))["releases"]


def discogs_get(path: str) -> dict[str, Any]:
    url = f"https://api.discogs.com{path}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def format_summary(release: dict[str, Any]) -> str:
    parts: list[str] = []
    for fmt in release.get("formats") or []:
        name = fmt.get("name") or ""
        desc = " ".join(fmt.get("descriptions") or [])
        parts.append(f"{name} {desc}".strip())
    return " | ".join(parts).lower()


def fetch_entry(discogs: dict[str, Any]) -> dict[str, Any]:
    if discogs["type"] == "master":
        master = discogs_get(f"/masters/{discogs['id']}")
        release = discogs_get(master["main_release_url"].replace("https://api.discogs.com", ""))
        images = master.get("images") or release.get("images") or []
        uri = master.get("uri") or release.get("uri")
        title = master.get("title") or release.get("title")
        tracklist = release.get("tracklist") or master.get("tracklist") or []
    else:
        release = discogs_get(f"/releases/{discogs['id']}")
        images = release.get("images") or []
        uri = release.get("uri")
        title = release.get("title")
        tracklist = release.get("tracklist") or []
    return {
        "title": title,
        "released": release.get("released"),
        "label": (release.get("labels") or [{}])[0].get("name"),
        "catalog_number": (release.get("labels") or [{}])[0].get("catno"),
        "uri": uri,
        "images": images,
        "tracklist": tracklist,
        "format_text": format_summary(release),
    }


def infer_type_and_format(entry: dict[str, Any], meta: dict[str, Any]) -> tuple[str, str]:
    if entry.get("album_type"):
        album_type = entry["album_type"]
        if album_type in ("vhs", "dvd"):
            return album_type, album_type
        if album_type == "demo":
            return "demo", "cassette"
        if album_type == "box_set":
            return "box_set", "cd"
        return album_type, "cd"

    kind = entry["kind"]
    text = meta.get("format_text") or ""

    if kind == "compilation":
        if "box set" in text:
            return "box_set", "cd"
        return "compilation", "cd"
    if kind == "misc":
        if "cassette" in text:
            return "demo", "cassette"
        return "album", "cd"
    if kind == "video":
        if "blu" in text:
            return "dvd", "other"
        if "vhs" in text:
            return "vhs", "vhs"
        if "dvd" in text:
            return "dvd", "dvd"
        return "vhs", "vhs"
    if "cassette" in text:
        return "demo", "cassette"
    if "vinyl" in text:
        return "album", "vinyl"
    return "album", "cd"


def yaml_dir_for_kind(kind: str) -> Path:
    if kind == "single":
        return ROOT / "data" / "singles"
    return ROOT / "data" / "albums"


def primary_image_url(images: list[dict[str, Any]]) -> str | None:
    for image in images:
        if image.get("type") == "primary" and image.get("uri"):
            return image["uri"]
    for image in images:
        if image.get("uri"):
            return image["uri"]
    return None


def download_cover(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        dest.write_bytes(response.read())


def normalize_date(released: str | None) -> tuple[str, str]:
    if not released:
        return "unknown", "year"
    parts = released.split("-")
    if len(parts) == 3:
        return released, "day"
    if len(parts) == 2:
        return released, "month"
    return released[:4], "year"


def title_en_from_discogs(title: str) -> str:
    return title.strip()


def title_parts(title: str) -> tuple[str, str]:
    """Use Discogs title for both JA and EN when not split."""
    return title, title


def a_b_sides(tracklist: list[dict[str, Any]]) -> tuple[str | None, str | None]:
    titles = [t.get("title", "") for t in tracklist if t.get("title")]
    if not titles:
        return None, None
    a = titles[0]
    b = titles[1] if len(titles) > 1 else None
    return a, b


# Discogs track title -> existing song slug (extend as songs are catalogued)
TRACK_SLUG: dict[str, str] = {
    "Transylvania": "transylvania",
    "Madrigal": "madrigal",
    "Au Revoir": "au-revoir",
    "ILLUMINATI": "illuminati",
    "Illuminati": "illuminati",
    "Le Ciel": "le-ciel",
    "Le Ciel～空白の彼方へ～": "le-ciel",
    "月下の夜想曲": "gekka-no-yasoukyoku",
    "Beast Of Blood": "beast-of-blood",
    "Beast of Blood": "beast-of-blood",
    "再会の血と薔薇": "saikai-no-chi-to-bara",
    "虚無の中での遊戯": "kyomu-no-naka-de-no-yugi",
    "ヴェル・エール～空白の瞬間の中で～": "bel-air",
    "Bel Air": "bel-air",
    "Ma Chérie～愛しい君へ～": "ma-cherie",
    "麗しき仮面の招待状": "uruwashii-kamen",
    "Gardenia": "gardenia",
    "Garnet～禁断の園へ～": "garnet",
    "真夜中に交わした約束～薔薇の婚礼～": "mayonaka-yakusoku",
    "薔薇の婚礼～真夜中に交わした約束～": "mayonaka-yakusoku",
    "白い肌に狂う愛と哀しみの輪舞": "shiroi-hada",
    "ヴェル・エール～空白の瞬間の中で～": "bel-air",
    "ヴェル・エール~空白の瞬間の中で~": "bel-air",
    "ヴェル・エール〜空白の瞬間の中で〜": "bel-air",
    "ヴェルエール - 空白の瞬間の中で": "bel-air",
    "エーゲ〜過ぎ去りし風と共に〜": "aege-sugisarishi-kaze",
}


def slugify(title: str) -> str:
    if title in TRACK_SLUG:
        return TRACK_SLUG[title]
    if title in TITLE_SLUG:
        return TITLE_SLUG[title]
    ascii_part = re.sub(r"[^\x00-\x7F]+", " ", title)
    ascii_part = re.sub(r"[^\w\s-]", "", ascii_part)
    slug = re.sub(r"[-\s]+", "-", ascii_part.strip().lower()).strip("-")
    return slug or "unknown-track"


# Full title -> slug (ASCII only)
TITLE_SLUG: dict[str, str] = {
    "De Memoire": "de-memoire",
    "記憶と空": "kioku-to-sora",
    "エーゲ海に捧ぐ ~ The Vault Of Heaven": "aege-kai-ni-sasagu",
    "午後のささやき": "gogo-no-sasayaki",
    "魅惑のローマ": "mihwaku-no-roma",
    "Seraph": "seraph",
    "闇の彼方へ～": "yami-no-kanata-e",
    "追憶の破片～A Piece Of Broken Recollection～": "tsuioku-no-hahen",
    "Premier Amour": "premier-amour",
    "偽りのMusetté": "itsuwari-no-musette",
    "N.p.s N.g.s. ～No Pains No Gains～": "nps-ngs",
    "Claire～月の調べ～": "claire-tsuki-no-shirabe",
    "死の舞踏～A Romance Of The \"Cendrillon\"～": "shi-no-butou",
    "～前兆～": "zencho",
    "～De Merveilles": "de-merveilles",
    "Syunikiss～二度目の哀悼～": "syunikiss",
    "Brise": "brise",
    "エーゲ～過ぎ去りし風と共に～": "aege-sugisarishi-kaze",
    "Ju Te Veux": "ju-te-veux",
    "S-Conscious": "s-conscious",
    "Bois De Merveilles": "bois-de-merveilles",
    "薔薇に彩られた悪意と悲劇の幕開け": "bara-makuake",
    "聖なる刻　永遠の祈り": "seinaru-toki",
    "鏡の舞踏　幻惑の夜": "kagami-no-butou",
    "真夜中に交わした約束": "mayonaka-yakusoku",
    "血塗られた果実": "chi-nurareta-kajitsu",
    "地下水脈の迷路": "chikasuimyaku-no-meiro",
    "破誡の果て": "hakai-no-hate",
    "神話": "shinwa",
    "Gardenia": "gardenia",
    "Garnet～禁断の園へ～": "garnet",
    "真夜中に交わした約束～薔薇の婚礼～": "mayonaka-yakusoku",
    "薔薇の婚礼～真夜中に交わした約束～": "mayonaka-yakusoku",
    "白い肌に狂う愛と哀しみの輪舞": "shiroi-hada",
    "聖なる刻 永遠の祈り": "seinaru-toki",
    "鏡の舞踏 幻惑の夜": "kagami-no-butou",
    "追憶の破片": "tsuioku-no-hahen",
    "死の舞踏": "shi-no-butou",
    "前兆": "zencho",
    "再会": "saikai",
    "運命の出会い": "unmei-no-deai",
    "運命の出会": "unmei-no-deai",
    "森の中の天使": "mori-no-naka-no-tenshi",
    "幻想楽園": "gensou-rakuen",
    "ジレンマ": "jirenma",
    "終幕への扉": "shuumaku-e-no-tobira",
    "バロック": "baroque",
    "古のルーマニア": "ino-no-rumania",
    "目醒めの螺旋": "mezame-no-rasen",
    "波紋 / 協奏曲": "hamon-kyousoukyoku",
    "波紋／協奏曲": "hamon-kyousoukyoku",
    "薔薇の伝承 (序章)": "bara-no-densho-prologue",
    "薇の葬列": "bara-no-souretsu",
    "薔薇の洗礼": "bara-no-senrei",
    "崩壊序曲": "houkai-jokyoku",
    "記憶と空～再会そして約束～": "kioku-to-sora-saikai-yakusoku",
    "約束": "yakusoku",
    "ヴェル・エール～空白の瞬間の中で～": "bel-air",
    "ヴェル・エール~空白の瞬間の中で~": "bel-air",
    "ヴェル・エール〜空白の瞬間の中で〜": "bel-air",
    "ヴェルエール - 空白の瞬間の中で": "bel-air",
    "エーゲ〜過ぎ去りし風と共に〜": "aege-sugisarishi-kaze",
}


DISCOGS_SECTION_HEADERS = {
    "cd",
    "vhs",
    "video",
    "data",
    "merveilles",
    "merveilles -cinq parelléle-",
    "merveilles l'espace",
    'malice mizer sur tv "l\'image de merveilles"',
}


def ensure_song(slug: str, title_ja: str, title_en: str) -> None:
    path = ROOT / "data" / "songs" / f"{slug}.yaml"
    if path.exists():
        return
    doc = {
        "id": slug,
        "title_ja": title_ja,
        "title_en": title_en,
        "writers": ["mana"],
        "lyricists": [],
        "composers": ["mana"],
        "notes": f"Auto-created from Discogs sync ({TODAY}).",
    }
    path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")


def track_entries(tracklist: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    pos = 0
    for track in tracklist:
        title = (track.get("title") or "").strip()
        if not title or title.lower() in DISCOGS_SECTION_HEADERS:
            continue
        pos += 1
        slug = slugify(title)
        ensure_song(slug, title, title)
        entry: dict[str, Any] = {"song": slug, "position": pos}
        entries.append(entry)
    return entries


def side_slug(title: str | None) -> str | None:
    if not title:
        return None
    return slugify(title)


def update_yaml(entry: dict[str, Any], meta: dict[str, Any], cover_rel: str | None) -> None:
    kind = entry["kind"]
    slug = entry["slug"]
    yaml_dir = yaml_dir_for_kind(kind)
    yaml_path = yaml_dir / f"{slug}.yaml"

    date, precision = normalize_date(meta.get("released"))
    title = meta.get("title") or slug
    title_ja, title_en = title_parts(title)

    if kind == "single":
        doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) if yaml_path.exists() else {}
        a_title, b_title = a_b_sides(meta.get("tracklist") or [])
        a_slug = side_slug(a_title)
        b_slug = side_slug(b_title)
        if a_slug:
            ensure_song(a_slug, a_title or a_slug, a_title or a_slug)
        if b_slug:
            ensure_song(b_slug, b_title or b_slug, b_title or b_slug)
        doc.update(
            {
                "id": slug,
                "title_ja": title_ja,
                "title_en": title_en_from_discogs(title),
                "release_date": date if date != "unknown" else doc.get("release_date", "unknown"),
                "date_precision": precision,
                "label": meta.get("label"),
                "catalog_number": meta.get("catalog_number"),
                "format": doc.get("format") or "cd",
                "a_side": a_slug or doc.get("a_side"),
                "b_side": b_slug or doc.get("b_side"),
                "coupling_tracks": doc.get("coupling_tracks") or [],
                "cover_image": cover_rel or doc.get("cover_image"),
                "verification_status": "verified",
                "notes": f"Synced from Discogs ({meta.get('uri')}).",
            }
        )
    else:
        doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) if yaml_path.exists() else {}
        tracks = track_entries(meta.get("tracklist") or [])
        album_type, physical_format = infer_type_and_format(entry, meta)
        doc.update(
            {
                "id": slug,
                "title_ja": title_ja,
                "title_en": title_en_from_discogs(title),
                "type": album_type,
                "release_date": date if date != "unknown" else doc.get("release_date", "unknown"),
                "date_precision": precision,
                "label": meta.get("label"),
                "catalog_number": meta.get("catalog_number"),
                "format": physical_format,
                "cover_image": cover_rel or doc.get("cover_image"),
                "verification_status": "verified",
                "tracks": tracks or doc.get("tracks") or [],
                "notes": f"Synced from Discogs ({meta.get('uri')}).",
            }
        )

    if "changelog" not in doc or not doc["changelog"]:
        doc["changelog"] = [
            {
                "date": TODAY,
                "action": "created",
                "source": "discogs_sync",
                "notes": f"Imported from {meta.get('uri')}",
            }
        ]
    else:
        doc["changelog"].append(
            {
                "date": TODAY,
                "action": "updated",
                "source": "discogs_sync",
                "notes": f"Metadata and cover from {meta.get('uri')}",
            }
        )

    yaml_dir.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")


def ensure_public_symlink() -> None:
    public_images = ROOT / "site" / "public" / "images"
    public_images.parent.mkdir(parents=True, exist_ok=True)
    if public_images.is_symlink() or public_images.exists():
        return
    try:
        public_images.symlink_to((ROOT / "images").resolve(), target_is_directory=True)
    except OSError:
        import shutil

        shutil.copytree(ROOT / "images", public_images, dirs_exist_ok=True)


def main() -> int:
    catalog = load_catalog()
    print(f"Syncing {len(catalog)} releases from Discogs...")
    ok = 0
    for entry in catalog:
        slug = entry["slug"]
        try:
            meta = fetch_entry(entry["discogs"])
            time.sleep(RATE_LIMIT_SEC)
        except urllib.error.HTTPError as exc:
            print(f"  FAIL {slug}: HTTP {exc.code}", file=sys.stderr)
            continue
        except urllib.error.URLError as exc:
            print(f"  FAIL {slug}: {exc}", file=sys.stderr)
            continue

        cover_rel = None
        image_url = primary_image_url(meta.get("images") or [])
        if image_url:
            dest = IMAGES / f"{slug}.jpg"
            try:
                if not dest.exists():
                    download_cover(image_url, dest)
                    time.sleep(0.5)
                cover_rel = f"images/covers/{slug}.jpg"
                print(f"  cover: {cover_rel}")
            except urllib.error.URLError as exc:
                print(f"  skip cover {slug}: {exc}", file=sys.stderr)

        update_yaml(entry, meta, cover_rel)
        print(f"  ok: {slug} ({meta.get('released')})")
        ok += 1

    ensure_public_symlink()
    print(f"Done: {ok}/{len(catalog)} releases synced.")
    return 0 if ok == len(catalog) else 1


if __name__ == "__main__":
    raise SystemExit(main())
