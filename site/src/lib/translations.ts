/** Helpers for local translation YAML paths → site routes. */

export function translationSlug(url: string | null | undefined): string | null {
  if (!url) return null;
  if (url.startsWith("data/translations/") && url.endsWith(".yaml")) {
    return url.slice("data/translations/".length, -".yaml".length);
  }
  return null;
}

export function translationHref(url: string | null | undefined): string | null {
  const slug = translationSlug(url);
  if (slug) return `/translation/${slug}`;
  if (url?.startsWith("http://") || url?.startsWith("https://")) return url;
  return null;
}

export function scanHref(path: string | null | undefined): string | null {
  if (!path) return null;
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  return path.startsWith("/") ? path : `/${path}`;
}
