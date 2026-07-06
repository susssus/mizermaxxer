#!/usr/bin/env python3
"""One-shot or maintenance pass: normalize images/scans JPEGs and archive originals."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "research"))

from scan_normalize import (  # noqa: E402
    SCANS_ORIGINAL_ROOT,
    SCANS_ROOT,
    format_size,
    iter_scan_files,
    normalize_existing_scan,
)


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    paths = iter_scan_files()
    if not paths:
        print(f"No scans under {SCANS_ROOT}")
        return 0

    before = sum(p.stat().st_size for p in paths)
    changed = 0
    downscaled = 0
    reencoded = 0

    for path in paths:
        action = normalize_existing_scan(path, dry_run=dry_run)
        if not action:
            continue
        changed += 1
        if action == "downscale":
            downscaled += 1
        else:
            reencoded += 1
        rel = path.relative_to(ROOT)
        print(f"  {action}: {rel}")

    after_paths = iter_scan_files()
    after = sum(p.stat().st_size for p in after_paths)

    prefix = "Would normalize" if dry_run else "Normalized"
    print(
        f"{prefix} {changed}/{len(paths)} scans "
        f"({downscaled} downscaled, {reencoded} re-encoded)."
    )
    if not dry_run and changed:
        print(
            f"Scan size: {format_size(before)} -> {format_size(after)} "
            f"(originals in {SCANS_ORIGINAL_ROOT.relative_to(ROOT)}/, gitignored)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
