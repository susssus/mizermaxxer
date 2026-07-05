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

Valid `source` values: free text (`ndl`, `ciinii`, `worldcat`, `yahoo_auctions`, `mandarake`, `user_bibliography`, etc.)

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
