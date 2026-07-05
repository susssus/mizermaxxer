#!/usr/bin/env python3
"""Repair song slugs created by Discogs sync (ASCII-only ids required)."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SONGS = ROOT / "data" / "songs"

# Discogs track title -> canonical slug
TITLE_SLUG: dict[str, str] = {
    "De Memoire": "de-memoire",
    "記憶と空": "kioku-to-sora",
    "エーゲ海に捧ぐ ~ The Vault Of Heaven": "aege-kai-ni-sasagu",
    "午後のささやき": "gogo-no-sasayaki",
    "魅惑のローマ": "mihwaku-no-roma",
    "Seraph": "seraph",
    "闇の彼方へ～": "yami-no-kanata-e",
    "追憶の破片～A Piece Of Broken Recollection～": "tsuioku-no-hahen",
    "Premier Amour": "premier-amour",
    "偽りのMusetté": "itsuwari-no-musette",
    "N.p.s N.g.s. ～No Pains No Gains～": "nps-ngs",
    "Claire～月の調べ～": "claire-tsuki-no-shirabe",
    "死の舞踏～A Romance Of The \"Cendrillon\"～": "shi-no-butou",
    "～前兆～": "zencho",
    "～De Merveilles": "de-merveilles",
    "Syunikiss～二度目の哀悼～": "syunikiss",
    "Brise": "brise",
    "エーゲ～過ぎ去りし風と共に～": "aege-sugisarishi-kaze",
    "Ju Te Veux": "ju-te-veux",
    "S-Conscious": "s-conscious",
    "Bois De Merveilles": "bois-de-merveilles",
    "薔薇に彩られた悪意と悲劇の幕開け": "bara-makuake",
    "聖なる刻　永遠の祈り": "seinaru-toki",
    "鏡の舞踏　幻惑の夜": "kagami-no-butou",
    "真夜中に交わした約束": "mayonaka-yakusoku",
    "真夜中に交わした約束～薔薇の婚礼～": "mayonaka-yakusoku",
    "薔薇の婚礼～真夜中に交わした約束～": "mayonaka-yakusoku",
    "血塗られた果実": "chi-nurareta-kajitsu",
    "地下水脈の迷路": "chikasuimyaku-no-meiro",
    "破誡の果て": "hakai-no-hate",
    "Prologue ～回想～": "prologue-kaisou",
    "Après-midi ～あるパリの午後で～": "apres-midi-paris",
    "森の中の天使": "mori-no-naka-no-tenshi",
    "幻想楽園": "gensou-rakuen",
    "再会": "saikai",
    "月下の夜想曲 de l'image": "gekka-de-limage",
    "Le ciel ～空白の彼方へ～ (Instrumental)": "le-ciel-instrumental",
    "白い肌に狂う愛と哀しみの輪舞 (Instrumental)": "shiroi-hada-instrumental",
    "真夜中に交わした約束 (Instrumental)": "mayonaka-yakusoku-instrumental",
    "聖なる刻 永遠の祈り": "seinaru-toki",
    "鏡の舞踏 幻惑の夜": "kagami-no-butou",
    "追憶の破片": "tsuioku-no-hahen",
    "死の舞踏": "shi-no-butou",
    "前兆": "zencho",
    "再会": "saikai",
    "運命の出会い": "unmei-no-deai",
    "運命の出会": "unmei-no-deai",
    "幻想楽園": "gensou-rakuen",
    "ジレンマ": "jirenma",
    "終幕への扉": "shuumaku-e-no-tobira",
    "バロック": "baroque",
    "古のルーマニア": "ino-no-rumania",
    "目醒めの螺旋": "mezame-no-rasen",
    "波紋 / 協奏曲": "hamon-kyousoukyoku",
    "波紋／協奏曲": "hamon-kyousoukyoku",
    "薔薇の伝承 (序章)": "bara-no-densho-prologue",
    "薇の葬列": "bara-no-souretsu",
    "薔薇の洗礼": "bara-no-senrei",
    "崩壊序曲": "houkai-jokyoku",
    "記憶と空～再会そして約束～": "kioku-to-sora-saikai-yakusoku",
    "約束": "yakusoku",
    "ヴェル・エール～空白の瞬間の中で～": "bel-air",
    "ヴェル・エール~空白の瞬間の中で~": "bel-air",
    "ヴェル・エール〜空白の瞬間の中で〜": "bel-air",
    "ヴェルエール - 空白の瞬間の中で": "bel-air",
    "エーゲ〜過ぎ去りし風と共に〜": "aege-sugisarishi-kaze",
}

# bad slug -> good slug (from broken auto-slugify)
SLUG_RENAME: dict[str, str] = {
    "記憶と空": "kioku-to-sora",
    "エーゲ海に捧ぐ-the-vault-of-heaven": "aege-kai-ni-sasagu",
    "午後のささやき": "gogo-no-sasayaki",
    "魅惑のローマ": "mihwaku-no-roma",
    "syunikiss二度目の哀悼": "syunikiss",
    "エーゲ過ぎ去りし風と共に": "aege-sugisarishi-kaze",
    "闇の彼方へ": "yami-no-kanata-e",
    "追憶の破片a-piece-of-broken-recollection": "tsuioku-no-hahen",
    "偽りのmusetté": "itsuwari-no-musette",
    "nps-ngs-no-pains-no-gains": "nps-ngs",
    "claire月の調べ": "claire-tsuki-no-shirabe",
    "死の舞踏a-romance-of-the-cendrillon": "shi-no-butou",
    "前兆": "zencho",
    "薔薇に彩られた悪意と悲劇の幕開け": "bara-makuake",
    "聖なる刻-永遠の祈り": "seinaru-toki",
    "鏡の舞踏-幻惑の夜": "kagami-no-butou",
    "血塗られた果実": "chi-nurareta-kajitsu",
    "地下水脈の迷路": "chikasuimyaku-no-meiro",
    "破誡の果て": "hakai-no-hate",
    "prologue-回想": "prologue-kaisou",
    "après-midiあるパリの午後で": "apres-midi-paris",
    "森の中の天使": "mori-no-naka-no-tenshi",
    "幻想楽園": "gensou-rakuen",
    "再会": "saikai",
    "月下の夜想曲-de-limage": "gekka-de-limage",
    "le-ciel空白の彼方へ-instrumental": "le-ciel-instrumental",
    "白い肌に狂う愛と哀しみの輪舞-instrumental": "shiroi-hada-instrumental",
    "真夜中に交わした約束-instrumental": "mayonaka-yakusoku-instrumental",
    "真夜中に交わした約束": "mayonaka-yakusoku",
    "運命の出会い": "unmei-no-deai",
}


def ascii_slug(title: str) -> str:
    if title in TITLE_SLUG:
        return TITLE_SLUG[title]
    ascii_part = re.sub(r"[^\w\s-]", "", title, flags=re.UNICODE)
    slug = re.sub(r"[-\s]+", "-", ascii_part.strip().lower()).strip("-")
    return slug or "unknown-track"


def rename_song_files() -> None:
    for bad, good in SLUG_RENAME.items():
        src = SONGS / f"{bad}.yaml"
        dst = SONGS / f"{good}.yaml"
        if not src.exists():
            continue
        doc = yaml.safe_load(src.read_text(encoding="utf-8"))
        doc["id"] = good
        if dst.exists():
            src.unlink()
        else:
            dst.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
            src.unlink()
        print(f"  song rename: {bad} -> {good}")


def patch_references() -> None:
    for yaml_path in list((ROOT / "data" / "albums").glob("*.yaml")) + list(
        (ROOT / "data" / "singles").glob("*.yaml")
    ):
        doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        changed = False
        for track in doc.get("tracks", []):
            old = track.get("song")
            if old in SLUG_RENAME:
                track["song"] = SLUG_RENAME[old]
                changed = True
        for field in ("a_side", "b_side"):
            if doc.get(field) in SLUG_RENAME:
                doc[field] = SLUG_RENAME[doc[field]]
                changed = True
        if changed:
            yaml_path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
            print(f"  patched: {yaml_path.name}")


def recreate_missing_from_titles() -> None:
    """Ensure every referenced slug has a valid song file."""
    needed: dict[str, tuple[str, str]] = {}
    for title, slug in TITLE_SLUG.items():
        needed[slug] = (title, title)
    for yaml_path in list((ROOT / "data" / "albums").glob("*.yaml")) + list(
        (ROOT / "data" / "singles").glob("*.yaml")
    ):
        doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        for track in doc.get("tracks", []):
            slug = track["song"]
            if not (SONGS / f"{slug}.yaml").exists():
                needed[slug] = (slug, slug)
        for field in ("a_side", "b_side"):
            slug = doc.get(field)
            if slug and not (SONGS / f"{slug}.yaml").exists():
                needed[slug] = (slug, slug)

    for slug, (ja, en) in needed.items():
        path = SONGS / f"{slug}.yaml"
        if path.exists():
            continue
        if not re.match(r"^[a-z0-9-]+$", slug):
            continue
        doc = {
            "id": slug,
            "title_ja": ja,
            "title_en": en,
            "writers": ["mana"],
            "lyricists": [],
            "composers": ["mana"],
            "notes": "Catalogued from Discogs tracklist.",
        }
        path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(f"  created: {slug}")


def main() -> None:
    print("Repairing Discogs song slugs...")
    rename_song_files()
    patch_references()
    recreate_missing_from_titles()
    print("Done.")


if __name__ == "__main__":
    main()
