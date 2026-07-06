# Archive Sources

Systematic sources for locating Malice Mizer print coverage.

## Music discography

| Source | URL | Use |
|--------|-----|-----|
| Discogs | https://www.discogs.com/artist/231908-Malice-Mizer | Official release dates, catalog numbers, tracklists, cover art |
| Discogs API | https://www.discogs.com/developers | Used by `scripts/research/sync_discogs.py` (unauthenticated, rate-limited) |

Run `make discogs-sync` to refresh album/single metadata and download covers to `images/covers/`.

## Libraries

| Source | URL | Notes |
|--------|-----|-------|
| National Diet Library | https://ndlsearch.ndl.go.jp/ | Primary bibliographic authority for Japanese magazines |
| NDL SRU API | https://ndlsearch.ndl.go.jp/en/help/api | Used by `scripts/research/ndl_search.py` |
| CiNii Research | https://cir.nii.ac.jp/ | Academic index; ISSN cross-reference |
| WorldCat | https://www.worldcat.org/ | International library holdings |

### NDL search templates

```
title exact "FOOL'S MATE" AND from=1992-01-01 AND until=1992-12-31
title exact "SHOXX" AND from=1993-01-01 AND until=1993-12-31
title exact "Arena37" AND from=1992-01-01 AND until=1992-12-31
```

## Auction and retail archives

| Source | URL | Use |
|--------|-----|-----|
| Yahoo! Auctions Japan | https://auctions.yahoo.co.jp/ | Issue existence, cover verification |
| Mercari | https://www.mercari.com/jp/ | Secondary market listings |
| Mandarake | https://order.mandarake.co.jp/ | Vintage magazine dealer |
| Suruga-ya | https://www.suruga-ya.jp/ | Used media retailer |

**Note:** Listing URLs go in `purchase_links`, not `scan.url`, unless the listing contains archival-quality scans with documented permission.

## Scan communities

| Source | URL | Notes |
|--------|-----|-------|
| Internet Archive | https://archive.org/search?query=malice+mizer | ~167 items (July 2026); see catalog below |
| Wayback Machine | https://web.archive.org/ | Defunct fan sites |
| Reddit r/visualkei | https://www.reddit.com/r/visualkei/ | Scan provenance threads; catalog in `scripts/research/reddit_scan_sources.yaml` |
| Tumblr | https://www.tumblr.com/search/visual%20kei%20scans | Fan scan blogs (verify provenance) |
| LiveJournal archives | https://www.livejournal.com/ | Historical VK communities |

## Internet Archive (MALICE MIZER)

**Search:** https://archive.org/search?query=malice+mizer  
**API:** `https://archive.org/advancedsearch.php?q=malice+mizer&output=json`  
**Curated catalog:** `scripts/research/internet_archive_catalog.yaml`  
**Reference stub:** `data/references/internet-archive-malicemizer.yaml`

Surveyed July 2026 — **167 total hits**. No dedicated standalone live-flyer uploads; closest paraphernalia are tour pamphlets, photobooks (Retour includes early flyers), and sticker scans.

### Print, photobooks, paraphernalia

