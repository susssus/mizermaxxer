#!/usr/bin/env python3
"""Download archive images locally and update YAML with paths.

Sources: malice-mizer.info (flyers, Cantavanda scans), Cover Art Archive (covers).
Writes images/manifest.json for attribution.
"""

from __future__ import annotations

import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
IMAGES = ROOT / "images"
MANIFEST_PATH = IMAGES / "manifest.json"
FLYER_BASE = "https://malice-mizer.info"
PHOTO_BASE = "https://www.malice-mizer.info"
VINTAGE_BASE = "https://malicemeezer.neocities.org"
VINTAGE_SOURCE = "Malice Meezer / malicemeezer.neocities.org"
USER_AGENT = "MaliceMizerArchive/1.0 (digital humanities research; local mirroring with attribution)"

# malicemeezer.neocities.org early-era flyers (article id -> source image path)
EARLY_FLYER_SOURCES: dict[str, str] = {
    "flyers-1992-08-debut-era": f"{VINTAGE_BASE}/tetsu/oldflyer5.jpg",
    "flyers-1993-01-demo-sadness": f"{VINTAGE_BASE}/tetsu/oldflyer7.jpg",
    "flyers-1993-06-live-1993": f"{VINTAGE_BASE}/tetsu/oldflyer2.jpg",
    "flyers-1993-08-artistic-expression": f"{VINTAGE_BASE}/tetsu/oldflyer3.jpg",
    "flyers-1993-12-upcoming-lives": f"{VINTAGE_BASE}/tetsu/oldflyer8.jpg",
    "flyers-1994-01-live-1994": f"{VINTAGE_BASE}/tetsu/oldflyer.jpg",
    "flyers-unknown-oldflyer9": f"{VINTAGE_BASE}/tetsu/oldflyer9.jpg",
    "flyers-unknown-oldflyer4": f"{VINTAGE_BASE}/tetsu/Oldflyer4.png",
}

# Tetsu-era gallery scans from malicemeezer.neocities.org/vintage (local name -> source path)
VINTAGE_GALLERY: dict[str, str] = {
    "mana-memoire-dx.webp": "/tetsu/mana1a.jpeg",
    "kozi-memoire-dx.webp": "/tetsu/kozi1a.jpeg",
    "yuki-memoire-dx.webp": "/tetsu/yuki1a.jpeg",
    "tetsu-memoire-dx.webp": "/tetsu/tetsu1a.jpeg",
    "mana-collage.webp": "/tetsu/manacollage.jpg",
    "kozi-collage.webp": "/tetsu/Kozicollage.jpg",
    "yuki-collage.webp": "/tetsu/yukicollage.jpg",
    "tetsu-collage.webp": "/tetsu/Tetsucollage.jpg",
    "mana-interview.webp": "/tetsu/Manainterview.jpg",
    "tetsu-interview.webp": "/tetsu/Tetsuinterview.jpg",
    "yuki-interview.webp": "/tetsu/yukiinterview.jpg",
    "kozi-interview.webp": "/tetsu/koziinterview.jpg",
    "live-1993.webp": "/tetsu/oldlive.jpg",
    "live-lineup-1993.webp": "/tetsu/oldlive2.jpg",
    "live-band-1993.webp": "/tetsu/oldlive3.jpg",
    "live-mana-yuki-tetsu.webp": "/tetsu/perform.jpg",
    "live-tetsu-kami-yuki.webp": "/tetsu/oldlive7.jpg",
    "live-full-lineup.webp": "/tetsu/oldlive8.jpg",
    "live-mana-yuki.webp": "/tetsu/oldlive9.jpg",
    "live-mana-tetsu.webp": "/tetsu/tetsumana.jpg",
    "live-memoire-final-1994.webp": "/tetsu/oldlive4.jpg",
    "live-kami-memoire-final-1994.webp": "/tetsu/oldlive5 (1).jpg",
    "live-kozi-memoire-final-1994.webp": "/tetsu/oldlive6.jpg",
    "mana-guitar-jellyfish.webp": "/tetsu/jellymana4.jpg",
    "mana-smiling-gaz.webp": "/tetsu/smilemana.jpg",
    "yuki-carrying-mana.webp": "/tetsu/carry.jpg",
    "halloween-mana-kozi-yuki.webp": "/tetsu/halloween.jpg",
    "kami-kozi.webp": "/tetsu/unknown-2.png",
}

# MusicBrainz release-group id -> archive album/single id
COVER_RELEASE_GROUPS: dict[str, tuple[str, str]] = {
    "4ce179f3-f548-3d1c-ab2b-7134e32774af": ("album", "memoire"),
    "3801f7a7-49d3-39fe-8c47-d4af9dcff49a": ("album", "voyage-sans-retour"),
    "d0fa6160-eeb8-35ca-92c3-e7475786dc6f": ("album", "merveilles"),
    "438e0f5d-e3fe-30f5-86dc-31bc6bd6a1db": ("album", "bara-no-seidou"),
    "b0f3fcc5-a1f7-3a11-a0db-96bebfde0a97": ("single", "gekka-no-yasoukyoku-single"),
    "78ffcb41-64fa-39cc-98fc-b71454f8484e": ("single", "beast-of-blood-single"),
}

