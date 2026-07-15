interface ProfileLike {
  id: string;
  portrait_image?: string | null;
}

interface MemberLike {
  slug: string;
  portrait_image?: string | null;
}

interface ArchiveLike {
  people_profiles?: ProfileLike[];
  people?: {
    members?: MemberLike[];
  };
}

/** Prefer the full profile portrait so member cards match /members/[slug] hero images. */
export function memberPortraitForSlug(slug: string, archive: ArchiveLike): string | null {
  const profile = archive.people_profiles?.find(
    (entry) => entry.id === `person_${slug}` || entry.id === slug,
  );
  if (profile?.portrait_image) return profile.portrait_image;

  const member = archive.people?.members?.find((entry) => entry.slug === slug);
  return member?.portrait_image ?? null;
}
