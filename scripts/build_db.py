#!/usr/bin/env python3
"""Build SQLite database and site JSON from YAML source files."""

from __future__ import annotations

import json
import sqlite3
import sys
from typing import Any

from common import (
    DB_PATH,
    ROOT,
    SITE_DATA_PATH,
    ensure_dirs,
    infer_translation_format,
    load_albums,
    load_concerts,
    load_issues,
    load_people,
    load_people_profiles,
    load_publications,
    load_references,
    load_singles,
    load_songs,
    load_venues,
    load_videos,
    load_yaml,
)

SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

GALLERY_PREVIEWS_PATH = ROOT / "site" / "src" / "data" / "gallery_previews.json"
TRANSLATIONS_DIR = ROOT / "data" / "translations"
TRANSLATIONS_PATH = ROOT / "site" / "src" / "data" / "translations.json"
ENTITY_CROSSWALK_PATH = ROOT / "site" / "src" / "data" / "entity_crosswalk.json"
LINKS_INDEX_PATH = ROOT / "site" / "src" / "data" / "links_index.json"
GALLERY_INDEX_PATH = ROOT / "site" / "src" / "data" / "gallery_index.json"
ATTRIBUTION_PATH = ROOT / "site" / "src" / "data" / "attribution.json"
MANIFEST_PATH = ROOT / "images" / "manifest.json"
SCAN_SOURCES_CATALOG = ROOT / "scripts" / "research" / "scan_sources_catalog.yaml"
SHOXX_VOL61_GALLERY = "https://malice-archive.neocities.org/Gackt%20Era/Shoxx/main.html"
SHOXX_VOL61_COVER = "https://file.garden/Zts7YeM0Ki6DRAfG/Shoxx/March%201998/01.jpg"


