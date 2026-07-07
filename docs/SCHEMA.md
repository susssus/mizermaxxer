# Entity schema (v2)

The archive uses **entity files** for facts and a **links layer** for relationships. Views (browse table, entity page, timeline) are renderings of the same resolved graph.

## Design principles

1. **IDs are stable and prefixed:** `song_au_revoir`, `album_merveilles`, `person_mana`, `ref_shoxx_061`, `concert_1998_04_14_tokyo`, `venue_tokyo_dome`
2. **Relationships are not duplicated** across every record — they live in `data/links.yaml` plus a small set of **derived** fields on entities (`appears_on`, `personnel`, `setlist`, …)
3. **Provenance is first-class:** `facts[]` on any entity cite `ref_*` sources with `confidence` and `status`
4. **Relation vocabulary is controlled:** `data/references/relation_types.yaml`

## Entity file layout

```
data/
  songs/au_revoir.yaml              # type: song, id: song_au_revoir
  albums/merveilles.entity.yaml     # type: album (legacy v1 slug files coexist)
  singles/gekka-no-yasoukyoku.yaml  # v1 release stubs; v2 singles use type: single
  people/mana.yaml                  # type: person, id: person_mana
  references/shoxx_061.yaml         # type: reference, id: ref_shoxx_061
  articles/pop_beat_1997_08_001.entity.yaml  # type: article, id: article_pop_beat_1997_08_001
  concerts/1998_04_14_tokyo.yaml
  appearances/1995_12_music_station.yaml
  organizations/tv_asahi.yaml
  venues/tokyo_dome.yaml
  videos/beast-of-blood-pv.yaml     # v1 video stubs; v2 uses type: video (reference schema)
  links.yaml                        # explicit cross-entity links
  references/relation_types.yaml
```

A file is a **v2 entity** when it has top-level `id` and `type` with a recognized prefix (`song_`, `album_`, `single_`, `person_`, `concert_`, `appearance_`, `venue_`, `ref_`, `video_`, `org_`, `image_`, `article_`). Legacy v1 files (slug `id`, no `type`) remain for the print bibliography pipeline until migrated.

## Song example

```yaml
id: song_au_revoir
type: song
title:
  original: オルヴォワール
  romanized: Au Revoir
duration_seconds: 292
appears_on:
  - album_merveilles
personnel:
  - person: person_mana
    role: guitar
  - person: person_kami
    role: drums
facts:
  - statement: >
      Kami first performed this arrangement live before its studio
      recording, with a slightly different bridge section.
    sources:
      - ref_shoxx_061
      - ref_foolsmate_188
    confidence: high
    status: verified
```

## Reference example

```yaml
id: ref_shoxx_061
type: reference
reference_type: magazine
title: "SHOXX Vol. 61"
publisher: SHOXX
date: 1998-03
pages_cited: [12, 13]
scan: images/scans/shoxx_061_p12.jpg
```

## Article example (magazine piece)

Bibliography articles (`data/issues/...` nested `articles[]`) migrate to v2 `article_*` entities. The `published_in` field points at the parent issue's `ref_*` entity; the link resolver derives `published_in` / `includes_article` edges automatically.

```yaml
id: article_pop_beat_1997_08_001
type: article
legacy_v1_slug: pop-beat-1997-08-001
title:
  original: 美しき表現者たち
  romanized: Beautiful expressors
article_type: interview
published_in: ref_pop_beat_1997_08
pages: "111"
members:
  - gackt
  - yuki
translation_slug: pop-beat-1997-08-interview
```

## Appearance example (TV / radio / variety / CM)

Use `appearance` for non-live broadcast media — distinct from `concert`:

```yaml
id: appearance_1995_12_music_station
type: appearance
title:
  original: ミュージックステーション
  romanized: Music Station
appearance_type: tv          # tv | radio | variety | cm | web | other
format: performance            # performance | interview | talk | cm | mixed | unknown
date: "1995-12"
date_precision: month
broadcast:
  network: org_tv_asahi        # org_* organization entity
  program: Music Station
members_present:
  - person_mana
  - person_gackt
songs_performed:
  - song_gekka_no_yasoukyoku
performances:
  - url: https://...
    platform: youtube
    quality: tv_broadcast
verification_status: needs_verification
```

Broadcasters are `organization` entities with `id: org_*` and `organization_type: broadcaster`.

## Explicit links (`data/links.yaml`)

```yaml
- from: song_au_revoir
  to: concert_1998_04_14_tokyo
  relation: performed_at

- from: song_au_revoir
  to: song_illuminati
  relation: related_song
  note: shares a chord progression in the bridge
```

Every `relation` in this file must appear under `explicit:` in `relation_types.yaml`.

## Derived links (automatic)

The build script infers these from entity fields — **do not** duplicate them in `links.yaml`:

