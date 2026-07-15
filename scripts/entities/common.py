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
ONTOLOGY_PATH = DATA_DIR / "ontology.yaml"
LINKS_INDEX_PATH = ROOT / "site" / "src" / "data" / "links_index.json"
EXPORTS_LINKS_PATH = ROOT / "exports" / "links_index.json"
ONTOLOGY_JSON_PATH = ROOT / "site" / "src" / "data" / "ontology.json"
EXPORTS_ONTOLOGY_MMD_PATH = ROOT / "exports" / "ontology.mmd"

ENTITY_TYPE_DIRS: dict[str, Path] = {
    "song": DATA_DIR / "songs",
    "album": DATA_DIR / "albums",
    "single": DATA_DIR / "singles",
    "concert": DATA_DIR / "concerts",
    "appearance": DATA_DIR / "appearances",
    "person": DATA_DIR / "people",
    "pet": DATA_DIR / "pets",
    "organization": DATA_DIR / "organizations",
    "reference": DATA_DIR / "references",
    "video": DATA_DIR / "videos",
    "venue": DATA_DIR / "venues",
    "article": DATA_DIR / "articles",
}

ENTITY_SCHEMA_BY_TYPE = {
    "song": "song.schema.json",
    "album": "album.schema.json",
    "single": "album.schema.json",
    "concert": "concert.schema.json",
    "appearance": "appearance.schema.json",
    "person": "person.schema.json",
    "pet": "pet.schema.json",
    "reference": "reference.schema.json",
    "organization": "organization.schema.json",
    "video": "reference.schema.json",
    "venue": "venue.schema.json",
    "article": "article.schema.json",
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
    "pet_",
    "concert_",
    "appearance_",
    "venue_",
    "ref_",
    "video_",
    "org_",
    "image_",
    "article_",
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


def load_ontology() -> dict[str, Any]:
    if not ONTOLOGY_PATH.exists():
        return {"entity_types": {}}
    data = load_yaml(ONTOLOGY_PATH)
    return data if isinstance(data, dict) else {"entity_types": {}}


def load_entity_type_ui() -> dict[str, dict[str, str]]:
    ontology = load_ontology()
    ui: dict[str, dict[str, str]] = {}
    for entity_type, meta in ontology.get("entity_types", {}).items():
        ui[entity_type] = {
            "category": meta.get("category", "meta"),
            "color": meta.get("color", "gray"),
            "label": meta.get("label", entity_type),
        }
    return ui


def load_relation_types() -> dict[str, dict[str, Any]]:
    data = load_yaml(RELATION_TYPES_PATH)
    index: dict[str, dict[str, Any]] = {}
    for section in ("derived", "explicit"):
        for item in data.get(section, []):
            rel_id = item["id"]
            existing = index.get(rel_id, {})
            origins = list(existing.get("origins", []))
            if section not in origins:
                origins.append(section)
            merged = {**existing, **item, "origins": origins, "origin": origins[0]}
            if merged.get("source_field") and "derived" not in merged["origins"]:
                merged["origins"] = ["derived", *merged["origins"]]
            index[rel_id] = merged
    return index


def active_explicit_relations(relation_types: dict[str, dict[str, Any]] | None = None) -> set[str]:
    types = relation_types or load_relation_types()
    return {
        rel_id
        for rel_id, meta in types.items()
        if "explicit" in meta.get("origins", [meta.get("origin")])
        and meta.get("status", "active") == "active"
    }


def entity_type_for_id(entity_id: str, entities: dict[str, dict[str, Any]]) -> str | None:
    entity = entities.get(entity_id)
    if entity:
        return entity.get("type")
    return None


def ensure_links_output_dirs() -> None:
    LINKS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPORTS_LINKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ONTOLOGY_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPORTS_ONTOLOGY_MMD_PATH.parent.mkdir(parents=True, exist_ok=True)
