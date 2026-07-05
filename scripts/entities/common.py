"""Entity loader utilities for v2 schema."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
SCHEMA_ENTITY_DIR = ROOT / "schema" / "entity"
LINKS_PATH = DATA_DIR / "links.yaml"
RELATION_TYPES_PATH = DATA_DIR / "references" / "relation_types.yaml"
LINKS_INDEX_PATH = ROOT / "site" / "src" / "data" / "links_index.json"
EXPORTS_LINKS_PATH = ROOT / "exports" / "links_index.json"

ENTITY_TYPE_DIRS: dict[str, Path] = {
    "song": DATA_DIR / "songs",
    "album": DATA_DIR / "albums",
    "single": DATA_DIR / "singles",
    "concert": DATA_DIR / "concerts",
    "appearance": DATA_DIR / "appearances",
    "person": DATA_DIR / "people",
    "organization": DATA_DIR / "organizations",
    "reference": DATA_DIR / "references",
    "video": DATA_DIR / "videos",
    "venue": DATA_DIR / "venues",
}

ENTITY_SCHEMA_BY_TYPE = {
    "song": "song.schema.json",
    "album": "album.schema.json",
    "single": "album.schema.json",
    "concert": "concert.schema.json",
    "appearance": "appearance.schema.json",
    "person": "person.schema.json",
    "reference": "reference.schema.json",
    "organization": "organization.schema.json",
    "video": "reference.schema.json",
    "venue": "venue.schema.json",
}

SKIP_FILENAMES = {"relation_types.yaml", "members.yaml"}


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


V2_ID_PREFIXES = (
    "song_",
    "album_",
    "single_",
    "person_",
    "concert_",
    "appearance_",
    "venue_",
    "ref_",
    "video_",
    "org_",
    "image_",
)


def is_entity_document(data: dict[str, Any]) -> bool:
    if not isinstance(data, dict) or "id" not in data or "type" not in data:
        return False
    entity_id = str(data["id"])
    return any(entity_id.startswith(prefix) for prefix in V2_ID_PREFIXES)


def iter_entity_files() -> list[Path]:
    files: list[Path] = []
    for directory in ENTITY_TYPE_DIRS.values():
        if not directory.exists():
            continue
        for path in sorted(directory.glob("*.yaml")):
            if path.name in SKIP_FILENAMES:
                continue
            data = load_yaml(path)
            if is_entity_document(data):
                files.append(path)
    return files


def load_entities() -> dict[str, dict[str, Any]]:
    entities: dict[str, dict[str, Any]] = {}
    for path in iter_entity_files():
        data = load_yaml(path)
        if not is_entity_document(data):
            continue
        entity_id = data["id"]
        if entity_id in entities:
            raise ValueError(f"Duplicate entity id '{entity_id}' in {path}")
        entities[entity_id] = {**data, "_path": str(path.relative_to(ROOT))}
    return entities


def load_explicit_links() -> list[dict[str, Any]]:
    if not LINKS_PATH.exists():
        return []
    data = load_yaml(LINKS_PATH)
    return data if isinstance(data, list) else []


def load_relation_types() -> dict[str, dict[str, Any]]:
    data = load_yaml(RELATION_TYPES_PATH)
    index: dict[str, dict[str, Any]] = {}
    for section in ("derived", "explicit"):
        for item in data.get(section, []):
            index[item["id"]] = {**item, "origin": section}
    return index


def ensure_links_output_dirs() -> None:
    LINKS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPORTS_LINKS_PATH.parent.mkdir(parents=True, exist_ok=True)
