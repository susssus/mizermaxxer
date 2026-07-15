import ForceGraph3D from "3d-force-graph";
import * as THREE from "three";
import {
  applyGraphView,
  isClusterNode,
  type ClusterNode,
  type ViewNode,
} from "../lib/graphCollapse";
import type { GraphEdge, GraphNode, GraphPayload } from "../lib/graphPayload";

const COLOR_HEX: Record<string, string> = {
  coral: "#e07a5f",
  purple: "#7b6dd6",
  pink: "#d65a8a",
  lavender: "#9b8ec4",
  teal: "#4a9e8e",
  gold: "#c9a227",
  amber: "#e9a319",
  gray: "#8a7f76",
};

const MEDIA_ICONS: Record<string, string> = {
  cd: "/icons/media/cd.svg",
  cassette: "/icons/media/cassette.svg",
  vhs: "/icons/media/vhs.svg",
  dvd: "/icons/media/dvd.svg",
};

type GraphApi = {
  graphData: (data?: { nodes: ViewNode[]; links: GraphEdge[] }) => unknown;
  nodeThreeObject: (fn: (node: ViewNode) => THREE.Object3D) => GraphApi;
  nodeThreeObjectExtend: (v: boolean) => GraphApi;
  nodeLabel: (fn: (node: ViewNode) => string) => GraphApi;
  linkColor: (fn: (link: GraphEdge) => string) => GraphApi;
  linkOpacity: (v: number) => GraphApi;
  linkWidth: (fn: (link: GraphEdge) => number) => GraphApi;
  backgroundColor: (c: string) => GraphApi;
  showNavInfo: (v: boolean) => GraphApi;
  warmupTicks: (n: number) => GraphApi;
  cooldownTicks: (n: number) => GraphApi;
  onNodeClick: (fn: (node: ViewNode, event: MouseEvent) => void) => GraphApi;
  onNodeHover: (fn: (node: ViewNode | null) => void) => GraphApi;
  width: (w: number) => GraphApi;
  height: (h: number) => GraphApi;
  cameraPosition: (pos: { x: number; y: number; z: number }, lookAt?: object, ms?: number) => GraphApi;
};

function hexFor(colorName: string | undefined): string {
  return COLOR_HEX[colorName || "gray"] || COLOR_HEX.gray;
}

function makeCircleTexture(imageUrl: string, rimColor: string): THREE.Texture {
  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext("2d")!;
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;

  const img = new Image();
  img.crossOrigin = "anonymous";
  img.onload = () => {
    ctx.clearRect(0, 0, 128, 128);
    ctx.beginPath();
    ctx.arc(64, 64, 58, 0, Math.PI * 2);
    ctx.closePath();
    ctx.clip();
    const scale = Math.max(128 / img.width, 128 / img.height);
    const w = img.width * scale;
    const h = img.height * scale;
    ctx.drawImage(img, (128 - w) / 2, (128 - h) / 2, w, h);
    ctx.beginPath();
    ctx.arc(64, 64, 57, 0, Math.PI * 2);
    ctx.strokeStyle = rimColor;
    ctx.lineWidth = 6;
    ctx.stroke();
    texture.needsUpdate = true;
  };
  img.src = imageUrl;
  return texture;
}

function makeIconTexture(iconUrl: string): THREE.Texture {
  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext("2d")!;
  // Placeholder disc while SVG loads
  ctx.beginPath();
  ctx.arc(64, 64, 52, 0, Math.PI * 2);
  ctx.fillStyle = "#c8c4bc";
  ctx.fill();
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const img = new Image();
  img.crossOrigin = "anonymous";
  img.onload = () => {
    ctx.clearRect(0, 0, 128, 128);
    ctx.drawImage(img, 8, 8, 112, 112);
    texture.needsUpdate = true;
  };
  img.src = iconUrl;
  return texture;
}

