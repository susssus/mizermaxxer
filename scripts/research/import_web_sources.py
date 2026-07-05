#!/usr/bin/env python3
"""Generate archive YAML from documented web sources (flyers, videos, references).

Sources catalogued here are fan-maintained or official pages discovered during
internet research. Each entry records the source URL; images are linked, not
mirrored, unless explicitly downloaded with permission.
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
TODAY = "2026-07-06"
CHANGELOG = [
    {
        "date": TODAY,
        "action": "created",
        "source": "web_research",
        "notes": "Catalogued from internet research with source attribution.",
    }
]

FLYER_BASE = "https://malice-mizer.info"
FLYER_GALLERY = "https://malice-mizer.info/flyers"

# Release flyers indexed at malice-mizer.info/flyers (fan-maintained catalog).
FLYERS = [
    ("1994-07-24", "memoire", "Mémoire release flyer", "94.7.24-memoire-flyer.webp"),
    ("1994-07-24", "memoire-ii", "Mémoire release flyer (variant II)", "94.7.24-memoire-flyer-II.webp"),
    ("1994-12-24", "memoire-dx", "Mémoire DX release flyer", "94.12.24-memoire-DX-flyer.webp"),
    ("1995-12-10", "uruwashiki-kamen", "麗しき仮面の招待状 release flyer", "95.12.10-Uruwashiki-Kamen-no-Shoutaijou-flyer.webp"),
    ("1996-06-09", "voyage", "Voyage ～sans retour～ release flyer", "96.6.9Voyage~sans-retour~flyer-cropped.webp"),
    ("1996-10-10", "ma-cherie", "ma chérie ～Itoshii Kimi e～ release flyer", "96.10.10-ma-cherie-flyer.webp"),
    ("1997-02-11", "gekka", "月下の夜想曲 release flyer", "97.2.11-Gekka-no-Yasoukyoku-release-flyer.webp"),
    ("1997-06-30", "derniere-vhs", "sans retour Voyage derniere VHS release flyer", "97.6.30-sans-retour-Voyage-LIVE-VIDEO-6-30-RELEASE-flyer.webp"),
    ("1997-07-19", "vers-elle", "Vers Elle debut single release flyer", "97.7.19-Debut-Single-Release-flyer-cropped.webp"),
    ("1998-04-01", "au-revoir", "au revoir release flyer", "98.4.1-au-revoir-flyer.webp"),
    ("1998-05-20", "illuminati", "ILLUMINATI release flyer", "98.5.20-ILLUMINATI-flyer-cropped.webp"),
    ("1998-09-30", "le-ciel", "Le ciel release flyer", "98.9.30-Le-ciel-flyer.webp"),
    ("1998-10-28", "lespace", "merveilles l'espace release flyer", "98.10.28-lespace-release.webp"),
    ("1998-11-27", "itan-shinmon", "異端審問 book release flyer", "98.11.webp"),
    ("1999-11-03", "saikai-single", "再会の血と薔薇 single release flyer", "99.11.3-再会の血と薔薇-flyer.webp"),
    ("1999-12-21", "saikai-de-limage", "再会の血と薔薇 de l'image release flyer", "99.12.21-再会の血と薔薇-flyer.webp"),
    ("2000-02-01", "shinwa-front", "神話 release flyer (front)", "00.2.1-神話-flyer-front.webp"),
    ("2000-02-01", "shinwa-back", "神話 release flyer (back)", "00.2.1-神話-flyer-back.webp"),
    ("2000-05-31", "kyomu", "虚無の中での遊戯 release flyer", "00.5.31-虚無の中での遊戯-flyer.webp"),
    ("2000-08-03", "bara-no-seidou-front", "薔薇の聖堂 release flyer (front)", "00.8.3-薔薇の聖堂-flyer-front.webp"),
    ("2000-08-03", "bara-no-seidou-back", "薔薇の聖堂 release flyer (back)", "00.8.3-薔薇の聖堂-flyer-back.webp"),
    ("2000-11-22", "budokan-vhs", "薔薇に彩られた悪意と悲劇の幕開け VHS/DVD flyer", "00.11.22-薇に彩られた悪意と悲劇の幕開け-flyer.webp"),
    ("2001-04-18", "derniere-dvd-front", "sans retour Voyage derniere DVD flyer (front)", "01.4.18-sans-retour-Voyage-DVD-flyer-front.webp"),
    ("2001-05-30", "gardenia", "Gardenia release flyer", "01.5.30-Gardenia-flyer.webp"),
    ("2001-10-30", "bara-no-konrei", "真夜中に交わした約束～薔薇の婚礼～ release flyer", "01.10.30-真夜中に交わした約束~薔薇の婚礼~flyer.webp"),
    ("2001-11-30", "garnet", "Garnet release flyer", "01.11.30-Garnet-flyer.webp"),
]

# Early-era live flyers documented at malicemeezer.neocities.org/vintage (Tetsu era).
# Each entry maps to a specific scan on the vintage gallery page.
EARLY_FLYERS = [
    ("1992-08", "debut-era", "Malice Mizer flyer (1992)", "https://malicemeezer.neocities.org/tetsu/oldflyer5.jpg"),
    ("1993-01", "demo-sadness", "Sadness demo tape flyer", "https://malicemeezer.neocities.org/tetsu/oldflyer7.jpg"),
    ("1993-06", "live-1993", "Malice Mizer live flyer (1993)", "https://malicemeezer.neocities.org/tetsu/oldflyer2.jpg"),
    ("1993-08", "artistic-expression", "Artistic expression flyer (translated quote)", "https://malicemeezer.neocities.org/tetsu/oldflyer3.jpg"),
    ("1993-12", "upcoming-lives", "Upcoming lives flyer", "https://malicemeezer.neocities.org/tetsu/oldflyer8.jpg"),
    ("1994-01", "live-1994", "Malice Mizer live flyer (1994)", "https://malicemeezer.neocities.org/tetsu/oldflyer.jpg"),
    ("1993-03", "oldflyer9", "Malice Mizer flyer (date unknown)", "https://malicemeezer.neocities.org/tetsu/oldflyer9.jpg"),
    ("1994-06", "oldflyer4", "Malice Mizer flyer (date unknown, variant)", "https://malicemeezer.neocities.org/tetsu/Oldflyer4.png"),
]

VIDEO_RELEASES = [
    ("derniere-vhs", "sans retour Voyage \"derniere\" VHS", "1997-06-30", "live_footage", "https://www.malice-mizer.info/derniere-vhs", "M:N-005"),
    ("lespace-vhs", "merveilles l'espace VHS", "1998-10-28", "live_footage", "https://www.malice-mizer.info/lespace-vhs", "COVA-6191"),
    ("cinq-parallele-vhs", "merveilles cinq parallele VHS", "1999-02-24", "pv", "https://malice-mizer.info/cinq-parallele-vhs", "COBA-4161"),
    ("saikai-de-limage-vhs", "Saikai no Chi to Bara de l'image VHS", "1999-12-21", "pv", "https://www.malice-mizer.info/", "MMVC-008"),
    ("kyomu-de-limage-vhs", "Kyomu no Naka de no Yuugi de l'image VHS", "2000-05-31", "pv", "https://www.malice-mizer.info/", "MMVC-011"),
    ("budokan-live-vhs", "Bara ni Irodorareta Akui to Higeki no Makuake VHS/DVD", "2000-11-22", "live_footage", "https://www.malice-mizer.info/", "MMVD-014"),
    ("bara-no-kiseki-vhs", "Bara no Kiseki VHS", "2001-04-25", "documentary", "https://www.malice-mizer.info/", "MMVC-017"),
    ("derniere-dvd", "sans retour Voyage derniere DVD", "2001-04-18", "live_footage", "https://www.malice-mizer.info/", "MMBV-016"),
    ("beast-of-blood-de-limage", "Beast of Blood de l'image VHS/DVD", "2001-07-11", "pv", "https://www.malice-mizer.info/", "MMVC-023"),
    ("cardinal-vhs", "Cardinal VHS/DVD", "2002-02-06", "live_footage", "https://www.malice-mizer.info/", "MMVC-027"),
    ("bara-no-konrei-film", "Bara no Konrei silent film VHS/DVD", "2002-03-22", "documentary", "https://www.malice-mizer.info/", "KSVD-24319"),
    ("deep-sanctuary-vi-blu-ray", "Deep Sanctuary VI 25th Anniversary Blu-ray", "2019-06-21", "live_footage", "https://www.malice-mizer.info/videos", "DS6-0001"),
]

REFERENCES = [
    ("malice-mizer-official", "MALICE MIZER Official Site", "website", "http://malice-mizer.co.jp/", "Official band site (2011–). History, discography, publications."),
    ("malice-mizer-official-history", "MALICE MIZER Official — Band History", "website", "http://malice-mizer.co.jp/History.html", "Authoritative chronology 1992–2001 from Midi:Nette."),
    ("malice-mizer-official-publications", "MALICE MIZER Official — Publications", "website", "http://malice-mizer.co.jp/Publications.html", "Official books, photobooks, magazines, band scores."),
    ("malice-mizer-info-flyers", "MALICE MIZER Info — Flyers", "website", "https://malice-mizer.info/flyers", "Fan-maintained release flyer gallery (34 items)."),
    ("malice-mizer-info-videos", "MALICE MIZER Info — Video Releases", "website", "https://www.malice-mizer.info/videos", "Fan-maintained VHS/DVD/Blu-ray catalog with track lists."),
    ("cantavanda-fansite", "Butterfly Rose — Cantavanda MALICE MIZER Fansite", "website", "https://cantavanda.com/malice-mizer/", "Discography scans, prints, fan club magazine scans."),
    ("cantavanda-fanclub-mags", "Cantavanda — ma chérie Fan Club Magazine Scans", "website", "https://cantavanda.com/malice-mizer/scans/fan-club-magazines/", "Vol. 1–7 scanned by Madame Tarantula (with permission)."),
    ("scape-translations", "scape.sc — Malice Mizer Translations", "website", "http://scape.sc/translations/mm-translations.php", "English translations by Kurai (interviews, pamphlets, disband messages)."),
    ("scape-cher-de-memoire", "scape.sc — Cher de memoire Pamphlet (1994)", "website", "http://www.scape.sc/pamphlets/cherdememoire/", "First tour pamphlet; translation available."),
    ("malicemeezer-vintage", "Malice Meezer — Tetsu Era Gallery + Translations", "website", "https://malicemeezer.neocities.org/vintage", "Early flyers, Memoire DX booklet translations, rare photos."),
    ("malice-archive-neocities", "The Malice Archive", "website", "https://malice-archive.neocities.org/", "Fan archive (last updated May 2026)."),
    ("vkgy-discography", "vkgy (ブイケージ) — Malice Mizer", "database", "https://www.jrock.gy/artists/malice-mizer/", "Discography and release cross-reference."),
    ("scape-discography", "scape.sc — Malice Mizer Discography", "website", "https://www.scape.sc/release.php", "Release metadata, pamphlets, lyrics."),
]

BOOK_REFERENCES = [
    ("book-itan-shinmon", "MALICE MIZER 異端審問", "book", "http://malice-mizer.co.jp/Publications.html", "1998-11-27. Ohta Publishing. First official interview book; Hosoe Nobuyoshi photos."),
    ("book-tanbi-jikken", "MALICEMIZER 耽美実験革命", "book", "http://malice-mizer.co.jp/Publications.html", "1998-10-25. Magazine Magazine. Cross-industry long interviews."),
    ("book-retoour", "Retour (ルトゥール)", "book", "http://malice-mizer.co.jp/Publications.html", "1999-02-05. FOOL'S MATE. Live history 1992–1998; flyers and goods."),
    ("book-aa-mujou-tenchi", "マリスミゼルの\"ああ、無情\"-天地鳴動編-", "book", "http://malice-mizer.co.jp/Publications.html", "1999-06-25. Sony Magazines. Gackt-era serialized history."),
    ("book-aa-mujou-hyakka", "マリスミゼルの\"ああ、無情\"－百花燎乱編－", "book", "http://malice-mizer.co.jp/Publications.html", "2001-02-20. Post-Gackt/Kami era; Budokan reunion."),
    ("book-aa-mujou-kousai", "マリスミゼルの\"ああ、無情\"-光彩陸離編-", "book", "http://malice-mizer.co.jp/Publications.html", "2002-01-20. Final serialized volume; activity hiatus."),
    ("book-uv-file", "UV SPECIAL MALICE MIZER FILE", "book", "http://malice-mizer.co.jp/Publications.html", "2001-12. Sony Magazines. Compiled hv/uv articles 1997–2001."),
    ("book-livre-rose", "薔薇の聖堂 LivreRose", "book", "http://malice-mizer.co.jp/Publications.html", "2000-12. Midi:Nette limited photobook."),
    ("book-livre-rose-blanche", "薔薇の聖堂 LivreRose Blanche", "book", "http://malice-mizer.co.jp/Publications.html", "2001-04-25. Kadokawa. General release with new shots."),
    ("book-merveilles-deux-dimension", "Merveilles deux dimension", "book", "http://malice-mizer.co.jp/Publications.html", "1998-07-30. Sony Magazines photobook."),
]

TRANSLATION_REFERENCES = [
    ("translation-shoxx-dec1992", "SHOXX first interview (Dec 1992) — English", "article", "http://scape.sc/translations/mm-translations.php", "Translated by Kurai; earliest magazine interview translation."),
    ("translation-cher-de-memoire-sep1994", "Cher de memoire pamphlet (Sep 1994) — English", "article", "https://www.scape.sc/translations/mm-cherdememoire-sep94.php", "Translated by Kurai / Alex Highsmith (jrockdimension)."),
    ("translation-memoire-dx-mana", "Memoire DX booklet — Mana interview (English)", "article", "https://malicemeezer.neocities.org/vintage", "Malice Meezer Tetsu-era translation collection."),
    ("translation-memoire-dx-tetsu", "Memoire DX booklet — Tetsu interview (English)", "article", "https://malicemeezer.neocities.org/vintage", "Malice Meezer Tetsu-era translation collection."),
    ("translation-disband-messages", "Malice Mizer disband messages — English", "article", "http://scape.sc/translations/mm-translations.php", "Translated by Kurai; Dec 2001 hiatus announcement."),
]


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.dump(data, handle, allow_unicode=True, sort_keys=False, default_flow_style=False)


def _has_cjk(text: str) -> bool:
    return any("\u3040" <= c <= "\u9fff" or "\u3400" <= c <= "\u4dbf" for c in text)


def flyer_article(date: str, slug: str, title: str, image_file: str) -> dict:
    has_japanese = _has_cjk(title)
    return {
        "id": f"flyers-{date}-{slug}",
        "title_ja": title if has_japanese else None,
        "title_en": None if has_japanese else title,
        "type": "flyer",
        "pages": None,
        "members": [],
        "photographer": None,
        "writer": None,
        "cover": False,
        "poster": False,
        "foldout": False,
        "scan": {
            "available": True,
            "quality": "medium",
            "url": f"{FLYER_BASE}/{image_file}",
        },
        "translation": {"available": False, "url": None},
        "purchase_links": [],
        "notes": f"Indexed at {FLYER_GALLERY}. Source: malice-mizer.info (fan catalog).",
    }


def early_flyer_article(date: str, slug: str, title: str, page_url: str) -> dict:
    has_japanese = _has_cjk(title)
    return {
        "id": f"flyers-{date}-{slug}",
        "title_ja": title if has_japanese else None,
        "title_en": None if has_japanese else title,
        "type": "flyer",
        "pages": None,
        "members": [],
        "photographer": None,
        "writer": None,
        "cover": False,
        "poster": False,
        "foldout": False,
        "scan": {
            "available": True,
            "quality": "medium",
            "url": page_url,
        },
        "translation": {"available": False, "url": None},
        "purchase_links": [],
        "notes": f"Tetsu-era flyer documented at {page_url}. Source: Malice Meezer (malicemeezer.neocities.org).",
    }


def generate_release_flyers() -> None:
    by_year: dict[str, list] = {}
    for date, slug, title, image in FLYERS:
        year = date[:4]
        by_year.setdefault(year, []).append(flyer_article(date, slug, title, image))

    for year, articles in sorted(by_year.items()):
        issue_id = f"flyers-{year}-releases"
        write_yaml(
            DATA / "issues" / "flyers" / f"{year}-releases.yaml",
            {
                "id": issue_id,
                "publication": "flyers",
                "issue_number": None,
                "volume": None,
                "publication_date": year,
                "date_precision": "year",
                "verification_status": "possible",
                "source_notes": f"Release flyers catalogued from {FLYER_GALLERY}.",
                "research_targets": ["confirm print run details", "locate physical copies"],
                "articles": articles,
                "changelog": CHANGELOG,
            },
        )


def generate_early_flyers() -> None:
    articles = [
        early_flyer_article(date, slug, title, url)
        for date, slug, title, url in EARLY_FLYERS
    ]
    write_yaml(
        DATA / "issues" / "flyers" / "1992-1994-live.yaml",
        {
            "id": "flyers-1992-1994-live",
            "publication": "flyers",
            "issue_number": None,
            "volume": None,
            "publication_date": "1992-08",
            "date_precision": "month",
            "verification_status": "possible",
            "source_notes": "Early live and demo flyers from Tetsu era. Source: malicemeezer.neocities.org/vintage.",
            "research_targets": ["scan high-resolution originals", "confirm event dates"],
            "articles": articles,
            "changelog": CHANGELOG,
        },
    )


def generate_videos() -> None:
    for vid_id, title, release_date, vtype, url, catalog in VIDEO_RELEASES:
        write_yaml(
            DATA / "videos" / f"{vid_id}.yaml",
            {
                "id": vid_id,
                "title_ja": None,
                "title_en": title,
                "type": vtype,
                "url": url,
                "platform": "other",
                "release_date": release_date,
                "song": None,
                "concert": None,
                "quality": "official",
                "verification_status": "possible",
                "notes": f"Catalog no. {catalog}. Source: malice-mizer.info/videos and official discography.",
                "changelog": CHANGELOG,
            },
        )


def generate_references() -> None:
    all_refs = REFERENCES + BOOK_REFERENCES + TRANSLATION_REFERENCES
    for ref_id, title, rtype, url, notes in all_refs:
        path = DATA / "references" / f"{ref_id}.yaml"
        if path.name == "malice-mizer-info-videos.yaml":
            continue  # already exists
        if path.name == "vkgy-discography.yaml":
            continue
        write_yaml(
            path,
            {"id": ref_id, "title": title, "type": rtype, "url": url, "notes": notes},
        )


def main() -> None:
    generate_release_flyers()
    generate_early_flyers()
    generate_videos()
    generate_references()
    print("Web source catalog generated.")


if __name__ == "__main__":
    main()
