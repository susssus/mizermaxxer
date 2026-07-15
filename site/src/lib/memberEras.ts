const BAND_ERAS = [
  { label: "Tetsu era", start: 1992, end: 1994 },
  { label: "Gackt era", start: 1995, end: 1999 },
  { label: "Klaha era", start: 2000, end: 2001 },
] as const;

type ActiveInput =
  | string
  | null
  | undefined
  | {
      start?: string | null;
      end?: string | null;
    };

function parseYear(value: string | null | undefined): number | null {
  if (!value) return null;
  const match = value.match(/^(\d{4})/);
  return match ? Number(match[1]) : null;
}

function parseActiveRange(active: ActiveInput): { start: number; end: number } | null {
  if (!active) return null;

  if (typeof active === "string") {
    const match = active.match(/^(\d{4})(?:-(\d{4}))?$/);
    if (!match) return null;
    const start = Number(match[1]);
    const end = match[2] ? Number(match[2]) : start;
    return { start, end };
  }

  const start = parseYear(active.start);
  if (start === null) return null;
  const end = parseYear(active.end) ?? start;
  return { start, end };
}

/** Return all vocalist-era labels a member overlapped with, oldest to newest. */
export function memberEraLabels(active: ActiveInput): string | null {
  const range = parseActiveRange(active);
  if (!range) return null;

  const labels = BAND_ERAS.filter(
    (era) => range.start <= era.end && range.end >= era.start
  ).map((era) => era.label);

  return labels.length > 0 ? labels.join(" · ") : null;
}
