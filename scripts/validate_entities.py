#!/usr/bin/env python3
"""Validate v2 entity files, links.yaml, and relation vocabulary."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from jsonschema import Draft202012Validator, RefResolver

from entities.common import (
    DATA_DIR,
    ENTITY_SCHEMA_BY_TYPE,
    LINKS_PATH,
    RELATION_TYPES_PATH,
    SCHEMA_ENTITY_DIR,
    load_entities,
    load_explicit_links,
    load_relation_types,
    load_yaml,
)


def load_schema(name: str) -> dict:
    with (SCHEMA_ENTITY_DIR / name).open(encoding="utf-8") as handle:
        return json.load(handle)


def schema_store() -> dict[str, dict]:
    names = [
        "entity.schema.json",
        "title.schema.json",
        "fact.schema.json",
        "song.schema.json",
        "album.schema.json",
        "person.schema.json",
        "reference.schema.json",
        "concert.schema.json",
        "appearance.schema.json",
        "organization.schema.json",
        "venue.schema.json",
        "link.schema.json",
    ]
    return {name: load_schema(name) for name in names}


def validator_for(entity_type: str) -> Draft202012Validator:
    schema_name = ENTITY_SCHEMA_BY_TYPE.get(entity_type, "entity.schema.json")
    store = schema_store()
    primary = store[schema_name]
    resolver = RefResolver(
        base_uri="file://" + str(SCHEMA_ENTITY_DIR) + "/",
        referrer=primary,
        store=store,
    )
    return Draft202012Validator(primary, resolver=resolver)


def validate_entities() -> list[str]:
    errors: list[str] = []
    entities = load_entities()
    ids = set(entities)

    for entity_id, entity in entities.items():
        rel_path = entity.get("_path", entity_id)
        try:
            validator = validator_for(entity["type"])
        except KeyError:
            errors.append(f"{rel_path}: unknown entity type '{entity.get('type')}'")
            continue
        for error in validator.iter_errors({k: v for k, v in entity.items() if k != "_path"}):
            errors.append(f"{rel_path}: {error.message}")

        if entity["type"] == "song":
            for album_id in entity.get("appears_on", []):
                if album_id not in ids:
                    errors.append(f"{rel_path}: appears_on references unknown entity '{album_id}'")
            for credit in entity.get("personnel", []):
                if credit["person"] not in ids:
                    errors.append(f"{rel_path}: personnel references unknown entity '{credit['person']}'")

        if entity["type"] == "album":
            for track in entity.get("tracklist", []):
                if track["song"] not in ids:
                    errors.append(f"{rel_path}: tracklist references unknown song '{track['song']}'")

        if entity["type"] == "concert":
            if entity.get("venue") and entity["venue"] not in ids:
                errors.append(f"{rel_path}: venue references unknown entity '{entity['venue']}'")
            for song_id in entity.get("setlist", []):
                if song_id not in ids:
                    errors.append(f"{rel_path}: setlist references unknown song '{song_id}'")
            for person_id in entity.get("members_present", []):
                if person_id not in ids:
                    errors.append(f"{rel_path}: members_present references unknown person '{person_id}'")

        if entity["type"] == "appearance":
            if entity.get("venue") and entity["venue"] not in ids:
                errors.append(f"{rel_path}: venue references unknown entity '{entity['venue']}'")
            broadcast = entity.get("broadcast") or {}
            if broadcast.get("network") and broadcast["network"] not in ids:
                errors.append(f"{rel_path}: broadcast.network references unknown entity '{broadcast['network']}'")
            for song_id in entity.get("songs_performed", []):
                if song_id not in ids:
                    errors.append(f"{rel_path}: songs_performed references unknown song '{song_id}'")
            for person_id in entity.get("members_present", []):
                if person_id not in ids:
                    errors.append(f"{rel_path}: members_present references unknown person '{person_id}'")

        if entity["type"] == "organization":
            pass

        for fact in entity.get("facts", []):
            for source in fact.get("sources", []):
                if source not in ids:
                    errors.append(f"{rel_path}: fact source references unknown entity '{source}'")

    return errors


def validate_links() -> list[str]:
    errors: list[str] = []
    if not LINKS_PATH.exists():
        return errors

    entities = load_entities()
    relation_types = load_relation_types()
    allowed = {item["id"] for item in relation_types.values() if item.get("origin") == "explicit"}
    store = schema_store()
    link_validator = Draft202012Validator(store["link.schema.json"])

    for index, link in enumerate(load_explicit_links()):
        for error in link_validator.iter_errors(link):
            errors.append(f"links.yaml[{index}]: {error.message}")
        if link["from"] not in entities:
            errors.append(f"links.yaml[{index}]: unknown from entity '{link['from']}'")
        if link["to"] not in entities:
            errors.append(f"links.yaml[{index}]: unknown to entity '{link['to']}'")
        if link["relation"] not in allowed:
            errors.append(f"links.yaml[{index}]: relation '{link['relation']}' not in relation_types explicit list")

    return errors


def validate_relation_types() -> list[str]:
    errors: list[str] = []
    data = load_yaml(RELATION_TYPES_PATH)
    seen: set[str] = set()
    for section in ("derived", "explicit"):
        for item in data.get(section, []):
            rel_id = item.get("id")
            if not rel_id:
                errors.append(f"relation_types.yaml: missing id in {section}")
                continue
            if rel_id in seen:
                errors.append(f"relation_types.yaml: duplicate relation id '{rel_id}'")
            seen.add(rel_id)
    return errors


def main() -> int:
    errors = validate_relation_types() + validate_entities() + validate_links()
    if errors:
        print("Entity validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    entity_count = len(load_entities())
    link_count = len(load_explicit_links())
    print(f"Entity validation passed ({entity_count} v2 entities, {link_count} explicit links).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
