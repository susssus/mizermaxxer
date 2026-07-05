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
| `/discography` | Albums and singles |
| `/gigs` | Concert list with performance links |
| `/videos` | PVs and standalone footage |

## Data entry

- **Magazines:** `data/issues/<publication>/`
- **Releases:** `data/albums/`, `data/singles/`, `data/songs/`
- **Live:** `data/concerts/`, `data/venues/`
- **Footage:** `performances[]` on concerts, or `data/videos/`
- **Images:** `images/covers/`, `images/flyers/`, etc. (link via `cover_image` fields)

Research rules: [docs/RESEARCH.md](docs/RESEARCH.md) · Sources: [docs/SOURCES.md](docs/SOURCES.md) · **Entity schema:** [docs/SCHEMA.md](docs/SCHEMA.md)

## Entity graph (v2)

Relationships live in [`data/links.yaml`](data/links.yaml) plus derived fields (`appears_on`, `personnel`, setlists). Build the resolved index with:

```bash
make entities    # validate + build links_index.json
```

See [docs/SCHEMA.md](docs/SCHEMA.md) for ID conventions, relation vocabulary, and migration from v1.

## Research tools

```bash
.venv/bin/python scripts/research/ndl_search.py --publication "FOOL'S MATE" --year 1992
```
