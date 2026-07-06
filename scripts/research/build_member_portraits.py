#!/usr/bin/env python3
"""Build verified member portrait images from the reference poster.

The poster is stored at images/members/source/throughout-the-years.png.
Tetsu uses the existing tetsu-profile.webp (verified separately).
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "images" / "members" / "source" / "throughout-the-years.png"
OUTPUT_DIR = ROOT / "images" / "members"
MANIFEST_PATH = ROOT / "images" / "manifest.json"
PORTRAIT_SIZE = 512
SOURCE_NAME = "Malice Mizer Throughout The Years reference poster"

# Normalized crop boxes (x1, y1, x2, y2) on the reference poster layout.
PORTRAIT_CROPS: dict[str, tuple[float, float, float, float]] = {
    "mana": (0.02, 0.16, 0.33, 0.42),
    "kozi": (0.34, 0.16, 0.66, 0.42),
    "yuki": (0.67, 0.16, 0.98, 0.42),
    "tetsu": (0.02, 0.43, 0.33, 0.68),
    "gackt": (0.34, 0.43, 0.66, 0.68),
    "klaha": (0.67, 0.43, 0.98, 0.68),
    "gaz": (0.18, 0.70, 0.48, 0.95),
    "kami": (0.52, 0.70, 0.82, 0.95),
}


def square_upper_crop(image):
    from PIL import Image

    width, height = image.size
    size = min(width, int(height * 0.9))
    left = max((width - size) // 2, 0)
    return image.crop((left, 0, left + size, size))


def load_manifest() -> list[dict]:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return []


def save_manifest(entries: list[dict]) -> None:
    MANIFEST_PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def upsert_manifest_entry(entries: list[dict], path: str, source_url: str) -> None:
    for entry in entries:
        if entry["path"] == path:
            entry["source_url"] = source_url
            entry["source_name"] = SOURCE_NAME
            entry["fetched_at"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")
            return
    entries.append(
        {
            "path": path,
            "source_url": source_url,
            "source_name": SOURCE_NAME,
            "fetched_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }
    )


def build_poster_portraits() -> list[str]:
    from PIL import Image

    if not REFERENCE.exists():
        raise FileNotFoundError(f"Missing reference poster: {REFERENCE}")

    poster = Image.open(REFERENCE)
    width, height = poster.size
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    built: list[str] = []

    for slug, (x1, y1, x2, y2) in PORTRAIT_CROPS.items():
        if slug == "tetsu":
            continue
        panel = poster.crop((int(x1 * width), int(y1 * height), int(x2 * width), int(y2 * height)))
        portrait = square_upper_crop(panel)
        portrait = portrait.resize((PORTRAIT_SIZE, PORTRAIT_SIZE), Image.Resampling.LANCZOS)
        rel_path = f"images/members/{slug}.webp"
        portrait.save(ROOT / rel_path, "WEBP", quality=88)
        built.append(rel_path)
        print(f"  portrait: {rel_path}")

    return built


def install_tetsu_portrait() -> str:
    from PIL import Image

    profile = OUTPUT_DIR / "tetsu-profile.webp"
    if not profile.exists():
        raise FileNotFoundError(f"Missing verified Tetsu portrait: {profile}")

    image = Image.open(profile)
    image = image.resize((PORTRAIT_SIZE, PORTRAIT_SIZE), Image.Resampling.LANCZOS)
    rel_path = "images/members/tetsu.webp"
    image.save(ROOT / rel_path, "WEBP", quality=88)
    print(f"  portrait: {rel_path} (from tetsu-profile.webp)")
    return rel_path


def main() -> int:
    try:
        built = build_poster_portraits()
        built.append(install_tetsu_portrait())
    except FileNotFoundError as exc:
        print(exc, file=sys.stderr)
        return 1

    entries = load_manifest()
    source_url = "images/members/source/throughout-the-years.png"
    for rel_path in built:
        upsert_manifest_entry(entries, rel_path, source_url)
    upsert_manifest_entry(
        entries,
        "images/members/tetsu.webp",
        "images/members/tetsu-profile.webp",
    )
    save_manifest(entries)
    print(f"Updated manifest: {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