| Identifier | Type | Title / notes | Linked in project |
|------------|------|---------------|-------------------|
| [retour-107](https://archive.org/details/retour-107) | photobook | Retour 1992–1998 (FOOL'S MATE); early lives, flyers | `data/references/internet-archive-retour-photobook.yaml` |
| [2012-07-11-01-33-19-01](https://archive.org/details/2012-07-11-01-33-19-01) | pamphlet | Sans Retour Voyage tour pamphlet (1996) | `data/issues/tour-pamphlets/sans-retour-voyage-1996.yaml` |
| [supervisualbook-malicemizer](https://archive.org/details/supervisualbook-malicemizer) | magazine | Super Visual Book: Le ciel (16 pages) | `data/references/internet-archive-super-visual-le-ciel.yaml` |
| [arena194-ss-2](https://archive.org/details/arena194-ss-2) | magazine | Arena37℃ Nov 1998 (incomplete, MM cover) | `data/issues/arena37/1998-11.yaml` |
| [arena-37-c-oct-97-01](https://archive.org/details/arena-37-c-oct-97-01) | magazine | Arena37℃ Oct 1997 (MM-only extract) | `data/issues/arena37/1997-10.yaml` |
| [fools-mate-207-january-1999-13](https://archive.org/details/fools-mate-207-january-1999-13) | magazine | FOOL'S MATE #207 Jan 1999 (MM & Luna Sea) | `data/issues/fools-mate/1999-01.yaml` |
| [marveilles-malice-mizer](https://archive.org/details/marveilles-malice-mizer) | photobook | Merveilles à Deux Dimensions | catalog only |
| [lrb-20](https://archive.org/details/lrb-20) | photobook | Livre Rose Blanche | catalog only |
| [photobook-malice-mizer-1998-070-071](https://archive.org/details/photobook-malice-mizer-1998-070-071) | book | 耽美実験革命 mook | catalog only |
| [les-mizerables-de-malice-mizer-14](https://archive.org/details/les-mizerables-de-malice-mizer-14) | book | Les Mizerables vol. 2 | catalog only |
| [sticker-sheet-1](https://archive.org/details/sticker-sheet-1) | paraphernalia | Sticker sheet (possibly unofficial) | catalog only |
| [mm-voyage-003](https://archive.org/details/mm-voyage-003) | release art | Voyage 1st press slipcase/booklet | catalog only |
| [MALICEMIZERSaikaiNoChiToBara](https://archive.org/details/MALICEMIZERSaikaiNoChiToBara) | release art | Saikai single materials | catalog only |

### Video highlights (not mirrored; cite IA URL)

| Identifier | Notes |
|------------|-------|
| [malice-mizer-merveilles-lespace-full-live](https://archive.org/details/malice-mizer-merveilles-lespace-full-live) | *merveilles l'espace* full concert film |
| [malice-mizer-cher-de-memoire-ii-final-tetsu-last-live-at-meguro-rock-may-27.12.1994](https://archive.org/details/malice-mizer-cher-de-memoire-ii-final-tetsu-last-live-at-meguro-rock-may-27.12.1994) | Tetsu last live (1994-12-27) |
| [nhk-pop-jam-le-ciel-02.10.98](https://archive.org/details/nhk-pop-jam-le-ciel-02.10.98) | POPJAM Le ciel live |
| [hot-wave-bel-air-part-1](https://archive.org/details/hot-wave-bel-air-part-1) | Hot Wave Bel Air segment |

See `scripts/research/internet_archive_catalog.yaml` for the full curated list (**72 items** catalogued; **167** total search hits on archive.org) including CD booklet scans and adjacent uploads.

## Scan sources (linked in project)

**Master catalog:** `scripts/research/scan_sources_catalog.yaml` (**47 items**, July 2026)

| Source id | Items | Notes |
|-----------|-------|-------|
| `malice-archive-incomplete-mags` | 23 | Google Drive folders; link externally — do not mirror |
| `internet-archive` | 12 | Community magazine/mook uploads |
| `cantavanda-magazine-appearances` | 5 | MM page clippings from print mags |
| `cantavanda-fan-club-mags` | 5 | ma chérie fan club zines |
| `malice-archive-neocities` | 1 | SHOXX Vol. 61 partial (file.garden) |
| `scape-cher-de-memoire` | 1 | 1994 tour pamphlet pages |

**Direct image URLs:** `scripts/research/image_urls_catalog.yaml` — **932 traced images** across **45 catalog entries** (July 2026). Regenerate with:

```bash
.venv/bin/python scripts/research/trace_image_urls.py --patch-catalogs
# optional: also trace vk.gy FOOL'S MATE cover scans (~2 min)
.venv/bin/python scripts/research/trace_image_urls.py --vkgy --patch-catalogs
```

Sources traced: Cantavanda gallery full-size hrefs, scape.sc pamphlet pages (`cherdememoireNN.jpg`), Internet Archive file metadata, Reddit gallery posts (`i.redd.it`), vk.gy cover art (with `--vkgy`). Per-item `image_urls` arrays are also written into `scan_sources_catalog.yaml`.

**Local mirrors:** `fetch_images.py` downloads allowed scan pages from `scan_sources_catalog.yaml` into `images/scans/` (~200 pages as of July 2026). Malice Archive incomplete-mag Drive links are catalogued for external reference only — do not mirror without permission.

| Issue | Pages | Scan gallery |
|-------|-------|--------------|
| FOOL'S MATE No. 189 (Jul 1997) | 3 | [gallery](https://cantavanda.com/malice-mizer/scans/magazine-appearances/gallery/fools-mate-no-189-july-1997/) → `data/issues/fools-mate/1997-07.yaml` |
| POP BEAT (Aug 1997) | 2 | [gallery](https://cantavanda.com/malice-mizer/scans/magazine-appearances/gallery/pop-beat-august-1997/) → `data/issues/pop-beat/1997-08.yaml` |
| Vicious (Oct 1997) | 3 | [gallery](https://cantavanda.com/malice-mizer/scans/magazine-appearances/gallery/vicious-october-1997/) → `data/issues/vicious/1997-10.yaml` |
| SHOXX (May 1998) | 13 | [gallery](https://cantavanda.com/malice-mizer/scans/magazine-appearances/gallery/shoxx-may-1998/) → `data/issues/shoxx/1998-05.yaml` |
| POP BEAT (Jun 1998) | 5 | [gallery](https://cantavanda.com/malice-mizer/scans/magazine-appearances/gallery/pop-beat-june-1998/) → `data/issues/pop-beat/1998-06.yaml` |

Index: [Cantavanda magazine appearances](https://cantavanda.com/malice-mizer/scans/magazine-appearances/)

### Cantavanda — ma chérie fan club zines

| Issue | Pages | Scan gallery |
|-------|-------|--------------|
| Vol. 1 (Autumn 1997) | 24 | [gallery](https://cantavanda.com/malice-mizer/scans/fan-club-magazines/gallery/ma-cherie-fan-club-magazine-vol-1-autumn-1997/) |
| Vol. 2&3 (Winter 1997) | 32 | [gallery](https://cantavanda.com/malice-mizer/scans/fan-club-magazines/gallery/malice-mizer-scans-fan-club-magazines-ma-cherie-vol-23-winter-1997/) |
| Vol. 4 (Spring 1998) | 24 | [gallery](https://cantavanda.com/malice-mizer/scans/fan-club-magazines/gallery/ma-cherie-fan-club-magazine-vol-4-spring-1998/) |
| Vol. 5 (Summer 1998) | 24 | [gallery](https://cantavanda.com/malice-mizer/scans/fan-club-magazines/gallery/ma-cherie-vol-5-summer-1998/) |
| Vol. 6–7 (Autumn 1998) | 40 | [gallery](https://cantavanda.com/malice-mizer/scans/fan-club-magazines/gallery/ma-cherie-vol-6-7-autumn-1998/) |

YAML: `data/issues/fan-club/*.yaml`

### Tour pamphlets & translations (scape.sc)

| Item | Scan | Translation |
|------|------|-------------|
| Cher de memoire (1994) | [scape.sc pamphlet](http://www.scape.sc/pamphlets/cherdememoire/) | [English](https://www.scape.sc/translations/mm-cherdememoire-sep94.php) |
| Sans Retour Voyage (1996) | [Internet Archive](https://archive.org/details/2012-07-11-01-33-19-01) | — |

Additional English interview translations (text only): [scape.sc index](http://scape.sc/translations/mm-translations.php) → `data/references/translation-*.yaml`

### Partial / not fully scanned (July 2026)

- **SHOXX Vol. 61** (Mar 1998) — **40 MM pages live** on [The Malice Archive](https://malice-archive.neocities.org/Gackt%20Era/Shoxx/main.html#vol61) (file.garden JPEGs; Anna scan, cover by Morgianasama). Joint La'cryma Christi + MM cover; 38pp MM feature per [MIsaO Lab](https://misaolab.hateblo.jp/entry/20000302/1356327963). **Not** the full 84-page issue — Eternal Silence RAR re-upload still **not found** (`scripts/research/shoxx_061_scan_hunt.yaml`). Also: [vk.gy cover](https://vk.gy/images/60280-cover.jpg), [Reddit repost crops](https://www.reddit.com/r/visualkei/comments/1ibrtct/where_are_these_scans_from/). → `ref_shoxx_061`, `scan_sources_catalog.yaml#shoxx-vol-61-partial`, `image_urls_catalog.yaml#shoxx-1998-03`

### Not found (July 2026)
- SHOXX Dec 1992 first interview — [English text](http://scape.sc/translations/mm-shoxx-dec92.php) only → `data/issues/shoxx/1992-12.yaml`
- Dedicated live-flyer zine scans on Internet Archive — none; see Retour photobook for embedded flyers

## Online magazine bibliography (comprehensive)

**Merged catalog:** `scripts/research/magazine_references_online.yaml` (**277 entries**, July 2026)  
**Regenerate:** `make bibliography-expand` (full pipeline) or `.venv/bin/python scripts/research/build_magazine_references_online.py` (catalog only)

| Source | URL | What it provides |
|--------|-----|------------------|
| vkgy / jrock.gy | https://www.jrock.gy/artists/malice-mizer/ | Timeline with ~157 magazine mentions |
| vkgy — FOOL'S MATE index | https://vk.gy/magazines/fools-mate/ | 39 MM issues (vol.154–242) with per-issue TOC → `scripts/research/vkgy_fools_mate_malice_mizer.yaml` |
| vkgy — per-magazine indexes | https://vk.gy/magazines/ | 13 publication indexes (`vkgy_*_malice_mizer.yaml`): SHOXX, Cure, GiGS, B-PASS, Arena37℃, Vicious, PATi PATi, M GAZETTE, J-Rock Magazine, Newsmaker, Ongaku to Hito, uv |
| The Malice Archive | https://malice-archive.neocities.org/list | Fan list: FOOL'S MATE vol.133–242, Arena37℃ 1997–2000, B-PASS, CD SKiT!, Artist Fan, Band Yarouze, etc. |
| MIsaO Lab — FOOL'S MATE | https://misaolab.hateblo.jp/entry/20000301/1356327963 | Detailed JP coverage notes vol.151–236 (pages, interviews, live reports) |
| MIsaO Lab — SHOXX | https://misaolab.hateblo.jp/entry/20000302/1356327963 | Detailed JP coverage notes vol.13–120 (covers vol.61, 67, 83, 88, 92, 95, 106…) |
| malice-mizer.info — ma chérie | https://malice-mizer.info/ma-cherie-magazine | Fan club zine index Vol. 1–21 (1997–2001) |
| scape.sc translations | http://scape.sc/translations/mm-translations.php | Names source magazines for translated interviews |
| Internet Archive | https://archive.org/search?query=malice+mizer | Partial magazine/mook scans (see Internet Archive section above) |

### Entries by publication (merged catalog)

| Publication | Entries | Scan refs in catalog |
|-------------|---------|----------------------|
| FOOL'S MATE | 87 | 6 |
| Arena37℃ | 49 | 4 |
| SHOXX | 46 | 8 |
| B-PASS | 17 | 2 |
| PATi PATi | 12 | 2 |
| CD SKiT! | 11 | 2 |
| Band Yarouze | 9 | 0 |
| Vicious | 9 | 2 |
| Artist Fan | 8 | 0 |
| GiGS | 5 | 2 |
| Après Guerre | 3 | 0 |
| GB | 3 | 3 |
| CD Data, Fruige | 2 each | 1 / 0 |
| astan, band-collection, band-style, band-x-artist, bidan, clap, creation, da-vinchi, friday, luck-das, myojo, quick-japan, zy | 1 each | scan ref where noted above |

Scan refs = merged-catalog entries with a `scan.url` (Cantavanda, Internet Archive, Malice Archive incomplete mags, etc.). **47** items in `scan_sources_catalog.yaml` feed local mirroring via `fetch_images.py`.

YAML reference stubs: `data/references/online-magazine-bibliography.yaml`, `malice-archive-magazine-list.yaml`, `vkgy-magazine-timeline.yaml`, `misaolab-*.yaml`.

**Note:** The Malice Archive HTML page appears truncated mid-list (ends at Fruige); vkgy and MIsaO Lab fill gaps for SHOXX, GiGS, Cure, Zappy, etc. **494** issue YAML files under `data/issues/` are mostly placeholders until individually verified against NDL/physical copies.

## Reddit (r/visualkei)

**Catalog:** `scripts/research/reddit_scan_sources.yaml`  
**Reference:** `data/references/reddit-visualkei-scan-threads.yaml`

Surveyed via [PullPush Reddit archive API](https://api.pullpush.io/) (direct reddit.com JSON often blocked).

| Thread | Finding | Project link |
|--------|---------|--------------|
| [Where are these scans from?](https://www.reddit.com/r/visualkei/comments/1ibrtct/where_are_these_scans_from/) | **SHOXX Vol. 61** (Mar 1998) — u/CatKingClay | `data/issues/shoxx/1998-03.yaml`, `ref_shoxx_061` |
| Same thread (follow-up) | **FOOL'S MATE #188** (Jun 1997) La'cryma Christi collab | `data/issues/fools-mate/1997-06.yaml`, `ref_foolsmate_188` |
| [Scan culture appreciation](https://www.reddit.com/r/visualkei/comments/17kvbv8/i_hope_this_post_is_threadappropriate/) | Fans uploaded Arena37℃ & Cure scans; MM Hot Wave subs | meta only |
| [Gackt left MM discussion](https://www.reddit.com/r/visualkei/comments/1f1kgt0/the_truth_behind_why_gackt_left_malice_mizer/) | cites **SHOXX Vol. 66** (Aug 1998) + [Wayback interview](https://web.archive.org/web/20050523100553/http://www.geocities.com/Tokyo/Bridge/7727/inter08.html) | catalog entry |
| [Gackt's songs of MM](https://www.reddit.com/r/visualkei/comments/1h1imwq/gackts_songs_of_malice_mizer/) | **SHOXX Vol. 38** (Mar 1996) → [Gackt Translation Archive](https://gackttranslationarchive.wordpress.com/shoxx-vol-38-march-1996/) | `data/references/gackt-translation-archive.yaml` |
| [VK posters advice](https://www.reddit.com/r/visualkei/comments/1el8w2z/id_love_to_get_some_vkei_posters/) | Collectors recommend **BAND Yarouze**, **SHOXX**, **uv** for MM covers/posters | catalog entry |

## Known ISSN references

| Publication | ISSN |
|-------------|------|
| FOOL'S MATE | 0288-7899 |
| SHOXX | 1340-3117 |
| Arena37℃ | 1340-3125 |
| GiGS | 1344-378X |

ISSN values should be re-verified against NDL/CiNii during research.

## Magazine research priority

1. FOOL'S MATE
2. SHOXX
3. Arena37℃
4. Cure
5. GiGS
6. PATi PATi
7. B-PASS
8. uv
9. Tour pamphlets
10. Fan club newsletters

Publications with `status: needs_confirmation` in `data/publications.yaml` (34 titles) include Vicious, Zappy, WHAT's IN?, POP BEAT, M GAZETTE, and other low-priority or single-mention titles. Priority magazines (FOOL'S MATE, SHOXX, Arena37℃, Cure, GiGS, PATi PATi, B-PASS, uv) are `status: verified`.

## Image assets (site)

Local copies live under `images/` and are mirrored to `site/public/images/` for the static site.

| Asset type | Directory | Primary sources | Fetch script |
|------------|-----------|-----------------|--------------|
| Release flyers | `images/flyers/` | [malice-mizer.info/flyers](https://malice-mizer.info/flyers), [Malice Meezer vintage](https://malicemeezer.neocities.org/vintage) | `scripts/research/fetch_images.py` |
| Album/single covers | `images/covers/` | [Cover Art Archive](https://coverartarchive.org/) (Cantavanda-attributed uploads) | same |
| Member portraits & hero | `images/members/` | [malice-mizer.info/photos](https://www.malice-mizer.info/photos) (Cantavanda scans) | same |
| Magazine & pamphlet scans | `images/scans/` | `scan_sources_catalog.yaml` (Cantavanda, IA, scape.sc, Malice Archive where permitted) | same |
| Fan club zines | `images/scans/fan-club/` | Cantavanda ma chérie galleries | same + `ingest_cantavanda_scans.py` |

Attribution manifest: `images/manifest.json` (path, source URL, source name, fetch date).

Regenerate after adding remote URLs to YAML:

```bash
.venv/bin/python scripts/research/fetch_images.py
.venv/bin/python scripts/build_db.py
```

## Official and fan-maintained web archives

| Source | URL | Use |
|--------|-----|-----|
| MALICE MIZER Official Site | http://malice-mizer.co.jp/ | Authoritative history, discography, publications list |
| Official band history | http://malice-mizer.co.jp/History.html | Chronology 1992–2001 (Midi:Nette) |
| Official publications | http://malice-mizer.co.jp/Publications.html | Books, photobooks, magazines, band scores |
| MALICE MIZER Info — Flyers | https://malice-mizer.info/flyers | Release flyer gallery (34 items) |
| MALICE MIZER Info — Videos | https://www.malice-mizer.info/videos | VHS/DVD/Blu-ray catalog with track lists |
| Cantavanda (Butterfly Rose) | https://cantavanda.com/malice-mizer/ | Discography scans, prints, fan club magazines |
| Cantavanda — ma chérie scans | https://cantavanda.com/malice-mizer/scans/fan-club-magazines/ | FC magazine Vol. 1–7 |
| scape.sc — Translations | http://scape.sc/translations/mm-translations.php | English interview/pamphlet translations (Kurai) |
| scape.sc — Cher de memoire | http://www.scape.sc/pamphlets/cherdememoire/ | 1994 tour pamphlet + translation |
| Malice Meezer — Vintage | https://malicemeezer.neocities.org/vintage | Tetsu-era flyers, Memoire DX translations, photos |
| The Malice Archive | https://malice-archive.neocities.org/ | General fan archive |
| vkgy (ブイケージ) | https://www.jrock.gy/artists/malice-mizer/ | Release metadata cross-reference |
| scape.sc — Discography | https://www.scape.sc/release.php | Release pages, lyrics, pamphlets |

YAML reference stubs for these sources live under `data/references/`. Release flyers
catalogued from malice-mizer.info are in `data/issues/flyers/*-releases.yaml`; early
live flyers from Malice Meezer are in `data/issues/flyers/1992-1994-live.yaml`.
Video release stubs are in `data/videos/`.

Regenerate the web catalog after editing source lists:

```bash
.venv/bin/python scripts/research/import_web_sources.py
```

## Streaming platforms (Spotify, Tidal)

| Status | Detail |
|--------|--------|
| Official MALICE MIZER | **Not on Spotify or Tidal** as of July 2026 |
| Mana statement | [Natalie (2025)](https://natalie.mu/music/news/638907) — neither MALICE MIZER nor Moi dix Mois currently stream officially; future releases will be announced officially |
| Impersonator | **Malace Mizer** — fraudulent actor, not the band; see profile below |
| Fan guidance | [Cantavanda — Listen to MALICE MIZER](https://cantavanda.com/malice-mizer/links/listen-to-malice-mizer/) |

YAML stubs: `data/references/malace-mizer-impersonator.yaml` (canonical actor profile), `streaming-platforms.yaml`, `spotify-malace-mizer-catalog.yaml`, `tidal-malace-mizer-catalog.yaml`.

### Malace Mizer impersonator profile

| Flag | Detail |
|------|--------|
| **IMPERSONATOR** | Publishes under misspelled **"Malace Mizer"** (sometimes **"MALICE MIZER"**). Not affiliated with Midi:Nette, Nippon Columbia, or any band member. |
| **DMCA / copyright claimant** | Registers MM recordings in platform copyright databases under this identity. Files copyright claims against fan uploads — YouTube videos, TikTok/Instagram posts using MM audio, cover performances — monetizing content the actor does not own. |
| **Distributor shells** | `9559586 Records DK`, `3761571 Records DK` |
| **Monetization** | Spotify/Tidal streams and copyright claims profit the impersonator, not the band. |
| **Sources** | [Cantavanda](https://cantavanda.com/malice-mizer/links/listen-to-malice-mizer/), [Natalie (2025)](https://natalie.mu/music/news/638907), [JROCK ONE forum](https://forum.jrockone.com/t/fake-malice-mizer-on-digital-platforms/14459) |

**Do not link to Spotify or Tidal uploads.** Platform IDs below are for research identification only.

### Spotify examples (unauthorized)

| Release | Platform ID | Label note |
|---------|-------------|------------|
| -merveilles- | `2vLTmWIK6BMEpOCcLilhft` | Malace Mizer |
| Voyage Sans Retour | `1qZoqKRcKhZuP6Wt8VCqpq` | © 2022 3761571 Records DK |
| Bara no seidou | `3Nsm00nPPOWscPKMVNMedC` | © 2025 9559586 Records DK |
| Beast of Blood | `7CjP4tT088kAmmzBqqCNDu` | © 2025 9559586 Records DK |
| ma chérie | `0qj9fvyFA0qYsh7eQW356T` | © 2025 9559586 Records DK |

### Tidal examples (unauthorized, partial)

| Release | Platform ID |
|---------|-------------|
| ma chérie | `490778848` |
| Gardenia | `514021384` |

Tidal did not cross-link the full Spotify album set at time of check; treat as incomplete mirror of the same unauthorized uploads.
