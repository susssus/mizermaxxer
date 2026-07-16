#!/usr/bin/env python3
"""Fill proposed_title_en/ja in the Discogs language audit, then apply to song YAML.

Rules:
- japanese: title_ja = Discogs; title_en = Romanization (Meaning)
- mixed: keep FR/EN segments; romanize JA segments; meaning of JA in parentheses
- french/english/other: keep Discogs form for both fields (no forced gloss)
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
AUDIT_PATH = Path(__file__).resolve().parent / "song_title_language_audit.yaml"
SONGS = ROOT / "data" / "songs"

# Romanization (Meaning) — Japanese / mixed only.
# Keys are song slugs. Values: (title_ja, title_en)
PROPOSED: dict[str, tuple[str, str]] = {
    # --- Shinwa ---
    "saikai": ("再会", "Saikai (Reunion)"),
    "unmei-no-deai": ("運命の出会い", "Unmei no Deai (Meeting with Fate)"),
    "mori-no-naka-no-tenshi": ("森の中の天使", "Mori no Naka no Tenshi (Angels in the Woods)"),
    # --- Bel Air / Gekka / Le Ciel (collection + singles) ---
    "bel-air": (
        "ヴェル・エール～空白の瞬間の中で～",
        "Bel Air ~Kuuhaku no Shunkan no Naka de~ (In a Blank Moment)",
    ),
    "gekka-no-yasoukyoku": ("月下の夜想曲", "Gekka no Yasoukyoku (Nocturne Under the Moon)"),
    "de-l-image": (
        "月下の夜想曲 De L’image",
        "Gekka no Yasoukyoku De L'Image (Nocturne Under the Moon)",
    ),
    "de-limage": (
        "月下の夜想曲 De L'Image",
        "Gekka no Yasoukyoku De L'Image (Nocturne Under the Moon)",
    ),
    "le-ciel": (
        "Le Ciel～空白の彼方へ～",
        "Le Ciel ~Kuuhaku no Kanata e~ (To the Blank Beyond)",
    ),
    "le-ciel-instrumental": (
        "Le Ciel～空白の彼方へ～ (Instrumental)",
        "Le Ciel ~Kuuhaku no Kanata e~ (To the Blank Beyond) (Instrumental)",
    ),
    # --- merveilles Japanese / mixed ---
    "aege-sugisarishi-kaze": (
        "エーゲ～過ぎ去りし風と共に～",
        "Aege ~Sugisarishi Kaze to Tomo ni~ (Aegean ~With the Wind That Passed~)",
    ),
    "syunikiss": (
        "Syunikiss～二度目の哀悼～",
        "Syunikiss ~Nidome no Aitou~ (Second Mourning)",
    ),
    # --- Memoire ---
    "kioku-to-sora": ("記憶と空", "Kioku to Sora (Memory and Sky)"),
    "the-vault-of-heaven": (
        "エーゲ海に捧ぐ ~ The Vault Of Heaven ~",
        "Aege Kai ni Sasagu ~ The Vault Of Heaven ~ (Dedicated to the Aegean Sea)",
    ),
    "aege-kai-ni-sasagu": (
        "エーゲ海に捧ぐ ~ The Vault Of Heaven ~",
        "Aege Kai ni Sasagu ~ The Vault Of Heaven ~ (Dedicated to the Aegean Sea)",
    ),
    "gogo-no-sasayaki": ("午後のささやき", "Gogo no Sasayaki (Afternoon Whisper)"),
    "mihwaku-no-roma": ("魅惑のローマ", "Miwaku no Roma (Enchanting Rome)"),
    "baroque": ("バロック", "Baroque"),
    # --- Voyage ---
    "yami-no-kanata-e": ("闇の彼方へ～", "Yami no Kanata e~ (To the Far Side of Darkness)"),
    "tsuioku-no-hahen": (
        "追憶の破片～A Piece Of Broken Recollection～",
        "Tsuioku no Hahen ~A Piece Of Broken Recollection~ (Fragments of Recollection)",
    ),
    "itsuwari-no-musette": ("偽りのMusetté", "Itsuwari no Musetté (False Musette)"),
    "claire-tsuki-no-shirabe": (
        "Claire～月の調べ～",
        "Claire ~Tsuki no Shirabe~ (Melody of the Moon)",
    ),
    "shi-no-butou": (
        '死の舞踏～A Romance Of The "Cendrillon"～',
        'Shi no Butou ~A Romance Of The "Cendrillon"~ (Dance of Death)',
    ),
    "zencho": ("～前兆～", "~Zencho~ (Omen)"),
    # --- Bara no Seidou ---
    "bara-makuake": (
        "薔薇に彩られた悪意と悲劇の幕開け",
        "Bara ni Irodorareta Akui to Higeki no Makuake "
        "(A Prelude of Malice and Tragedy Painted by the Rose)",
    ),
    "seinaru-toki": (
        "聖なる刻　永遠の祈り",
        "Seinaru Toki Eien no Inori (Holy Time, Eternal Prayer)",
    ),
    "kyomu-no-naka-de-no-yugi": (
        "虚無の中での遊戯",
        "Kyomu no Naka de no Yugi (Amusement in Nihilism)",
    ),
    "kagami-no-butou": (
        "鏡の舞踏　幻惑の夜",
        "Kagami no Butou Genwaku no Yoru (Mirror Dance, Night of Bewitchment)",
    ),
    "mayonaka-yakusoku": (
        "真夜中に交わした約束",
        "Mayonaka ni Kawashita Yakusoku (Promises Exchanged at Midnight)",
    ),
    "mayonaka-yakusoku-instrumental": (
        "真夜中に交わした約束 (Instrumental)",
        "Mayonaka ni Kawashita Yakusoku (Promises Exchanged at Midnight) (Instrumental)",
    ),
    "chi-nurareta-kajitsu": (
        "血塗られた果実",
        "Chi Nurareta Kajitsu (Blood-stained Fruit)",
    ),
    "chikasuimyaku-no-meiro": (
        "地下水脈の迷路",
        "Chikasuimyaku no Meiro (Labyrinth of Underground Rivers)",
    ),
    "hakai-no-hate": ("破誡の果て", "Hakai no Hate (Blasphemy's Culmination)"),
    "shiroi-hada": (
        "白い肌に狂う愛と哀しみの輪舞",
        "Shiroi Hada ni Kuruu Ai to Kanashimi no Rondo "
        "(Rondo of Love and Sadness Driven Mad by White Skin)",
    ),
    "shiroi-hada-instrumental": (
        "白い肌に狂う愛と哀しみの輪舞 (Instrumental)",
        "Shiroi Hada ni Kuruu Ai to Kanashimi no Rondo "
        "(Rondo of Love and Sadness Driven Mad by White Skin) (Instrumental)",
    ),
    "saikai-no-chi-to-bara": (
        "再会の血と薔薇",
        "Saikai no Chi to Bara (Blood and Roses of Reunion)",
    ),
    # --- Singles / other JA ---
    "uruwashii-kamen": (
        "麗しき仮面の招待状",
        "Uruwashiki Kamen no Shoutaijou (Invitation of the Beautiful Mask)",
    ),
    "ma-cherie": (
        "Ma Chérie～愛しい君へ～",
        "Ma Chérie ~Itoshii Kimi e~ (To My Beloved)",
    ),
    "ma-ch-rie": (
        "Ma Chérie ~愛しい君へ~",
        "Ma Chérie ~Itoshii Kimi e~ (To My Beloved)",
    ),
    "garnet": (
        "Garnet～禁断の園へ～",
        "Garnet ~Kindan no Sono e~ (To the Forbidden Garden)",
    ),
    "apr-s-midi": (
        "APRÈS MIDI～あるパリの午後で～",
        "APRÈS MIDI ~Aru Pari no Gogo de~ (On a Certain Paris Afternoon)",
    ),
    "apres-midi": (
        "Apres Midi - あるパリの午後で",
        "Apres Midi ~Aru Pari no Gogo de~ (On a Certain Paris Afternoon)",
    ),
    "apres-midi-paris": (
        "APRÈS MIDI～あるパリの午後で～",
        "APRÈS MIDI ~Aru Pari no Gogo de~ (On a Certain Paris Afternoon)",
    ),
    "n-p-s-n-g-s": ("N・p・s N・g・s", "N.p.s N.g.s (No Pains No Gains)"),
    "n-p-s-n-g-s-n-type": (
        "N・p・s N・g・s [N-type]",
        "N.p.s N.g.s [N-type] (No Pains No Gains)",
    ),
    "nps-ngs-n-type": (
        "N・p・s N・g・s [N-type]",
        "N.p.s N.g.s [N-type] (No Pains No Gains)",
    ),
    "prologue-gardenia": (
        "Prologue - 回想 - Gardenia",
        "Prologue - Kaisou - Gardenia (Recollection)",
    ),
    "prologue-kaisou": ("Prologue ~回想~", "Prologue ~Kaisou~ (Recollection)"),
    # --- Video / misc JA often on discography ---
    "bara-no-densho-prologue": (
        "薔薇の伝承 (序章)",
        "Bara no Densho (Joshou) (Rose Legend — Prologue)",
    ),
    "bara-no-senrei": ("薔薇の洗礼", "Bara no Senrei (Baptism of Roses)"),
    "bara-no-souretsu": ("薇の葬列", "Bara no Soretsu (Funeral Procession of Roses)"),
    "gensou-rakuen": ("幻想楽園", "Gensou Rakuen (Illusion Paradise)"),
    "houkai-jokyoku": ("崩壊序曲", "Houkai Jokyoku (Overture of Collapse)"),
    "ino-no-rumania": ("古のルーマニア", "Inishie no Rumania (Ancient Romania)"),
    "jirenma": ("ジレンマ", "Jirenma (Dilemma)"),
    "kioku-to-sora-saikai-yakusoku": (
        "記憶と空～再会そして約束～",
        "Kioku to Sora ~Saikai Soshite Yakusoku~ (Memory and Sky ~Reunion and Promise~)",
    ),
    "mezame-no-rasen": ("目醒めの螺旋", "Mezame no Rasen (Spiral of Awakening)"),
    "hamon-kyousoukyoku": (
        "波紋 / 協奏曲",
        "Hamon / Kyousoukyoku (Ripple / Concerto)",
    ),
    "shuumaku-e-no-tobira": (
        "終幕への扉",
        "Shuumaku e no Tobira (Door to the Finale)",
    ),
    "yakusoku": ("約束", "Yakusoku (Promise)"),
}


def set_field(text: str, key: str, value: str) -> str:
    pattern = rf"^{re.escape(key)}:.*$"
    repl = f"{key}: {value}"
    new_text, n = re.subn(pattern, repl, text, count=1, flags=re.M)
    if n != 1:
        raise ValueError(f"could not set {key}")
    return new_text


def apply_v1(slug: str, title_ja: str, title_en: str) -> bool:
    path = SONGS / f"{slug}.yaml"
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    new = set_field(text, "title_ja", title_ja)
    new = set_field(new, "title_en", title_en)
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def apply_entity(slug: str, title_ja: str, title_en: str) -> bool:
    updated = False
    for path in SONGS.glob("*.entity.yaml"):
        text = path.read_text(encoding="utf-8")
        if f"legacy_v1_slug: {slug}" not in text and f"legacy_v1_slug: {slug}\n" not in text:
            # exact line match
            if not re.search(rf"^legacy_v1_slug:\s*{re.escape(slug)}\s*$", text, re.M):
                continue
        new = text
        if re.search(r"^(\s*)original:.*$", new, re.M):
            new = re.sub(
                r"^(\s*)original:.*$",
                rf"\1original: {title_ja}",
                new,
                count=1,
                flags=re.M,
            )
        if re.search(r"^(\s*)romanized:.*$", new, re.M):
            new = re.sub(
                r"^(\s*)romanized:.*$",
                rf"\1romanized: {title_en}",
                new,
                count=1,
                flags=re.M,
            )
        if new != text:
            path.write_text(new, encoding="utf-8")
            updated = True
        break
    return updated


def main() -> None:
    audit = yaml.safe_load(AUDIT_PATH.read_text(encoding="utf-8"))
    songs = audit["songs"]

    # Fill proposed fields from PROPOSED map + leave FR/EN as Discogs
    filled = 0
    for slug, entry in songs.items():
        lang = entry["language"]
        discogs = entry["discogs_title"]
        if slug in PROPOSED:
            ja, en = PROPOSED[slug]
            entry["proposed_title_ja"] = ja
            entry["proposed_title_en"] = en
            entry["notes"] = "editorial Romanization (Meaning) from Discogs language audit"
            filled += 1
        elif lang in ("french", "english", "other"):
            entry["proposed_title_ja"] = discogs
            entry["proposed_title_en"] = discogs
            entry["notes"] = "keep Discogs Latin title; no forced gloss"
        else:
            # japanese/mixed without mapping yet — keep discogs, flag
            entry["proposed_title_ja"] = discogs
            entry["proposed_title_en"] = discogs
            entry["notes"] = "NEEDS_MEANING: japanese/mixed not yet editorialized"
            entry["needs_meaning"] = True

    # Add scope instrumentals / missing audit entries into audit for apply
    for slug, (ja, en) in PROPOSED.items():
        if slug not in songs:
            songs[slug] = {
                "discogs_title": ja,
                "language": "japanese" if re.search(r"[\u3040-\u9fff]", ja) else "mixed",
                "proposed_title_ja": ja,
                "proposed_title_en": en,
                "source_release": "derived",
                "source_kind": "derived",
                "source_uri": "",
                "in_catalog": (SONGS / f"{slug}.yaml").exists(),
                "also_seen_as": [],
                "notes": "derived from parent / catalog; not a separate Discogs heading",
            }

    AUDIT_PATH.write_text(
        yaml.dump(audit, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    print(f"Updated audit ({filled} explicit proposed titles)")

    needs = [s for s, e in songs.items() if e.get("needs_meaning") and e.get("in_catalog")]
    if needs:
        print("Still needs meaning:", ", ".join(needs))

    # Apply to all in-catalog songs that have proposed titles
    v1_n = ent_n = 0
    for slug, entry in sorted(songs.items()):
        if not entry.get("in_catalog") and not (SONGS / f"{slug}.yaml").exists():
            continue
        if not (SONGS / f"{slug}.yaml").exists():
            continue
        ja = entry["proposed_title_ja"]
        en = entry["proposed_title_en"]
        if entry.get("needs_meaning"):
            continue
        if apply_v1(slug, ja, en):
            v1_n += 1
            print(f"  v1 {slug}: {en}")
        if apply_entity(slug, ja, en):
            ent_n += 1

    # Also apply PROPOSED entries even if only in PROPOSED
    for slug, (ja, en) in sorted(PROPOSED.items()):
        if not (SONGS / f"{slug}.yaml").exists():
            continue
        if apply_v1(slug, ja, en):
            v1_n += 1
            print(f"  v1+ {slug}: {en}")
        if apply_entity(slug, ja, en):
            ent_n += 1

    print(f"Applied: {v1_n} v1 song files, {ent_n} entity files")


if __name__ == "__main__":
    main()
