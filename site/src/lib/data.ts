export interface Publication {
  slug: string;
  name_ja: string;
  name_en: string;
  publisher: string | null;
  issn: string | null;
  years_active_start: number | null;
  years_active_end: number | null;
  priority: number;
  status: string;
  notes?: string;
}

export interface Article {
  id: string;
  issue_id: string;
  title_ja: string | null;
  title_en: string | null;
  type: string;
  pages: string | null;
  members: string[];
  photographer: string | null;
  writer: string | null;
  cover: boolean;
  poster: boolean;
  foldout: boolean;
  scan_available: boolean;
  scan_quality: string | null;
  scan_url: string | null;
  translation_available: boolean;
  translation_url: string | null;
  purchase_links: Array<{ url: string; platform?: string | null; notes?: string }>;
  notes: string;
}

export interface Issue {
  id: string;
  publication: string;
  issue_number: string | null;
  volume: string | null;
  publication_date: string;
  date_precision: string;
  verification_status: string;
  source_notes: string;
  research_targets: string[];
  changelog: Array<{
    date: string;
    action: string;
    source: string;
    notes: string;
  }>;
  articles: Article[];
}

export interface ArchiveData {
  generated_at: string;
  publications: Publication[];
  issues: Issue[];
  stats: {
    issue_count: number;
    article_count: number;
    verified_count: number;
    scan_count: number;
  };
}

export function loadArchive(): ArchiveData {
  return JSON.parse(JSON.stringify(require("../data/archive.json"))) as ArchiveData;
}

export function publicationMap(data: ArchiveData): Map<string, Publication> {
  return new Map(data.publications.map((pub) => [pub.slug, pub]));
}

export function flattenRows(data: ArchiveData) {
  const pubs = publicationMap(data);
  return data.issues.flatMap((issue) =>
    issue.articles.map((article) => ({
      issue,
      article,
      publication: pubs.get(issue.publication),
    }))
  );
}
