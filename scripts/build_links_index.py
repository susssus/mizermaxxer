#!/usr/bin/env python3
"""Resolve entity links into a per-id linked_entities index."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from entities.common import (
    EXPORTS_LINKS_PATH,
    LINKS_INDEX_PATH,
    active_explicit_relations,
    ensure_links_output_dirs,
    load_entities,
    load_entity_type_ui,
    load_explicit_links,
    load_relation_types,
)


@dataclass
class Edge:
    from_id: str
    to_id: str
    relation: str
    source: str
    direction: str
    role: str | None = None
    note: str | None = None
    sources: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "entity_id": self.to_id if self.direction == "outgoing" else self.from_id,
            "relation": self.relation,
            "direction": self.direction,
            "source": self.source,
            "role": self.role,
            "note": self.note,
            "sources": self.sources,
        }

    def key(self) -> tuple:
        return (self.from_id, self.to_id, self.relation, self.role or "", self.note or "")


def add_edge(edges: list[Edge], edge: Edge, seen: set[tuple]) -> None:
    if edge.key() in seen:
        return
    seen.add(edge.key())
    edges.append(edge)


def inverse_relation(relation: str, relation_types: dict[str, dict[str, Any]]) -> str | None:
    meta = relation_types.get(relation)
    if not meta:
        return None
    inverse = meta.get("inverse")
    return inverse if isinstance(inverse, str) else None


def derive_edges(entities: dict[str, dict[str, Any]], seen: set[tuple]) -> list[Edge]:
    edges: list[Edge] = []

    for entity_id, entity in entities.items():
        entity_type = entity["type"]

        if entity_type == "song":
            for album_id in entity.get("appears_on", []):
                add_edge(
                    edges,
                    Edge(entity_id, album_id, "appears_on", "entity_field", "outgoing"),
                    seen,
                )
                add_edge(
                    edges,
                    Edge(album_id, entity_id, "includes_song", "entity_field", "outgoing"),
                    seen,
                )
            for credit in entity.get("personnel", []):
                person_id = credit["person"]
                role = credit.get("role")
                add_edge(
                    edges,
                    Edge(entity_id, person_id, "personnel", "entity_field", "outgoing", role=role),
                    seen,
                )
                add_edge(
                    edges,
                    Edge(person_id, entity_id, "credited_on", "entity_field", "outgoing", role=role),
                    seen,
                )

        if entity_type == "album":
            for track in entity.get("tracklist", []):
                song_id = track["song"]
                add_edge(
                    edges,
                    Edge(entity_id, song_id, "includes_song", "entity_field", "outgoing"),
                    seen,
                )
                add_edge(
                    edges,
                    Edge(song_id, entity_id, "appears_on", "entity_field", "outgoing"),
                    seen,
                )

        if entity_type == "concert":
            for song_id in entity.get("setlist", []):
                add_edge(
                    edges,
                    Edge(song_id, entity_id, "performed_at_concert", "entity_field", "outgoing"),
                    seen,
                )
                add_edge(
                    edges,
                    Edge(entity_id, song_id, "features_concert", "entity_field", "outgoing"),
                    seen,
                )
            for person_id in entity.get("members_present", []):
                add_edge(
                    edges,
                    Edge(person_id, entity_id, "performed_at_concert", "entity_field", "outgoing"),
                    seen,
                )
                add_edge(
                    edges,
                    Edge(entity_id, person_id, "features_concert", "entity_field", "outgoing"),
                    seen,
                )
            venue_id = entity.get("venue")
            if venue_id:
                add_edge(
                    edges,
                    Edge(entity_id, venue_id, "held_at", "entity_field", "outgoing", note="held at venue"),
                    seen,
                )
                add_edge(
                    edges,
                    Edge(venue_id, entity_id, "hosted", "entity_field", "outgoing"),
                    seen,
                )

        if entity_type == "appearance":
            for song_id in entity.get("songs_performed", []):
                add_edge(
                    edges,
                    Edge(song_id, entity_id, "performed_at_appearance", "entity_field", "outgoing"),
                    seen,
                )
                add_edge(
                    edges,
                    Edge(entity_id, song_id, "features_appearance", "entity_field", "outgoing"),
                    seen,
                )
            for person_id in entity.get("members_present", []):
                add_edge(
                    edges,
                    Edge(person_id, entity_id, "appeared_at", "entity_field", "outgoing"),
                    seen,
                )
                add_edge(
                    edges,
                    Edge(entity_id, person_id, "featured_appearance", "entity_field", "outgoing"),
                    seen,
                )
            broadcast = entity.get("broadcast") or {}
            network_id = broadcast.get("network")
            if network_id:
                add_edge(
                    edges,
                    Edge(entity_id, network_id, "broadcast_on", "entity_field", "outgoing"),
                    seen,
                )
                add_edge(
                    edges,
                    Edge(network_id, entity_id, "aired", "entity_field", "outgoing"),
                    seen,
                )
            venue_id = entity.get("venue")
            if venue_id:
                add_edge(
                    edges,
                    Edge(entity_id, venue_id, "held_at", "entity_field", "outgoing", note="recorded at venue"),
                    seen,
                )
                add_edge(
                    edges,
                    Edge(venue_id, entity_id, "hosted", "entity_field", "outgoing"),
                    seen,
                )

        if entity_type == "reference":
            for fact in entity.get("facts", []):
                for target in fact.get("targets", []):
                    add_edge(
                        edges,
                        Edge(entity_id, target, "discusses", "entity_field", "outgoing"),
                        seen,
                    )
                    add_edge(
                        edges,
                        Edge(target, entity_id, "cited_by", "entity_field", "outgoing"),
                        seen,
                    )

        if entity_type == "article":
            ref_id = entity.get("published_in")
            if ref_id:
                add_edge(
                    edges,
                    Edge(entity_id, ref_id, "published_in", "entity_field", "outgoing"),
                    seen,
                )
                add_edge(
                    edges,
                    Edge(ref_id, entity_id, "includes_article", "entity_field", "outgoing"),
                    seen,
                )

    return edges


def explicit_edges(links: list[dict[str, Any]], entities: dict[str, dict[str, Any]], seen: set[tuple]) -> list[Edge]:
    edges: list[Edge] = []
    relation_types = load_relation_types()

    for link in links:
        from_id = link["from"]
        to_id = link["to"]
        relation = link["relation"]
        role = link.get("role")
        note = link.get("note")
        sources = link.get("sources", [])

        if from_id not in entities:
            raise ValueError(f"Link from unknown entity '{from_id}'")
        if to_id not in entities:
            raise ValueError(f"Link to unknown entity '{to_id}'")

        add_edge(
            edges,
            Edge(from_id, to_id, relation, "links_yaml", "outgoing", role=role, note=note, sources=sources),
            seen,
        )

        inverse = inverse_relation(relation, relation_types)
        meta = relation_types.get(relation, {})
        if meta.get("direction") == "symmetric":
            add_edge(
                edges,
                Edge(to_id, from_id, relation, "links_yaml", "outgoing", role=role, note=note, sources=sources),
                seen,
            )
        elif inverse:
            add_edge(
                edges,
                Edge(to_id, from_id, inverse, "links_yaml", "outgoing", role=role, note=note, sources=sources),
                seen,
            )

    return edges


def build_linked_entities_index(
    entities: dict[str, dict[str, Any]], edges: list[Edge]
) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {
        entity_id: {"outgoing": [], "incoming": [], "all": [], "link_count": 0}
        for entity_id in entities
    }

    for edge in edges:
        if edge.from_id not in index:
            index[edge.from_id] = {"outgoing": [], "incoming": [], "all": [], "link_count": 0}
        if edge.to_id not in index:
            index[edge.to_id] = {"outgoing": [], "incoming": [], "all": [], "link_count": 0}

        outgoing = edge.as_dict()
        outgoing["entity_id"] = edge.to_id
        outgoing["direction"] = "outgoing"
        index[edge.from_id]["outgoing"].append(outgoing)

        incoming = edge.as_dict()
        incoming["entity_id"] = edge.from_id
        incoming["direction"] = "incoming"
        index[edge.to_id]["incoming"].append(incoming)

    relation_types = load_relation_types()

    for entity_id, bucket in index.items():
        merged: dict[tuple, dict[str, Any]] = {}
        for entry in bucket["outgoing"] + bucket["incoming"]:
            key = (entry["entity_id"], entry["relation"], entry.get("role") or "", entry.get("note") or "")
            if key not in merged:
                relation_meta = relation_types.get(entry["relation"], {})
                merged[key] = {
                    **entry,
                    "category": relation_meta.get("category"),
                    "color": relation_meta.get("color"),
                    "label": relation_meta.get("label", entry["relation"]),
                }
        bucket["all"] = sorted(merged.values(), key=lambda item: (item.get("category") or "", item["relation"]))
        bucket["link_count"] = len(bucket["all"])

    return index


def entity_title(entity: dict[str, Any]) -> str:
    if "title" in entity and isinstance(entity["title"], dict):
        return entity["title"].get("romanized") or entity["title"].get("original") or entity["id"]
    if "title" in entity:
        return str(entity["title"])
    if "name" in entity and isinstance(entity["name"], dict):
        return entity["name"].get("romanized") or entity["name"].get("original") or entity["id"]
    return entity["id"]


TYPE_UI = load_entity_type_ui()

STATUS_PRIORITY = {
    "verified": 5,
    "possible": 4,
    "unverified": 3,
    "needs_verification": 2,
    "disputed": 1,
}


def extract_date(entity: dict[str, Any]) -> str | None:
    entity_type = entity.get("type")
    if entity_type == "album":
        return entity.get("release", {}).get("date")
    if entity_type == "concert":
        return entity.get("date")
    if entity_type == "appearance":
        return entity.get("date")
    if entity_type == "reference":
        return entity.get("date")
    if entity_type == "single":
        return entity.get("release_date")
    if entity_type == "video":
        return entity.get("release_date")
    if entity_type == "article":
        return None
    return None


def extract_status(entity: dict[str, Any]) -> str:
    if entity.get("verification_status"):
        return entity["verification_status"]
    facts = entity.get("facts", [])
    if facts:
        return max(facts, key=lambda fact: STATUS_PRIORITY.get(fact.get("status", ""), 0))["status"]
    return "unverified"


def browse_rows(
    entities: dict[str, dict[str, Any]], linked_entities: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entity_id, entity in entities.items():
        ui = TYPE_UI.get(entity["type"], {"category": "meta", "color": "gray", "label": entity["type"]})
        date = extract_date(entity)
        rows.append(
            {
                "id": entity_id,
                "type": entity["type"],
                "type_label": ui["label"],
                "type_category": ui["category"],
                "type_color": ui["color"],
                "title": entity_title(entity),
                "date": date,
                "year": date[:4] if date else None,
                "status": extract_status(entity),
                "link_count": linked_entities.get(entity_id, {}).get("link_count", 0),
            }
        )
    return sorted(rows, key=lambda row: (row["date"] or "9999", row["title"]))


def entity_summary(entities: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    for entity_id, entity in sorted(entities.items()):
        summaries.append(
            {
                "id": entity_id,
                "type": entity["type"],
                "title": entity_title(entity),
                "path": entity.get("_path"),
            }
        )
    return summaries


def main() -> int:
    try:
        entities = load_entities()
        relation_types = load_relation_types()
        explicit = load_explicit_links()

        allowed_explicit = active_explicit_relations(relation_types)
        for link in explicit:
            if link["relation"] not in allowed_explicit:
                raise ValueError(
                    f"Unknown relation '{link['relation']}' in links.yaml (must be in relation_types.yaml explicit list)"
                )

        seen: set[tuple] = set()
        edges = derive_edges(entities, seen) + explicit_edges(explicit, entities, seen)
        linked_entities = build_linked_entities_index(entities, edges)
        browse = browse_rows(entities, linked_entities)

        payload = {
            "generated_at": __import__("datetime").datetime.now(__import__("datetime").UTC)
            .isoformat()
            .replace("+00:00", "Z"),
            "entity_count": len(entities),
            "edge_count": len(edges),
            "entities": entity_summary(entities),
            "browse": browse,
            "entities_by_id": {entity_id: {k: v for k, v in entity.items() if k != "_path"} for entity_id, entity in entities.items()},
            "linked_entities": linked_entities,
            "relation_types": relation_types,
            "type_ui": TYPE_UI,
        }

        ensure_links_output_dirs()
        encoded = json.dumps(payload, ensure_ascii=False, indent=2)
        LINKS_INDEX_PATH.write_text(encoded, encoding="utf-8")
        EXPORTS_LINKS_PATH.write_text(encoded, encoding="utf-8")

        print(f"Built links index: {len(entities)} entities, {len(edges)} edges.")
        print(f"  → {LINKS_INDEX_PATH}")
        return 0
    except (ValueError, KeyError) as exc:
        print(f"Link index build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
