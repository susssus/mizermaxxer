import attribution from "../data/attribution.json";

export interface ImageAttribution {
  sourceName: string;
  sourceUrl?: string | null;
}

type AttributionRecord = {
  source_name?: string | null;
  source_url?: string | null;
  path?: string | null;
};

const byPath = (attribution.by_path ?? {}) as Record<string, AttributionRecord>;
const bySourceUrl = (attribution.by_source_url ?? {}) as Record<string, AttributionRecord>;

const SOURCE_HOME_PAGES: Array<{ match: RegExp; url: string }> = [
  { match: /cantavanda/i, url: "https://cantavanda.com/malice-mizer/" },
  { match: /malice[- ]?mizer\.info/i, url: "https://malice-mizer.info/" },
  { match: /malice meezer|malicemeezer/i, url: "https://malicemeezer.neocities.org/vintage" },
  { match: /cover art archive/i, url: "https://coverartarchive.org/" },
  { match: /discogs/i, url: "https://www.discogs.com/artist/231908-Malice-Mizer" },
  { match: /vk\.?gy/i, url: "https://vk.gy/artists/malice-mizer/" },
];

export function normalizeImagePath(src?: string | null): string | null {
  if (!src) return null;
  let path = src.split("#")[0].split("?")[0];
  if (path.startsWith("/")) path = path.slice(1);
  if (path.startsWith("images/")) return path;
  return null;
}

function homepageForSourceName(sourceName: string): string | null {
  for (const entry of SOURCE_HOME_PAGES) {
    if (entry.match.test(sourceName)) return entry.url;
  }
  return null;
}

function recordToAttribution(record: AttributionRecord | undefined): ImageAttribution | null {
  if (!record?.source_name) return null;
  return {
    sourceName: record.source_name,
    sourceUrl: record.source_url ?? homepageForSourceName(record.source_name),
  };
}

export function imageAttributionForPath(path: string): ImageAttribution | null {
  const normalized = normalizeImagePath(path) ?? path.replace(/^\//, "");
  return recordToAttribution(byPath[normalized]);
}

export function imageAttributionForSrc(
  src?: string | null,
  overrides?: { sourceName?: string | null; sourceUrl?: string | null },
): ImageAttribution | null {
  if (overrides?.sourceUrl) {
    return {
      sourceName: overrides.sourceName ?? "Source",
      sourceUrl: overrides.sourceUrl,
    };
  }

  const localPath = normalizeImagePath(src);
  if (localPath) {
    const fromManifest = imageAttributionForPath(localPath);
    if (fromManifest) return fromManifest;
  }

  if (src && (src.startsWith("http://") || src.startsWith("https://"))) {
    const direct = recordToAttribution(bySourceUrl[src]);
    if (direct) return direct;
    if (overrides?.sourceName) {
      return {
        sourceName: overrides.sourceName,
        sourceUrl: homepageForSourceName(overrides.sourceName) ?? src,
      };
    }
    return null;
  }

  if (overrides?.sourceName) {
    return {
      sourceName: overrides.sourceName,
      sourceUrl: homepageForSourceName(overrides.sourceName),
    };
  }

  return null;
}
