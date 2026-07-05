#!/usr/bin/env python3
"""Generate discography, song, concert, and video seed files."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TODAY = "2026-07-06"


def changelog(notes: str, action: str = "created") -> list[dict]:
    return [{"date": TODAY, "action": action, "source": "seed_script", "notes": notes}]


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


SONGS = [
    ("ma-cherie", "ma chérie ～愛しい君へ～", "ma chérie ~Itoshii Kimi e~"),
    ("uruwashii-kamen", "麗しき仮面の招待状", "Uruwashii Kamen no Shoutaijo"),
    ("serenade", "セレナード", "Serenade"),
    ("ayakashi", "妖", "Ayakashi"),
    ("shijin-no-shouzou", "詩人の肖像", "Shijin no Shouzou"),
    ("bois-dor", "Bois d'or", "Bois d'or"),
    ("regret-message", "倫逸メッセージ", "Regret Message"),
    ("transylvania", "Transylvania", "Transylvania"),
    ("madrigal", "Madrigal", "Madrigal"),
    ("antique-doll", "Antique Doll", "Antique Doll"),
    ("de-miserie", "De Miserie", "De Miserie"),
    ("gekka-no-yasoukyoku", "月下の夜想曲", "Gekka no Yasoukyoku"),
    ("bel-air", "Bel Air", "Bel Air"),
    ("illuminati", "ILLUMINATI", "ILLUMINATI"),
    ("le-ciel", "Le ciel ～空白の彼方へ～", "Le ciel ~Kuuhaku no Kanata e~"),
    ("au-revoir", "au revoir", "au revoir"),
    ("beast-of-blood", "Beast of Blood", "Beast of Blood"),
    ("saikai-no-chi-to-bara", "再会の血と薔薇", "Saikai no Chi to Bara"),
    ("intro-des-congratulations", "Intro ~Des congratulations~", "Intro ~Des congratulations~"),
    ("synthesizer-no-maria", "シンセサイザーのマリア", "Synthesizer no Maria"),
]


def seed_songs() -> None:
    for slug, ja, en in SONGS:
        write(
            DATA / "songs" / f"{slug}.yaml",
            {
                "id": slug,
                "title_ja": ja,
                "title_en": en,
                "writers": ["mana"],
                "lyricists": [],
                "composers": ["mana"],
                "notes": "",
            },
        )


ALBUMS = [
    {
        "id": "fait-malice-et-fin",
        "title_ja": "Fait malice et fin",
        "title_en": "Fait malice et fin",
        "type": "demo",
        "release_date": "1993",
        "date_precision": "year",
        "label": "independent",
        "catalog_number": None,
        "format": "cassette",
        "track_slugs": [],
        "notes": "Early demo cassette. Track listing needs verification.",
        "verification_status": "needs_verification",
    },
    {
        "id": "memoire",
        "title_ja": "Mémoire",
        "title_en": "Memoire",
        "type": "album",
        "release_date": "1994-03-10",
        "date_precision": "day",
        "label": "independent",
        "catalog_number": "MR-001",
        "format": "cd",
        "track_slugs": [
            "ma-cherie",
            "uruwashii-kamen",
            "serenade",
            "ayakashi",
            "shijin-no-shouzou",
            "bois-dor",
            "regret-message",
            "transylvania",
            "madrigal",
            "antique-doll",
        ],
        "notes": "First full album; indie release prior to major label debut.",
        "verification_status": "verified",
    },
    {
        "id": "merveilles",
        "title_ja": "Merveilles",
        "title_en": "Merveilles",
        "type": "album",
        "release_date": "1995-09-01",
        "date_precision": "month",
        "label": "Columbia Music Entertainment",
        "catalog_number": "COCX-00105",
        "format": "cd",
        "track_slugs": [
            "de-miserie",
            "gekka-no-yasoukyoku",
            "bel-air",
            "illuminati",
            "le-ciel",
            "au-revoir",
            "regret-message",
            "transylvania",
        ],
        "notes": "Major-label debut album. Full track order to be verified.",
        "verification_status": "possible",
    },
    {
        "id": "voyage-sans-retour",
        "title_ja": "Voyage ~sans retour~",
        "title_en": "Voyage ~sans retour~",
        "type": "album",
        "release_date": "1996-11-21",
        "date_precision": "day",
        "label": "Columbia Music Entertainment",
        "catalog_number": None,
        "format": "cd",
        "track_slugs": [],
        "notes": "Instrumental and narrative album. Track listing stub.",
        "verification_status": "needs_verification",
    },
    {
        "id": "nocturne",
        "title_ja": "Nocturne",
        "title_en": "Nocturne",
        "type": "album",
        "release_date": "1998-03-04",
        "date_precision": "day",
        "label": "Columbia Music Entertainment",
        "catalog_number": None,
        "format": "cd",
        "track_slugs": [],
        "notes": "",
        "verification_status": "possible",
    },
    {
        "id": "bara-no-seidou",
        "title_ja": "薔薇の聖堂",
        "title_en": "Bara no Seidou",
        "type": "album",
        "release_date": "2000-04-05",
        "date_precision": "day",
        "label": "Columbia Music Entertainment",
        "catalog_number": None,
        "format": "cd",
        "track_slugs": [],
        "notes": "Final studio album before hiatus.",
        "verification_status": "possible",
    },
]


def seed_albums() -> None:
    for album in ALBUMS:
        track_slugs = album.pop("track_slugs")
        write(
            DATA / "albums" / f"{album['id']}.yaml",
            {
                **album,
                "cover_image": None,
                "tracks": [{"song": song, "position": index + 1} for index, song in enumerate(track_slugs)],
                "changelog": changelog(f"Seed entry for {album['title_en']}"),
            },
        )


SINGLES = [
    {
        "id": "regret-message-single",
        "title_ja": "倫逸メッセージ",
        "title_en": "Regret Message",
        "release_date": "1995",
        "date_precision": "year",
        "label": "independent",
        "catalog_number": None,
        "a_side": "regret-message",
        "b_side": None,
        "notes": "Indie single predating Merveilles.",
    },
    {
        "id": "gekka-no-yasoukyoku-single",
        "title_ja": "月下の夜想曲",
        "title_en": "Gekka no Yasoukyoku",
        "release_date": "1995-12-06",
        "date_precision": "day",
        "label": "Columbia Music Entertainment",
        "catalog_number": "CODA-764",
        "a_side": "gekka-no-yasoukyoku",
        "b_side": "bel-air",
        "notes": "Major debut single.",
    },
    {
        "id": "beast-of-blood-single",
        "title_ja": "Beast of Blood",
        "title_en": "Beast of Blood",
        "release_date": "1999-04-21",
        "date_precision": "day",
        "label": "Columbia Music Entertainment",
        "catalog_number": None,
        "a_side": "beast-of-blood",
        "b_side": None,
        "notes": "",
    },
]


def seed_singles() -> None:
    for single in SINGLES:
        write(
            DATA / "singles" / f"{single['id']}.yaml",
            {
                **single,
                "format": "cd",
                "coupling_tracks": [],
                "cover_image": None,
                "verification_status": "possible",
                "changelog": changelog(f"Seed entry for single {single['title_en']}"),
            },
        )


CONCERTS = [
    {
        "id": "1992-08-10-osaka-debut",
        "date": "1992-08-10",
        "date_precision": "day",
        "venue": "osaka-heartland",
        "event_name_ja": None,
        "event_name_en": "Early indie live (debut period)",
        "type": "live",
        "tour": None,
        "setlist": [],
        "members_present": ["mana", "kozi", "yuki", "tetsu", "birith"],
        "verification_status": "needs_verification",
        "source_notes": "Formation-era live; date and venue require primary source confirmation.",
        "performances": [],
        "notes": "Linked to earliest flyer stub in magazine archive.",
    },
    {
        "id": "1992-09-24-shibuya-indies",
        "date": "1992-09-24",
        "date_precision": "day",
        "venue": "shibuya-on-air-west",
        "event_name_ja": None,
        "event_name_en": "Indies live bill",
        "type": "live",
        "tour": None,
        "setlist": [],
        "members_present": ["mana", "kozi", "yuki", "tetsu", "karis"],
        "verification_status": "needs_verification",
        "source_notes": "Possible FOOL'S MATE live listing cross-reference target.",
        "performances": [],
        "notes": "",
    },
    {
        "id": "1995-12-09-gekka-promo",
        "date": "1995-12-09",
        "date_precision": "day",
        "venue": "shibuya-on-air-west",
        "event_name_ja": "月下の夜想曲 発売記念",
        "event_name_en": "Gekka no Yasoukyoku release event",
        "type": "event",
        "tour": None,
        "setlist": ["gekka-no-yasoukyoku", "bel-air"],
        "members_present": ["mana", "kozi", "yuki", "kami", "gackt"],
        "verification_status": "possible",
        "source_notes": "Major debut promotional live.",
        "performances": [],
        "notes": "",
    },
    {
        "id": "1998-12-26-tokyo-dome",
        "date": "1998-12-26",
        "date_precision": "day",
        "venue": "tokyo-dome",
        "event_name_ja": "『禁断の扉～終焉の舞台～』",
        "event_name_en": "Kindan no Tobira ~Shuuen no Butai~",
        "type": "oneman",
        "tour": None,
        "setlist": ["intro-des-congratulations", "beast-of-blood", "gekka-no-yasoukyoku"],
        "members_present": ["mana", "kozi", "yuki", "kami", "klaha"],
        "verification_status": "verified",
        "source_notes": "Major documented oneman; widely bootlegged.",
        "performances": [
            {
                "url": "https://www.youtube.com/watch?v=94gn00m6rf4",
                "platform": "youtube",
                "quality": "pro_shot",
                "title": "merveilles ~Shuuen to Kisuu~ l'espace (1998 concert film)",
                "notes": "Official VHS/DVD edit of Budokan 1998-04-01 and Yokohama Arena 1998-07-22.",
            }
        ],
        "notes": "",
    },
    {
        "id": "1999-08-08-yokohama-arena",
        "date": "1999-08-08",
        "date_precision": "day",
        "venue": None,
        "event_name_ja": "『禁断の扉～再開の宴～』",
        "event_name_en": "Kindan no Tobira ~Saikai no Utage~",
        "type": "oneman",
        "tour": None,
        "setlist": [],
        "members_present": ["mana", "kozi", "yuki", "kami", "klaha"],
        "verification_status": "verified",
        "source_notes": "Final era major live before Kami's passing.",
        "performances": [
            {
                "url": "https://www.youtube.com/watch?v=94gn00m6rf4",
                "platform": "youtube",
                "quality": "pro_shot",
                "title": "merveilles ~Shuuen to Kisuu~ l'espace (Yokohama Arena 1998-07-22)",
                "notes": "Documented Yokohama Arena performance in official l'espace film.",
            }
        ],
        "notes": "",
    },
]


def seed_concerts() -> None:
    for concert in CONCERTS:
        write(
            DATA / "concerts" / f"{concert['id']}.yaml",
            {**concert, "changelog": changelog(f"Seed entry for {concert['id']}")},
        )


VIDEOS = [
    {
        "id": "bel-air-pv",
        "title_ja": "ヴェル・エール～空白の瞬間の中で～",
        "title_en": "Bel Air (PV)",
        "type": "pv",
        "url": "https://www.youtube.com/watch?v=t1mcnxf8S9A",
        "platform": "youtube",
        "release_date": "1997-08-06",
        "song": "bel-air",
        "concert": None,
        "quality": "official",
        "verification_status": "verified",
        "notes": "Official PV on @Malice_Mizer_Official YouTube channel.",
    },
    {
        "id": "au-revoir-pv",
        "title_ja": "au revoir",
        "title_en": "Au Revoir (PV)",
        "type": "pv",
        "url": "https://www.youtube.com/watch?v=RcQCJfK2n-c",
        "platform": "youtube",
        "release_date": "1997-12-03",
        "song": "au-revoir",
        "concert": None,
        "quality": "official",
        "verification_status": "verified",
        "notes": "Official PV on @Malice_Mizer_Official YouTube channel.",
    },
    {
        "id": "gekka-no-yasoukyoku-pv",
        "title_ja": "月下の夜想曲",
        "title_en": "Gekka no Yasoukyoku (PV)",
        "type": "pv",
        "url": "https://www.youtube.com/watch?v=L0_fUEOz3dY",
        "platform": "youtube",
        "release_date": "1995-12-06",
        "song": "gekka-no-yasoukyoku",
        "concert": None,
        "quality": "official",
        "verification_status": "verified",
        "notes": "Official PV on @Malice_Mizer_Official YouTube channel.",
    },
    {
        "id": "le-ciel-pv",
        "title_ja": "Le ciel ～空白の彼方へ～",
        "title_en": "Le ciel (PV)",
        "type": "pv",
        "url": "https://www.youtube.com/watch?v=HTDmJcfEHUA",
        "platform": "youtube",
        "release_date": "1998-09-30",
        "song": "le-ciel",
        "concert": None,
        "quality": "official",
        "verification_status": "verified",
        "notes": "Official PV on @Malice_Mizer_Official YouTube channel.",
    },
    {
        "id": "beast-of-blood-pv",
        "title_ja": "Beast of Blood",
        "title_en": "Beast of Blood (PV)",
        "type": "pv",
        "url": "https://www.youtube.com/watch?v=mAi-0JLjkgg",
        "platform": "youtube",
        "release_date": "1999-04-21",
        "song": "beast-of-blood",
        "concert": None,
        "quality": "official",
        "verification_status": "verified",
        "notes": "Official PV on @Malice_Mizer_Official YouTube channel.",
    },
    {
        "id": "saikai-no-chi-to-bara-pv",
        "title_ja": "再会の血と薔薇",
        "title_en": "Saikai no Chi to Bara (PV)",
        "type": "pv",
        "url": "https://www.youtube.com/watch?v=TR4bfD18Ttg",
        "platform": "youtube",
        "release_date": "1999-12-21",
        "song": "saikai-no-chi-to-bara",
        "concert": None,
        "quality": "official",
        "verification_status": "verified",
        "notes": "Official PV on @Malice_Mizer_Official YouTube channel.",
    },
    {
        "id": "kyomu-no-naka-de-no-yugi-pv",
        "title_ja": "虚無の中での遊戯",
        "title_en": "Kyomu no Naka de no Yuugi (PV)",
        "type": "pv",
        "url": "https://www.youtube.com/watch?v=7wynBDVwhrk",
        "platform": "youtube",
        "release_date": "2000-05-31",
        "song": "kyomu-no-naka-de-no-yugi",
        "concert": None,
        "quality": "official",
        "verification_status": "verified",
        "notes": "Official PV on @Malice_Mizer_Official YouTube channel.",
    },
    {
        "id": "shiroi-hada-pv",
        "title_ja": "白い肌に狂う愛と哀しみの輪舞",
        "title_en": "Shiroi Hada ni Kuruu Ai to Kanashimi no Rondo (PV)",
        "type": "pv",
        "url": "https://www.youtube.com/watch?v=TaLJscmFOTQ",
        "platform": "youtube",
        "release_date": "2000-07-26",
        "song": "shiroi-hada",
        "concert": None,
        "quality": "official",
        "verification_status": "verified",
        "notes": "Official PV on @Malice_Mizer_Official YouTube channel.",
    },
    {
        "id": "gardenia-pv",
        "title_ja": "Gardenia",
        "title_en": "Gardenia (PV)",
        "type": "pv",
        "url": "https://www.youtube.com/watch?v=XuTknvtvRN0",
        "platform": "youtube",
        "release_date": "2001-05-30",
        "song": "gardenia",
        "concert": None,
        "quality": "official",
        "verification_status": "verified",
        "notes": "Official PV on @Malice_Mizer_Official YouTube channel.",
    },
    {
        "id": "mayonaka-yakusoku-pv",
        "title_ja": "真夜中に交わした約束",
        "title_en": "Mayonaka ni Kawashita Yakusoku (PV)",
        "type": "pv",
        "url": "https://www.youtube.com/watch?v=yuQvijmGxH4",
        "platform": "youtube",
        "release_date": "2001-10-30",
        "song": "mayonaka-yakusoku",
        "concert": None,
        "quality": "official",
        "verification_status": "verified",
        "notes": "Official PV on @Malice_Mizer_Official YouTube channel.",
    },
    {
        "id": "garnet-pv",
        "title_ja": "Garnet～禁断の園へ～",
        "title_en": "Garnet (PV)",
        "type": "pv",
        "url": "https://www.youtube.com/watch?v=0JuOFzVgeUU",
        "platform": "youtube",
        "release_date": "2001-11-30",
        "song": "garnet",
        "concert": None,
        "quality": "official",
        "verification_status": "verified",
        "notes": "Official PV on @Malice_Mizer_Official YouTube channel.",
    },
]


def seed_videos() -> None:
    for video in VIDEOS:
        write(
            DATA / "videos" / f"{video['id']}.yaml",
            {**video, "changelog": changelog(f"Seed entry for {video['title_en']}")},
        )


REFERENCES = [
    {
        "id": "malice-mizer-info-videos",
        "title": "MALICE MIZER Info — Video Releases",
        "type": "website",
        "url": "https://www.malice-mizer.info/videos",
        "notes": "Fan-maintained videoography reference.",
    },
    {
        "id": "vkgy-discography",
        "title": "vkgy (ブイケージ) — Malice Mizer",
        "type": "website",
        "url": "https://www.jrock.gy/artists/malice-mizer/",
        "notes": "Discography and song cross-reference.",
    },
]


def seed_references() -> None:
    for ref in REFERENCES:
        write(DATA / "references" / f"{ref['id']}.yaml", ref)


def main() -> None:
    seed_songs()
    seed_albums()
    seed_singles()
    seed_concerts()
    seed_videos()
    seed_references()
    print("Generated music seed data.")


if __name__ == "__main__":
    main()
