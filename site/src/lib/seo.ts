export const SITE_NAME = "Malice Mizer Research Archive";

export const SITE_URL = "https://mizermaxxer.vercel.app";

export const DEFAULT_DESCRIPTION =
  "Research archive for Malice Mizer — visual kei magazine bibliography, discography, concert setlists, flyers, videos, and member profiles (1992–2001). Verified sources and scans.";

export const DEFAULT_KEYWORDS = [
  "Malice Mizer",
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
  if (!pageTitle || pageTitle === SITE_NAME) return SITE_NAME;
  if (pageTitle.includes(SITE_NAME)) return pageTitle;
  return `${pageTitle} — ${SITE_NAME}`;
}
