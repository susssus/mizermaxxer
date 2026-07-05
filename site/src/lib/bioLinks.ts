/** Auto-link band names, releases, and related terms in person biography text. */

type BioLinkEntry = {
  /** Literal phrase as it appears in bio copy (longest matches first). */
  label: string;
  href: string;
  external?: boolean;
};

const BIO_LINKS: BioLinkEntry[] = [
  // Malice Mizer releases (this archive)
  { label: "Gekka no Yasoukyoku", href: "/discography/gekka-no-yasoukyoku-single" },
  { label: "Bara no Seidou", href: "/discography/bara-no-seidou" },
  { label: "Deep Sanctuary", href: "/discography/deep-sanctuary-vi" },
  { label: "Malice Mizer", href: "http://malice-mizer.co.jp/", external: true },
  { label: "Shinwa EP", href: "/discography/shinwa" },
  { label: "Merveilles", href: "/discography/merveilles" },
  { label: "Illuminati", href: "/discography/illuminati-single" },
  { label: "Memoire", href: "/discography/memoire" },
  { label: "Syunikiss", href: "/discography/merveilles" },

  // Labels & related projects
  { label: "Moi-même-Moitié", href: "https://www.manam-ss.com/", external: true },
  { label: "Moi dix Mois", href: "https://www.moixdismois.com/", external: true },
  { label: "Afro Skull Records", href: "https://www.afroskull.com/", external: true },
  { label: "Midi:Nette", href: "http://www.midi-nette.com/", external: true },
  { label: "Eve of Destiny", href: "https://kozi-web.com/", external: true },

  // Tetsu post-MM projects (Afro Skull umbrella)
  { label: "The Black Comet Club Band", href: "https://www.afroskull.com/", external: true },
  { label: "The JuneJulyAugust", href: "https://www.afroskull.com/", external: true },
  { label: "Disco Volante", href: "https://www.afroskull.com/", external: true },
  { label: "Mega8Ball", href: "https://www.afroskull.com/", external: true },

  // Other bands & genres with stable references
  { label: "Pride of Mind", href: "https://en.wikipedia.org/wiki/Pride_of_Mind", external: true },
  { label: "Cains:Feel", href: "https://en.wikipedia.org/wiki/Gackt", external: true },
  { label: "visual kei", href: "https://en.wikipedia.org/wiki/Visual_kei", external: true },
  { label: "Girl'e", href: "https://en.wikipedia.org/wiki/Girl_(Japanese_band)", external: true },
  { label: "Girl", href: "https://en.wikipedia.org/wiki/Girl_(Japanese_band)", external: true },
  { label: "Zigzo", href: "https://en.wikipedia.org/wiki/Zigzo", external: true },
  { label: "Dalle", href: "https://kozi-web.com/", external: true },
  { label: "XA-VAT", href: "https://kozi-web.com/", external: true },
  { label: "ZIZ", href: "https://kozi-web.com/", external: true },
  { label: "nil", href: "https://nil-web.net/", external: true },
  { label: "Közi", href: "https://kozi-web.com/", external: true },
];

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeRegex(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function linkPattern(label: string): RegExp {
  const core = escapeRegex(label);
  if (label === "Malice Mizer") {
    return new RegExp(`${core}(?='s\\b)?`, "g");
  }
  if (/^[A-Za-z0-9:.'~\-]+$/.test(label)) {
    return new RegExp(`(?<![\\w/"=])${core}(?![\\w/"=])`, "g");
  }
  return new RegExp(core, "g");
}

const SORTED_LINKS = [...BIO_LINKS].sort((a, b) => b.label.length - a.label.length);

export function linkBioText(text: string): string {
  let html = escapeHtml(text.trim());

  for (const { label, href, external } of SORTED_LINKS) {
    const pattern = linkPattern(label);
    html = html.replace(pattern, (match, offset) => {
      const before = html.slice(0, offset);
      if (before.lastIndexOf("<a ") > before.lastIndexOf("</a>")) {
        return match;
      }
      const attrs = external ? ' target="_blank" rel="noopener noreferrer"' : "";
      return `<a href="${href}"${attrs}>${match}</a>`;
    });
  }

  return html;
}