| Field | Produces |
|-------|----------|
| `song.appears_on[]` | `appears_on` (song→album) + `includes_song` (album→song) |
| `song.personnel[]` | `personnel` (song→person) + `credited_on` (person→song) |
| `album.tracklist[]` | `includes_song` / `appears_on` |
| `concert.setlist[]` | `performed_at` (song→concert) + `features_performance` |
| `concert.members_present[]` | `performed_at` (person→concert) |
| `appearance.songs_performed[]` | `performed_at` (song→appearance) + `features_performance` |
| `appearance.members_present[]` | `appeared_at` (person→appearance) + `featured_appearance` |
| `appearance.broadcast.network` | `broadcast_on` (appearance→org) + `aired` (org→appearance) |
| `article.published_in` | `published_in` (article→ref) + `includes_article` (ref→article) |

Explicit link `discusses` (reference→entity) also generates inverse `cited_by`.

## Relation vocabulary

See [`data/references/relation_types.yaml`](../data/references/relation_types.yaml).

Each relation defines:

- `label` — UI display name
- `category` — concert / release / press / song / person / …
- `color` — coral, purple, pink, … (consistent across browse, entity page, timeline)
- `direction` — outgoing, incoming, or symmetric
- `inverse` — auto-generated reverse edge (except symmetric)

## Build pipeline

```bash
make entities          # validate v2 entities + build links index
make entities-validate # JSON Schema + referential checks only
make links             # build links index only
```

Outputs (generated; gitignored — run `make entities` or `make links` before `make site`):

- `site/src/data/links_index.json` — feeds UI (`linked_entities`, `link_count`, `browse`, `entities_by_id`)
- `exports/links_index.json` — same data for export/research

### `linked_entities` shape

```json
{
  "song_au_revoir": {
    "outgoing": [ ... ],
    "incoming": [ ... ],
    "all": [ ... ],
    "link_count": 7
  }
}
```

The browse table **Links** column = `link_count`. Entity page grids read from `all`.

## JSON Schema

Definitions live in [`schema/entity/`](../schema/entity/):

| File | Entity types |
|------|----------------|
| `entity.schema.json` | base `type` enum and shared fields |
| `song.schema.json` | `song_*` |
| `album.schema.json` | `album_*`, `single_*` |
| `person.schema.json` | `person_*` |
| `reference.schema.json` | `ref_*`, `video_*` |
| `article.schema.json` | `article_*` |
| `concert.schema.json` | `concert_*` |
| `appearance.schema.json` | `appearance_*` |
| `organization.schema.json` | `org_*` |
| `venue.schema.json` | `venue_*` |
| `title.schema.json` | `title` object (`original`, `romanized`, …) |
| `link.schema.json` | entries in `links.yaml` |
| `fact.schema.json` | `facts[]` on any entity |

## Migration from v1

| v1 | v2 | Status |
|----|-----|--------|
| `data/songs/au-revoir.yaml` (`id: au-revoir`) | `data/songs/au_revoir.entity.yaml` (`id: song_au_revoir`) | ✅ 133/133 migrated |
| `data/issues/` magazine stubs | `ref_*` references + `article_*` entities | ✅ 482 refs, ~488 articles (`published_in` derived) |
| `data/people/members.yaml` (bulk) | one `person_*.yaml` per member | partial (8 members) |
| Performance URLs on concerts | unchanged; also linkable via `links.yaml` | — |

Legacy v1 and v2 coexist: `make validate` runs the bibliography validator; `make entities` runs the entity validator.

## Suggested implementation order

1. **Schema + seed entities** ✅
2. **Link-resolution script** ✅
3. **Browse table** ✅ — `/browse` reads `links_index.browse`
4. **Entity pages** ✅ (partial) — `/entity/[id]` renders type chips, facts with provenance, linked-entity grid; appearance and person layouts expanded
5. **Timeline** — needs broadest date coverage across concerts, appearances, and releases
6. **Magazine migration** ✅ — `ref_*` references, `article_*` entities, derived `published_in` links (`make migrate-v2-catalog`)

## v1 / v2 slug crosswalk

Some records exist in both models during migration:

| v1 slug (catalog) | v2 entity ID | Notes |
|-------------------|--------------|-------|
| `tokyo-dome` | `venue_tokyo_dome` | Concerts reference v1 slug; browse graph uses v2 ID |
| `pop-beat-1997-08` | `ref_pop_beat_1997_08` | Magazine issue → reference entity |
| `pop-beat-1997-08-001` | `article_pop_beat_1997_08_001` | Bibliography article → article entity |

The site generates `site/src/data/entity_crosswalk.json` during `make build`. Keys: `songs`, `venues`, `people`, `albums`, `concerts`, `issues` (magazine issue id → `ref_*`).

Duplicate venue YAML files should not diverge in naming — prefer the v2 entity as canonical and keep the v1 stub for concert foreign keys until concerts migrate to entity IDs.
