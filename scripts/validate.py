#!/usr/bin/env python3
"""Validate YAML data against JSON Schema."""

from __future__ import annotations

import json
import sys

from jsonschema import Draft202012Validator, RefResolver

from common import (
    DATA_DIR,
    SCHEMA_DIR,
    iter_issue_files,
    iter_yaml_files,
    load_albums,
    load_concerts,
    load_publications,
    load_singles,
    load_songs,
    load_videos,
    load_venues,
    load_yaml,
    song_slugs,
    venue_slugs,
)


def load_schema(name: str) -> dict:
    with (SCHEMA_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def make_validator(*schema_names: str) -> Draft202012Validator:
    primary = load_schema(schema_names[0])
    store = {name: load_schema(name) for name in schema_names}
    resolver = RefResolver(
        base_uri="file://" + str(SCHEMA_DIR) + "/",
        referrer=primary,
        store=store,
    )
    return Draft202012Validator(primary, resolver=resolver)


def validate_publications() -> list[str]:
    errors: list[str] = []
    validator = Draft202012Validator(load_schema("publication.schema.json"))
    for index, publication in enumerate(load_publications()):
        for error in validator.iter_errors(publication):
            errors.append(f"publications.yaml[{index}]: {error.message}")
    return errors


def validate_issues() -> list[str]:
    errors: list[str] = []
    validator = make_validator("issue.schema.json", "article.schema.json")
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
    if schema_name in {"album.schema.json", "single.schema.json", "concert.schema.json", "video.schema.json"}:
        schemas.append("changelog.schema.json")
    if schema_name == "concert.schema.json":
        schemas.append("performance.schema.json")
    validator = make_validator(*schemas)
    directory = DATA_DIR / name
    for path in iter_yaml_files(directory):
        item = load_yaml(path)
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


def validate_videos() -> list[str]:
    songs = song_slugs()

    def extra(video, rel):
        found = []
        song = video.get("song")
        if song and song not in songs:
            found.append(f"{rel}: unknown song slug '{song}'")
        return found

    return validate_directory("videos", "video.schema.json", extra)


def main() -> int:
    errors = (
        validate_publications()
        + validate_issues()
        + validate_directory("songs", "song.schema.json")
        + validate_directory("venues", "venue.schema.json")
        + validate_albums()
        + validate_singles()
        + validate_concerts()
        + validate_videos()
        + validate_directory("references", "reference.schema.json")
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
        "venues": len(load_venues()),
    }
    summary = ", ".join(f"{value} {key}" for key, value in counts.items())
    print(f"Validation passed ({summary}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
