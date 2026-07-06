# Research Workflow

This document defines how entries move from stub to verified status in the Malice Mizer Print Archive.

## Search order

For each issue stub, search sources in this order:

1. **National Diet Library (NDL)** — confirm issue exists; record issue number, volume, page count
2. **CiNii** — cross-reference ISSN and bibliographic metadata
3. **WorldCat** — confirm library holdings for complete runs
4. **Yahoo! Auctions Japan / Mercari / Mandarake / Suruga-ya** — confirm physical issue; note listing URLs in `purchase_links`
5. **Internet Archive / Wayback Machine / scan communities** — flag scans with quality rating

## Verification rules

| Rule | Detail |
|------|--------|
| Issue numbers | Never guess. Leave `issue_number: null` until confirmed. |
| Promotion to `verified` | Requires issue number **and** page reference from **two independent sources** (e.g. NDL + auction TOC photo). |
| Promotion to `possible` | Single credible source (NDL bibliographic record, auction listing with cover visible). |
| `mention_only` | Secondary citation or fan community reference without primary source access. |
| Scans | Seller listing photos are **not** archival scans unless explicitly documented. |

## Changelog requirements

Every status change must add a changelog entry:

```yaml
changelog:
  - date: 2026-07-06
    action: verified
    source: ndl
    notes: "NDL bib ID 0001234567; issue no. 145 confirmed."
```

Valid `action` values: `created`, `updated`, `verified`, `status_change`, `research_note`

Valid `source` values: free text (`ndl`, `ciinii`, `worldcat`, `yahoo_auctions`, `mandarake`, `user_bibliography`, `catalog_mirror`, `vkgy`, etc.)

## Automated bibliography pipeline

Regenerate online catalogs and import issue stubs with:

```bash
make bibliography-expand
```

This runs, in order:

1. `patch_scan_sources_incomplete_mags.py` — add Malice Archive incomplete-mag scan URLs to `scan_sources_catalog.yaml`
2. `fetch_vkgy_magazines.py` — refresh per-magazine vk.gy indexes (`scripts/research/vkgy_*_malice_mizer.yaml`)
3. `parse_vkgy_artist_timeline.py` — parse vk.gy artist timeline mentions
4. `build_magazine_references_online.py` — merge into `magazine_references_online.yaml`
5. `import_online_catalog_stubs.py` — create missing `data/issues/` stubs from the merged catalog
6. `promote_vkgy_issues.py` — promote stubs when vk.gy + scan evidence meets rules below
7. `fix_imported_stubs.py` — normalize imported stub fields
8. `verify_ndl_placeholders.py` — NDL SRU lookup for `needs_verification` stubs (FOOL'S MATE, SHOXX, Arena37℃)
9. `build_db.py` — rebuild site JSON

**Do not** treat catalog output as verified without manual review. Promotion script rules mirror the table above:

| Target status | Promotion criteria |
|---------------|-------------------|
| `verified` | Issue number + page/cover evidence from two independent sources, **or** Cantavanda/local scans with identified pages |
| `possible` | vk.gy per-issue TOC + artist timeline agree on issue/date/number, or a single credible scan source without full page audit |

vk.gy HTML cache for timeline parsing: `scripts/research/.cache/vkgy/` (override with `VKGY_CACHE_DIR`).

## Local scan mirroring

Magazine pages listed in `scripts/research/scan_sources_catalog.yaml` can be mirrored locally:

```bash
.venv/bin/python scripts/research/fetch_images.py
```

- Writes to `images/scans/<publication>/<YYYY-MM>/` and updates issue YAML `scan.url`
- Skips external-only references: vk.gy cover crops, Reddit `i.redd.it`, blogspot thumbnails
- Sources: Cantavanda galleries, Internet Archive file metadata, Malice Archive incomplete mags (where permitted), scape.sc pamphlet pages
- After Cantavanda downloads, run `ingest_cantavanda_scans.py` to sync manifest + article fields

Direct image URL tracing (external links, not mirrored) remains in `image_urls_catalog.yaml` via `trace_image_urls.py`.

## FOOL'S MATE priority queue (Phase 1)

Work chronologically:

1. **1992-09** — live listing (confirm issue exists)
2. **1992-12** — possible live report
3. **1993** — all issues with any Malice Mizer mention
4. **1994** — Memoire era: cover, poster, review, interview, ad, release calendar
5. **1995** — transition period coverage

## NDL search helper

```bash
.venv/bin/python scripts/research/ndl_search.py \
  --publication "FOOL'S MATE" \
  --year 1992 \
  --month 9

# Save results to CSV for review
.venv/bin/python scripts/research/ndl_search.py \
  --publication "FOOL'S MATE" \
  --year 1993 \
  --csv exports/ndl-fools-mate-1993.csv
```

The script outputs candidates only. **Do not auto-import results into YAML** without manual verification.

## Research checklist per article

- [ ] Exact issue number
- [ ] Page numbers
- [ ] Photographer (if photo spread)
- [ ] Interviewer / writer
- [ ] Scan availability and quality
- [ ] Translation availability

## Commit convention

```
data: verify fools-mate-1992-09 issue number
data: add shoxx-1994-06 interview stub
data: note ndl candidate for fools-mate-1993-04
```
