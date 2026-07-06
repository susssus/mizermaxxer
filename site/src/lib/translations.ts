/** Helpers for local translation YAML paths → site routes. */

import archive from "../data/archive.json";
import translationsData from "../data/translations.json";

export type TranslationReviewStatus = "needs_review" | "reviewed";

export interface IssueRef {
  issueId: string;
  publication: string;
  publicationDate: string;
}

const issueByArticleId = new Map<string, IssueRef>();
for (const issue of archive.issues) {
  for (const article of issue.articles) {
    issueByArticleId.set(article.id, {
      issueId: issue.id,
      publication: issue.publication,
      publicationDate: issue.publication_date,
    });
  }
}

export function issueForArticle(articleId: string | null | undefined): IssueRef | null {
  if (!articleId) return null;
  return issueByArticleId.get(articleId) ?? null;
}

export function publicationName(slug: string): string {
  return archive.publications.find((pub) => pub.slug === slug)?.name_en ?? slug;
}

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

export function translationReviewStatus(
  url: string | null | undefined,
): TranslationReviewStatus | null {
  const slug = translationSlug(url);
  if (!slug) return null;
  const doc = translationsData.by_id[slug as keyof typeof translationsData.by_id];
  const status = doc?.review_status;
  if (status === "needs_review" || status === "reviewed") return status;
  return null;
}

export function translationReviewLabel(status: TranslationReviewStatus | null): string | null {
  if (status === "needs_review") return "unreviewed";
  if (status === "reviewed") return "reviewed";
  return null;
}

export function scanHref(path: string | null | undefined): string | null {
  if (!path) return null;
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  return path.startsWith("/") ? path : `/${path}`;
}
