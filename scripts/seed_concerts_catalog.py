#!/usr/bin/env python3
"""Seed the full Malice Mizer concert catalog into data/concerts/ and data/venues/."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TODAY = "2026-07-06"
SOURCE_NOTES = (
    "Official: http://malice-mizer.co.jp/History.html · "
    "Cantavanda: https://cantavanda.com/malice-mizer/about-malice-mizer/concert-history/"
)

venues: dict[str, dict] = {}
concerts: list[dict] = []


def changelog(notes: str) -> list[dict]:
    return [{"date": TODAY, "action": "created", "source": "concert_catalog_seed", "notes": notes}]


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def register_venue(
    slug: str,
    name_ja: str,
    name_en: str,
    city: str,
    prefecture: str | None = "Tokyo",
    country: str = "Japan",
    notes: str = "",
) -> str:
    venues[slug] = {
        "id": slug,
        "name_ja": name_ja,
        "name_en": name_en,
        "city": city,
        "prefecture": prefecture,
        "country": country,
        "notes": notes,
    }
    return slug


def members_for(date: str) -> list[str]:
    if date >= "2018-01-01":
        return ["mana", "kozi", "yuki"]
    if date >= "2000-08-01":
        return ["mana", "kozi", "yuki", "klaha"]
    if date >= "1995-10-01":
        return ["mana", "kozi", "yuki", "kami", "gackt"]
    if date >= "1993-03-17":
        return ["mana", "kozi", "yuki", "tetsu", "kami"]
    return ["mana", "kozi", "yuki", "tetsu", "gaz"]


def add_concert(
    date: str,
    slug: str,
    venue_slug: str | None,
    event_en: str,
    *,
    event_ja: str | None = None,
    type: str = "live",
    tour: str | None = None,
    members: list[str] | None = None,
    performances: list[dict] | None = None,
    setlist: list[str] | None = None,
    verification_status: str = "verified",
    source_notes: str = SOURCE_NOTES,
    notes: str = "",
) -> None:
    concerts.append(
        {
            "id": f"{date}-{slug}",
            "date": date,
            "date_precision": "day",
            "venue": venue_slug,
            "event_name_ja": event_ja,
            "event_name_en": event_en,
            "type": type,
            "tour": tour,
            "setlist": setlist or [],
            "members_present": members if members is not None else members_for(date),
            "verification_status": verification_status,
            "source_notes": source_notes,
            "performances": performances or [],
            "notes": notes,
            "changelog": changelog(f"Catalog entry {date} {event_en}"),
        }
    )


def define_venues() -> None:
    register_venue("meguro-rockmaykan", "目黒鹿鳴館", "Meguro Rockmaykan", "Tokyo")
    register_venue("ichikawa-club-gio", "市川 CLUB GIO", "Ichikawa CLUB GIO", "Ichikawa", "Chiba")
    register_venue("shinjuku-loft", "新宿 LOFT", "Shinjuku LOFT", "Tokyo")
    register_venue("koenji-lazy-ways", "高円寺 LAZY WAYS", "Koenji LAZY WAYS", "Tokyo")
    register_venue("yokohama-monster", "横浜 MONSTER", "Yokohama MONSTER", "Yokohama", "Kanagawa")
    register_venue("shimokitazawa-shelter", "下北沢 SHELTER", "Shimokitazawa SHELTER", "Tokyo")
    register_venue("yoyogi-chocolate-city", "代々木 CHOCOLATE CITY", "Yoyogi CHOCOLATE CITY", "Tokyo")
    register_venue("nichifutsu-kaikan", "日仏会館", "Nichifutsu Kaikan", "Tokyo")
    register_venue("osaka-namba-rockets", "大阪 難波 ROCKETS", "Osaka Namba ROCKETS", "Osaka", "Osaka")
    register_venue("nagoya-diamond-hall", "名古屋 DIAMOND HALL", "Nagoya DIAMOND HALL", "Nagoya", "Aichi")
    register_venue("harajuku-ruido", "原宿 RUIDO", "Harajuku RUIDO", "Tokyo")
    register_venue("shinjuku-antiknock", "新宿 ANTIKNOCK", "Shinjuku ANTIKNOCK", "Tokyo")
    register_venue("shibuya-la-mama", "渋谷 La.mama", "Shibuya La.mama", "Tokyo")
    register_venue("ibaraki-light-house", "茨城 LIGHT HOUSE", "Ibaraki LIGHT HOUSE", "Mito", "Ibaraki")
    register_venue("niigata-junk-box", "新潟 JUNK BOX", "Niigata JUNK BOX", "Niigata", "Niigata")
    register_venue("nagano-j", "長野 J", "Nagano J", "Nagano", "Nagano")
    register_venue("kawasaki-club-citta", "川崎 CLUB CITTA'", "Kawasaki CLUB CITTA'", "Kawasaki", "Kanagawa")
    register_venue("osaka-shinsaibashi-muse-hall", "大阪 心斎橋 MUSE HALL", "Osaka Shinsaibashi MUSE HALL", "Osaka", "Osaka")
    register_venue("meguro-live-station", "目黒 Live Station", "Meguro Live Station", "Tokyo")
    register_venue("sapporo-messe-hall", "札幌 MESSE HALL", "Sapporo MESSE HALL", "Sapporo", "Hokkaido")
    register_venue("sendai-kimachi-yamaha-hall", "仙台 木町 YAMAHA HALL", "Sendai Kimachi YAMAHA HALL", "Sendai", "Miyagi")
    register_venue("nagoya-music-farm", "名古屋 MUSIC FARM", "Nagoya MUSIC FARM", "Nagoya", "Aichi")
    register_venue("okayama-pepperland", "岡山 PEPPERLAND", "Okayama PEPPERLAND", "Okayama", "Okayama")
    register_venue("hiroshima-namiki-junction", "広島 NAMIKI JUNCTION", "Hiroshima NAMIKI JUNCTION", "Hiroshima", "Hiroshima")
    register_venue("oita-tops", "大分 TOP'S", "Oita TOP'S", "Oita", "Oita")
    register_venue("hakata-be-1", "博多 Be-1", "Hakata Be-1", "Fukuoka", "Fukuoka")
    register_venue("kochi-caravan-sary", "高知 CARAVAN SARY", "Kochi CARAVAN SARY", "Kochi", "Kochi")
    register_venue("maebashi-rattan", "前橋 RATTAN", "Maebashi RATTAN", "Maebashi", "Gunma")
    register_venue("sendai-birdland", "仙台 BIRDLAND", "Sendai BIRDLAND", "Sendai", "Miyagi")
    register_venue("niigata-o-do", "新潟 O-DO", "Niigata O-DO", "Niigata", "Niigata")
    register_venue("shibuya-on-air-west", "渋谷 ON AIR WEST", "Shibuya ON AIR WEST", "Tokyo")
    register_venue("alinnos", "ALINNOS", "ALINNOS", "Tokyo")
    register_venue("nagoya-heartland", "名古屋 HEARTLAND", "Nagoya HEARTLAND", "Nagoya", "Aichi")
    register_venue("osaka-wohol", "大阪 W'OHOL", "Osaka W'OHOL", "Osaka", "Osaka")
    register_venue("ikebukuro-cyber", "池袋 CYBER", "Ikebukuro CYBER", "Tokyo")
    register_venue("kumamoto-jango", "熊本 JANGO", "Kumamoto JANGO", "Kumamoto", "Kumamoto")
    register_venue("sendai-macana", "仙台 MACANA", "Sendai MACANA", "Sendai", "Miyagi")
    register_venue("kyoto-muse-hall", "京都 MUSE HALL", "Kyoto MUSE HALL", "Kyoto", "Kyoto")
    register_venue("hiroshima-bad-lands", "広島 BAD LANDS", "Hiroshima BAD LANDS", "Hiroshima", "Hiroshima")
    register_venue("matsuyama-salon-kitty", "松山 SALON KITTY", "Matsuyama SALON KITTY", "Matsuyama", "Ehime")
    register_venue("nippong-seinenkan", "日本青年館", "Nippon Seinenkan", "Tokyo")
    register_venue("osaka-merpark-hall", "大阪 メルパルクホール", "Osaka Merpark Hall", "Osaka", "Osaka")
    register_venue("shibuya-public-hall", "渋谷公会堂", "Shibuya Public Hall", "Tokyo")
    register_venue("akasaka-blitz", "赤坂 BLITZ", "Akasaka BLITZ", "Tokyo")
    register_venue("sapporo-penny-rain-24", "札幌 PENNY RAIN 24", "Sapporo Penny Rain 24", "Sapporo", "Hokkaido")
    register_venue("niigata-phase", "新潟 PHASE", "Niigata PHASE", "Niigata", "Niigata")
    register_venue("kanazawa-az", "金沢 AZ", "Kanazawa AZ", "Kanazawa", "Ishikawa")
    register_venue("kobe-chicken-george", "神戸 CHICKEN GEORGE", "Kobe Chicken George", "Kobe", "Hyogo")
    register_venue("osaka-imp-hall", "大阪 IMP HALL", "Osaka IMP Hall", "Osaka", "Osaka")
    register_venue("fukuoka-logos", "福岡 LOGOS", "Fukuoka LOGOS", "Fukuoka", "Fukuoka")
    register_venue("hibiya-open-air", "日比谷野外音楽堂", "Hibiya Open-Air Music Hall", "Tokyo")
    register_venue("aichi-kinro-kaikan", "愛知勤労会館", "Aichi Kinro Kaikan", "Nagoya", "Aichi")
    register_venue("osaka-kosei-nenkin-kaikan", "大阪厚生年金会館", "Osaka Kosei Nenkin Kaikan", "Osaka", "Osaka")
    register_venue("nippon-budokan", "日本武道館", "Nippon Budokan", "Tokyo")
    register_venue("nissin-power-station", "日清パワーステーション", "Nissin Power Station", "Tokyo")
    register_venue("ichikawa-cultural-hall", "市川市文化会館", "Ichikawa City Cultural Hall", "Ichikawa", "Chiba")
    register_venue("sapporo-education-culture-hall", "札幌市教育文化会館", "Sapporo Education & Culture Hall", "Sapporo", "Hokkaido")
    register_venue("sendai-civic-auditorium", "仙台市民会館", "Sendai Civic Auditorium", "Sendai", "Miyagi")
    register_venue("niigata-terusa", "新潟テルサ", "Niigata TERUSA", "Niigata", "Niigata")
    register_venue("ibaraki-prefectural-culture-center", "茨城県立県民文化センター", "Ibaraki Prefectural Culture Center", "Mito", "Ibaraki")
    register_venue("nagoya-civic-auditorium", "名古屋市民会館", "Nagoya Civic Auditorium", "Nagoya", "Aichi")
    register_venue("hiroshima-asteel", "広島アステール", "Hiroshima ASTEEL", "Hiroshima", "Hiroshima")
    register_venue("kobe-international-memorial-hall", "神戸国際会館", "Kobe International Memorial Hall", "Kobe", "Hyogo")
    register_venue("fukuoka-civic-auditorium", "福岡市民会館", "Fukuoka Civic Auditorium", "Fukuoka", "Fukuoka")
    register_venue("ehime-prefectural-culture-center", "愛媛県民文化会館", "Ehime Prefectural Culture Center", "Matsuyama", "Ehime")
    register_venue("yokohama-arena", "横浜アリーナ", "Yokohama Arena", "Yokohama", "Kanagawa")
    register_venue("sendai-youth-culture-center", "仙台市青年文化センター", "Sendai Youth Culture Center", "Sendai", "Miyagi")
    register_venue("zepp-sapporo", "Zepp SAPPORO", "Zepp SAPPORO", "Sapporo", "Hokkaido")
    register_venue("fukuoka-momochi-palace", "福岡ももちパレス", "Fukuoka Momochi Palace", "Fukuoka", "Fukuoka")
    register_venue("hiroshima-asteel-plaza", "広島アステールプラザ", "Hiroshima ASTEEL Plaza", "Hiroshima", "Hiroshima")
    register_venue("nagoya-civic-auditorium-medium", "名古屋市民会館（中）", "Nagoya Civic Auditorium (Medium)", "Nagoya", "Aichi")
    register_venue("zepp-osaka", "Zepp OSAKA", "Zepp OSAKA", "Osaka", "Osaka")
    register_venue("zepp-tokyo", "Zepp Tokyo", "Zepp Tokyo", "Tokyo")
    register_venue("shibuya-ax", "SHIBUYA-AX", "Shibuya AX", "Tokyo")
    register_venue("toyosu-pit", "豊洲PIT", "Toyosu PIT", "Tokyo")
    register_venue("tokyo-dome", "東京ドーム", "Tokyo Dome", "Tokyo")


LESPACE = [
    {
        "url": "https://archive.org/details/malice-mizer-merveilles-lespace-full-live",
        "platform": "archive_org",
        "quality": "pro_shot",
        "title": "merveilles l'espace (Internet Archive)",
        "notes": "Official concert film; Budokan 1998-04-01 and Yokohama Arena 1998-07-22.",
    },
    {
        "url": "https://www.youtube.com/watch?v=94gn00m6rf4",
        "platform": "youtube",
        "quality": "pro_shot",
        "title": "merveilles l'espace (YouTube)",
        "notes": "Fan upload of official VHS/DVD edit.",
    },
]


def define_concerts() -> None:
    # --- 1992 ---
    add_concert("1992-10-31", "first-live", "meguro-rockmaykan", "First live", event_ja="ファーストライブ", notes="Sans Logique demo distributed.")
    add_concert("1992-11-16", "indie-bill", "ichikawa-club-gio", "Indie live")
    add_concert("1992-11-24", "indie-bill", "shinjuku-loft", "Indie live")
    add_concert("1992-12-30", "indie-bill", "koenji-lazy-ways", "Indie live")
    add_concert("1992-12-31", "indie-bill", "yokohama-monster", "Indie live")

    # --- 1993 ---
    add_concert("1993-01-15", "indie-live", "meguro-rockmaykan", "Indie live")
    add_concert("1993-02-05", "indie-live", "shimokitazawa-shelter", "Indie live")
    add_concert("1993-02-20", "indie-live", "ichikawa-club-gio", "Indie live")
    add_concert("1993-03-06", "indie-live", "shinjuku-loft", "Indie live")
    add_concert("1993-03-11", "indie-live", "meguro-rockmaykan", "Indie live")
    add_concert("1993-03-15", "gaz-last-live", "yoyogi-chocolate-city", "Gaz's last live", notes="Drummer Gaz departs.")
    add_concert("1993-03-17", "kami-joins", "yokohama-monster", "Kami joins", notes="Drummer Kami joins.")
    add_concert("1993-03-27", "shock-age", "nichifutsu-kaikan", "SHOCK AGE event", type="festival")
    add_concert("1993-03-29", "indie-live", "meguro-rockmaykan", "Indie live")
    add_concert("1993-04-05", "first-osaka", "osaka-namba-rockets", "First Osaka live", notes="Sadness demo distributed.")
    add_concert("1993-04-06", "shock-age", "nagoya-diamond-hall", "SHOCK AGE event", type="festival")
    add_concert("1993-04-11", "indie-live", "yokohama-monster", "Indie live")
    add_concert("1993-04-15", "indie-live", "harajuku-ruido", "Indie live")
    add_concert("1993-05-03", "indie-live", "ichikawa-club-gio", "Indie live")
    add_concert("1993-05-22", "indie-live", "shinjuku-antiknock", "Indie live")
    add_concert("1993-06-20", "indie-live", "meguro-rockmaykan", "Indie live")
    add_concert("1993-07-18", "indie-live", "shinjuku-loft", "Indie live")
    add_concert("1993-07-26", "indie-live", "shibuya-la-mama", "Indie live")

    tour = "seductive-1993"
    for date, venue_slug in [
        ("1993-08-09", "yokohama-monster"),
        ("1993-08-11", "osaka-namba-rockets"),
        ("1993-08-13", "nagoya-music-farm"),
        ("1993-08-17", "ibaraki-light-house"),
        ("1993-08-19", "niigata-junk-box"),
        ("1993-08-21", "nagano-j"),
        ("1993-08-27", "kawasaki-club-citta"),
    ]:
        add_concert(date, "seductive-tour", venue_slug, "Se·duc·tive Tour", tour=tour)

    add_concert(
        "1993-09-13",
        "club-gio",
        "ichikawa-club-gio",
        "Club Gio live",
        notes="Lafflesia live recording on The 1th Anniversary demo.",
        performances=[
            {
                "url": "https://www.discogs.com/release/2610648-Malice-Mizer-The-1th-Anniversary",
                "platform": "other",
                "quality": "audience",
                "title": "The 1th Anniversary demo (Discogs)",
            }
        ],
    )
    add_concert("1993-10-12", "first-anniversary", "meguro-rockmaykan", "First anniversary live", event_ja="1周年記念LIVE", notes="The 1th Anniversary demo distributed.")
    add_concert("1993-10-24", "indie-live", "meguro-rockmaykan", "Indie live")
    add_concert("1993-11-03", "higeki-vol1", "shinjuku-loft", "Dai Ichiya Higeki no Bansan Vol.1", event_ja="第一夜 悲劇の晩餐 Vol.1", type="event")
    add_concert("1993-11-19", "indie-live", "yokohama-monster", "Indie live")
    add_concert("1993-12-15", "indie-live", "meguro-live-station", "Indie live")
    add_concert("1993-12-29", "katharsis-vol3", "osaka-shinsaibashi-muse-hall", "KATHARSIS Vol.3", type="festival")
    add_concert("1993-12-30", "72h-monster", "yokohama-monster", "72h BATTLE OF MONSTER", type="festival")

    # --- 1994 ---
    add_concert("1994-01-22", "higeki-vol2", "shinjuku-loft", "Dai Niya Higeki no Bansan Vol.2", event_ja="第二夜 悲劇の晩餐 Vol.2", type="event")
    add_concert("1994-02-11", "indie-live", "ichikawa-club-gio", "Indie live")
    add_concert("1994-03-11", "indie-live", "meguro-rockmaykan", "Indie live")
    add_concert("1994-04-06", "indie-live", "meguro-rockmaykan", "Indie live")
    add_concert("1994-04-24", "indie-live", "meguro-rockmaykan", "Indie live")
    add_concert("1994-05-01", "indie-live", "meguro-live-station", "Indie live")
    add_concert("1994-06-04", "higeki-vol3", "shinjuku-loft", "Dai San'ya Higeki no Bansan Vol.3", event_ja="第三夜 悲劇の晩餐 Vol.3", type="event")

    tour = "cher-de-memoire-1994"
    for date, venue_slug, label in [
        ("1994-07-30", "shinjuku-loft", "CD release commemorative oneman (SOLD OUT)"),
        ("1994-08-03", "sapporo-messe-hall", "Cher de memoire Tour"),
        ("1994-08-05", "sendai-kimachi-yamaha-hall", "Cher de memoire Tour"),
        ("1994-08-08", "nagoya-music-farm", "Cher de memoire Tour"),
        ("1994-08-10", "osaka-namba-rockets", "Cher de memoire Tour"),
        ("1994-08-12", "okayama-pepperland", "Cher de memoire Tour"),
        ("1994-08-13", "hiroshima-namiki-junction", "Cher de memoire Tour"),
        ("1994-08-15", "oita-tops", "Cher de memoire Tour"),
        ("1994-08-17", "hakata-be-1", "Cher de memoire Tour"),
        ("1994-08-19", "kochi-caravan-sary", "Cher de memoire Tour"),
        ("1994-08-22", "meguro-rockmaykan", "Cher de memoire Tour"),
        ("1994-08-24", "nagano-j", "Cher de memoire Tour"),
        ("1994-08-26", "niigata-junk-box", "Cher de memoire Tour"),
        ("1994-08-28", "ibaraki-light-house", "Cher de memoire Tour"),
        ("1994-08-30", "maebashi-rattan", "Cher de memoire Tour"),
        ("1994-09-23", "meguro-rockmaykan", "Cher de memoire Tour final (SOLD OUT)"),
    ]:
        add_concert(date, "cher-de-memoire", venue_slug, label, event_ja="Cher de memoire Tour 1994", tour=tour, type="oneman" if "oneman" in label else "live")

    add_concert("1994-10-23", "second-anniversary", "meguro-rockmaykan", "Second anniversary live (SOLD OUT)", event_ja="2周年記念LIVE", type="oneman")
    add_concert("1994-11-17", "higeki-vol4", "shinjuku-loft", "Dai Yon'ya Higeki no Bansan Vol.4", event_ja="第四夜 悲劇の晩餐 Vol.4", type="event")

    tour = "cher-de-memoire-ii-1994"
    for date, venue_slug, label in [
        ("1994-12-05", "nagoya-music-farm", "Cher de memoire II oneman"),
        ("1994-12-07", "osaka-namba-rockets", "Cher de memoire II oneman"),
        ("1994-12-10", "okayama-pepperland", "Cher de memoire II oneman"),
        ("1994-12-12", "hakata-be-1", "Cher de memoire II oneman"),
        ("1994-12-17", "sendai-birdland", "Cher de memoire II oneman"),
        ("1994-12-19", "nagano-j", "Cher de memoire II oneman"),
        ("1994-12-21", "niigata-o-do", "Cher de memoire II — RISKY GAME event"),
    ]:
        add_concert(date, "cher-de-memoire-ii", venue_slug, label, tour=tour, type="oneman")

    add_concert(
        "1994-12-27",
        "tetsu-final",
        "meguro-rockmaykan",
        "Cher de memoire II tour final (SOLD OUT)",
        event_ja="Vo.TETSU脱退",
        tour=tour,
        type="oneman",
        notes="Tetsu's last performance with Malice Mizer.",
        performances=[
            {
                "url": "https://archive.org/details/malice-mizer-cher-de-memoire-ii-final-tetsu-last-live-at-meguro-rock-may-27.12.1994",
                "platform": "archive_org",
                "quality": "audience",
                "title": "Cher de memoire II final (Internet Archive)",
            }
        ],
    )

    # --- 1995 ---
    add_concert("1995-09-22", "higeki-vol5", "shinjuku-loft", "第五夜 悲劇の晩餐 Vol.5", type="event")
    add_concert(
        "1995-10-10",
        "gackt-debut",
        "shibuya-on-air-west",
        "Gackt debut oneman — Karei naru Fukkatsugeki",
        event_ja="華麗なる復活劇",
        type="oneman",
        notes="SOLD OUT; 600 attendees.",
    )
    add_concert("1995-12-09", "first-single-event", "alinnos", "1st single release commemoration", type="event", notes="Signing event; not a full concert.")

    tour = "sans-retour-voyage-1995"
    for date, venue_slug in [
        ("1995-11-01", "nagano-j"),
        ("1995-11-03", "niigata-o-do"),
        ("1995-11-06", "sendai-kimachi-yamaha-hall"),
        ("1995-11-12", "osaka-namba-rockets"),
        ("1995-11-14", "hakata-be-1"),
        ("1995-11-16", "hiroshima-bad-lands"),
        ("1995-11-18", "matsuyama-salon-kitty"),
        ("1995-11-20", "kyoto-muse-hall"),
        ("1995-11-22", "nagoya-music-farm"),
    ]:
        add_concert(date, "sans-retour-voyage", venue_slug, "Sans retour Voyage 1995", tour=tour, type="oneman")

    # --- 1996 ---
    for date, venue_slug, label in [
        ("1996-01-06", "shibuya-on-air-west", "Oneman (SOLD OUT)"),
        ("1996-01-09", "nagoya-heartland", "Live"),
        ("1996-01-11", "osaka-wohol", "Live"),
        ("1996-03-17", "nagoya-diamond-hall", "SHOCK WAVE event"),
        ("1996-03-24", "osaka-wohol", "Live"),
        ("1996-03-31", "shibuya-on-air-west", "Tokyo 3 Days in Club House (SOLD OUT)"),
        ("1996-05-03", "meguro-rockmaykan", "Oneman (SOLD OUT)"),
        ("1996-05-04", "shinjuku-loft", "Oneman (SOLD OUT)"),
        ("1996-05-05", "ikebukuro-cyber", "Oneman (SOLD OUT)"),
        ("1996-06-23", "shibuya-on-air-west", "Voyage release commemoration (SOLD OUT)"),
    ]:
        add_concert(date, "voyage-era", venue_slug, label)

    tour = "sans-retour-voyage-deux-1996"
    for date, venue_slug, sold in [
        ("1996-07-20", "nagoya-heartland", True),
        ("1996-07-22", "kyoto-muse-hall", True),
        ("1996-07-24", "hiroshima-namiki-junction", False),
        ("1996-07-26", "okayama-pepperland", False),
        ("1996-07-29", "kumamoto-jango", False),
        ("1996-07-31", "hakata-be-1", False),
        ("1996-08-06", "osaka-wohol", False),
        ("1996-08-11", "kawasaki-club-citta", False),
        ("1996-08-23", "nagano-j", True),
        ("1996-08-25", "sendai-macana", True),
        ("1996-08-28", "niigata-o-do", False),
    ]:
        note = "SOLD OUT" if sold else ""
        add_concert(date, "sans-retour-deux", venue_slug, "Sans retour Voyage deux 1996", tour=tour, type="oneman", notes=note)

    add_concert("1996-11-08", "kigeki-vol1", "shibuya-on-air-west", "喜劇の晩餐 Vol.1", type="event", notes="SOLD OUT")
    add_concert("1996-11-09", "fc-event-1", "ikebukuro-cyber", "First fan club event", type="event")
    add_concert("1996-11-17", "school-festival", None, "Mejiro Gakuen school festival", type="event", notes="800 seats; SOLD OUT.")
    add_concert("1996-12-27", "fc-event-2", "shibuya-on-air-west", "Second fan club event", type="event")

    # --- 1997 ---
    tour = "sans-retour-voyage-derniere"
    add_concert("1997-01-10", "derniere", "nippong-seinenkan", "Sans retour Voyage derniere", tour=tour, type="oneman", notes="SOLD OUT")
    add_concert("1997-03-24", "derniere-osaka", "osaka-merpark-hall", "Sans retour Voyage derniere (added)", tour=tour, type="oneman", notes="SOLD OUT")
    add_concert(
        "1997-04-01",
        "derniere-final",
        "shibuya-public-hall",
        "Sans retour Voyage derniere — indies farewell",
        event_ja="インディーズラスト公演",
        tour=tour,
        type="oneman",
        notes="SOLD OUT; filmed for VHS/DVD.",
        performances=[
            {
                "url": "https://www.discogs.com/master/1222590-Malice-Mizer-Sans-Retour-Voyage-Derniere-Encoure-Une-Fois",
                "platform": "other",
                "quality": "pro_shot",
                "title": "Sans retour Voyage derniere VHS/DVD (Discogs)",
            }
        ],
    )

    tour = "pays-de-merveilles-1997"
    for date, venue_slug in [
        ("1997-07-20", "akasaka-blitz"),
        ("1997-07-21", "akasaka-blitz"),
        ("1997-07-25", "sendai-macana"),
        ("1997-07-26", "sendai-macana"),
        ("1997-07-28", "sapporo-penny-rain-24"),
        ("1997-07-30", "niigata-phase"),
        ("1997-08-01", "kanazawa-az"),
        ("1997-08-03", "kobe-chicken-george"),
        ("1997-08-19", "nagoya-diamond-hall"),
        ("1997-08-21", "kyoto-muse-hall"),
        ("1997-08-22", "osaka-imp-hall"),
        ("1997-08-24", "hiroshima-namiki-junction"),
        ("1997-08-26", "fukuoka-logos"),
    ]:
        add_concert(date, "pays-de-merveilles", venue_slug, "Standing Tour '97 Pays de merveilles", tour=tour, type="oneman", notes="SOLD OUT")

    add_concert("1997-10-10", "deuxieme-anniversaire", "hibiya-open-air", "deuxieme anniversaire — Karei naru Fukkatsugeki", type="festival")
    add_concert("1997-10-11", "pays-de-merveilles-hibiya", "hibiya-open-air", "pays de merveilles — Kuuhaku no Shunkan no Tobira", type="festival")

    tour = "ville-de-merveilles-1997"
    for date, venue_slug in [
        ("1997-12-22", "aichi-kinro-kaikan"),
        ("1997-12-24", "osaka-kosei-nenkin-kaikan"),
        ("1997-12-28", "shibuya-public-hall"),
        ("1997-12-29", "shibuya-public-hall"),
    ]:
        add_concert(date, "ville-de-merveilles", venue_slug, "Ville de merveilles — Toumei no Rasen", tour=tour, type="oneman", notes="SOLD OUT")

    # --- 1998 ---
    add_concert("1998-03-24", "secret-live", "nissin-power-station", "Secret live — Human Science High Society Syndrome", type="secret")
    add_concert(
        "1998-04-01",
        "merveilles-budokan",
        "nippon-budokan",
        "merveilles ~Shuuen to kisuu~",
        event_ja="merveilles ～終焉と帰趨～",
        type="oneman",
        tour="merveilles-1998",
        notes="SOLD OUT in 2 minutes after album release.",
        performances=LESPACE,
    )

    tour = "merveilles-1998"
    for date, venue_slug in [
        ("1998-05-23", "ichikawa-cultural-hall"),
        ("1998-05-29", "sapporo-education-culture-hall"),
        ("1998-06-01", "sendai-civic-auditorium"),
        ("1998-06-03", "niigata-terusa"),
        ("1998-06-14", "ibaraki-prefectural-culture-center"),
        ("1998-06-18", "nagoya-civic-auditorium"),
        ("1998-06-20", "osaka-kosei-nenkin-kaikan"),
        ("1998-06-21", "osaka-kosei-nenkin-kaikan"),
        ("1998-06-23", "hiroshima-asteel"),
        ("1998-06-25", "kobe-international-memorial-hall"),
        ("1998-06-27", "fukuoka-civic-auditorium"),
        ("1998-06-29", "ehime-prefectural-culture-center"),
    ]:
        add_concert(date, "merveilles-tour", venue_slug, "merveilles ~Shuuen to kisuu~ tour", event_ja="merveilles ～終焉と帰趨～", tour=tour, type="oneman", notes="SOLD OUT")

    add_concert(
        "1998-07-22",
        "merveilles-yokohama-arena",
        "yokohama-arena",
        "merveilles ~Shuuen to kisuu~ — Yokohama Arena",
        tour=tour,
        type="oneman",
        notes="Gackt's last performance with Malice Mizer.",
        performances=LESPACE,
    )

    # --- 1999 FC events ---
    tour = "fc-system-file-002-1999"
    for date, venue_slug in [
        ("1999-04-03", "shibuya-public-hall"),
        ("1999-04-04", "shibuya-public-hall"),
        ("1999-04-06", "sendai-youth-culture-center"),
        ("1999-04-08", "zepp-sapporo"),
        ("1999-04-12", "fukuoka-momochi-palace"),
        ("1999-04-14", "hiroshima-asteel-plaza"),
        ("1999-04-15", "nagoya-civic-auditorium-medium"),
        ("1999-04-18", "zepp-osaka"),
        ("1999-04-20", "niigata-phase"),
    ]:
        add_concert(
            date,
            "fc-system-file-002",
            venue_slug,
            "FC event — Human Science High Society Syndrome",
            tour=tour,
            type="event",
            members=["mana", "kozi", "yuki", "kami"],
        )

    # --- 2000 Budokan ---
    tour = "bara-no-seidou-2000"
    for date, slug, title_en, title_ja in [
        ("2000-08-31", "night1", "Bara no Seidou — Night 1: Saikai no Bara", "第一夜 再会の薔薇"),
        ("2000-09-01", "night2", "Bara no Seidou — Night 2: Yakusoku no Bara", "第二夜 約束の薔薇"),
    ]:
        add_concert(
            date,
            slug,
            "nippon-budokan",
            title_en,
            event_ja=title_ja,
            tour=tour,
            type="oneman",
            notes="Klaha officially inducted; theatrical two-night Budokan live.",
        )
    add_concert("2000-11-19", "fc-societe", "zepp-tokyo", "FC event — Société de parenté", type="event")

    # --- 2001 Gardenia tour ---
    tour = "gardenia-2001"
    for date, venue_slug in [
        ("2001-07-02", "shibuya-ax"),
        ("2001-07-03", "shibuya-ax"),
        ("2001-07-05", "zepp-osaka"),
        ("2001-07-09", "akasaka-blitz"),
    ]:
        add_concert(
            date,
            "gardenia-standing",
            venue_slug,
            "Gardenia ~yoake no teien~ standing live",
            event_ja="Gardenia～夜明けの庭園～",
            tour=tour,
            type="oneman",
        )

    # --- 2018 25th anniversary ---
    ds6_performances = [
        {
            "url": "https://www.youtube.com/watch?v=1pXZotZCl-o",
            "platform": "youtube",
            "quality": "pro_shot",
            "title": "Deep Sanctuary VI (YouTube)",
            "notes": "Fan remaster of both nights; guest vocalists Shuji, KAMIJO, Hitomi.",
        },
        {
            "url": "https://www.discogs.com/release/13852986-Malice-Mizer-Deep-Sanctuary-VI-Live-At-Toyosu-Pit-September-9-Malice-Mizer-25th-Anniversary-Special",
            "platform": "other",
            "quality": "official",
            "title": "Deep Sanctuary VI Blu-ray/DVD (Discogs)",
        },
        {
            "url": "https://www.setlist.fm/setlist/malice-mizer/2018/toyosu-pit-tokyo-japan-1be9a548.html",
            "platform": "other",
            "quality": "unknown",
            "title": "Setlist.fm (2018-09-09)",
        },
    ]
    tour = "deep-sanctuary-vi-2018"
    add_concert(
        "2018-09-08",
        "deep-sanctuary-vi",
        "toyosu-pit",
        "Deep Sanctuary VI — MALICE MIZER 25th Anniversary Special",
        event_ja="Deep Sanctuary VI MALICE MIZER 25th Anniversary Special",
        tour=tour,
        type="festival",
        notes="Added show (announced 2018-06-08). Sakura on drums using Kami's kit.",
        performances=ds6_performances,
    )
    add_concert(
        "2018-09-09",
        "deep-sanctuary-vi",
        "toyosu-pit",
        "Deep Sanctuary VI — MALICE MIZER 25th Anniversary Special",
        event_ja="Deep Sanctuary VI MALICE MIZER 25th Anniversary Special",
        tour=tour,
        type="festival",
        notes="Official Blu-ray/DVD documents this date. Moi dix Mois and ZIZ also performed.",
        performances=ds6_performances,
    )


def seed_files() -> None:
    define_venues()
    define_concerts()

    for venue_data in venues.values():
        write(DATA / "venues" / f"{venue_data['id']}.yaml", venue_data)

    catalog_ids = {concert["id"] for concert in concerts}
    concerts_dir = DATA / "concerts"
    for path in concerts_dir.glob("*.yaml"):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        if doc.get("id") not in catalog_ids:
            path.unlink()

    for concert in concerts:
        write(concerts_dir / f"{concert['id']}.yaml", concert)


def main() -> None:
    seed_files()
    print(f"Seeded {len(venues)} venues and {len(concerts)} concerts.")


if __name__ == "__main__":
    main()
