/**
 * Build a compact 3D graph payload from links_index + archive enrichments.
 */

import linksIndex from "../data/links_index.json";
import archive from "../data/archive.json";
import crosswalk from "../data/entity_crosswalk.json";

export type GraphNode = {
  id: string;
  type: string;
  title: string;
  color: string;
  typeLabel: string;
  degree: number;
  portrait?: string | null;
  format?: string | null;
  cover?: string | null;
  href: string;
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  relation: string;
  relationLabel: string;
  color: string;
  category: string;
};

export type GraphTypeMeta = {
  id: string;
  label: string;
  color: string;
  count: number;
};

export type GraphRelationMeta = {
  id: string;
  label: string;
  color: string;
  category: string;
  count: number;
};

export type GraphPayload = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  types: GraphTypeMeta[];
  relations: GraphRelationMeta[];
  defaults: {
    typesOff: string[];
    relationsOff: string[];
  };
};

type RelationMeta = {
  id: string;
  label?: string;
  color?: string;
  category?: string;
  inverse?: string;
  direction?: string;
};

type LinkedEdge = {
  entity_id: string;
  relation: string;
};

const PRESS_TYPES = ["article", "reference"];
/** Outgoing halves — match what remains after undirected canonicalization. */
const PRESS_RELATIONS = ["published_in"];

