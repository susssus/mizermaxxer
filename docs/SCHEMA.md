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
  songs/au_revoir.yaml          # type: song, id: song_au_revoir
  albums/merveilles.entity.yaml # type: album (legacy v1 files coexist until migrated)
  people/mana.yaml
  references/shoxx_061.yaml
  concerts/1998_04_14_tokyo.yaml
  appearances/1995_12_music_station.yaml
  organizations/tv_asahi.yaml
  venues/tokyo_dome.yaml
  links.yaml                    # explicit cross-entity links
  references/relation_types.yaml
```

A file is a **v2 entity** when it has top-level `id` and `type`. Legacy v1 files (no `type`) remain for the print bibliography pipeline until migrated.

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

Outputs:

- `site/src/data/links_index.json` — feeds UI (`linked_entities`, `link_count`)
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
| `song.schema.json` | `song_*` |
| `album.schema.json` | `album_*` |
| `person.schema.json` | `person_*` |
| `reference.schema.json` | `ref_*` |
| `concert.schema.json` | `concert_*` |
| `appearance.schema.json` | `appearance_*` |
| `organization.schema.json` | `org_*` |
| `venue.schema.json` | `venue_*` |
| `link.schema.json` | entries in `links.yaml` |
| `fact.schema.json` | `facts[]` on any entity |

## Migration from v1

| v1 | v2 |
|----|-----|
| `data/songs/au-revoir.yaml` (`id: au-revoir`) | `data/songs/au_revoir.yaml` (`id: song_au_revoir`) |
| `data/issues/` magazine stubs | `ref_*` references + `published_in` links (planned) |
| `data/people/members.yaml` (bulk) | one `person_*.yaml` per member |
| Performance URLs on concerts | unchanged; also linkable via `links.yaml` |

Legacy v1 and v2 coexist: `make validate` runs the bibliography validator; `make entities` runs the entity validator.

## Suggested implementation order

1. **Schema + seed entities** ✅
2. **Link-resolution script** ✅
3. **Browse table** ✅ — `/browse` reads `links_index.browse`
4. **Entity pages** — `/entity/[id]` stub exists; expand with full fact/provenance UI
5. **Timeline** (needs broadest date coverage)
