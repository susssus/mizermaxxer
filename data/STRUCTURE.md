# Project structure

This repository is a unified **Malice Mizer Archive**. The layout below maps the suggested multi-domain structure to what exists in git.

## Directory map

| Suggested path | This project | Contents |
|----------------|--------------|----------|
| `data/magazines/` | [`data/magazines/README.md`](magazines/README.md) → [`data/issues/`](../issues/) | Print bibliography (one YAML per issue) |
| `data/albums/` | [`data/albums/`](albums/) | Albums, demos, live albums, VHS/DVD releases |
| `data/singles/` | [`data/singles/`](singles/) | Single releases |
| `data/songs/` | [`data/songs/`](songs/) | Song master list (referenced by albums/setlists) |
| `data/concerts/` | [`data/concerts/`](concerts/) | Gig list with setlists and performance links |
| `data/appearances/` | [`data/appearances/`](appearances/) | TV, radio, variety, and CM appearances (v2 `appearance_*`) |
| `data/organizations/` | [`data/organizations/`](organizations/) | Broadcasters, labels, publishers (`org_*`) |
| `data/videos/` | [`data/videos/`](videos/) | PVs, TV footage, standalone video links |
| `data/people/` | [`data/people/members.yaml`](people/members.yaml) | Band members and contributors |
| `data/pets/` | [`data/pets/`](pets/) | Pet entities (`pet_*`) — ontological subtype of person; site index at `/pets` |
| `data/venues/` | [`data/venues/`](venues/) | Live houses and event venues |
| `data/references/` | [`data/references/`](references/) | External bibliographic sources |
| `data/interviews/` | *planned* | Standalone interview transcripts (currently in magazine articles) |
| `data/books/` | *planned* | Book citations |
| `data/translations/` | [`data/translations/`](translations/) | English translation YAML keyed to issue articles (`article_id` + local `/translation/[id]` routes) |
| `images/covers/` | [`images/covers/`](../../images/covers/) | Release artwork |
| `images/flyers/` | [`images/flyers/`](../../images/flyers/) | Live flyers |
| `images/tickets/` | [`images/tickets/`](../../images/tickets/) | Ticket scans |
| `images/scans/` | [`images/scans/`](../../images/scans/) | Magazine page scans (normalized for git/site) |
| `images/scans-original/` | *(local only, gitignored)* | Full-resolution scan masters before normalization |
| `website/` | [`site/`](../../site/) | Astro static site (bibliography, timeline, discography, gigs, translations, browse, gallery) |
| `bibliography/` | [`exports/`](../exports/) + [`data/issues/`](../issues/) | Generated CSV/XLSX/PDF + YAML source |
| `docs/` | [`docs/`](../../docs/) | Research workflow and source lists |
| `scripts/` | [`scripts/`](../../scripts/) | Validation and build pipeline |

## Performance links

Performance URLs can appear in two places:

1. **`data/concerts/*.yaml`** — `performances[]` on a specific gig (YouTube bootlegs, TV broadcasts, etc.)
2. **`data/videos/*.yaml`** — standalone PVs or footage not tied to one concert date

Use `platform`, `quality`, and `notes` on each link. Replace search-hub URLs with canonical uploads as they are verified.

## Adding a new concert

```yaml
# data/concerts/YYYY-MM-DD-slug.yaml
id: 1998-12-26-tokyo-dome
date: 1998-12-26
date_precision: day
venue: tokyo-dome
event_name_en: Kindan no Tobira ~Shuuen no Butai~
type: oneman
setlist: [beast-of-blood, gekka-no-yasoukyoku]
members_present: [mana, kozi, yuki, kami, klaha]
verification_status: verified
performances:
  - url: https://www.youtube.com/watch?v=...
    platform: youtube
    quality: audience
    title: Tokyo Dome 1998 fan upload
    notes: Full show; verify uploader permissions separately.
changelog:
  - date: 2026-07-06
    action: created
    source: manual
    notes: Initial entry
```

Run `make build` after editing YAML.

## Licensing

- **Code** — MIT ([LICENSE](../../LICENSE))
- **YAML data and English translations** — CC BY-NC 4.0 ([LICENSE-CC-BY-NC-4.0.md](../../LICENSE-CC-BY-NC-4.0.md))
- **Mirrored scans** — third-party rights; see [docs/SOURCES.md](../../docs/SOURCES.md)

## Appearances (v2, research-only)

Files under [`data/appearances/`](appearances/) use the v2 entity schema (`appearance_*` IDs). They are validated by `make entities` but are **not** exported to `archive.json` until the v1→v2 migration completes. Use them for research and entity graph work via [`data/links.yaml`](links.yaml).
