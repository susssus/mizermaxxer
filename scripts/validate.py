#!/usr/bin/env python3
"""Validate YAML data against JSON Schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from common import (
    DATA_DIR,
    SCHEMA_DIR,
    infer_translation_format,
    is_entity_stub,
    iter_issue_files,
    iter_yaml_files,
    load_albums,
    load_concerts,
    load_publications,
    load_singles,
    load_songs,
    load_pets,
    load_videos,
    load_venues,
    load_vocabularies,
    load_yaml,
    song_slugs,
    translation_has_renderable_content,
    venue_slugs,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manifest_coverage import validate_manifest_coverage
from schema_registry import v1_validator


def validate_publications() -> list[str]:
    errors: list[str] = []
    validator = v1_validator("publication.schema.json")
    for index, publication in enumerate(load_publications()):
        for error in validator.iter_errors(publication):
            errors.append(f"publications.yaml[{index}]: {error.message}")
    return errors


def validate_issues() -> list[str]:
    errors: list[str] = []
    validator = v1_validator("issue.schema.json", "article.schema.json", "changelog.schema.json")
    slugs = publication_slugs()

    for path in iter_issue_files():
        issue = load_yaml(path)
        rel = path.relative_to(DATA_DIR)
        for error in validator.iter_errors(issue):
            errors.append(f"{rel}: {error.message}")
        if issue["publication"] not in slugs:
            errors.append(f"{rel}: unknown publication slug '{issue['publication']}'")
        article_ids = set()
        for article in issue.get("articles", []):
            if article["id"] in article_ids:
                errors.append(f"{rel}: duplicate article id '{article['id']}'")
            article_ids.add(article["id"])
    return errors


def publication_slugs() -> set[str]:
    return {pub["slug"] for pub in load_publications()}


def validate_directory(name: str, schema_name: str, extra=None) -> list[str]:
    errors: list[str] = []
    schemas = [schema_name]
    if schema_name in {
        "album.schema.json",
        "single.schema.json",
        "concert.schema.json",
        "video.schema.json",
    }:
        schemas.append("changelog.schema.json")
    if schema_name == "concert.schema.json":
        schemas.append("performance.schema.json")
    validator = v1_validator(*schemas)
    directory = DATA_DIR / name
    for path in iter_yaml_files(directory):
        item = load_yaml(path)
        if is_entity_stub(item):
            continue
        rel = path.relative_to(DATA_DIR)
        for error in validator.iter_errors(item):
            errors.append(f"{rel}: {error.message}")
        if extra:
            errors.extend(extra(item, rel))
    return errors


def validate_albums() -> list[str]:
    songs = song_slugs()

    def extra(album, rel):
        found = []
        for track in album.get("tracks", []):
            if track["song"] not in songs:
                found.append(f"{rel}: unknown song slug '{track['song']}'")
        return found

    return validate_directory("albums", "album.schema.json", extra)


def validate_singles() -> list[str]:
    songs = song_slugs()

    def extra(single, rel):
        found = []
        for field in ("a_side", "b_side"):
            value = single.get(field)
            if value and value not in songs:
                found.append(f"{rel}: unknown song slug '{value}' in {field}")
        return found

    return validate_directory("singles", "single.schema.json", extra)


def validate_concerts() -> list[str]:
    songs = song_slugs()
    venues = venue_slugs()

    def extra(concert, rel):
        found = []
        venue = concert.get("venue")
        if venue and venue not in venues:
            found.append(f"{rel}: unknown venue slug '{venue}'")
        for song in concert.get("setlist", []):
            if song not in songs:
                found.append(f"{rel}: unknown song slug '{song}' in setlist")
        return found

    return validate_directory("concerts", "concert.schema.json", extra)


def translation_slug_from_url(url: str) -> str | None:
    prefix = "data/translations/"
    if url.startswith(prefix) and url.endswith(".yaml"):
        return url[len(prefix) : -len(".yaml")]
    return None


def build_article_index() -> tuple[dict[str, dict], dict[str, str]]:
    """Map article_id → {issue, article, path}; article_id → local translation slug."""
    articles_by_id: dict[str, dict] = {}
    article_translation_slugs: dict[str, str] = {}

    for path in iter_issue_files():
        issue = load_yaml(path)
        rel = path.relative_to(DATA_DIR)
        for article in issue.get("articles", []):
            articles_by_id[article["id"]] = {
                "issue": issue,
                "article": article,
                "path": str(rel),
            }
            translation = article.get("translation") or {}
            if translation.get("available") and translation.get("url"):
                slug = translation_slug_from_url(translation["url"])
                if slug:
                    article_translation_slugs[article["id"]] = slug

    return articles_by_id, article_translation_slugs


def normalize_yaml_dates(value: object) -> object:
    """Convert date/datetime objects from PyYAML into ISO strings for schema checks."""
    if isinstance(value, dict):
        return {key: normalize_yaml_dates(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_yaml_dates(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def validate_translations() -> list[str]:
    errors: list[str] = []
    validator = v1_validator("translation.schema.json")
    translations_dir = DATA_DIR / "translations"

    translations_by_id: dict[str, dict] = {}
    for path in iter_yaml_files(translations_dir):
        doc = normalize_yaml_dates(load_yaml(path))
        rel = path.relative_to(DATA_DIR)
        for error in validator.iter_errors(doc):
            errors.append(f"{rel}: {error.message}")
        translation_id = doc.get("id")
        if not translation_id:
            continue
        if translation_id in translations_by_id:
            errors.append(f"{rel}: duplicate translation id '{translation_id}'")
        translations_by_id[translation_id] = doc

    articles_by_id, article_translation_slugs = build_article_index()
    linked_translation_ids = set(article_translation_slugs.values())

    for translation_id, doc in translations_by_id.items():
        rel = f"translations/{translation_id}.yaml"
        article_id = doc.get("article_id")
        if article_id and article_id not in articles_by_id:
            errors.append(f"{rel}: unknown article_id '{article_id}'")
            continue

        expected_slug = article_translation_slugs.get(article_id or "")
        if article_id:
            if expected_slug is None:
                errors.append(
                    f"{rel}: article '{article_id}' has no local translation.url pointing to this file"
                )
            elif expected_slug != translation_id:
                errors.append(
                    f"{rel}: article '{article_id}' points to translation '{expected_slug}', not '{translation_id}'"
                )

        if translation_id not in linked_translation_ids:
            errors.append(f"{rel}: orphan translation (no issue article links to it)")

        if not translation_has_renderable_content(doc):
            fmt = infer_translation_format(doc)
            errors.append(f"{rel}: no renderable translation body for format '{fmt}'")

        license_notes = doc.get("license_notes") or ""
        if doc.get("license") == "CC-BY-NC-4.0" and "CC BY-NC" not in license_notes:
            errors.append(f"{rel}: license_notes must mention CC BY-NC 4.0 for the English translation")

    for article_id, slug in article_translation_slugs.items():
        if slug not in translations_by_id:
            article_path = articles_by_id[article_id]["path"]
            errors.append(f"{article_path}: translation.url points to missing file '{slug}'")

    return errors


def validate_videos() -> list[str]:
    songs = song_slugs()

    def extra(video, rel):
        found = []
        song = video.get("song")
        if song and song not in songs:
            found.append(f"{rel}: unknown song slug '{song}'")
        return found

    return validate_directory("videos", "video.schema.json", extra)


def validate_pets() -> list[str]:
    """Pets are v2 entities; schema checked by validate_entities. Soft checks only here."""
    errors: list[str] = []
    translation_ids: set[str] = set()
    translations_dir = DATA_DIR / "translations"
    if translations_dir.exists():
        for path in iter_yaml_files(translations_dir):
            doc = load_yaml(path)
            if doc.get("id"):
                translation_ids.add(doc["id"])

    for pet in load_pets():
        rel = f"pets/{pet.get('legacy_v1_slug') or pet['id']}.yaml"
        for translation_id in pet.get("translation_ids") or []:
            if translation_id not in translation_ids:
                errors.append(f"{rel}: unknown translation id '{translation_id}'")
        for index, image in enumerate(pet.get("gallery_images") or []):
            src = image.get("src")
            if src and src.startswith("images/") and not (DATA_DIR.parent / src).exists():
                errors.append(f"{rel}: gallery_images[{index}].src file not found '{src}'")
        portrait = pet.get("portrait_image")
        if portrait and portrait.startswith("images/") and not (DATA_DIR.parent / portrait).exists():
            errors.append(f"{rel}: portrait_image file not found '{portrait}'")
        owner = pet.get("owner_entity_id") or pet.get("person") or pet.get("owner")
        if owner and not str(owner).startswith("person_"):
            errors.append(f"{rel}: person/owner should resolve to person_* id")
    return errors


def validate_vocabularies() -> list[str]:
    errors: list[str] = []
    vocab_path = SCHEMA_DIR / "vocabularies.json"
    if not vocab_path.exists():
        errors.append("vocabularies.json: missing vocabulary file")
        return errors

    vocabularies = load_vocabularies()
    if not vocabularies:
        errors.append("vocabularies.json: no vocabulary definitions found")
        return errors

    for name, values in vocabularies.items():
        if not values:
            errors.append(f"vocabularies.json $defs/{name}: enum must not be empty")
        elif len(values) != len(set(values)):
            errors.append(f"vocabularies.json $defs/{name}: duplicate enum values")

    required_defs = {
        "verification_status",
        "date_precision",
        "article_type",
        "member_slug",
        "scan_quality",
        "publication_status",
        "trigger_warning",
        "changelog_action",
        "translation_review_status",
    }
    missing = sorted(required_defs - set(vocabularies))
    for name in missing:
        errors.append(f"vocabularies.json: missing required $defs/{name}")

    return errors


def main() -> int:
    errors = (
        validate_vocabularies()
        + validate_publications()
        + validate_issues()
        + validate_directory("songs", "song.schema.json")
        + validate_directory("venues", "venue.schema.json")
        + validate_albums()
        + validate_singles()
        + validate_concerts()
        + validate_videos()
        + validate_pets()
        + validate_directory("references", "reference.schema.json")
        + validate_translations()
        + validate_manifest_coverage()
    )

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    counts = {
        "issues": len(list(iter_issue_files())),
        "albums": len(load_albums()),
        "singles": len(load_singles()),
        "songs": len(load_songs()),
        "concerts": len(load_concerts()),
        "videos": len(load_videos()),
        "pets": len(load_pets()),
        "venues": len(load_venues()),
    }
    summary = ", ".join(f"{value} {key}" for key, value in counts.items())
    print(f"Validation passed ({summary}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
