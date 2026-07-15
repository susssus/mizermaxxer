/** Career membership helpers for Mother Band timelines. */

import linksIndex from "../data/links_index.json";

export const MM_ORG_ID = "org_malice_mizer";
export const PRESENT_YEAR = 2026;

export type CareerPhase = "before" | "during" | "after";

export type ActiveRange = {
  start?: string | null;
  end?: string | null;
};

export type CareerMembership = {
  orgId: string;
  orgName: string;
  role?: string | null;
  note?: string | null;
  active: ActiveRange;
  startYear: number;
  endYear: number;
  openEnded: boolean;
  phase: CareerPhase;
  isMotherBand: boolean;
};

type LinkEntry = {
  entity_id: string;
  relation: string;
  direction?: string;
  role?: string | null;
  note?: string | null;
  active?: ActiveRange | null;
};

const titleById: Record<string, string> = Object.fromEntries(
  linksIndex.browse.map((row) => [row.id, row.title as string])
);

/** Parse YYYY or YYYY-MM into a fractional year for ordering. */
export function parseYearValue(value: string | null | undefined): number | null {
  if (!value) return null;
  const match = value.match(/^(\d{4})(?:-(\d{2}))?/);
  if (!match) return null;
  const year = Number(match[1]);
  const month = match[2] ? Number(match[2]) : 1;
  return year + (month - 1) / 12;
}

export function parseYear(value: string | null | undefined): number | null {
  const frac = parseYearValue(value);
  return frac === null ? null : Math.floor(frac);
}

export function formatActiveRange(active: ActiveRange, openEnded: boolean): string {
  const start = active.start ?? "?";
  if (openEnded || active.end == null) return `${start}–present`;
  return `${start}–${active.end}`;
}

function mmTenureForPerson(personId: string): { start: number; end: number } | null {
  const outgoing = (linksIndex.linked_entities[personId]?.outgoing ?? []) as LinkEntry[];
  const mm = outgoing.find(
    (link) => link.relation === "member_of" && link.entity_id === MM_ORG_ID
  );
  if (mm?.active) {
    const start = parseYearValue(mm.active.start);
    const end = parseYearValue(mm.active.end) ?? PRESENT_YEAR;
    if (start !== null) return { start, end };
  }

  const person = linksIndex.entities_by_id[personId] as
    | { active?: ActiveRange | null }
    | undefined;
  if (person?.active?.start) {
    const start = parseYearValue(person.active.start);
    const end = parseYearValue(person.active.end) ?? PRESENT_YEAR;
    if (start !== null) return { start, end };
  }
  return null;
}

function classifyPhase(
  orgId: string,
  start: number,
  end: number,
  mm: { start: number; end: number } | null
): CareerPhase {
  if (orgId === MM_ORG_ID) return "during";
  if (!mm) {
    return end < 1992 ? "before" : start > 2001 ? "after" : "during";
  }
  // Overlap with the member's MM tenure → during (includes concurrent support projects)
  if (start <= mm.end && end >= mm.start) return "during";
  const mid = (start + end) / 2;
  if (mid < mm.start) return "before";
  return "after";
}

export function membershipsForPerson(personId: string): CareerMembership[] {
  const outgoing = (linksIndex.linked_entities[personId]?.outgoing ?? []) as LinkEntry[];
  const mm = mmTenureForPerson(personId);

  const items: CareerMembership[] = [];
  for (const link of outgoing) {
    if (link.relation !== "member_of") continue;
    const active = link.active ?? {};
    const startFrac = parseYearValue(active.start);
    if (startFrac === null) continue;
    const openEnded = active.end == null || active.end === "";
    const endFrac = openEnded ? PRESENT_YEAR : (parseYearValue(active.end) ?? startFrac);
    const startYear = Math.floor(startFrac);
    const endYear = Math.floor(endFrac);
    const orgId = link.entity_id;
    items.push({
      orgId,
      orgName: titleById[orgId] ?? orgId,
      role: link.role,
      note: link.note,
      active,
      startYear,
      endYear,
      openEnded,
      phase: classifyPhase(orgId, startFrac, endFrac, mm),
      isMotherBand: orgId === MM_ORG_ID,
    });
  }

  return items.sort(
    (a, b) =>
      a.startYear - b.startYear ||
      a.endYear - b.endYear ||
      a.orgName.localeCompare(b.orgName)
  );
}

export type TimelineBounds = {
  minYear: number;
  maxYear: number;
};

export function boundsForMemberships(
  memberships: CareerMembership[],
  pad = 1
): TimelineBounds {
  if (memberships.length === 0) {
    return { minYear: 1990, maxYear: PRESENT_YEAR };
  }
  let minYear = Math.min(...memberships.map((m) => m.startYear));
  let maxYear = Math.max(...memberships.map((m) => m.endYear));
  minYear = Math.max(1980, minYear - pad);
  maxYear = Math.min(PRESENT_YEAR + 1, maxYear + pad);
  if (maxYear <= minYear) maxYear = minYear + 1;
  return { minYear, maxYear };
}

export type LayoutBar = CareerMembership & {
  lane: number;
  x: number;
  width: number;
};

/** Pack overlapping spans into lanes within one person's timeline. */
export function layoutMembershipBars(
  memberships: CareerMembership[],
  bounds: TimelineBounds,
  trackWidth: number
): { bars: LayoutBar[]; laneCount: number } {
  const span = bounds.maxYear - bounds.minYear || 1;
  const laneEnds: number[] = [];
  const bars: LayoutBar[] = [];

  for (const m of memberships) {
    let lane = 0;
    while (lane < laneEnds.length && laneEnds[lane]! > m.startYear) {
      lane += 1;
    }
    if (lane === laneEnds.length) laneEnds.push(m.endYear);
    else laneEnds[lane] = m.endYear;

    const x = ((m.startYear - bounds.minYear) / span) * trackWidth;
    const rawWidth = ((m.endYear - m.startYear) / span) * trackWidth;
    const width = Math.max(rawWidth, 4);
    bars.push({ ...m, lane, x, width });
  }

  return { bars, laneCount: Math.max(1, laneEnds.length) };
}

export const MEMBER_CAREER_ORDER = [
  "person_tetsu",
  "person_mana",
  "person_kozi",
  "person_yuki",
  "person_gaz",
  "person_kami",
  "person_gackt",
  "person_klaha",
] as const;

export function memberDisplayName(personId: string): string {
  return titleById[personId] ?? personId.replace(/^person_/, "");
}

export function phaseLabel(phase: CareerPhase): string {
  switch (phase) {
    case "before":
      return "Before Malice Mizer";
    case "during":
      return "During Malice Mizer";
    case "after":
      return "After Malice Mizer";
  }
}

export const MM_BAND_YEARS = { start: 1992, end: 2001 } as const;
