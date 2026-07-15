# Content taxonomy

Bibliography articles are classified along two axes:

1. **`content_nature`** — editorial vs promotional (high level)
2. **`promotional_subtype`** — what kind of promotional material (when applicable)

Definitions live in [`data/content_taxonomy.yaml`](../data/content_taxonomy.yaml). Inference helpers are in [`scripts/content_taxonomy.py`](../scripts/content_taxonomy.py).

## Fields

| Field | When to use |
|-------|-------------|
| `content_nature` | `editorial` for interviews, features, reviews; `promotional` for ads, flyers, listings |
| `promotional_subtype` | Required when `content_nature: promotional` — see subtypes below |
| `promotional_carrier` | Where it appeared: `standalone`, `magazine_page`, `magazine_inset` |
| `vkgy_roles` | Parsed vk.gy roles (`flyer`, `cover`, `large_feature`, …) from import notes |

`type` / `article_type` remains the **format** (interview, flyer, advertisement, mention). The new fields describe **what the content actually is**.

## Promotional subtypes

| Subtype | Examples in this archive |
|---------|--------------------------|
| `gig_flyer` | Tetsu-era live flyers, “upcoming lives” handbills |
| `release_flyer` | malice-mizer.info single/album/VHS flyers |
| `demo_flyer` | Sadness demo tape flyer |
| `tour_ad` | POP BEAT Bel Air ad with STANDING TOUR schedule |
| `release_ad` | Release-only magazine advertisements |
| `gig_listing` | Magazine live schedule entries |
| `magazine_inset` | vk.gy-tagged inset flyers inside magazine issues |
| `goods_ad` | Merchandise or photobook ads |
| `poster_ad` | Poster pull-outs |
| `other` | Promotional but subtype unclear |

## Flyers vs magazine ads

The **`flyers`** publication holds standalone physical promotional scans. Many are release flyers, but early items include **gig flyers** and demo promos — now distinguished by `promotional_subtype`, not just `type: flyer`.

Magazine **advertisements** stay under their publication issue with `type: advertisement` and subtypes like `tour_ad` or `release_ad`.

## Applying classification

```bash
make classify-content   # write inferred fields into data/issues/**/*.yaml
make build              # rebuild archive.json with classification columns
```

Classification is also inferred at build time when fields are missing, but committing explicit YAML values is preferred for verified records.

## v2 article entities

Optional fields on `article_*` entities mirror the v1 article shape: `content_nature`, `promotional_subtype`, `promotional_carrier`, `vkgy_roles`.