# malice-mizer.info photo gallery (Cantavanda scans)
MEMBER_PHOTOS: dict[str, str] = {
    "hero": "GK7xiQ1XoAAmE6m.webp",
    "mana": "GIBE9LOWwAEwwIp.webp",
    "kozi": "GIBE9LVXQAAhrpr.webp",
    "yuki": "20240201_185706.webp",
    "kami": "20240201_185708.webp",
    "gackt": "GGTOj8ZXkAAFu6R.webp",
    "klaha": "GIBE9LQWwAE5Er9.webp",
    "tetsu": "20240201_185653.webp",
}

PERSON_SLUGS = {
    "mana": "person_mana",
    "kozi": "person_kozi",
    "yuki": "person_yuki",
    "kami": "person_kami",
    "gackt": "person_gackt",
    "klaha": "person_klaha",
}


def load_manifest() -> list[dict[str, Any]]:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return []


def save_manifest(entries: list[dict[str, Any]]) -> None:
    MANIFEST_PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def manifest_index(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {entry["path"]: entry for entry in entries}


def add_manifest_entry(
    entries: list[dict[str, Any]],
    index: dict[str, dict[str, Any]],
    path: str,
    source_url: str,
    source_name: str,
) -> None:
    if path in index:
        return
    entry = {
        "path": path,
        "source_url": source_url,
        "source_name": source_name,
        "fetched_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    entries.append(entry)
    index[path] = entry


def fetch_url(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    parsed = urllib.parse.urlsplit(url)
    safe_path = urllib.parse.quote(parsed.path, safe="/:@!$&'()*+,;=-._~")
    safe_url = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, safe_path, parsed.query, parsed.fragment))
    request = urllib.request.Request(safe_url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        raw = response.read()

    if dest.suffix.lower() == ".webp" and not url.lower().endswith(".webp"):
        from PIL import Image

        img = Image.open(io.BytesIO(raw))
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        img.save(dest, "WEBP", quality=88)
    else:
        dest.write_bytes(raw)


def safe_filename(text: str) -> str:
    cleaned = re.sub(r"[^\w.\-]+", "-", text.strip())
    return cleaned.strip("-") or "image"


def flyer_local_name(article_id: str, url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    ext = Path(parsed.path).suffix or ".webp"
    return f"{safe_filename(article_id)}{ext}"


def download_flyers(entries: list[dict[str, Any]], index: dict[str, dict[str, Any]]) -> int:
    count = 0
    for yaml_path in sorted((ROOT / "data" / "issues" / "flyers").glob("*.yaml")):
        issue = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        changed = False
        for article in issue.get("articles", []):
            scan = article.get("scan") or {}
            url = scan.get("url")
            article_id = article["id"]

            if url and url.startswith("http"):
                source_url = url
                source_name = "malice-mizer.info"
            elif article_id in EARLY_FLYER_SOURCES:
                source_url = EARLY_FLYER_SOURCES[article_id]
                source_name = "Malice Meezer / malicemeezer.neocities.org"
                local_name = f"{safe_filename(article_id)}.webp"
                rel_path = f"images/flyers/{local_name}"
                scan["url"] = rel_path
                url = rel_path
            else:
                continue

            if url.startswith("http"):
                local_name = flyer_local_name(article_id, url)
                rel_path = f"images/flyers/{local_name}"
            else:
                rel_path = url

            dest = ROOT / rel_path
            if not dest.exists() or dest.stat().st_size < 50_000:
                try:
                    fetch_url(source_url, dest)
                    print(f"  flyer: {rel_path}")
                except (urllib.error.URLError, TimeoutError, UnicodeEncodeError) as exc:
                    print(f"  skip flyer {article_id}: {exc}", file=sys.stderr)
                    continue
            add_manifest_entry(entries, index, rel_path, source_url, source_name)
            scan["url"] = rel_path
            scan["available"] = True
            changed = True
            count += 1
        if changed:
            yaml_path.write_text(
                yaml.dump(issue, allow_unicode=True, sort_keys=False, default_flow_style=False),
                encoding="utf-8",
            )
    return count


def download_vintage_gallery(entries: list[dict[str, Any]], index: dict[str, dict[str, Any]]) -> int:
    count = 0
    for local_name, remote_path in VINTAGE_GALLERY.items():
        source_url = f"{VINTAGE_BASE}{remote_path}"
        rel_path = f"images/vintage/{local_name}"
        dest = ROOT / rel_path
        if not dest.exists() or dest.stat().st_size < 10_000:
            try:
                fetch_url(source_url, dest)
                print(f"  vintage: {rel_path}")
            except (urllib.error.URLError, TimeoutError, UnicodeEncodeError) as exc:
                print(f"  skip vintage {local_name}: {exc}", file=sys.stderr)
                continue
        add_manifest_entry(entries, index, rel_path, source_url, VINTAGE_SOURCE)
        count += 1
    return count


def cover_art_url(release_group_id: str) -> str | None:
    url = f"https://coverartarchive.org/release-group/{release_group_id}"
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError:
        return None
    for image in data.get("images", []):
        if image.get("front") and image.get("approved"):
            thumbs = image.get("thumbnails") or {}
            return thumbs.get("500") or image.get("image")
    for image in data.get("images", []):
        if image.get("approved"):
            thumbs = image.get("thumbnails") or {}
            return thumbs.get("500") or image.get("image")
    return None


def download_covers(entries: list[dict[str, Any]], index: dict[str, dict[str, Any]]) -> int:
    count = 0
    for release_group_id, (kind, slug) in COVER_RELEASE_GROUPS.items():
        cover_url = cover_art_url(release_group_id)
        if not cover_url:
            print(f"  skip cover {slug}: no Cover Art Archive image", file=sys.stderr)
            continue
        ext = Path(urllib.parse.urlparse(cover_url).path).suffix or ".jpg"
        rel_path = f"images/covers/{slug}{ext}"
        dest = ROOT / rel_path
        if not dest.exists():
            try:
                fetch_url(cover_url, dest)
                print(f"  cover: {rel_path}")
                time.sleep(1)
            except (urllib.error.URLError, TimeoutError) as exc:
                print(f"  skip cover {slug}: {exc}", file=sys.stderr)
                continue
        add_manifest_entry(entries, index, rel_path, cover_url, "Cover Art Archive / Cantavanda")
        yaml_dir = "singles" if kind == "single" else "albums"
        yaml_path = ROOT / "data" / yaml_dir / f"{slug}.yaml"
        if yaml_path.exists():
            doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
            doc["cover_image"] = rel_path
            yaml_path.write_text(
                yaml.dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False),
                encoding="utf-8",
            )
        count += 1
    return count


def download_members(entries: list[dict[str, Any]], index: dict[str, dict[str, Any]]) -> int:
    count = 0
    for slug, filename in MEMBER_PHOTOS.items():
        source_url = f"{PHOTO_BASE}/{filename}"
        rel_path = f"images/members/{slug}.webp"
        dest = ROOT / rel_path
        if not dest.exists():
            try:
                fetch_url(source_url, dest)
                print(f"  member: {rel_path}")
            except (urllib.error.URLError, TimeoutError) as exc:
                print(f"  skip member {slug}: {exc}", file=sys.stderr)
                continue
        add_manifest_entry(entries, index, rel_path, source_url, "malice-mizer.info / Cantavanda")
        count += 1

    for slug, person_id in PERSON_SLUGS.items():
        rel_path = f"images/members/{slug}.webp"
        if not (ROOT / rel_path).exists():
            continue
        yaml_path = ROOT / "data" / "people" / f"{slug}.yaml"
        if yaml_path.exists():
            doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
            doc["portrait_image"] = rel_path
            yaml_path.write_text(
                yaml.dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False),
                encoding="utf-8",
            )

    members_path = ROOT / "data" / "people" / "members.yaml"
    if members_path.exists():
        doc = yaml.safe_load(members_path.read_text(encoding="utf-8"))
        portrait_map = {slug: f"images/members/{slug}.webp" for slug in PERSON_SLUGS}
        portrait_map["tetsu"] = "images/members/tetsu.webp"
        for member in doc.get("members", []):
            slug = member.get("slug")
            if slug in portrait_map and (ROOT / portrait_map[slug]).exists():
                member["portrait_image"] = portrait_map[slug]
        members_path.write_text(
            yaml.dump(doc, allow_unicode=True, sort_keys=False, default_flow_style=False),
            encoding="utf-8",
        )
    return count


def ensure_public_symlink() -> None:
    public_images = ROOT / "site" / "public" / "images"
    public_images.parent.mkdir(parents=True, exist_ok=True)
    if public_images.is_symlink() or public_images.exists():
        if public_images.is_symlink() or public_images.is_dir():
            return
    try:
        public_images.symlink_to(IMAGES.resolve(), target_is_directory=True)
        print(f"  symlink: site/public/images -> {IMAGES}")
    except OSError:
        import shutil

        if public_images.exists():
            shutil.rmtree(public_images)
        shutil.copytree(IMAGES, public_images, dirs_exist_ok=True)
        print(f"  copied: site/public/images")


def main() -> int:
    print("Fetching archive images...")
    entries = load_manifest()
    index = manifest_index(entries)

    flyer_count = download_flyers(entries, index)
    vintage_count = download_vintage_gallery(entries, index)
    cover_count = download_covers(entries, index)
    member_count = download_members(entries, index)

    save_manifest(entries)
    ensure_public_symlink()

    print(
        f"Done: {flyer_count} flyers, {vintage_count} vintage gallery, {cover_count} covers, "
        f"{member_count} member/hero images. Manifest: {MANIFEST_PATH}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
