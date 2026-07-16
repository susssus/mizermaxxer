export const SITE_NAME = "Malice Mizer Research Archive";

export const SITE_URL = "https://mizermaxxer.org";

/** Short brand used in copy and WebSite alternateName — targets “Malice Mizer archive” queries. */
export const SITE_SHORT_NAME = "Malice Mizer Archive";

export const DEFAULT_DESCRIPTION =
  "Malice Mizer archive — visual kei magazine bibliography, discography, concert setlists, flyers, videos, and member profiles (1992–2001). Verified sources and scans.";

export const DEFAULT_KEYWORDS = [
  "Malice Mizer",
  "Malice Mizer archive",
  "Malice Mizer Research Archive",
  "マリスミゼール",
  "visual kei",
  "J-rock",
  "discography",
  "Merveilles",
  "Gackt",
  "Mana",
  "Közi",
  "Klaha",
  "concert setlists",
  "magazine scans",
  "flyers",
  "music archive",
].join(", ");

export const DEFAULT_OG_IMAGE = "/images/members/hero.webp";

export const DEFAULT_OG_IMAGE_ALT =
  "MALICE MIZER — promotional photograph from the research archive";

export function absoluteUrl(path: string, site = SITE_URL): string {
  return new URL(path, site).href;
}

export function pageTitle(pageTitle?: string): string {
  if (!pageTitle || pageTitle === SITE_NAME || pageTitle === SITE_SHORT_NAME) {
    return SITE_NAME;
  }
  if (pageTitle.includes(SITE_NAME)) return pageTitle;
  return `${pageTitle} — ${SITE_NAME}`;
}

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

/** schema.org BreadcrumbList for nav crumbs (absolute URLs). */
export function breadcrumbListJsonLd(
  items: BreadcrumbItem[],
  site = SITE_URL,
): Record<string, unknown> {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.label,
      ...(item.href
        ? { item: absoluteUrl(item.href, site) }
        : {}),
    })),
  };
}
