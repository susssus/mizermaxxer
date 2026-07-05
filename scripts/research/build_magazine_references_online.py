#!/usr/bin/env python3
"""Build scripts/research/magazine_references_online.yaml from online bibliographies.

Sources:
  - vkgy / jrock.gy artist timeline (magazine mentions in chronology)
  - malice-archive.neocities.org/list (fan-maintained comprehensive list)
  - MIsaO Lab FOOL'S MATE ownership index (detailed coverage notes)
  - scripts/research/scan_sources_catalog.yaml (known scan URLs)
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "scripts/research/magazine_references_online.yaml"
INCOMPLETE_MAGS = ROOT / "scripts/research/malice_archive_incomplete_mags.yaml"
VKGY_GLOB = "vkgy_*_malice_mizer.yaml"
VKGY_CACHE = (
    Path.home()
    / ".cursor/projects/Users-annasusanna-malice-mizer-print-archive/agent-tools"
)

PUB_ALIASES = {
    "fool's mate": "fools-mate",
    "fools mate": "fools-mate",
    "shoxx": "shoxx",
    "gigs": "gigs",
    "b-pass": "b-pass",
    "bpass": "b-pass",
    "pati▶pati": "pati-pati",
    "pati pati": "pati-pati",
    "vicious": "vicious",
    "arena 37c": "arena37",
    "arena37": "arena37",
    "cure": "cure",
    "uv": "uv",
    "m gazette": "m-gazette",
    "mgazette": "m-gazette",
    "j-rock magazine": "j-rock-magazine",
    "pop beat": "pop-beat",
    "popbeat": "pop-beat",
    "hyper-popbeat": "hyper-popbeat",
    "zappy": "zappy",
    "cutie": "cutie",
    "artist fan": "artist-fan",
    "apres guerre": "apres-guerre",
    "band yarouze": "band-yarouze",
    "quarter maze": "quarter-maze",
    "imperfection": "imperfection",
    "fall of midsummer snow": "fall-of-midsummer-snow",
    "cd skit!": "cd-skit",
    "visualized beats": "visualized-beats",
    "rock and read": "rock-and-read",
    "rockin'f": "rockinf",
    "rockin'on": "rockinon",
    "friday": "friday",
    "cd data": "cd-data",
    "astan": "astan",
    "band style": "band-style",
    "band x artist": "band-x-artist",
    "band collection": "band-collection",
    "bidan": "bidan",
    "creation": "creation",
    "clap!": "clap",
    "da vinchi": "da-vinchi",
    "fruige": "fruige",
    "myojo": "myojo",
    "quick japan": "quick-japan",
    "luck-das": "luck-das",
    "popbeat": "pop-beat",
    "gb": "gb",
    "zy": "zy",
    "pati pati": "pati-pati",
    "cd skit!": "cd-skit",
}

MONTHS = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
}

MISAOLAB_FM = """
1994/05（151）：-
1994/07（153）：Vox View（Al「memoire」発売記事）
1994/08（154）：カラー2p、初インタビュー（Al「memoire」）
1994/12（158）：AFTER IMAGE 2p（Al「黒い結晶」）
1996/06（176）：カラー1p、1996/3/31 O-WESTレポ
1997/02（184）：カラー4p、1996/11/18 O-WEST「喜劇の晩餐」、目黒学園女子短大レポ&個別インタビュー（Kami欠席）
1997/04（186）：カラー6p、STYLE#5（個別・合同インタビュー）
1997/06（188）：表紙（La'cryma Christiと合同）。カラー6p、ラクリマとインタビュー。1997/4/1 渋谷公会堂、1997/4/2 六本木TATOU東京レポ
1998/03（197）：カラー10p、Mana×FULL(Guniw Tools）対談、1997/12/28,29 渋谷公会堂レポ、Sg「月下の夜想曲」インタビュー（Gackt,Kozi）
1999/01（207）：表紙。カラー12p
1999/02（208）：カラー4p、インタビュー振り返り。年賀状（Mana）。
1999/03（209）：カラー4p、公開質問状
1999/07（213）：カラー4p、FCイベント後インタビュー（Mana&Kami）
1999/09（215）：カラー4p、Kami追悼
2000/02（220）：カラー4p、個別インタビュー
2000/05（223）：PlatinA Forest 半p 2000/3/2 高田馬場 AREAレポ
2000/07（225）：カラー8p、Sg「虚無の中での遊戯」インタビュー
2000/09（227）：カラー3p、Sg「白い肌に狂う愛と哀しみの輪舞」インタビュー
2000/11（229）：カラー4p、2000/9/1 日本武道館レポ
2001/01（231）：カラー6p、メンバー全員インタビュー
2001/02（232）：カラー3p、2000/11/19 Zepp Tokyoレポ&インタビュー（Klaha,Mana）
2001/07（236）：Vox View（Sg「Gardenia」Klaha,Manaコメント）
"""

MISAOLAB_SHOXX_RAW = """
1993/01（013）：インディーズハードロック最新情報（1992/11/24 新宿LOFTライブ告知）
1994/11（028）：インディーズハードロック最新情報（1994/10/23 目黒鹿鳴館ライブ告知） AFTER IMAGE 2p、Al「黒い結晶」メンバー全員インタビュー
1996/05（041）：4p、SHOCK WAVE '96レポ
1996/11（047）：カラー1p・モノ3p、Sg「ma cherie」メンバー全員インタビュー
1997/05（051）：MALICE MIZERの不思議シアター（Koziコラージュ4コマ）
1997/05（052）：Personal Interview; 1997/4/1 渋谷公会堂レポ; SHOCK WAVE '97レポ
1997/07（053）：カラー12p、メンバー全員パーソナルインタビュー（衣装：軍服）
1997/07（054）：切り抜き（詳細不明）
1998/03（061）：（La'cryma Christiと合同）表紙。カラー38p、パート別対談、Q&A（衣装：au revoir）
1998/04（062）：カラー14p、パーソナルインタビュー（衣装：サイバー）&1997/12/28 渋谷公会堂レポ
1998/05（063）：カラー13p、スーパービジュアルフォト集（衣装：月下の夜想曲）&A to Zインタビュー
1998/06（064）：カラー10p、Mana・Koziフォトセッション（衣装：merveilles）&1998/4/1 日本武道館レポ
1998/09（067）：表紙。カラー32p、世界5大美女図鑑、Q&Aインタビュー
1999/02（072）：PlatinA Forest（1stAl告知等）
1999/06（076）：-
1999/09（079）：-
2000/01（083）：表紙。カラー24p、フォトセッション（衣装：再会の血と薔薇）&インタビュー
2000/02（084）：カラー6p、メンバー全員写真&Manaインタビュー
2000/06（088）：表紙。カラー28p、Manaシアトリカルフォトストーリー&インタビュー
2000/10（092）：表紙。カラー26p、フォトギャラリー（衣装：白い肌に狂う愛と哀しみの輪舞）&インタビュー
2001/01（095）：表紙。カラー26p、フォトギャラリー&メンバー全員インタビュー
2001/02（096）：カラー3p、2000/11/19 Zepp Tokyoレポ
2001/07（101）：Parsonal Series Klaha 撮り下ろし&インタビュー
2001/12（106）：表紙。カラー24p、フォトギャラリー&インタビュー&「薔薇の婚礼」レビュー
2002/07（113）：Vanilla 1p、1stSg「サガシモノ/小さな願い」メンバー全員インタビュー
2002/10（116）：カラー2p、2002/7/31 渋谷AXレポ
2003/02（120）：カラー4p、メンバー全員インタビュー
"""

# Known online scan URLs keyed by (publication, issue_number or issue_date)
SCAN_URLS: dict[tuple[str, str], str] = {
    ("fools-mate", "189"): "https://cantavanda.com/malice-mizer/scans/magazine-appearances/gallery/fools-mate-no-189-july-1997/",
    ("fools-mate", "207"): "https://archive.org/details/fools-mate-207-january-1999-13",
    ("shoxx", "63"): "https://cantavanda.com/malice-mizer/scans/magazine-appearances/gallery/shoxx-may-1998/",
    ("vicious", "1997-10"): "https://cantavanda.com/malice-mizer/scans/magazine-appearances/gallery/vicious-october-1997/",
    ("pop-beat", "1997-08"): "https://cantavanda.com/malice-mizer/scans/magazine-appearances/gallery/pop-beat-august-1997/",
    ("pop-beat", "1998-06"): "https://cantavanda.com/malice-mizer/scans/magazine-appearances/gallery/pop-beat-june-1998/",
    ("arena37", "1997-10"): "https://archive.org/details/arena-37-c-oct-97-01",
    ("arena37", "1998-11"): "https://archive.org/details/arena194-ss-2",
    ("b-pass", "1999-06"): "https://archive.org/details/scan-10188",
    ("artist-fan", "2000-04"): "https://archive.org/details/af7-x-1",
}


def load_incomplete_mags_scan_urls() -> dict[tuple[str, str], str]:
    """Load Drive scan URLs from malice_archive_incomplete_mags.yaml."""
    extra: dict[tuple[str, str], str] = {}
    if not INCOMPLETE_MAGS.exists():
        return extra
    doc = yaml.safe_load(INCOMPLETE_MAGS.read_text(encoding="utf-8"))
    for item in doc.get("items") or []:
        pub = item["publication"]
        url = item.get("scan_url")
        if not url:
            continue
        if item.get("issue_date"):
            date = str(item["issue_date"])[:7]
            extra[(pub, date)] = url
        if item.get("issue_number"):
            num = str(item["issue_number"]).lstrip("0") or str(item["issue_number"])
            extra[(pub, num)] = url
    return extra


def parse_incomplete_mags_entries() -> list[dict]:
    if not INCOMPLETE_MAGS.exists():
        return []
    doc = yaml.safe_load(INCOMPLETE_MAGS.read_text(encoding="utf-8"))
    source_url = doc["source"]["url"]
    entries: list[dict] = []
    for item in doc.get("items") or []:
        entry: dict = {
            "publication": item["publication"],
            "sources": [{"id": "malice-archive-incomplete-mags", "url": source_url}],
            "notes": "Partial scan on Google Drive (malice-archive Incompletemags).",
        }
        if item.get("issue_date"):
            date = str(item["issue_date"])
            entry["issue_date"] = date[:7] if len(date) >= 7 else date
        if item.get("issue_number"):
            entry["issue_number"] = str(item["issue_number"])
        if item.get("title"):
            entry["coverage_notes"] = item["title"]
        entries.append(entry)
    return entries


def load_vkgy_catalog_entries() -> list[dict]:
    entries: list[dict] = []
    for path in sorted((ROOT / "scripts" / "research").glob(VKGY_GLOB)):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        pub = doc.get("publication")
        if not pub and "fools-mate" in path.name:
            pub = "fools-mate"
        if not pub:
            stem = path.stem.replace("vkgy_", "").replace("_malice_mizer", "")
            pub = stem.replace("_", "-")
        for e in doc.get("entries") or []:
            entry: dict = {
                "publication": pub,
                "sources": [{"id": "vkgy", "url": e.get("url") or doc.get("source_index", "")}],
            }
            if e.get("issue_number"):
                entry["issue_number"] = str(e["issue_number"])
            if e.get("publication_date"):
                entry["issue_date"] = e["publication_date"]
            roles = e.get("roles") or []
            if roles:
                entry["coverage_notes"] = f"vkgy roles: {', '.join(roles)}"
            entries.append(entry)
    return entries


def parse_misaolab_pub(raw: str, publication: str, source_url: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"(\d{4})/(\d{2})（(\d+)）：(.+)", line)
        if not m:
            continue
        y, mo, num, notes = m.groups()
        out[num.lstrip("0") or num] = {
            "issue_date": f"{y}-{mo}",
            "coverage_notes": notes.strip(),
            "source_url": source_url,
            "publication": publication,
        }
        # also store zero-padded key alias via same dict value
        if num.startswith("0") and num.lstrip("0"):
            out[num] = out[num.lstrip("0")]
    return out


def parse_misaolab_fm() -> dict[str, dict]:
    return parse_misaolab_pub(
        MISAOLAB_FM,
        "fools-mate",
        "https://misaolab.hateblo.jp/entry/20000301/1356327963",
    )


def parse_misaolab_shoxx() -> dict[str, dict]:
    return parse_misaolab_pub(
        MISAOLAB_SHOXX_RAW,
        "shoxx",
        "https://misaolab.hateblo.jp/entry/20000302/1356327963",
    )


def find_vkgy_file() -> Path | None:
    candidates = sorted(VKGY_CACHE.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True)
    for p in candidates:
        if "FOOL'S MATE" in p.read_text(encoding="utf-8", errors="ignore")[:50000]:
            return p
    return None


def parse_vkgy(text: str) -> list[dict]:
    entries: list[dict] = []
    patterns = [
        (r"FOOL'S MATEFOOL'S MATE №(\d+)№\d+", "fools-mate", "issue_number"),
        (r"SHOXXSHOXX Vol\.(\d+)Vol\.\d+", "shoxx", "issue_number"),
        (r"GiGSGiGS No\.(\d+)No\.\d+", "gigs", "issue_number"),
        (r"B-PASSB-PASS (\d{4}-\d{2})\d{4}-\d{2}", "b-pass", "issue_date"),
        (r"PATi▶PATiPATi▶PATi VOL\.(\d+)VOL\.\d+", "pati-pati", "issue_number"),
        (r"ViciousVicious (\d{4}) (\d+)(?: Vol\.(\d+))?", "vicious", "issue_date"),
        (r"M GAZETTEM GAZETTE Vol\.(\d+)Vol\.\d+", "m-gazette", "issue_number"),
        (r"J-Rock MagazineJ-Rock Magazine Vol\.(\d+)Vol\.\d+", "j-rock-magazine", "issue_number"),
        (r"POP BEAT|POPBEAT|Popbeat", "pop-beat", "mention"),
        (r"Zappy", "zappy", "mention"),
        (r"Cure", "cure", "mention"),
        (r"uv", "uv", "mention"),
        (r"Arena 37C", "arena37", "mention"),
    ]
    for pat, pub, kind in patterns:
        for m in re.finditer(pat, text):
            entry: dict = {
                "publication": pub,
                "sources": [{"id": "vkgy", "url": "https://www.jrock.gy/artists/malice-mizer/"}],
            }
            if kind == "issue_number":
                entry["issue_number"] = m.group(1)
            elif kind == "issue_date":
                if pub == "vicious":
                    entry["issue_date"] = f"{m.group(1)}-{int(m.group(2)):02d}"
                    if m.group(3):
                        entry["issue_number"] = m.group(3)
                else:
                    entry["issue_date"] = m.group(1)
            entries.append(entry)
    return entries


def parse_malice_archive_list(text: str) -> list[dict]:
    entries: list[dict] = []
    current_pub: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("This is a list"):
            continue
        if line.endswith(":") and len(line) < 50:
            current_pub = line[:-1].strip().lower()
            continue
        if not current_pub:
            continue
        slug = PUB_ALIASES.get(current_pub)
        if not slug:
            continue
        entry: dict = {
            "publication": slug,
            "sources": [{"id": "malice-archive", "url": "https://malice-archive.neocities.org/list"}],
        }
        incomplete = line.startswith("*")
        if incomplete:
            line = line.lstrip("* ").strip()
        # Fool's Mate: November 1992, Vol. 133
        fm = re.match(
            r"(?:(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4}),?\s+)?Vol\.\s*(\d+)",
            line,
            re.I,
        )
        if fm:
            if fm.group(1):
                entry["issue_date"] = f"{fm.group(2)}-{MONTHS[fm.group(1).lower()]}"
            entry["issue_number"] = fm.group(3)
            entries.append(entry)
            continue
        # Month Year: August 1997
        my = re.match(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})", line, re.I)
        if my:
            entry["issue_date"] = f"{my.group(2)}-{MONTHS[my.group(1).lower()]}"
            entries.append(entry)
            continue
        # Vol. N
        vol = re.match(r"Vol\.\s*(\d+)", line, re.I)
        if vol:
            entry["issue_number"] = vol.group(1)
            entries.append(entry)
            continue
        if incomplete:
            entry["notes"] = "malice-archive marks incomplete / no scan"
            entries.append(entry)
    return entries


def entry_key(e: dict) -> tuple:
    num = e.get("issue_number")
    if num is not None:
        num = str(num).lstrip("0") or str(num)
    return (e["publication"], num, e.get("issue_date"))


def merge_entries(*groups: list[dict], misaolab_fm: dict[str, dict], misaolab_shoxx: dict[str, dict]) -> list[dict]:
    merged: dict[tuple, dict] = {}
    for group in groups:
        for e in group:
            k = entry_key(e)
            if k not in merged:
                merged[k] = {
                    "publication": e["publication"],
                    "issue_number": e.get("issue_number"),
                    "issue_date": e.get("issue_date"),
                    "sources": [],
                    "coverage_notes": e.get("coverage_notes"),
                    "notes": e.get("notes"),
                }
            m = merged[k]
            for s in e.get("sources", []):
                if s not in m["sources"]:
                    m["sources"].append(s)
            if e.get("coverage_notes") and not m.get("coverage_notes"):
                m["coverage_notes"] = e["coverage_notes"]
            if e.get("notes"):
                m["notes"] = (m.get("notes") or "") + (" " if m.get("notes") else "") + e["notes"]

    for num, detail in misaolab_fm.items():
        norm = str(num).lstrip("0") or str(num)
        target = None
        for k, v in list(merged.items()):
            if v["publication"] == "fools-mate" and str(v.get("issue_number", "")).lstrip("0") == norm:
                target = v
                break
        if not target:
            target = {
                "publication": "fools-mate",
                "issue_number": norm,
                "issue_date": detail["issue_date"],
                "sources": [],
            }
            merged[("fools-mate", norm, detail["issue_date"])] = target
        target["coverage_notes"] = detail["coverage_notes"]
        if not target.get("issue_date"):
            target["issue_date"] = detail["issue_date"]
        src = {"id": "misaolab-fools-mate", "url": detail["source_url"]}
        if src not in target["sources"]:
            target["sources"].append(src)

    for num, detail in misaolab_shoxx.items():
        norm = str(num).lstrip("0") or str(num)
        target = None
        for v in merged.values():
            if v["publication"] == "shoxx" and str(v.get("issue_number", "")).lstrip("0") == norm:
                target = v
                break
        if not target:
            target = {
                "publication": "shoxx",
                "issue_number": norm,
                "issue_date": detail["issue_date"],
                "sources": [],
            }
            merged[("shoxx", norm, detail["issue_date"])] = target
        target["coverage_notes"] = detail["coverage_notes"]
        if not target.get("issue_date"):
            target["issue_date"] = detail["issue_date"]
        src = {"id": "misaolab-shoxx", "url": detail["source_url"]}
        if src not in target["sources"]:
            target["sources"].append(src)

    scan_urls = {**SCAN_URLS, **load_incomplete_mags_scan_urls()}

    # attach scan URLs
    result = []
    for e in sorted(merged.values(), key=lambda x: (x["publication"], x.get("issue_date") or "", x.get("issue_number") or "")):
        pub = e["publication"]
        scan = None
        num = e.get("issue_number")
        if num:
            norm = str(num).lstrip("0") or str(num)
            scan = scan_urls.get((pub, norm)) or scan_urls.get((pub, str(num)))
        if not scan and e.get("issue_date"):
            scan = scan_urls.get((pub, e["issue_date"]))
        e["scan"] = {"available": bool(scan), "url": scan}
        result.append(e)
    return result


def main() -> None:
    misaolab_fm = parse_misaolab_fm()
    misaolab_shoxx = parse_misaolab_shoxx()
    vkgy_file = find_vkgy_file()
    vkgy_entries: list[dict] = []
    if vkgy_file:
        vkgy_entries = parse_vkgy(vkgy_file.read_text(encoding="utf-8", errors="ignore"))

    archive_text = ""
    archive_path = Path("/tmp/malice-archive-list.txt")
    if archive_path.exists():
        archive_text = archive_path.read_text()
    else:
        import urllib.request

        archive_text = urllib.request.urlopen("https://malice-archive.neocities.org/list").read().decode("utf-8", errors="ignore")
    archive_entries = parse_malice_archive_list(archive_text)
    incomplete_entries = parse_incomplete_mags_entries()
    vkgy_catalog_entries = load_vkgy_catalog_entries()

    entries = merge_entries(
        vkgy_entries,
        archive_entries,
        incomplete_entries,
        vkgy_catalog_entries,
        misaolab_fm=misaolab_fm,
        misaolab_shoxx=misaolab_shoxx,
    )

    by_pub: dict[str, int] = {}
    scans = 0
    for e in entries:
        by_pub[e["publication"]] = by_pub.get(e["publication"], 0) + 1
        if e["scan"]["available"]:
            scans += 1

    doc = {
        "generated": "2026-07-06",
        "description": "Online magazine bibliography for MALICE MIZER merged from fan/community sources.",
        "source_indexes": [
            {
                "id": "vkgy",
                "title": "vkgy / jrock.gy artist timeline",
                "url": "https://www.jrock.gy/artists/malice-mizer/",
                "notes": "Magazine mentions embedded in band chronology (~157 unique refs parsed).",
            },
            {
                "id": "malice-archive",
                "title": "The Malice Archive — magazine list",
                "url": "https://malice-archive.neocities.org/list",
                "notes": "Fan-maintained comprehensive list; site page may be partially truncated in HTML.",
            },
            {
                "id": "misaolab-fools-mate",
                "title": "MIsaO Lab — FOOL'S MATE ownership index",
                "url": "https://misaolab.hateblo.jp/entry/20000301/1356327963",
                "notes": "Detailed Japanese coverage notes for FOOL'S MATE issues (MM section).",
            },
            {
                "id": "misaolab-shoxx",
                "title": "MIsaO Lab — SHOXX ownership index",
                "url": "https://misaolab.hateblo.jp/entry/20000302/1356327963",
                "notes": "Detailed Japanese coverage notes for SHOXX issues (MM section), vol.13–120.",
            },
            {
                "id": "cantavanda",
                "title": "Cantavanda — magazine appearance scans",
                "url": "https://cantavanda.com/malice-mizer/scans/magazine-appearances/",
            },
            {
                "id": "malice-mizer-info-fc",
                "title": "malice-mizer.info — ma chérie fan club magazine index",
                "url": "https://malice-mizer.info/ma-cherie-magazine",
                "notes": "Vol. 1–21 quarterly fan club zines (1997–2001).",
            },
            {
                "id": "scape-translations",
                "title": "scape.sc — interview translations (names source magazines)",
                "url": "http://scape.sc/translations/mm-translations.php",
            },
            {
                "id": "internet-archive",
                "title": "Internet Archive search",
                "url": "https://archive.org/search?query=malice+mizer",
            },
            {
                "id": "malice-archive-incomplete-mags",
                "title": "The Malice Archive — Incomplete Mags (Google Drive)",
                "url": "https://malice-archive.neocities.org/Incompletemags/main",
                "notes": "Partial magazine scans hosted on Google Drive.",
            },
            {
                "id": "vkgy-magazine-indexes",
                "title": "vkgy per-magazine indexes",
                "url": "https://vk.gy/magazines/",
                "notes": "Per-issue TOC harvested via fetch_vkgy_magazines.py.",
            },
        ],
        "statistics": {
            "total_entries": len(entries),
            "publications_count": len(by_pub),
            "entries_with_scan_url": scans,
            "by_publication": dict(sorted(by_pub.items(), key=lambda x: -x[1])),
        },
        "entries": entries,
    }

    OUT.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    print(f"Wrote {len(entries)} entries ({scans} with scans) to {OUT}")


if __name__ == "__main__":
    main()
