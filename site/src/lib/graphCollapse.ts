/**
 * Filter and collapse dense neighborhoods into expandable supernodes.
 */

import type { GraphEdge, GraphNode } from "./graphPayload";

export const COLLAPSE_THRESHOLD = 8;

/** Entity types that should never be hidden inside a cluster. */
export const NEVER_COLLAPSE_TYPES = new Set(["person", "pet", "organization"]);

export type ClusterNode = GraphNode & {
  isCluster: true;
  clusterHubId: string;
  clusterNeighborType: string;
  childIds: string[];
};

export type ViewNode = GraphNode | ClusterNode;

export type ViewEdge = GraphEdge & {
  /** True when this edge connects to a cluster supernode. */
  isClusterEdge?: boolean;
};

export function isClusterNode(node: ViewNode): node is ClusterNode {
  return (node as ClusterNode).isCluster === true;
}

export function clusterId(hubId: string, neighborType: string): string {
  return `cluster:${hubId}:${neighborType}`;
}

export function filterGraph(
  nodes: GraphNode[],
  edges: GraphEdge[],
  enabledTypes: Set<string>,
  enabledRelations: Set<string>,
): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const visibleIds = new Set(
    nodes.filter((n) => enabledTypes.has(n.type)).map((n) => n.id),
  );
  const filteredEdges = edges.filter(
    (e) =>
      enabledRelations.has(e.relation) &&
      visibleIds.has(e.source) &&
      visibleIds.has(e.target),
  );
  const connected = new Set<string>();
  for (const e of filteredEdges) {
    connected.add(e.source);
    connected.add(e.target);
  }
  // Keep isolated nodes of enabled types (useful for persons with no remaining edges)
  const filteredNodes = nodes.filter(
    (n) => enabledTypes.has(n.type) && (connected.has(n.id) || NEVER_COLLAPSE_TYPES.has(n.type)),
  );
  return { nodes: filteredNodes, edges: filteredEdges };
}

/**
 * Collapse dense same-type stars into supernodes.
 * Clusters already listed in `expandedClusters` stay expanded.
 */
export function collapseDenseBranches(
  nodes: GraphNode[],
  edges: GraphEdge[],
  expandedClusters: Set<string>,
  threshold = COLLAPSE_THRESHOLD,
): { nodes: ViewNode[]; edges: ViewEdge[] } {
  const nodeById = new Map(nodes.map((n) => [n.id, n]));
  const adj = new Map<string, Set<string>>();
  for (const n of nodes) adj.set(n.id, new Set());
  for (const e of edges) {
    adj.get(e.source)?.add(e.target);
    adj.get(e.target)?.add(e.source);
  }

  const hideIds = new Set<string>();
  const clusters: ClusterNode[] = [];
  const clusterByChild = new Map<string, string>();

  for (const hub of nodes) {
    const neighbors = [...(adj.get(hub.id) ?? [])]
      .map((id) => nodeById.get(id))
      .filter((n): n is GraphNode => Boolean(n));

    const byType = new Map<string, GraphNode[]>();
    for (const n of neighbors) {
      const list = byType.get(n.type) ?? [];
      list.push(n);
      byType.set(n.type, list);
    }

    for (const [neighborType, group] of byType) {
      if (group.length < threshold) continue;
      if (NEVER_COLLAPSE_TYPES.has(neighborType)) continue;

      const cid = clusterId(hub.id, neighborType);
      if (expandedClusters.has(cid)) continue;

      // Prefer collapsing leaf-like neighbors (low degree relative to the branch)
      const collapsible = group.filter((n) => {
        if (NEVER_COLLAPSE_TYPES.has(n.type)) return false;
        if (hideIds.has(n.id)) return false;
        // Don't collapse a node that is itself a high-degree hub to other types
        const deg = adj.get(n.id)?.size ?? 0;
        return deg <= threshold + 2;
      });

      if (collapsible.length < threshold) continue;

      for (const child of collapsible) {
        hideIds.add(child.id);
        clusterByChild.set(child.id, cid);
      }

      const label = `${neighborTypeLabel(neighborType)} via ${hub.title}`;
      clusters.push({
        id: cid,
        type: "cluster",
        title: `${label} (${collapsible.length})`,
        color: collapsible[0]?.color || hub.color,
        typeLabel: "Cluster",
        degree: collapsible.length,
        href: hub.href,
        isCluster: true,
        clusterHubId: hub.id,
        clusterNeighborType: neighborType,
        childIds: collapsible.map((c) => c.id),
        portrait: null,
        format: null,
        cover: null,
      });
    }
  }

  const visibleNodes: ViewNode[] = [
    ...nodes.filter((n) => !hideIds.has(n.id)),
    ...clusters,
  ];
  const visibleIds = new Set(visibleNodes.map((n) => n.id));

  const viewEdges: ViewEdge[] = [];
  const seen = new Set<string>();

  for (const e of edges) {
    let source = e.source;
    let target = e.target;

    if (hideIds.has(source) && hideIds.has(target)) continue;

    const srcCluster = clusterByChild.get(source);
    const tgtCluster = clusterByChild.get(target);

    if (srcCluster) source = srcCluster;
    if (tgtCluster) target = tgtCluster;

    if (source === target) continue;
    if (!visibleIds.has(source) || !visibleIds.has(target)) continue;

    const key = source < target ? `${source}|${target}|${e.relation}` : `${target}|${source}|${e.relation}`;
    if (seen.has(key)) continue;
    seen.add(key);

    viewEdges.push({
      ...e,
      id: key,
      source,
      target,
      isClusterEdge: Boolean(srcCluster || tgtCluster),
    });
  }

  return { nodes: visibleNodes, edges: viewEdges };
}

function neighborTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    article: "Articles",
    reference: "References",
    song: "Songs",
    album: "Albums",
    single: "Singles",
    concert: "Concerts",
    appearance: "Appearances",
    person: "People",
    venue: "Venues",
    organization: "Organizations",
  };
  return labels[type] || `${type}s`;
}

export function applyGraphView(
  nodes: GraphNode[],
  edges: GraphEdge[],
  enabledTypes: Set<string>,
  enabledRelations: Set<string>,
  expandedClusters: Set<string>,
  threshold = COLLAPSE_THRESHOLD,
): { nodes: ViewNode[]; edges: ViewEdge[] } {
  const filtered = filterGraph(nodes, edges, enabledTypes, enabledRelations);
  return collapseDenseBranches(filtered.nodes, filtered.edges, expandedClusters, threshold);
}
