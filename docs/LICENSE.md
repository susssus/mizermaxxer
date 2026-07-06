# Licensing

Mizermaxxer is an **open research archive** with a dual-license model: permissive
open-source code, and openly licensed (non-commercial) project-contributed data.

| Material | License | File |
|----------|---------|------|
| Scripts, site source, JSON schemas | [MIT](../LICENSE) | `LICENSE` |
| Bibliographic YAML, English translations, exported datasets | [CC BY-NC 4.0](../LICENSE-CC-BY-NC-4.0.md) | `LICENSE-CC-BY-NC-4.0.md` |
| Mirrored scans and magazine pages | **Third-party rights** | [SOURCES.md](SOURCES.md), site `/attribution` |

## Open source plan (summary)

1. **Fork and improve the tooling** — MIT lets you reuse scripts, the Astro site, and schemas in other projects with attribution.
2. **Reuse bibliographic data and translations** — CC BY-NC 4.0 allows non-commercial sharing and adaptation with credit; commercial reuse requires permission.
3. **Respect third-party media** — scans, covers, and magazine pages stay © their original archivists and publishers; we document sources and link back, but do not re-license those files.

## What CC BY-NC 4.0 means here

Contributors may copy, share, and adapt the project’s **YAML catalogues** and **English translation text** for non-commercial purposes if they:

- credit Mizermaxxer contributors,
- link to the [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) license, and
- note changes.

Commercial republication, paid services built on the dataset, or similar uses require separate permission.

## Translations

Every file in `data/translations/` must include:

```yaml
license: CC-BY-NC-4.0
license_notes: >
  …source scan attribution… English translation © Mizermaxxer contributors (CC BY-NC 4.0).
```

- `license` — SPDX-style identifier for the **English translation text** (always `CC-BY-NC-4.0`)
- `license_notes` — provenance for underlying scans plus the CC BY-NC 4.0 notice for translation text

## Trademarks and affiliation

This project is **not affiliated** with Malice Mizer, Mana, Midi:Nette, Nippon Columbia, or any official rights holder. Band names, logos, and magazine titles remain trademarks or copyrights of their respective owners.

## Contributing

By contributing code, YAML, or translation text, you agree to license your contributions under MIT (code) and CC BY-NC 4.0 (content), as applicable. Do not submit third-party scans without documented permission or a recorded fair-use rationale in `license_notes`.

## Site

The public site publishes the same policy at [/legal](https://mizermaxxer.org/legal) with links to [privacy](https://mizermaxxer.org/privacy) and [image attribution](https://mizermaxxer.org/attribution).
