#!/usr/bin/env python3
"""JSON Schema registry helpers (referencing-based, no deprecated RefResolver)."""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from common import SCHEMA_DIR

SCHEMA_ENTITY_DIR = SCHEMA_DIR / "entity"
VOCABULARIES_SCHEMA = "vocabularies.json"

V1_SCHEMA_NAMES = [
    "publication.schema.json",
    "issue.schema.json",
    "article.schema.json",
    "changelog.schema.json",
    "album.schema.json",
    "single.schema.json",
    "song.schema.json",
    "concert.schema.json",
    "video.schema.json",
    "performance.schema.json",
    "venue.schema.json",
    "reference.schema.json",
    "translation.schema.json",
    VOCABULARIES_SCHEMA,
]

ENTITY_SCHEMA_NAMES = [
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
    "article.schema.json",
    "link.schema.json",
    VOCABULARIES_SCHEMA,
]


def load_schema(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_registry(*schema_dirs: Path, schema_names: list[str]) -> Registry:
    """Register schemas by their ``$id`` for cross-file ``$ref`` resolution."""
    registry = Registry()
    wanted = set(schema_names)
    for directory in schema_dirs:
        for name in sorted(wanted):
            path = directory / name
            if not path.exists():
                continue
            schema = load_schema(path)
            resource_id = schema.get("$id", name)
            registry = registry.with_resource(
                resource_id,
                Resource.from_contents(schema, default_specification=DRAFT202012),
            )
    return registry


def make_validator(
    primary_name: str,
    *schema_names: str,
    schema_dir: Path = SCHEMA_DIR,
    extra_dirs: tuple[Path, ...] = (),
) -> Draft202012Validator:
    names = list(dict.fromkeys((primary_name, *schema_names, VOCABULARIES_SCHEMA)))
    dirs = (schema_dir, *extra_dirs)
    if SCHEMA_DIR not in dirs and schema_dir != SCHEMA_DIR:
        dirs = (*dirs, SCHEMA_DIR)
    registry = build_registry(*dirs, schema_names=names)
    primary = load_schema(schema_dir / primary_name)
    return Draft202012Validator(primary, registry=registry)


def v1_validator(primary_name: str, *schema_names: str) -> Draft202012Validator:
    return make_validator(primary_name, *schema_names, schema_dir=SCHEMA_DIR)


def entity_validator(primary_name: str) -> Draft202012Validator:
    return make_validator(
        primary_name,
        *ENTITY_SCHEMA_NAMES,
        schema_dir=SCHEMA_ENTITY_DIR,
        extra_dirs=(SCHEMA_DIR,),
    )