function publicImagePath(src: string | null | undefined): string | null {
  if (!src) return null;
  if (/^https?:\/\//i.test(src)) return src;
  return src.startsWith("/") ? src : `/${src}`;
}

function buildPortraitMap(): Map<string, string> {
  const map = new Map<string, string>();
  for (const profile of archive.people_profiles ?? []) {
    const path = publicImagePath(profile.portrait_image);
    if (path && profile.id) map.set(profile.id, path);
  }
  for (const pet of archive.pets ?? []) {
    const path = publicImagePath(pet.portrait_image);
    if (path && pet.id) map.set(pet.id, path);
  }
  return map;
}

function buildReleaseEnrichment(): Map<string, { format?: string | null; cover?: string | null }> {
  const map = new Map<string, { format?: string | null; cover?: string | null }>();
  const albums = crosswalk.albums as Record<string, string>;
  for (const album of archive.albums ?? []) {
    const entityId = albums[album.id] ?? (album.id.startsWith("album_") ? album.id : null);
    if (!entityId) continue;
    map.set(entityId, {
      format: album.format ?? null,
      cover: publicImagePath(album.cover_image),
    });
  }
  const singlesCw = (crosswalk as { singles?: Record<string, string> }).singles ?? {};
  for (const single of archive.singles ?? []) {
    const entityId =
      singlesCw[single.id] ??
      (single.id.startsWith("single_") ? single.id : `single_${single.id.replace(/-/g, "_")}`);
    // Only enrich if the entity exists in the graph
    map.set(entityId, {
      format: single.format ?? null,
      cover: publicImagePath(single.cover_image),
    });
  }
  // Direct lookup for entity-style album ids already in graph
  for (const album of archive.albums ?? []) {
    const guessed = `album_${album.id.replace(/-/g, "_")}`;
    if (!map.has(guessed)) {
      map.set(guessed, {
        format: album.format ?? null,
        cover: publicImagePath(album.cover_image),
      });
    }
  }
  return map;
}

/** Build bidirectional inverse lookup (source JSON only sets inverse on one side). */
function buildInverseMap(relationTypes: Record<string, RelationMeta>): Map<string, string> {
  const map = new Map<string, string>();
  for (const [id, meta] of Object.entries(relationTypes)) {
    if (meta.inverse) {
      map.set(id, meta.inverse);
      map.set(meta.inverse, id);
    }
  }
  return map;
}

/** Prefer the outgoing half of a pair as the undirected edge's relation id. */
function canonicalRelation(
  relation: string,
  inverseMap: Map<string, string>,
  relationTypes: Record<string, RelationMeta>,
): string {
  const inverse = inverseMap.get(relation);
  if (!inverse) return relation;
  const a = relationTypes[relation];
  const b = relationTypes[inverse];
  if (a?.direction === "outgoing") return relation;
  if (b?.direction === "outgoing") return inverse;
  return relation <= inverse ? relation : inverse;
}

function canonicalEdgeKey(
  from: string,
  to: string,
  relation: string,
  inverseMap: Map<string, string>,
  relationTypes: Record<string, RelationMeta>,
): { key: string; source: string; target: string; relation: string } {
  const canonRel = canonicalRelation(relation, inverseMap, relationTypes);
  const [source, target] = from <= to ? [from, to] : [to, from];
  return { key: `${source}|${target}|${canonRel}`, source, target, relation: canonRel };
}

export function buildGraphPayload(): GraphPayload {
  const relationTypes = linksIndex.relation_types as Record<string, RelationMeta>;
  const inverseMap = buildInverseMap(relationTypes);
  const typeUi = linksIndex.type_ui as Record<string, { color?: string; label?: string }>;
  const portraits = buildPortraitMap();
  const releases = buildReleaseEnrichment();

  const nodeMap = new Map<string, GraphNode>();
  for (const row of linksIndex.browse) {
    const enrichment = releases.get(row.id);
    nodeMap.set(row.id, {
      id: row.id,
      type: row.type,
      title: row.title || row.id,
      color: row.type_color || typeUi[row.type]?.color || "gray",
      typeLabel: row.type_label || typeUi[row.type]?.label || row.type,
      degree: 0,
      portrait: portraits.get(row.id) ?? null,
      format: enrichment?.format ?? null,
      cover: enrichment?.cover ?? null,
      href: `/entity/${row.id}`,
    });
  }

  const edgeMap = new Map<string, GraphEdge>();
  const linked = linksIndex.linked_entities as Record<
    string,
    { outgoing?: LinkedEdge[] }
  >;

  for (const [fromId, bucket] of Object.entries(linked)) {
    if (!nodeMap.has(fromId)) continue;
    for (const link of bucket.outgoing ?? []) {
      const toId = link.entity_id;
      if (!nodeMap.has(toId)) continue;
      const { key, source, target, relation } = canonicalEdgeKey(
        fromId,
        toId,
        link.relation,
        inverseMap,
        relationTypes,
      );
      if (edgeMap.has(key)) continue;
      const meta = relationTypes[relation] ?? relationTypes[link.relation];
      edgeMap.set(key, {
        id: key,
        source,
        target,
        relation,
        relationLabel: meta?.label || relation,
        color: meta?.color || "gray",
        category: meta?.category || "meta",
      });
    }
  }

  const degree = new Map<string, number>();
  for (const edge of edgeMap.values()) {
    degree.set(edge.source, (degree.get(edge.source) ?? 0) + 1);
    degree.set(edge.target, (degree.get(edge.target) ?? 0) + 1);
  }
  for (const node of nodeMap.values()) {
    node.degree = degree.get(node.id) ?? 0;
  }

  const typeCounts = new Map<string, number>();
  for (const node of nodeMap.values()) {
    typeCounts.set(node.type, (typeCounts.get(node.type) ?? 0) + 1);
  }
  const types: GraphTypeMeta[] = [...typeCounts.entries()]
    .map(([id, count]) => ({
      id,
      label: typeUi[id]?.label || id,
      color: typeUi[id]?.color || "gray",
      count,
    }))
    .sort((a, b) => a.label.localeCompare(b.label));

  const relationCounts = new Map<string, number>();
  for (const edge of edgeMap.values()) {
    relationCounts.set(edge.relation, (relationCounts.get(edge.relation) ?? 0) + 1);
  }
  const relations: GraphRelationMeta[] = [...relationCounts.entries()]
    .map(([id, count]) => {
      const meta = relationTypes[id];
      return {
        id,
        label: meta?.label || id,
        color: meta?.color || "gray",
        category: meta?.category || "meta",
        count,
      };
    })
    .sort((a, b) => a.label.localeCompare(b.label));

  return {
    nodes: [...nodeMap.values()],
    edges: [...edgeMap.values()],
    types,
    relations,
    defaults: {
      typesOff: PRESS_TYPES.filter((t) => typeCounts.has(t)),
      relationsOff: PRESS_RELATIONS.filter((r) => relationCounts.has(r)),
    },
  };
}