def _json_safe(value: Any) -> Any:
    """Recursively convert YAML date/datetime values for JSON export."""
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS publications (
            slug TEXT PRIMARY KEY,
            name_ja TEXT NOT NULL,
            name_en TEXT NOT NULL,
            publisher TEXT,
            issn TEXT,
            years_active_start INTEGER,
            years_active_end INTEGER,
            priority INTEGER NOT NULL,
            status TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS issues (
            id TEXT PRIMARY KEY,
            publication TEXT NOT NULL REFERENCES publications(slug),
            issue_number TEXT,
            volume TEXT,
            publication_date TEXT NOT NULL,
            date_precision TEXT NOT NULL,
            verification_status TEXT NOT NULL,
            source_notes TEXT,
            research_targets_json TEXT,
            changelog_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            issue_id TEXT NOT NULL REFERENCES issues(id),
            title_ja TEXT,
            title_en TEXT,
            type TEXT NOT NULL,
            pages TEXT,
            members_json TEXT NOT NULL,
            photographer TEXT,
            writer TEXT,
            cover INTEGER NOT NULL,
            poster INTEGER NOT NULL,
            foldout INTEGER NOT NULL,
            scan_available INTEGER NOT NULL,
            scan_quality TEXT,
            scan_url TEXT,
            translation_available INTEGER NOT NULL,
            translation_url TEXT,
            purchase_links_json TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS songs (
            id TEXT PRIMARY KEY,
            title_ja TEXT NOT NULL,
            title_en TEXT NOT NULL,
            writers_json TEXT NOT NULL,
            lyricists_json TEXT NOT NULL,
            composers_json TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS albums (
            id TEXT PRIMARY KEY,
            title_ja TEXT NOT NULL,
            title_en TEXT NOT NULL,
            type TEXT NOT NULL,
            release_date TEXT NOT NULL,
            date_precision TEXT NOT NULL,
            label TEXT,
            catalog_number TEXT,
            format TEXT,
            cover_image TEXT,
            verification_status TEXT NOT NULL,
            tracks_json TEXT NOT NULL,
            notes TEXT,
            changelog_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS singles (
            id TEXT PRIMARY KEY,
            title_ja TEXT NOT NULL,
            title_en TEXT NOT NULL,
            release_date TEXT NOT NULL,
            date_precision TEXT NOT NULL,
            label TEXT,
            catalog_number TEXT,
            format TEXT,
            a_side TEXT,
            b_side TEXT,
            coupling_tracks_json TEXT NOT NULL,
            cover_image TEXT,
            verification_status TEXT NOT NULL,
            notes TEXT,
            changelog_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS venues (
            id TEXT PRIMARY KEY,
            name_ja TEXT NOT NULL,
            name_en TEXT NOT NULL,
            city TEXT NOT NULL,
            prefecture TEXT,
            country TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS concerts (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            date_precision TEXT NOT NULL,
            venue TEXT REFERENCES venues(id),
            event_name_ja TEXT,
            event_name_en TEXT,
            type TEXT NOT NULL,
            tour TEXT,
            setlist_json TEXT NOT NULL,
            members_present_json TEXT NOT NULL,
            verification_status TEXT NOT NULL,
            source_notes TEXT,
            performances_json TEXT NOT NULL,
            notes TEXT,
            changelog_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            title_ja TEXT,
            title_en TEXT NOT NULL,
            type TEXT NOT NULL,
            url TEXT NOT NULL,
            platform TEXT,
            release_date TEXT,
            song TEXT REFERENCES songs(id),
            concert TEXT REFERENCES concerts(id),
            quality TEXT,
            verification_status TEXT NOT NULL,
            notes TEXT,
            trigger_warnings_json TEXT NOT NULL DEFAULT '[]',
            changelog_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS references_table (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            url TEXT NOT NULL,
            notes TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_issues_publication ON issues(publication);
        CREATE INDEX IF NOT EXISTS idx_issues_date ON issues(publication_date);
        CREATE INDEX IF NOT EXISTS idx_articles_issue ON articles(issue_id);
        CREATE INDEX IF NOT EXISTS idx_albums_date ON albums(release_date);
        CREATE INDEX IF NOT EXISTS idx_singles_date ON singles(release_date);
        CREATE INDEX IF NOT EXISTS idx_concerts_date ON concerts(date);
        """
    )
    migrate_schema(connection)


def migrate_schema(connection: sqlite3.Connection) -> None:
    video_columns = {
        row[1] for row in connection.execute("PRAGMA table_info(videos)").fetchall()
    }
    if video_columns and "trigger_warnings_json" not in video_columns:
        connection.execute(
            "ALTER TABLE videos ADD COLUMN trigger_warnings_json TEXT NOT NULL DEFAULT '[]'"
        )


def clear_all(connection: sqlite3.Connection) -> None:
    for table in (
        "articles",
        "issues",
        "videos",
        "concerts",
        "singles",
        "albums",
        "songs",
        "venues",
        "references_table",
        "publications",
    ):
        connection.execute(f"DELETE FROM {table}")


def insert_publications(connection: sqlite3.Connection) -> None:
    for pub in load_publications():
        connection.execute(
            """
            INSERT INTO publications (
                slug, name_ja, name_en, publisher, issn,
                years_active_start, years_active_end, priority, status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pub["slug"],
                pub["name_ja"],
                pub["name_en"],
                pub.get("publisher"),
                pub.get("issn"),
                pub.get("years_active_start"),
                pub.get("years_active_end"),
                pub["priority"],
                pub["status"],
                pub.get("notes", ""),
            ),
        )


def insert_issues_and_articles(connection: sqlite3.Connection) -> None:
    for issue in load_issues():
        connection.execute(
            """
            INSERT INTO issues (
                id, publication, issue_number, volume, publication_date,
                date_precision, verification_status, source_notes,
                research_targets_json, changelog_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                issue["id"],
                issue["publication"],
                issue.get("issue_number"),
                issue.get("volume"),
                issue["publication_date"],
                issue["date_precision"],
                issue["verification_status"],
                issue.get("source_notes", ""),
                json.dumps(issue.get("research_targets", []), ensure_ascii=False),
                json.dumps(issue["changelog"], ensure_ascii=False),
            ),
        )
        for article in issue["articles"]:
            scan = article.get("scan", {"available": False, "quality": None, "url": None})
            translation = article.get("translation", {"available": False, "url": None})
            connection.execute(
                """
                INSERT INTO articles (
                    id, issue_id, title_ja, title_en, type, pages,
                    members_json, photographer, writer, cover, poster, foldout,
                    scan_available, scan_quality, scan_url,
                    translation_available, translation_url,
                    purchase_links_json, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    article["id"],
                    issue["id"],
                    article.get("title_ja"),
                    article.get("title_en"),
                    article["type"],
                    article.get("pages"),
                    json.dumps(article.get("members", []), ensure_ascii=False),
                    article.get("photographer"),
                    article.get("writer"),
                    int(article.get("cover", False)),
                    int(article.get("poster", False)),
                    int(article.get("foldout", False)),
                    int(scan.get("available", False)),
                    scan.get("quality"),
                    scan.get("url"),
                    int(translation.get("available", False)),
                    translation.get("url"),
                    json.dumps(article.get("purchase_links", []), ensure_ascii=False),
                    article.get("notes", ""),
                ),
            )


def insert_music_data(connection: sqlite3.Connection) -> None:
    for song in load_songs():
        connection.execute(
            """
            INSERT INTO songs (id, title_ja, title_en, writers_json, lyricists_json, composers_json, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                song["id"],
                song["title_ja"],
                song["title_en"],
                json.dumps(song.get("writers", []), ensure_ascii=False),
                json.dumps(song.get("lyricists", []), ensure_ascii=False),
                json.dumps(song.get("composers", []), ensure_ascii=False),
                song.get("notes", ""),
            ),
        )

    for venue in load_venues():
        connection.execute(
            """
            INSERT INTO venues (id, name_ja, name_en, city, prefecture, country, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                venue["id"],
                venue["name_ja"],
                venue["name_en"],
                venue["city"],
                venue.get("prefecture"),
                venue["country"],
                venue.get("notes", ""),
            ),
        )

    for album in load_albums():
        connection.execute(
            """
            INSERT INTO albums (
                id, title_ja, title_en, type, release_date, date_precision,
                label, catalog_number, format, cover_image, verification_status,
                tracks_json, notes, changelog_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                album["id"],
                album["title_ja"],
                album["title_en"],
                album["type"],
                album["release_date"],
                album["date_precision"],
                album.get("label"),
                album.get("catalog_number"),
                album.get("format"),
                album.get("cover_image"),
                album["verification_status"],
                json.dumps(album.get("tracks", []), ensure_ascii=False),
                album.get("notes", ""),
                json.dumps(album["changelog"], ensure_ascii=False),
            ),
        )

    for single in load_singles():
        connection.execute(
            """
            INSERT INTO singles (
                id, title_ja, title_en, release_date, date_precision,
                label, catalog_number, format, a_side, b_side,
                coupling_tracks_json, cover_image, verification_status, notes, changelog_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                single["id"],
                single["title_ja"],
                single["title_en"],
                single["release_date"],
                single["date_precision"],
                single.get("label"),
                single.get("catalog_number"),
                single.get("format"),
                single.get("a_side"),
                single.get("b_side"),
                json.dumps(single.get("coupling_tracks", []), ensure_ascii=False),
                single.get("cover_image"),
                single["verification_status"],
                single.get("notes", ""),
                json.dumps(single["changelog"], ensure_ascii=False),
            ),
        )

    for concert in load_concerts():
        connection.execute(
            """
            INSERT INTO concerts (
                id, date, date_precision, venue, event_name_ja, event_name_en,
                type, tour, setlist_json, members_present_json, verification_status,
                source_notes, performances_json, notes, changelog_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                concert["id"],
                concert["date"],
                concert["date_precision"],
                concert.get("venue"),
                concert.get("event_name_ja"),
                concert.get("event_name_en"),
                concert["type"],
                concert.get("tour"),
                json.dumps(concert.get("setlist", []), ensure_ascii=False),
                json.dumps(concert.get("members_present", []), ensure_ascii=False),
                concert["verification_status"],
                concert.get("source_notes", ""),
                json.dumps(concert.get("performances", []), ensure_ascii=False),
                concert.get("notes", ""),
                json.dumps(concert["changelog"], ensure_ascii=False),
            ),
        )

    for video in load_videos():
        connection.execute(
            """
            INSERT INTO videos (
                id, title_ja, title_en, type, url, platform, release_date,
                song, concert, quality, verification_status, notes,
                trigger_warnings_json, changelog_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                video["id"],
                video.get("title_ja"),
                video["title_en"],
                video["type"],
                video["url"],
                video.get("platform"),
                video.get("release_date"),
                video.get("song"),
                video.get("concert"),
                video.get("quality"),
                video["verification_status"],
                video.get("notes", ""),
                json.dumps(video.get("trigger_warnings", []), ensure_ascii=False),
                json.dumps(video["changelog"], ensure_ascii=False),
            ),
        )

    for reference in load_references():
        connection.execute(
            """
            INSERT INTO references_table (id, title, type, url, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                reference["id"],
                reference["title"],
                reference["type"],
                reference["url"],
                reference.get("notes", ""),
            ),
        )


def decode_json_fields(rows: list[dict], mapping: dict[str, str]) -> None:
    for row in rows:
        for json_field, target in mapping.items():
            if json_field in row:
                row[target] = json.loads(row.pop(json_field) or "[]")


def export_site_json(connection: sqlite3.Connection) -> None:
    connection.row_factory = sqlite3.Row
    publications = [dict(row) for row in connection.execute("SELECT * FROM publications ORDER BY priority, name_en")]
    issues = [dict(row) for row in connection.execute("SELECT * FROM issues ORDER BY publication_date, id")]
    articles = [dict(row) for row in connection.execute("SELECT * FROM articles ORDER BY issue_id, id")]
    songs = [dict(row) for row in connection.execute("SELECT * FROM songs ORDER BY title_en")]
    albums = [dict(row) for row in connection.execute("SELECT * FROM albums ORDER BY release_date, id")]
    singles = [dict(row) for row in connection.execute("SELECT * FROM singles ORDER BY release_date, id")]
    venues = [dict(row) for row in connection.execute("SELECT * FROM venues ORDER BY name_en")]
    concerts = [dict(row) for row in connection.execute("SELECT * FROM concerts ORDER BY date, id")]
    videos = [dict(row) for row in connection.execute("SELECT * FROM videos ORDER BY release_date, title_en")]
    references = [dict(row) for row in connection.execute("SELECT * FROM references_table ORDER BY title")]

    decode_json_fields(issues, {"research_targets_json": "research_targets", "changelog_json": "changelog"})
    decode_json_fields(articles, {"members_json": "members", "purchase_links_json": "purchase_links"})
    decode_json_fields(songs, {"writers_json": "writers", "lyricists_json": "lyricists", "composers_json": "composers"})
    decode_json_fields(albums, {"tracks_json": "tracks", "changelog_json": "changelog"})
    decode_json_fields(singles, {"coupling_tracks_json": "coupling_tracks", "changelog_json": "changelog"})
    decode_json_fields(
        concerts,
        {
            "setlist_json": "setlist",
            "members_present_json": "members_present",
            "performances_json": "performances",
            "changelog_json": "changelog",
        },
    )
    decode_json_fields(videos, {"changelog_json": "changelog", "trigger_warnings_json": "trigger_warnings"})

    for row in articles:
        row["cover"] = bool(row["cover"])
        row["poster"] = bool(row["poster"])
        row["foldout"] = bool(row["foldout"])
        row["scan_available"] = bool(row["scan_available"])
        row["translation_available"] = bool(row["translation_available"])

    articles_by_issue: dict[str, list[dict[str, Any]]] = {}
    for article in articles:
        articles_by_issue.setdefault(article["issue_id"], []).append(article)

    enriched_issues = []
    for issue in issues:
        enriched = dict(issue)
        enriched["articles"] = articles_by_issue.get(issue["id"], [])
        enriched_issues.append(enriched)

    song_map = {song["id"]: song for song in songs}
    venue_map = {venue["id"]: venue for venue in venues}

    for album in albums:
        album["track_details"] = [
            {**track, "song_detail": song_map.get(track["song"])} for track in album.get("tracks", [])
        ]

    for concert in concerts:
        concert["venue_detail"] = venue_map.get(concert["venue"]) if concert.get("venue") else None
        concert["setlist_details"] = [song_map.get(song_id) for song_id in concert.get("setlist", [])]

    for video in videos:
        video["song_detail"] = song_map.get(video["song"]) if video.get("song") else None

    performance_count = sum(len(concert.get("performances", [])) for concert in concerts)
    appearances = export_appearances_rows()

    payload = {
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat().replace("+00:00", "Z"),
        "people": load_people(),
        "people_profiles": load_people_profiles(),
        "publications": publications,
        "issues": enriched_issues,
        "songs": songs,
        "albums": albums,
        "singles": singles,
        "venues": venues,
        "concerts": concerts,
        "videos": videos,
        "references": references,
        "appearances": appearances,
        "stats": {
            "issue_count": len(enriched_issues),
            "article_count": len(articles),
            "verified_issue_count": sum(1 for issue in enriched_issues if issue["verification_status"] == "verified"),
            "scan_count": sum(1 for article in articles if article["scan_available"]),
            "album_count": len(albums),
            "single_count": len(singles),
            "song_count": len(songs),
            "concert_count": len(concerts),
            "video_count": len(videos),
            "appearance_count": len(appearances),
            "performance_link_count": performance_count + len(videos),
        },
    }

    SITE_DATA_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def export_attribution() -> None:
    """Export grouped image attribution for the /attribution site page."""
    generated_at = (
        __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat().replace("+00:00", "Z")
    )

    if not MANIFEST_PATH.exists():
        payload = {"generated_at": generated_at, "total_count": 0, "sources": [], "by_path": {}, "by_source_url": {}}
    else:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        by_source: dict[str, list[dict[str, str | None]]] = {}
        for entry in manifest:
            name = entry.get("source_name") or "Unknown"
            by_source.setdefault(name, []).append(
                {
                    "path": entry["path"],
                    "filename": __import__("pathlib").Path(entry["path"]).name,
                    "site_url": f"/{entry['path']}",
                    "source_url": entry.get("source_url"),
                    "fetched_at": entry.get("fetched_at"),
                }
            )

        sources = []
        for name in sorted(by_source, key=lambda key: (-len(by_source[key]), key.lower())):
            images = sorted(by_source[name], key=lambda item: item["path"] or "")
            sources.append({"source_name": name, "count": len(images), "images": images})

        by_path: dict[str, dict[str, str | None]] = {}
        by_source_url: dict[str, dict[str, str | None]] = {}
        for entry in manifest:
            path = entry["path"]
            record = {
                "source_name": entry.get("source_name"),
                "source_url": entry.get("source_url"),
            }
            by_path[path] = record
            source_url = entry.get("source_url")
            if source_url:
                by_source_url[source_url] = {**record, "path": path}

        payload = {
            "generated_at": generated_at,
            "total_count": len(manifest),
            "sources": sources,
            "by_path": by_path,
            "by_source_url": by_source_url,
        }

    ATTRIBUTION_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_gallery_previews() -> None:
    """Map gallery page URLs to first-page preview images for ArchiveImage."""
    previews: dict[str, str] = {}
    if SCAN_SOURCES_CATALOG.exists():
        catalog = load_yaml(SCAN_SOURCES_CATALOG)
        for item in catalog.get("items") or []:
            gallery = item.get("scan_url")
            images = item.get("image_urls") or []
            if gallery and images:
                previews[gallery.rstrip("/")] = images[0]

    previews[SHOXX_VOL61_GALLERY] = SHOXX_VOL61_COVER
    previews[f"{SHOXX_VOL61_GALLERY}#vol61"] = SHOXX_VOL61_COVER

    GALLERY_PREVIEWS_PATH.write_text(
        json.dumps(previews, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def export_promo_gallery(albums: list[dict[str, Any]], profiles: list[dict[str, Any]]) -> None:
    """Promo / cover / member images for the site gallery page."""
    items: list[dict[str, Any]] = []
    manifest_by_path: dict[str, dict[str, Any]] = {}
    if MANIFEST_PATH.exists():
        for entry in json.loads(MANIFEST_PATH.read_text(encoding="utf-8")):
            manifest_by_path[entry["path"]] = entry

    def attribution_for_local(path: str | None) -> tuple[str | None, str | None]:
        if not path or path.startswith("http"):
            return None, None
        normalized = path.lstrip("/")
        entry = manifest_by_path.get(normalized)
        if not entry:
            return None, None
        return entry.get("source_name"), entry.get("source_url")

    for profile in profiles:
        name = (profile.get("name") or {}).get("romanized") or profile.get("id", "")
        era = (profile.get("active") or {}).get("start")
        for img in profile.get("gallery_images") or []:
            src = img.get("src")
            manifest_name, manifest_url = attribution_for_local(src)
            items.append(
                {
                    "title": name,
                    "src": src,
                    "caption": img.get("caption"),
                    "source": img.get("source") or manifest_name,
                    "source_url": manifest_url,
                    "era": era,
                    "category": "member",
                    "external": str(src or "").startswith("http"),
                }
            )
        if profile.get("portrait_image"):
            portrait = profile["portrait_image"]
            manifest_name, manifest_url = attribution_for_local(portrait)
            items.append(
                {
                    "title": name,
                    "src": portrait,
                    "caption": "Portrait",
                    "source": manifest_name or "Archive",
                    "source_url": manifest_url,
                    "era": era,
                    "category": "member",
                    "external": False,
                }
            )

    for album in albums:
        cover = album.get("cover_image")
        if not cover:
            continue
        manifest_name, manifest_url = attribution_for_local(cover)
        items.append(
            {
                "title": album.get("title_en") or album.get("title_ja"),
                "src": cover,
                "caption": album.get("type", "").replace("_", " "),
                "source": manifest_name or "Cover Art Archive",
                "source_url": manifest_url,
                "era": (album.get("release_date") or "")[:4] or None,
                "category": "release",
                "external": False,
            }
        )

    catalog_path = ROOT / "scripts" / "research" / "image_urls_catalog.yaml"
    if catalog_path.exists():
        catalog = load_yaml(catalog_path)
        for entry in catalog.get("entries") or []:
            source = entry.get("source") or ""
            if "vkgy" not in source and "vk.gy" not in (entry.get("gallery_url") or ""):
                continue
            url = entry.get("cover_image_medium_url") or entry.get("cover_image_url")
            if not url:
                images = entry.get("images") or []
                url = images[0].get("url") if images else None
            if url:
                items.append(
                    {
                        "title": entry.get("title"),
                        "src": url,
                        "caption": "Magazine cover",
                        "source": "vk.gy",
                        "source_url": entry.get("gallery_url") or url,
                        "era": None,
                        "category": "promo",
                        "external": True,
                    }
                )

    payload = {
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").UTC)
        .isoformat()
        .replace("+00:00", "Z"),
        "count": len(items),
        "items": items,
    }
    GALLERY_INDEX_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_translations() -> None:
    """Export data/translations/*.yaml for the site /translation/[id] pages."""
    generated_at = (
        __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat().replace("+00:00", "Z")
    )
    by_id: dict[str, dict[str, Any]] = {}

    if TRANSLATIONS_DIR.exists():
        for path in sorted(TRANSLATIONS_DIR.glob("*.yaml")):
            doc = load_yaml(path)
            if not doc or not doc.get("id"):
                continue
            entry = dict(doc)
            entry["format"] = infer_translation_format(entry)
            by_id[entry["id"]] = _json_safe(entry)

    payload = {
        "generated_at": generated_at,
        "count": len(by_id),
        "ids": sorted(by_id),
        "by_id": by_id,
    }
    TRANSLATIONS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def export_appearances_rows() -> list[dict[str, Any]]:
    """Summarize v2 appearance entities for the public /appearances index."""
    from entities.common import load_entities

    rows: list[dict[str, Any]] = []
    for entity_id, entity in load_entities().items():
        if entity.get("type") != "appearance":
            continue
        title = entity.get("title") or {}
        rows.append(
            {
                "id": entity_id,
                "title": title.get("english") or title.get("romanized") or title.get("original") or entity_id,
                "appearance_type": entity.get("appearance_type"),
                "format": entity.get("format"),
                "date": entity.get("date"),
                "date_precision": entity.get("date_precision"),
                "verification_status": entity.get("verification_status", "unverified"),
            }
        )
    rows.sort(key=lambda row: row.get("date") or "")
    return rows


def _legacy_v1_slug_map(entity_type: str) -> dict[str, str]:
    from entities.common import load_entities

    mapping: dict[str, str] = {}
    for entity_id, entity in load_entities().items():
        if entity.get("type") != entity_type:
            continue
        legacy = entity.get("legacy_v1_slug")
        if legacy:
            mapping[str(legacy)] = entity_id
    return mapping


def _magazine_issue_crosswalk() -> dict[str, str]:
    from entities.common import load_entities

    mapping: dict[str, str] = {}
    for entity_id, entity in load_entities().items():
        if entity.get("type") != "reference" or entity.get("reference_type") != "magazine":
            continue
        legacy = entity.get("legacy_v1_slug")
        if legacy:
            mapping[str(legacy)] = entity_id
    return mapping


def export_entity_crosswalk() -> None:
    """Export v1 slug → v2 entity ID mappings for site cross-links."""
    generated_at = (
        __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat().replace("+00:00", "Z")
    )
    entity_ids: set[str] = set()
    if LINKS_INDEX_PATH.exists():
        links_index = json.loads(LINKS_INDEX_PATH.read_text(encoding="utf-8"))
        entity_ids = {row["id"] for row in links_index.get("browse", [])}

    def keep(mapping: dict[str, str]) -> dict[str, str]:
        if not entity_ids:
            return mapping
        return {key: value for key, value in mapping.items() if value in entity_ids}

    def merge_legacy(auto: dict[str, str], entity_type: str) -> dict[str, str]:
        merged = dict(auto)
        merged.update(_legacy_v1_slug_map(entity_type))
        return merged

    members = load_people().get("members", [])
    payload = {
        "generated_at": generated_at,
        "songs": keep(
            merge_legacy(
                {song["id"]: f"song_{song['id'].replace('-', '_')}" for song in load_songs()},
                "song",
            )
        ),
        "venues": keep(
            merge_legacy(
                {venue["id"]: f"venue_{venue['id'].replace('-', '_')}" for venue in load_venues()},
                "venue",
            )
        ),
        "people": keep({member["slug"]: f"person_{member['slug']}" for member in members}),
        "albums": keep({album["id"]: f"album_{album['id'].replace('-', '_')}" for album in load_albums()}),
        "concerts": keep(
            merge_legacy(
                {concert["id"]: f"concert_{concert['id'].replace('-', '_')}" for concert in load_concerts()},
                "concert",
            )
        ),
        "issues": keep(_magazine_issue_crosswalk()),
    }
    ENTITY_CROSSWALK_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ensure_dirs()
    connection = sqlite3.connect(DB_PATH)
    try:
        create_schema(connection)
        clear_all(connection)
        insert_publications(connection)
        insert_issues_and_articles(connection)
        insert_music_data(connection)
        connection.commit()
        export_site_json(connection)
        export_gallery_previews()
        export_promo_gallery(load_albums(), load_people_profiles())
        export_attribution()
        export_translations()
        export_entity_crosswalk()
    finally:
        connection.close()

    print(
        f"Built database at {DB_PATH} "
        f"({len(load_issues())} issues, {len(load_albums())} albums, {len(load_concerts())} concerts)."
    )
    print(f"Exported site JSON to {SITE_DATA_PATH}.")
    print(f"Exported gallery previews to {GALLERY_PREVIEWS_PATH}.")
    print(f"Exported promo gallery to {GALLERY_INDEX_PATH}.")
    print(f"Exported image attribution to {ATTRIBUTION_PATH}.")
    print(f"Exported translations to {TRANSLATIONS_PATH}.")
    print(f"Exported entity crosswalk to {ENTITY_CROSSWALK_PATH}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
