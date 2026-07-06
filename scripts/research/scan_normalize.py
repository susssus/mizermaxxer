"""Normalize magazine scan JPEGs for git/site use; archive full-size originals locally."""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SCANS_ROOT = ROOT / "images" / "scans"
SCANS_ORIGINAL_ROOT = ROOT / "images" / "scans-original"

# Long edge for web reading + translation; Cantavanda pages are ~1600px tall.
MAX_LONG_EDGE = 2400
JPEG_QUALITY = 88

# Downscale when above this; re-encode (same dimensions) when file is bloated.
DOWNSCALE_IF_LONG_EDGE_OVER = 2600
REENCODE_IF_BYTES_OVER = 1_500_000


def scans_relative_path(path: Path) -> str:
    rel = path.resolve().relative_to(ROOT.resolve())
    return rel.as_posix()


def original_archive_path(scans_rel: str) -> Path:
    prefix = "images/scans/"
    if not scans_rel.startswith(prefix):
        raise ValueError(f"not a scan path: {scans_rel}")
    return SCANS_ORIGINAL_ROOT / scans_rel[len(prefix) :]


def _prepare_rgb(img: Image.Image) -> Image.Image:
    if img.mode in ("RGB", "L"):
        return img.convert("RGB")
    if img.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        converted = img.convert("RGBA")
        background.paste(converted, mask=converted.split()[-1])
        return background
    return img.convert("RGB")


def normalization_plan(width: int, height: int, size_bytes: int) -> str | None:
    long_edge = max(width, height)
    if long_edge > DOWNSCALE_IF_LONG_EDGE_OVER:
        return "downscale"
    if size_bytes > REENCODE_IF_BYTES_OVER:
        return "reencode"
    return None


def normalize_jpeg_bytes(raw: bytes) -> tuple[bytes, str | None]:
    """Return normalized JPEG bytes and action taken (or None if unchanged)."""
    img = Image.open(io.BytesIO(raw))
    width, height = img.size
    action = normalization_plan(width, height, len(raw))
    if not action:
        return raw, None

    img = _prepare_rgb(img)
    if action == "downscale":
        long_edge = max(width, height)
        scale = MAX_LONG_EDGE / long_edge
        new_size = (max(1, int(width * scale)), max(1, int(height * scale)))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return out.getvalue(), action


def archive_original_bytes(scans_rel: str, raw: bytes) -> Path:
    archive = original_archive_path(scans_rel)
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        archive.write_bytes(raw)
    return archive


def save_magazine_scan(dest: Path, raw: bytes) -> str | None:
    """Write normalized scan to dest; keep full download in scans-original when changed."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    scans_rel = scans_relative_path(dest)
    normalized, action = normalize_jpeg_bytes(raw)
    if action:
        archive_original_bytes(scans_rel, raw)
        dest.write_bytes(normalized)
    else:
        dest.write_bytes(raw)
    return action


def normalize_existing_scan(path: Path, *, dry_run: bool = False) -> str | None:
    """Normalize a scan already on disk. Archives pre-change bytes when modified."""
    if not path.is_file() or path.suffix.lower() not in {".jpg", ".jpeg"}:
        return None
    raw = path.read_bytes()
    normalized, action = normalize_jpeg_bytes(raw)
    if not action:
        return None
    if dry_run:
        return action
    scans_rel = scans_relative_path(path)
    archive_original_bytes(scans_rel, raw)
    path.write_bytes(normalized)
    return action


def iter_scan_files(root: Path | None = None) -> list[Path]:
    base = root or SCANS_ROOT
    if not base.exists():
        return []
    return sorted(
        p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg"}
    )


def format_size(num_bytes: int) -> str:
    if num_bytes >= 1_000_000:
        return f"{num_bytes / 1_000_000:.1f} MB"
    return f"{num_bytes / 1000:.0f} KB"
