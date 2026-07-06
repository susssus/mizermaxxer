# Contributing to Mizermaxxer

Thank you for helping improve this research archive. This project combines structured YAML data, validation scripts, and a static Astro site.

## Before you start

1. Read [docs/RESEARCH.md](docs/RESEARCH.md) for sourcing rules.
2. Read [docs/SCHEMA.md](docs/SCHEMA.md) for ID conventions and the v1/v2 entity model.
3. Run `make venv` once, then use the Makefile targets below.

## Data entry checklist

- [ ] Source recorded in issue/article `changelog` or `source_notes`
- [ ] `verification_status` reflects confidence (`verified`, `possible`, `needs_verification`, …)
- [ ] Foreign keys resolve (`song`, `venue`, `publication` slugs exist)
- [ ] Scans linked via `scan.url` when available locally
- [ ] Local translations use `data/translations/<id>.yaml` and matching `article.translation.url`
- [ ] Translation YAML includes `review_status`, `license: CC-BY-NC-4.0`, and `license_notes`

## Commands

```bash
make validate   # JSON Schema + cross-reference checks
make build      # SQLite + site JSON exports
make site       # Astro build
make all        # validate, build, export, pdf, site
```

## Pull requests

- Keep changes focused (data, site, or scripts — not unrelated refactors).
- Run `make validate && make build` before opening a PR.
- For translation edits, note whether the piece was reviewed against the source scan.
- Do not commit secrets, credentials, or full-res scan masters from `images/scans-original/`.

## Translation review workflow

See [docs/EDITORIAL.md](docs/EDITORIAL.md) for promoting translations from `needs_review` to `reviewed`.

## Licensing

- **Code** — [MIT License](LICENSE)
- **Archive content** (YAML data, English translations) — [CC BY-NC 4.0](LICENSE-CC-BY-NC-4.0.md)
- **Third-party scans** — not re-licensed by this project; see [docs/SOURCES.md](docs/SOURCES.md) and the site attribution page.

See [docs/LICENSE.md](docs/LICENSE.md) for the full dual-license policy.
