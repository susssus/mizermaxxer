#!/usr/bin/env python3
"""Shared utilities for the Malice Mizer Archive build pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SCHEMA_DIR = ROOT / "schema"
DB_PATH = ROOT / "db" / "archive.sqlite"
EXPORTS_DIR = ROOT / "exports"
SITE_DATA_PATH = ROOT / "site" / "src" / "data" / "archive.json"


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_vocabularies() -> dict[str, list[str]]:
    with (SCHEMA_DIR / "vocabularies.json").open(encoding="utf-8") as handle:
        return json.load(handle)


ENTITY_STUB_PREFIXES = ("song_", "album_", "concert_", "venue_", "ref_", "person_")


def is_entity_stub(doc: dict[str, Any]) -> bool:
    """Skip v2 entity YAML files co-located in v1 collection directories."""
    entity_id = doc.get("id", "")
    return bool(doc.get("type")) and any(entity_id.startswith(prefix) for prefix in ENTITY_STUB_PREFIXES)


def iter_yaml_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    skip = {"relation_types.yaml"}
    return sorted(
        path
        for path in directory.glob("*.yaml")
        if path.name not in skip and not path.name.endswith(".entity.yaml")
    )


def load_collection(name: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in iter_yaml_files(DATA_DIR / name):
        doc = load_yaml(path)
        if is_entity_stub(doc):
            continue
        results.append(doc)
    return results


def load_publications() -> list[dict[str, Any]]:
    data = load_yaml(DATA_DIR / "publications.yaml")
    return data["publications"]


def publication_slugs() -> set[str]:
    return {pub["slug"] for pub in load_publications()}


def iter_issue_files() -> list[Path]:
    return sorted((DATA_DIR / "issues").rglob("*.yaml"))


def load_issues() -> list[dict[str, Any]]:
    return [load_yaml(path) for path in iter_issue_files()]


def load_people() -> dict[str, Any]:
    path = DATA_DIR / "people" / "members.yaml"
    if path.exists():
        return load_yaml(path)
    return load_yaml(DATA_DIR / "people.yaml")


def load_albums() -> list[dict[str, Any]]:
    return load_collection("albums")


def load_singles() -> list[dict[str, Any]]:
    return load_collection("singles")


def load_songs() -> list[dict[str, Any]]:
    return load_collection("songs")


def load_concerts() -> list[dict[str, Any]]:
    return load_collection("concerts")


def load_videos() -> list[dict[str, Any]]:
    return load_collection("videos")


def load_venues() -> list[dict[str, Any]]:
    return load_collection("venues")


def load_references() -> list[dict[str, Any]]:
    return load_collection("references")


def song_slugs() -> set[str]:
    return {song["id"] for song in load_songs()}


def venue_slugs() -> set[str]:
    return {venue["id"] for venue in load_venues()}


def ensure_dirs() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    SITE_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
