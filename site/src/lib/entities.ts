/** Map v1 catalog slugs to v2 entity IDs when present in links_index.json. */

import crosswalk from "../data/entity_crosswalk.json";
import linksIndex from "../data/links_index.json";

const entityIds = new Set(linksIndex.browse.map((row) => row.id));

export function entityHref(id: string | null | undefined): string | null {
  if (!id || !entityIds.has(id)) return null;
  return `/entity/${id}`;
}

function slugHref(mapping: Record<string, string>, slug: string): string | null {
  return entityHref(mapping[slug]);
}

export function personEntityHref(slug: string): string | null {
  return slugHref(crosswalk.people, slug);
}

export function songEntityHref(songSlug: string): string | null {
  return slugHref(crosswalk.songs, songSlug);
}

export function venueEntityHref(venueSlug: string): string | null {
  return slugHref(crosswalk.venues, venueSlug);
}

export function albumEntityHref(albumId: string): string | null {
  return slugHref(crosswalk.albums, albumId);
}

export function concertEntityHref(concertId: string): string | null {
  return slugHref(crosswalk.concerts, concertId);
}
