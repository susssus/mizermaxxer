#!/usr/bin/env python3
"""Generate ontology documentation and Mermaid diagrams from the ontology spec."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from entities.common import (
    EXPORTS_ONTOLOGY_MMD_PATH,
    ONTOLOGY_JSON_PATH,
    ONTOLOGY_PATH,
    ROOT,
    load_ontology,
    load_relation_types,
    load_yaml,
)

DOCS_ONTOLOGY_PATH = ROOT / "docs" / "ONTOLOGY.md"


def mermaid_entity_name(entity_type: str) -> str:
    return entity_type.replace("_", "")


def mermaid_relation_label(relation: dict[str, Any]) -> str:
    label = relation.get("label", relation["id"])
    status = relation.get("status", "active")
    if status == "planned":
        return f"{label} (planned)"
    return label


def build_er_diagram(relation_types: dict[str, dict[str, Any]]) -> str:
    lines = ["erDiagram"]
    seen_pairs: set[tuple[str, str, str]] = set()

    for rel_id, meta in sorted(relation_types.items()):
        if meta.get("status") == "deprecated":
            continue
        domain = meta.get("domain") or []
        range_types = meta.get("range") or []
        direction = meta.get("direction", "outgoing")
        origins = meta.get("origins", [meta.get("origin", "derived")])
        origin = "explicit" if "explicit" in origins and "derived" not in origins else (
            "both" if "explicit" in origins and "derived" in origins else "derived"
        )
        label = mermaid_relation_label(meta)

        for from_type in domain:
            for to_type in range_types:
                pair_key = (from_type, to_type, rel_id)
                if pair_key in seen_pairs:
                    continue
                seen_pairs.add(pair_key)
                from_name = mermaid_entity_name(from_type)
                to_name = mermaid_entity_name(to_type)
                cardinality = "||--o{" if direction != "symmetric" else "}o--o{"
                annotation = f' : "{label}"'
                if origin == "derived":
                    annotation = f' : "{label} [derived]"'
                elif origin == "both":
                    annotation = f' : "{label} [derived+explicit]"'
                lines.append(f"    {from_name} {cardinality} {to_name}{annotation}")

    return "\n".join(lines)


def relation_table_rows(relation_types: dict[str, dict[str, Any]]) -> list[str]:
    rows: list[str] = []
    rows.append("| Relation | Label | Domain → Range | Origin | Status |")
    rows.append("|----------|-------|----------------|--------|--------|")
    for rel_id, meta in sorted(relation_types.items()):
        domain = ", ".join(meta.get("domain", [])) or "—"
        range_types = ", ".join(meta.get("range", [])) or "—"
        origins = ", ".join(meta.get("origins", [meta.get("origin", "")]))
        rows.append(
            f"| `{rel_id}` | {meta.get('label', rel_id)} | {domain} → {range_types} | {origins} | {meta.get('status', 'active')} |"
        )
    return rows


def entity_type_table_rows(ontology: dict[str, Any]) -> list[str]:
    rows: list[str] = []
    rows.append("| Type | Label | Prefix | Category |")
    rows.append("|------|-------|--------|----------|")
    for entity_type, meta in sorted(ontology.get("entity_types", {}).items()):
        rows.append(
            f"| `{entity_type}` | {meta.get('label', entity_type)} | `{meta.get('prefix', '')}` | {meta.get('category', '')} |"
        )
    return rows


def build_markdown(
    ontology: dict[str, Any],
    relation_types: dict[str, dict[str, Any]],
    mermaid: str,
) -> str:
    generated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    active_count = sum(1 for meta in relation_types.values() if meta.get("status", "active") == "active")
    planned_count = sum(1 for meta in relation_types.values() if meta.get("status") == "planned")

    sections = [
        "# Entity ontology",
        "",
        f"_Generated at {generated_at} by `make ontology`. Edit [`data/ontology.yaml`](../data/ontology.yaml) "
        "and [`data/references/relation_types.yaml`](../data/references/relation_types.yaml), then regenerate._",
        "",
        "The archive models Malice Mizer research data as a typed entity graph. This document shows the "
        "**type-level** relationships (ontology), not individual entity instances.",
        "",
        "## Entity types",
        "",
        *entity_type_table_rows(ontology),
        "",
        f"**{len(ontology.get('entity_types', {}))}** entity types defined.",
        "",
        "## Relations",
        "",
        *relation_table_rows(relation_types),
        "",
        f"**{active_count}** active relations, **{planned_count}** planned (defined but not yet used in data).",
        "",
        "### Type-level diagram",
        "",
        "Solid annotations are explicit-only; `[derived]` edges are inferred from entity fields; "
        "`[derived+explicit]` relations can be both inferred and stated in `data/links.yaml`.",
        "",
        "```mermaid",
        mermaid,
        "```",
        "",
        "## Labeling fields",
        "",
        "Each relation in `relation_types.yaml` supports:",
        "",
        "- `label` / `label_ja` — English and Japanese display names",
        "- `domain` / `range` — allowed entity type pairs (enforced by `make entities-validate`)",
        "- `category` / `color` — UI grouping on browse and entity pages",
        "- `examples` — worked instance edges for editors",
        "- `status` — `active` or `planned`",
        "",
        "Personnel credits use the `role` sub-label (see `personnel_role` in [`schema/vocabularies.json`](../schema/vocabularies.json)).",
        "",
    ]
    return "\n".join(sections)


def main() -> int:
    try:
        ontology = load_ontology()
        relation_types = load_relation_types()
        relation_data = load_yaml(ROOT / "data" / "references" / "relation_types.yaml")
        mermaid = build_er_diagram(relation_types)
        markdown = build_markdown(ontology, relation_types, mermaid)

        payload = {
            "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "entity_types": ontology.get("entity_types", {}),
            "relation_types": relation_types,
            "categories": relation_data.get("categories", {}),
            "mermaid_er": mermaid,
        }

        DOCS_ONTOLOGY_PATH.write_text(markdown, encoding="utf-8")
        EXPORTS_ONTOLOGY_MMD_PATH.write_text(mermaid + "\n", encoding="utf-8")
        ONTOLOGY_JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"Built ontology docs: {len(ontology.get('entity_types', {}))} types, {len(relation_types)} relations.")
        print(f"  → {DOCS_ONTOLOGY_PATH}")
        print(f"  → {EXPORTS_ONTOLOGY_MMD_PATH}")
        print(f"  → {ONTOLOGY_JSON_PATH}")
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print(f"Ontology build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