function makePetFallbackTexture(rimColor: string): THREE.Texture {
  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext("2d")!;
  ctx.beginPath();
  ctx.arc(64, 64, 58, 0, Math.PI * 2);
  ctx.fillStyle = "#e8dfd6";
  ctx.fill();
  ctx.strokeStyle = rimColor;
  ctx.lineWidth = 6;
  ctx.stroke();
  ctx.fillStyle = "#6b5f57";
  ctx.beginPath();
  ctx.arc(64, 58, 14, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(42, 78, 9, 0, Math.PI * 2);
  ctx.arc(54, 88, 9, 0, Math.PI * 2);
  ctx.arc(74, 88, 9, 0, Math.PI * 2);
  ctx.arc(86, 78, 9, 0, Math.PI * 2);
  ctx.fill();
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function makeClusterTexture(color: string, count: number): THREE.Texture {
  const canvas = document.createElement("canvas");
  canvas.width = 128;
  canvas.height = 128;
  const ctx = canvas.getContext("2d")!;
  ctx.beginPath();
  ctx.arc(64, 64, 58, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.globalAlpha = 0.85;
  ctx.fill();
  ctx.globalAlpha = 1;
  ctx.strokeStyle = "#1a1410";
  ctx.lineWidth = 4;
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(64, 64, 40, 0, Math.PI * 2);
  ctx.strokeStyle = "rgba(255,255,255,0.45)";
  ctx.lineWidth = 3;
  ctx.stroke();
  ctx.beginPath();
  ctx.arc(64, 64, 22, 0, Math.PI * 2);
  ctx.stroke();
  ctx.fillStyle = "#faf8f5";
  const label = String(count);
  ctx.font = `bold ${label.length > 2 ? 22 : 28}px Georgia, serif`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(label, 64, 66);
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  return texture;
}

function spriteFromTexture(texture: THREE.Texture, size: number): THREE.Sprite {
  const mat = new THREE.SpriteMaterial({
    map: texture,
    transparent: true,
    depthWrite: false,
  });
  const sprite = new THREE.Sprite(mat);
  sprite.scale.set(size, size, 1);
  return sprite;
}

function createNodeObject(node: ViewNode): THREE.Object3D {
  const color = hexFor(node.color);
  const sizeBase = 6 + Math.min(10, Math.sqrt(node.degree || 1));

  if (isClusterNode(node)) {
    const tex = makeClusterTexture(color, node.childIds.length);
    return spriteFromTexture(tex, sizeBase * 1.6);
  }

  if (node.type === "person" && node.portrait) {
    const tex = makeCircleTexture(node.portrait, color);
    return spriteFromTexture(tex, sizeBase * 1.8);
  }

  if (node.type === "pet") {
    const tex = node.portrait
      ? makeCircleTexture(node.portrait, color)
      : makePetFallbackTexture(color);
    return spriteFromTexture(tex, sizeBase * 1.6);
  }

  if ((node.type === "album" || node.type === "single") && node.format && MEDIA_ICONS[node.format]) {
    const tex = makeIconTexture(MEDIA_ICONS[node.format]);
    return spriteFromTexture(tex, sizeBase * 1.7);
  }

  // Default: colored sphere
  const geom = new THREE.SphereGeometry(sizeBase * 0.45, 16, 16);
  const mat = new THREE.MeshLambertMaterial({ color, transparent: true, opacity: 0.92 });
  return new THREE.Mesh(geom, mat);
}

export function initOntologyGraph(root: HTMLElement, payload: GraphPayload): void {
  const canvasHost = root.querySelector<HTMLElement>("[data-graph-canvas]");
  const typeFilters = root.querySelector<HTMLElement>("[data-type-filters]");
  const relationFilters = root.querySelector<HTMLElement>("[data-relation-filters]");
  const selectionEl = root.querySelector<HTMLElement>("[data-selection]");
  const hoverEl = root.querySelector<HTMLElement>("[data-hover]");
  const statsEl = root.querySelector<HTMLElement>("[data-graph-stats]");
  const expandAllBtn = root.querySelector<HTMLButtonElement>("[data-expand-all]");
  const collapseAllBtn = root.querySelector<HTMLButtonElement>("[data-collapse-all]");
  const togglePanelBtn = root.querySelector<HTMLButtonElement>("[data-toggle-panel]");
  const panel = root.querySelector<HTMLElement>("[data-panel]");

  if (!canvasHost || !typeFilters || !relationFilters || !selectionEl) return;

  const enabledTypes = new Set(
    payload.types.filter((t) => !payload.defaults.typesOff.includes(t.id)).map((t) => t.id),
  );
  const enabledRelations = new Set(
    payload.relations
      .filter((r) => !payload.defaults.relationsOff.includes(r.id))
      .map((r) => r.id),
  );
  const expandedClusters = new Set<string>();

  // Build filter checkboxes
  typeFilters.innerHTML = payload.types
    .map(
      (t) => `
      <label class="og-filter">
        <input type="checkbox" data-type="${t.id}" ${enabledTypes.has(t.id) ? "checked" : ""} />
        <span class="type-chip ${t.color}">${t.label}</span>
        <span class="og-filter__count">${t.count}</span>
      </label>`,
    )
    .join("");

  relationFilters.innerHTML = payload.relations
    .map(
      (r) => `
      <label class="og-filter">
        <input type="checkbox" data-relation="${r.id}" ${enabledRelations.has(r.id) ? "checked" : ""} />
        <span class="type-chip ${r.color}">${r.label}</span>
        <span class="og-filter__count">${r.count}</span>
      </label>`,
    )
    .join("");

  const bg =
    getComputedStyle(document.documentElement).getPropertyValue("--bg").trim() || "#faf8f5";

  const graph = ForceGraph3D({ controlType: "orbit" })(canvasHost) as unknown as GraphApi;
  graph
    .backgroundColor(bg)
    .showNavInfo(false)
    .warmupTicks(40)
    .cooldownTicks(120)
    .linkOpacity(0.35)
    .nodeThreeObjectExtend(false)
    .nodeThreeObject((node) => createNodeObject(node))
    .nodeLabel((node) => {
      if (isClusterNode(node)) {
        return `${node.title}\nClick to expand`;
      }
      return `${node.title}\n${node.typeLabel}`;
    })
    .linkColor((link) => hexFor(link.color))
    .linkWidth((link) => (link.isClusterEdge ? 1.6 : 0.8))
    .onNodeHover((node) => {
      if (!hoverEl) return;
      if (!node) {
        hoverEl.textContent = "Hover a node · drag to orbit · scroll to zoom";
        return;
      }
      hoverEl.textContent = isClusterNode(node)
        ? `${node.title} — click to expand`
        : `${node.title} (${node.typeLabel})`;
    })
    .onNodeClick((node, event) => {
      if (isClusterNode(node)) {
        expandedClusters.add(node.id);
        refresh();
        renderSelection(node);
        return;
      }
      renderSelection(node);
      if (event.detail === 2 || (event as MouseEvent).metaKey || (event as MouseEvent).ctrlKey) {
        window.location.href = node.href;
      }
    });

  function renderSelection(node: ViewNode | null) {
    if (!node) {
      selectionEl!.innerHTML = `<p class="muted">Select a node to inspect it.</p>`;
      return;
    }
    if (isClusterNode(node)) {
      const cluster = node as ClusterNode;
      selectionEl!.innerHTML = `
        <h3>${escapeHtml(cluster.title)}</h3>
        <p class="muted">Collapsed ${cluster.childIds.length} ${escapeHtml(cluster.clusterNeighborType)} nodes linked to this hub.</p>
        <button type="button" class="og-btn" data-expand-cluster="${escapeAttr(cluster.id)}">Expand cluster</button>
        <p style="margin-top:0.75rem;"><a href="${escapeAttr(cluster.href)}">Open hub entity →</a></p>
      `;
      selectionEl!.querySelector<HTMLButtonElement>("[data-expand-cluster]")?.addEventListener("click", () => {
        expandedClusters.add(cluster.id);
        refresh();
      });
      return;
    }
    const bits = [
      `<h3>${escapeHtml(node.title)}</h3>`,
      `<p><span class="type-chip ${escapeAttr(node.color)}">${escapeHtml(node.typeLabel)}</span></p>`,
      `<p class="muted">Degree ${node.degree}${node.format ? ` · ${escapeHtml(node.format)}` : ""}</p>`,
      `<p><a href="${escapeAttr(node.href)}">Open entity →</a></p>`,
    ];
    selectionEl!.innerHTML = bits.join("");
  }

  function refresh() {
    const view = applyGraphView(
      payload.nodes as GraphNode[],
      payload.edges as GraphEdge[],
      enabledTypes,
      enabledRelations,
      expandedClusters,
    );
    // ForceGraph expects `links` with source/target; mutate-safe copies
    const data = {
      nodes: view.nodes.map((n) => ({ ...n })),
      links: view.edges.map((e) => ({ ...e })),
    };
    graph.graphData(data);
    if (statsEl) {
      const clusters = view.nodes.filter(isClusterNode).length;
      statsEl.textContent = `${view.nodes.length} nodes · ${view.edges.length} links${clusters ? ` · ${clusters} collapsed` : ""}`;
    }
  }

  function resize() {
    const rect = canvasHost.getBoundingClientRect();
    graph.width(rect.width);
    graph.height(rect.height);
  }

  typeFilters.addEventListener("change", (ev) => {
    const input = (ev.target as HTMLElement).closest("input[data-type]") as HTMLInputElement | null;
    if (!input) return;
    if (input.checked) enabledTypes.add(input.dataset.type!);
    else enabledTypes.delete(input.dataset.type!);
    refresh();
  });

  relationFilters.addEventListener("change", (ev) => {
    const input = (ev.target as HTMLElement).closest("input[data-relation]") as HTMLInputElement | null;
    if (!input) return;
    if (input.checked) enabledRelations.add(input.dataset.relation!);
    else enabledRelations.delete(input.dataset.relation!);
    refresh();
  });

  expandAllBtn?.addEventListener("click", () => {
    // Expand every currently visible cluster id by running collapse-discovery once
    const view = applyGraphView(
      payload.nodes as GraphNode[],
      payload.edges as GraphEdge[],
      enabledTypes,
      enabledRelations,
      new Set(),
    );
    for (const n of view.nodes) {
      if (isClusterNode(n)) expandedClusters.add(n.id);
    }
    refresh();
  });

  collapseAllBtn?.addEventListener("click", () => {
    expandedClusters.clear();
    refresh();
  });

  togglePanelBtn?.addEventListener("click", () => {
    panel?.classList.toggle("og-panel--open");
    togglePanelBtn.setAttribute(
      "aria-expanded",
      panel?.classList.contains("og-panel--open") ? "true" : "false",
    );
  });

  window.addEventListener("resize", resize);
  resize();
  refresh();
  renderSelection(null);
  graph.cameraPosition({ x: 0, y: 0, z: 280 });
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttr(s: string): string {
  return escapeHtml(s).replace(/'/g, "&#39;");
}
