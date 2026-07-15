#!/usr/bin/env python3
"""Validate v2 entity files, links.yaml, and relation vocabulary."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_concerts, load_issues, load_songs, load_venues
from entities.common import (
    DATA_DIR,
    ENTITY_SCHEMA_BY_TYPE,
    LINKS_PATH,
    ONTOLOGY_PATH,
    RELATION_TYPES_PATH,
    SCHEMA_ENTITY_DIR,
    active_explicit_relations,
    entity_type_for_id,
    load_entities,
    load_explicit_links,
    load_ontology,
    load_relation_types,
    load_yaml,
)
from schema_registry import entity_validator


def validator_for(entity_type: str):
    schema_name = ENTITY_SCHEMA_BY_TYPE.get(entity_type, "entity.schema.json")
    return entity_validator(schema_name)


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

        if entity["type"] == "article":
            published_in = entity.get("published_in")
            if published_in and published_in not in ids:
                errors.append(f"{rel_path}: published_in references unknown entity '{published_in}'")
            elif published_in:
                ref = entities.get(published_in, {})
                if ref.get("type") != "reference" or ref.get("reference_type") != "magazine":
                    errors.append(
                        f"{rel_path}: published_in must reference a magazine ref_* entity, not '{published_in}'"
                    )

        for fact in entity.get("facts", []):
            for source in fact.get("sources", []):
                if source not in ids:
                    errors.append(f"{rel_path}: fact source references unknown entity '{source}'")

    return errors


def build_v1_article_ids() -> set[str]:
    article_ids: set[str] = set()
    for issue in load_issues():
        if issue.get("publication") == "flyers":
            continue
        for article in issue.get("articles") or []:
            article_ids.add(article["id"])
    return article_ids


def validate_legacy_v1_slugs(entities: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    v1_venue_ids = {venue["id"] for venue in load_venues()}
    v1_concert_ids = {concert["id"] for concert in load_concerts()}
    v1_song_ids = {song["id"] for song in load_songs()}
    v1_issue_ids = {
        issue["id"]
        for issue in load_issues()
        if issue.get("publication") != "flyers"
    }
    v1_article_ids = build_v1_article_ids()
    seen: dict[str, str] = {}

    for entity_id, entity in entities.items():
        entity_type = entity.get("type")
        rel_path = entity.get("_path", entity_id)
        legacy = entity.get("legacy_v1_slug")

        if entity_type in ("venue", "concert", "song"):
            if not legacy:
                errors.append(f"{rel_path}: missing legacy_v1_slug (required for {entity_type} entities)")
                continue
            catalog = {
                "venue": v1_venue_ids,
                "concert": v1_concert_ids,
                "song": v1_song_ids,
            }[entity_type]
            if legacy not in catalog:
                errors.append(f"{rel_path}: legacy_v1_slug '{legacy}' not found in v1 catalog")
            if legacy in seen:
                errors.append(f"{rel_path}: duplicate legacy_v1_slug '{legacy}' (also used by {seen[legacy]})")
            seen[legacy] = entity_id
            continue

        if entity_type == "reference" and entity.get("reference_type") == "magazine":
            if not legacy:
                errors.append(f"{rel_path}: missing legacy_v1_slug (required for magazine reference entities)")
                continue
            if legacy not in v1_issue_ids:
                errors.append(f"{rel_path}: legacy_v1_slug '{legacy}' not found in v1 issue catalog")
            if legacy in seen:
                errors.append(f"{rel_path}: duplicate legacy_v1_slug '{legacy}' (also used by {seen[legacy]})")
            seen[legacy] = entity_id
            continue

        if entity_type == "article":
            if not legacy:
                errors.append(f"{rel_path}: missing legacy_v1_slug (required for article entities)")
                continue
            if legacy not in v1_article_ids:
                errors.append(f"{rel_path}: legacy_v1_slug '{legacy}' not found in v1 article catalog")
            if legacy in seen:
                errors.append(f"{rel_path}: duplicate legacy_v1_slug '{legacy}' (also used by {seen[legacy]})")
            seen[legacy] = entity_id

    return errors


def validate_relation_types() -> list[str]:
    errors: list[str] = []
    data = load_yaml(RELATION_TYPES_PATH)
    ontology = load_ontology()
    seen: set[str] = set()
    required_fields = ("id", "label", "category", "domain", "range", "status")

    for section in ("derived", "explicit"):
        for item in data.get(section, []):
            rel_id = item.get("id")
            if not rel_id:
                errors.append(f"relation_types.yaml: missing id in {section}")
                continue
            if rel_id in seen:
                errors.append(f"relation_types.yaml: duplicate relation id '{rel_id}'")
            seen.add(rel_id)
            for field in required_fields:
                if field not in item:
                    errors.append(f"relation_types.yaml: relation '{rel_id}' missing required field '{field}'")
            status = item.get("status", "active")
            if status == "planned" and item.get("examples") is None:
                errors.append(f"relation_types.yaml: planned relation '{rel_id}' must include examples: []")
            elif status == "active" and not item.get("examples"):
                errors.append(f"relation_types.yaml: active relation '{rel_id}' must include at least one example")

    for entity_type, meta in ontology.get("entity_types", {}).items():
        for field in ("label", "prefix", "schema", "category", "color"):
            if field not in meta:
                errors.append(f"ontology.yaml: entity type '{entity_type}' missing required field '{field}'")

    return errors


def validate_domain_range(
    from_id: str,
    to_id: str,
    relation: str,
    relation_types: dict[str, dict[str, Any]],
    entities: dict[str, dict[str, Any]],
    context: str,
) -> list[str]:
    errors: list[str] = []
    meta = relation_types.get(relation)
    if not meta:
        errors.append(f"{context}: unknown relation '{relation}'")
        return errors

    from_type = entity_type_for_id(from_id, entities)
    to_type = entity_type_for_id(to_id, entities)
    if not from_type or not to_type:
        return errors

    domain = meta.get("domain", [])
    range_types = meta.get("range", [])
    if domain and from_type not in domain:
        errors.append(
            f"{context}: relation '{relation}' domain mismatch — '{from_id}' is type '{from_type}', expected {domain}"
        )
    if range_types and to_type not in range_types:
        errors.append(
            f"{context}: relation '{relation}' range mismatch — '{to_id}' is type '{to_type}', expected {range_types}"
        )
    return errors


def validate_links() -> list[str]:
    errors: list[str] = []
    if not LINKS_PATH.exists():
        return errors

    entities = load_entities()
    relation_types = load_relation_types()
    allowed = active_explicit_relations(relation_types)
    link_validator = entity_validator("link.schema.json")

    for index, link in enumerate(load_explicit_links()):
        for error in link_validator.iter_errors(link):
            errors.append(f"links.yaml[{index}]: {error.message}")
        if link["from"] not in entities:
            errors.append(f"links.yaml[{index}]: unknown from entity '{link['from']}'")
        if link["to"] not in entities:
            errors.append(f"links.yaml[{index}]: unknown to entity '{link['to']}'")
        if link["relation"] not in allowed:
            errors.append(
                f"links.yaml[{index}]: relation '{link['relation']}' not in active explicit relation list"
            )
        errors.extend(
            validate_domain_range(
                link["from"],
                link["to"],
                link["relation"],
                relation_types,
                entities,
                f"links.yaml[{index}]",
            )
        )

    return errors


def validate_derived_domain_range(entities: dict[str, dict[str, Any]]) -> list[str]:
    """Validate that entity fields produce edges within ontology domain/range."""
    errors: list[str] = []
    relation_types = load_relation_types()
    ids = set(entities)

    def check(from_id: str, to_id: str, relation: str, context: str) -> None:
        if from_id in ids and to_id in ids:
            errors.extend(validate_domain_range(from_id, to_id, relation, relation_types, entities, context))

    for entity_id, entity in entities.items():
        rel_path = entity.get("_path", entity_id)
        entity_type = entity.get("type")

        if entity_type == "song":
            for album_id in entity.get("appears_on", []):
                check(entity_id, album_id, "appears_on", rel_path)
            for credit in entity.get("personnel", []):
                check(entity_id, credit["person"], "personnel", rel_path)

        if entity_type == "album":
            for track in entity.get("tracklist", []):
                check(entity_id, track["song"], "includes_song", rel_path)

        if entity_type == "concert":
            for song_id in entity.get("setlist", []):
                check(song_id, entity_id, "performed_at_concert", rel_path)
            for person_id in entity.get("members_present", []):
                check(person_id, entity_id, "performed_at_concert", rel_path)
            if entity.get("venue"):
                check(entity_id, entity["venue"], "held_at", rel_path)

        if entity_type == "appearance":
            for song_id in entity.get("songs_performed", []):
                check(song_id, entity_id, "performed_at_appearance", rel_path)
            for person_id in entity.get("members_present", []):
                check(person_id, entity_id, "appeared_at", rel_path)
            broadcast = entity.get("broadcast") or {}
            if broadcast.get("network"):
                check(entity_id, broadcast["network"], "broadcast_on", rel_path)
            if entity.get("venue"):
                check(entity_id, entity["venue"], "held_at", rel_path)

        if entity_type == "reference":
            for fact in entity.get("facts", []):
                for target in fact.get("targets", []):
                    check(entity_id, target, "discusses", rel_path)

        if entity_type == "article":
            if entity.get("published_in"):
                check(entity_id, entity["published_in"], "published_in", rel_path)

    return errors


def main() -> int:
    entities = load_entities()
    errors = (
        validate_relation_types()
        + validate_entities()
        + validate_legacy_v1_slugs(entities)
        + validate_derived_domain_range(entities)
        + validate_links()
    )
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
