#!/usr/bin/env python3
"""Generate v2 song and magazine reference entities from v1 catalog YAML."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (
    DATA_DIR,
    ROOT,
    is_entity_stub,
    iter_issue_files,
    iter_yaml_files,
    load_albums,
    load_publications,
    load_songs,
    load_yaml,
)
from entities.common import load_entities

REFERENCES_DIR = DATA_DIR / "references"
SONGS_DIR = DATA_DIR / "songs"
ARTICLES_DIR = DATA_DIR / "articles"

# Hand-curated refs that predate issue-id naming; map issue id → existing entity id.
EXISTING_ISSUE_REF_IDS: dict[str, str] = {
    "fools-mate-1997-06": "ref_foolsmate_188",
    "shoxx-1998-03": "ref_shoxx_061",
}

V2_ALBUM_IDS: dict[str, str] = {"merveilles": "album_merveilles"}

MEMBER_SLUGS = {
    "klaha",
    "mana",
    "kozi",
    "yuki",
    "kami",
    "gackt",
    "gaz",
    "tetsu",
}


def song_entity_id(v1_slug: str) -> str:
    return f"song_{v1_slug.replace('-', '_')}"


def issue_ref_entity_id(issue_id: str) -> str:
    return f"ref_{issue_id.replace('-', '_')}"


def issue_ref_id_for_issue(issue_id: str) -> str:
    return EXISTING_ISSUE_REF_IDS.get(issue_id, issue_ref_entity_id(issue_id))


def article_entity_id(article_id: str) -> str:
    return f"article_{article_id.replace('-', '_')}"


def song_entity_path(v1_slug: str) -> Path:
    return SONGS_DIR / f"{v1_slug.replace('-', '_')}.entity.yaml"


def issue_ref_path(issue_id: str) -> Path:
    return REFERENCES_DIR / f"{issue_id}.entity.yaml"


def article_entity_path(article_id: str) -> Path:
    return ARTICLES_DIR / f"{article_id.replace('-', '_')}.entity.yaml"


def dump_yaml(path: Path, doc: dict[str, Any], dry_run: bool) -> bool:
    if path.exists():
        return False
    if dry_run:
        print(f"would write {path.relative_to(ROOT)}")
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    print(f"wrote {path.relative_to(ROOT)}")
    return True


def update_yaml_legacy(path: Path, legacy_v1_slug: str, dry_run: bool) -> bool:
    if not path.exists():
        return False
    doc = load_yaml(path)
    if doc.get("legacy_v1_slug") == legacy_v1_slug:
        return False
    doc["legacy_v1_slug"] = legacy_v1_slug
    if dry_run:
        print(f"would update legacy_v1_slug on {path.relative_to(ROOT)} → {legacy_v1_slug}")
        return True
    path.write_text(
        yaml.dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    print(f"updated {path.relative_to(ROOT)}")
    return True


def build_appears_on_index() -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for album in load_albums():
        v2_id = V2_ALBUM_IDS.get(album["id"])
        if not v2_id:
            continue
        for track in album.get("tracks", []):
            song_slug = track.get("song")
            if song_slug:
                index.setdefault(song_slug, [])
                if v2_id not in index[song_slug]:
                    index[song_slug].append(v2_id)
    return index


def song_title_block(v1: dict[str, Any]) -> dict[str, str]:
    ja = (v1.get("title_ja") or "").strip()
    en = (v1.get("title_en") or "").strip()
    romanized = en or ja or v1["id"]
    block: dict[str, str] = {"romanized": romanized}
    if ja and ja != romanized:
        block["original"] = ja
    return block


def song_personnel(v1: dict[str, Any]) -> list[dict[str, str]]:
    personnel: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(slug: str | None, role: str) -> None:
        if not slug or slug not in MEMBER_SLUGS:
            return
        key = (slug, role)
        if key in seen:
            return
        seen.add(key)
        personnel.append({"person": f"person_{slug}", "role": role})

    for slug in v1.get("writers") or []:
        add(slug, "writer")
    for slug in v1.get("lyricists") or []:
        add(slug, "lyricist")
    for slug in v1.get("composers") or []:
        add(slug, "composer")

    return personnel


def build_song_entity(v1: dict[str, Any], appears_on: list[str]) -> dict[str, Any]:
    slug = v1["id"]
    doc: dict[str, Any] = {
        "id": song_entity_id(slug),
        "type": "song",
        "legacy_v1_slug": slug,
        "title": song_title_block(v1),
        "duration_seconds": v1.get("duration_seconds"),
        "appears_on": appears_on,
        "personnel": song_personnel(v1),
        "facts": [],
        "notes": (v1.get("notes") or "").strip()
        or "v2 entity stub migrated from v1 song catalog.",
    }
    if v1.get("verification_status"):
        doc["verification_status"] = v1["verification_status"]
    return doc


def publication_map() -> dict[str, dict[str, Any]]:
    return {pub["slug"]: pub for pub in load_publications()}


def issue_ref_title(issue: dict[str, Any], pub: dict[str, Any] | None) -> str:
    name = (pub or {}).get("name_en") or issue["publication"]
    number = issue.get("issue_number")
    if number:
        return f"{name} No. {number}"
    return f"{name} ({issue['publication_date']})"


def first_local_scan(issue: dict[str, Any]) -> str | None:
    for article in issue.get("articles", []):
        url = (article.get("scan") or {}).get("url")
        if url and isinstance(url, str) and url.startswith("images/"):
            return url
    return None


def build_issue_ref_entity(issue: dict[str, Any], pub: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "id": issue_ref_id_for_issue(issue["id"]),
        "type": "reference",
        "legacy_v1_slug": issue["id"],
        "reference_type": "magazine",
        "title": issue_ref_title(issue, pub),
        "publisher": (pub or {}).get("name_en"),
        "date": issue.get("publication_date"),
        "pages_cited": [],
        "url": None,
        "scan": first_local_scan(issue),
        "verification_status": issue.get("verification_status", "needs_verification"),
        "facts": [],
        "notes": (issue.get("source_notes") or "").strip()
        or f"Migrated from bibliography issue {issue['id']}.",
    }


def existing_song_slugs() -> set[str]:
    slugs: set[str] = set()
    for entity in load_entities().values():
        if entity.get("type") != "song":
            continue
        legacy = entity.get("legacy_v1_slug")
        if legacy:
            slugs.add(legacy)
        elif entity["id"].startswith("song_"):
            slugs.add(entity["id"][5:].replace("_", "-"))
    return slugs


def existing_issue_legacy_slugs() -> set[str]:
    slugs: set[str] = set()
    for entity in load_entities().values():
        if entity.get("type") != "reference":
            continue
        legacy = entity.get("legacy_v1_slug")
        if legacy:
            slugs.add(legacy)
    slugs.update(EXISTING_ISSUE_REF_IDS.keys())
    return slugs


def migrate_songs(dry_run: bool) -> tuple[int, int]:
    appears_on_index = build_appears_on_index()
    existing = existing_song_slugs()
    created = updated = 0

    for v1 in load_songs():
        slug = v1["id"]
        entity_path = song_entity_path(slug)
        if entity_path.exists():
            if slug not in existing and update_yaml_legacy(entity_path, slug, dry_run):
                updated += 1
            elif slug in existing:
                update_yaml_legacy(entity_path, slug, dry_run)
            continue
        if slug in existing:
            continue
        doc = build_song_entity(v1, appears_on_index.get(slug, []))
        if dump_yaml(entity_path, doc, dry_run):
            created += 1

    # Ensure curated entities have legacy slugs.
    for path in SONGS_DIR.glob("*.entity.yaml"):
        doc = load_yaml(path)
        if doc.get("type") != "song":
            continue
        legacy = doc.get("legacy_v1_slug")
        if legacy:
            continue
        inferred = doc["id"][5:].replace("_", "-") if doc["id"].startswith("song_") else None
        if inferred and update_yaml_legacy(path, inferred, dry_run):
            updated += 1

    return created, updated


def article_title_block(article: dict[str, Any]) -> dict[str, str]:
    ja = (article.get("title_ja") or "").strip()
    en = (article.get("title_en") or "").strip()
    romanized = en or ja or article["id"]
    block: dict[str, str] = {"romanized": romanized}
    if ja and ja != romanized:
        block["original"] = ja
    return block


def translation_slug(article: dict[str, Any]) -> str | None:
    translation = article.get("translation") or {}
    url = translation.get("url")
    if not url or not isinstance(url, str):
        return None
    name = Path(url).name
    if name.endswith(".yaml"):
        return name[:-5]
    return None


def build_article_entity(issue: dict[str, Any], article: dict[str, Any]) -> dict[str, Any]:
    article_id = article["id"]
    scan = article.get("scan")
    doc: dict[str, Any] = {
        "id": article_entity_id(article_id),
        "type": "article",
        "legacy_v1_slug": article_id,
        "title": article_title_block(article),
        "article_type": article["type"],
        "published_in": issue_ref_id_for_issue(issue["id"]),
        "pages": article.get("pages"),
        "members": article.get("members") or [],
        "photographer": article.get("photographer"),
        "writer": article.get("writer"),
        "cover": bool(article.get("cover", False)),
        "poster": bool(article.get("poster", False)),
        "foldout": bool(article.get("foldout", False)),
        "facts": [],
        "notes": (article.get("notes") or "").strip()
        or f"Migrated from bibliography article {article_id} in issue {issue['id']}.",
    }
    if scan:
        doc["scan"] = scan
    slug = translation_slug(article)
    if slug:
        doc["translation_slug"] = slug
    if issue.get("verification_status"):
        doc["verification_status"] = issue["verification_status"]
    return doc


def existing_article_legacy_slugs() -> set[str]:
    slugs: set[str] = set()
    for entity in load_entities().values():
        if entity.get("type") != "article":
            continue
        legacy = entity.get("legacy_v1_slug")
        if legacy:
            slugs.add(legacy)
    return slugs


def migrate_articles(dry_run: bool) -> tuple[int, int]:
    existing = existing_article_legacy_slugs()
    created = updated = 0

    for path in iter_issue_files():
        issue = load_yaml(path)
        if issue.get("publication") == "flyers":
            continue
        issue_id = issue["id"]
        ref_id = issue_ref_id_for_issue(issue_id)

        for article in issue.get("articles") or []:
            article_id = article["id"]
            entity_path = article_entity_path(article_id)
            if article_id in existing or entity_path.exists():
                continue
            doc = build_article_entity(issue, article)
            if doc["published_in"] != ref_id:
                doc["published_in"] = ref_id
            if dump_yaml(entity_path, doc, dry_run):
                created += 1

    return created, updated


def migrate_magazine_refs(dry_run: bool) -> tuple[int, int]:
    pubs = publication_map()
    existing = existing_issue_legacy_slugs()
    created = updated = 0

    for path in iter_issue_files():
        issue = load_yaml(path)
        if issue.get("publication") == "flyers":
            continue
        issue_id = issue["id"]

        if issue_id in EXISTING_ISSUE_REF_IDS:
            curated_id = EXISTING_ISSUE_REF_IDS[issue_id]
            curated_path = None
            for candidate in REFERENCES_DIR.glob("*.yaml"):
                if load_yaml(candidate).get("id") == curated_id:
                    curated_path = candidate
                    break
            if curated_path and update_yaml_legacy(curated_path, issue_id, dry_run):
                updated += 1
            continue

        if issue_id in existing:
            continue

        ref_path = issue_ref_path(issue_id)
        if ref_path.exists():
            continue

        pub = pubs.get(issue["publication"])
        doc = build_issue_ref_entity(issue, pub)
        if dump_yaml(ref_path, doc, dry_run):
            created += 1

    return created, updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print actions without writing files")
    parser.add_argument("--songs-only", action="store_true")
    parser.add_argument("--issues-only", action="store_true")
    parser.add_argument("--articles-only", action="store_true")
    args = parser.parse_args()

    song_created = song_updated = issue_created = issue_updated = article_created = article_updated = 0
    if not args.issues_only and not args.articles_only:
        song_created, song_updated = migrate_songs(args.dry_run)
    if not args.songs_only and not args.articles_only:
        issue_created, issue_updated = migrate_magazine_refs(args.dry_run)
    if not args.songs_only and not args.issues_only:
        article_created, article_updated = migrate_articles(args.dry_run)

    print(
        f"Migration complete: "
        f"{song_created} song entities created, {song_updated} songs updated; "
        f"{issue_created} magazine refs created, {issue_updated} refs updated; "
        f"{article_created} article entities created, {article_updated} articles updated."
    )
    if not args.dry_run:
        print("Run: make entities && make validate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
