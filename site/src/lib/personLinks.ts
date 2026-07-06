export type PersonLinkPlatform =
  | "website"
  | "youtube"
  | "twitter"
  | "instagram"
  | "facebook"
  | "tiktok"
  | "threads"
  | "other";

export interface PersonLink {
  url: string;
  platform: PersonLinkPlatform;
  label?: string;
}

const PLATFORM_LABELS: Record<PersonLinkPlatform, string> = {
  website: "Website",
  youtube: "YouTube",
  twitter: "X",
  instagram: "Instagram",
  facebook: "Facebook",
  tiktok: "TikTok",
  threads: "Threads",
  other: "Link",
};

export function personLinkLabel(link: PersonLink): string {
  return link.label?.trim() || PLATFORM_LABELS[link.platform] || "Link";
}
