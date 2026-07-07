# Malice Mizer Archive

A version-controlled digital humanities project for Malice Mizer:

- **Print bibliography** — magazine coverage (1992–2001)
- **Discography** — albums, singles, songs
- **Gig lists** — concerts with setlists and lineups
- **Performance links** — YouTube and other footage URLs

## Source of truth

Structured YAML under `data/` generates SQLite, CSV/XLSX/PDF exports, and a static website.

See [data/STRUCTURE.md](data/STRUCTURE.md) for how this maps to the suggested multi-folder archive layout.

## Quick start

```bash
make venv
make seed          # magazine stubs (first time)
make music-seed    # discography + gig stubs (first time)
make all
```

| Command | Description |
|---------|-------------|
| `make validate` | Validate all YAML against JSON Schema |
| `make build` | Build SQLite + site JSON |
| `make export` | Export CSV and XLSX |
| `make site` | Build Astro static site |
| `make pdf` | Generate print bibliography PDF |

## Site sections

| URL | Content |
|-----|---------|
| `/` | Magazine bibliography with filters |
| `/timeline` | Unified chronology (releases, gigs, magazine issues) |
| `/discography` | Albums and singles |
| `/gigs` | Concert list with performance links |
| `/appearances` | TV, radio, and variety appearances (entity graph) |
| `/members` | Member profiles |
| `/gallery` | Curated promo and portrait gallery |
| `/flyers` | Flyer catalog |
| `/videos` | PVs and standalone footage |
| `/translations` | English translations index |
| `/browse` | Entity graph explorer |
| `/attribution` | Image and scan provenance |
| `/legal` | Licenses, affiliation notice, and reuse terms |

## Licensing

Project source code is licensed under the [MIT License](LICENSE). Archive content
(bibliographic YAML, English translations, exported datasets) is licensed under
[CC BY-NC 4.0](LICENSE-CC-BY-NC-4.0.md). Third-party scans and magazine pages remain
subject to original rights holders — see [docs/LICENSE.md](docs/LICENSE.md),
[docs/SOURCES.md](docs/SOURCES.md), and the site [attribution page](https://mizermaxxer.org/attribution).

## Data entry

- **Magazines:** `data/issues/<publication>/`
- **Releases:** `data/albums/`, `data/singles/`, `data/songs/`
- **Live:** `data/concerts/`, `data/venues/`
- **Footage:** `performances[]` on concerts, or `data/videos/`
- **Images:** `images/covers/`, `images/flyers/`, etc. (link via `cover_image` fields)

Research rules: [docs/RESEARCH.md](docs/RESEARCH.md) · Sources: [docs/SOURCES.md](docs/SOURCES.md) · **Entity schema:** [docs/SCHEMA.md](docs/SCHEMA.md) · **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

## Entity graph (v2)

Relationships live in [`data/links.yaml`](data/links.yaml) plus derived fields (`appears_on`, `personnel`, setlists). Build the resolved index with:

```bash
make entities    # validate + build links_index.json
```

See [docs/SCHEMA.md](docs/SCHEMA.md) for ID conventions, relation vocabulary, and migration from v1.

`data/appearances/` is validated by `make entities` and summarized on the public `/appearances` index (full relationship data on entity pages).

## Research tools

```bash
.venv/bin/python scripts/research/ndl_search.py --publication "FOOL'S MATE" --year 1992
```
