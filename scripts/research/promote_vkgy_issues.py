#!/usr/bin/env python3
"""Promote POP BEAT / uv issues using vk.gy cross-references and known scan sources.

Promotion rules (docs/RESEARCH.md):
- verified: issue number + page/cover evidence from two independent sources, OR
  Cantavanda/local scans with identified pages.
- possible: vk.gy per-issue TOC + vk.gy artist timeline agree on issue/date/number,
  or single scan source without full page audit.

Also consolidates duplicate uv vol-* vs date-* stubs (keeps month-dated file).
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ISSUES = ROOT / "data" / "issues"
VKGY_DIR = ROOT / "scripts" / "research"
TODAY = "2026-07-06"
ARTIST_URL = "https://vk.gy/artists/malice-mizer/"

ROLE_TO_TYPE = {
    "cover": "cover",
    "large_feature": "photo_spread",
    "other_appearance": "mention",
    "flyer": "flyer",
    "mention": "mention",
}


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def dump_yaml(path: Path, doc: dict) -> None:
    path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")


def load_vkgy_harvest(pub: str) -> dict[str, dict]:
    """Map issue_number -> vkgy harvest entry."""
    path = VKGY_DIR / f"vkgy_{pub.replace('-', '_')}_malice_mizer.yaml"
    if not path.exists():
        return {}
    doc = load_yaml(path)
    out: dict[str, dict] = {}
    for entry in doc.get("entries") or []:
        num = entry.get("issue_number")
        if num is not None:
            out[str(int(num)) if str(num).isdigit() else str(num)] = entry
    return out


def load_incomplete_scans(pub: str) -> dict[str, str]:
    path = VKGY_DIR / "malice_archive_incomplete_mags.yaml"
    if not path.exists():
        return {}
    doc = load_yaml(path)
    out: dict[str, str] = {}
    for item in doc.get("items") or []:
        if item.get("publication") != pub:
            continue
        date = item.get("issue_date")
        if date and len(str(date)) >= 7:
            out[str(date)[:7]] = item["scan_url"]
    return out


def article_type_from_roles(roles: list[str] | None) -> str:
    if not roles:
        return "mention"
    for role in ("cover", "large_feature", "flyer", "other_appearance"):
        if role in roles:
            return ROLE_TO_TYPE[role]
    return "mention"


def add_changelog(doc: dict, action: str, source: str, notes: str) -> None:
    doc.setdefault("changelog", []).append(
        {"date": TODAY, "action": action, "source": source, "notes": notes}
    )


def merge_vkgy_into_issue(doc: dict, vkgy: dict) -> bool:
    changed = False
    issue_num = str(int(vkgy["issue_number"])) if str(vkgy.get("issue_number", "")).isdigit() else vkgy.get("issue_number")
    pub_date = vkgy.get("publication_date")
    if pub_date and len(pub_date) >= 7:
        pub_date = pub_date[:7]

    if issue_num and doc.get("issue_number") != issue_num:
        doc["issue_number"] = issue_num
        changed = True
    if pub_date and doc.get("publication_date") != pub_date:
        doc["publication_date"] = pub_date
        doc["date_precision"] = "month"
        changed = True

    url = vkgy.get("url", "")
    roles = vkgy.get("roles") or []
    notes_lines = [
        f"uv Vol.{issue_num} ({pub_date})" if doc.get("publication") == "uv" else f"POP BEAT {pub_date}",
        f"[vkgy-per-issue] {url}",
        f"[vkgy-timeline] {ARTIST_URL}",
    ]
    if roles:
        notes_lines.append(f"vkgy roles: {', '.join(roles)}")
    new_notes = "\n".join(notes_lines)
    if doc.get("source_notes") != new_notes:
        doc["source_notes"] = new_notes
        changed = True

    articles = doc.get("articles") or []
    if not articles:
        articles = [{"id": f"{doc['id']}-001", "type": "mention", "members": [], "scan": {"available": False}}]
        doc["articles"] = articles

    art = articles[0]
    atype = article_type_from_roles(roles)
    if art.get("type") != atype:
        art["type"] = atype
        changed = True
    is_cover = "cover" in roles
    if is_cover:
        art["cover"] = True
        if not art.get("pages"):
            art["pages"] = "cover"
        changed = True
    elif art.get("cover"):
        art["cover"] = False
        changed = True
    role_note = f"vkgy roles: {', '.join(roles)}" if roles else ""
    if role_note and art.get("notes") != role_note:
        art["notes"] = role_note
        changed = True

    return changed


def has_local_scans(doc: dict) -> bool:
    for art in doc.get("articles") or []:
        url = (art.get("scan") or {}).get("url") or ""
        if url.startswith("images/scans/"):
            return True
    return False


def has_identified_pages(doc: dict) -> bool:
    for art in doc.get("articles") or []:
        if art.get("pages"):
            return True
    return False


def decide_status(doc: dict, vkgy: dict | None, scan_url: str | None) -> str | None:
    """Return new status if promotion warranted, else None."""
    current = doc.get("verification_status", "mention_only")
    roles = (vkgy or {}).get("roles") or []
    has_vkgy_issue = bool(vkgy and vkgy.get("url"))
    has_timeline = ARTIST_URL in (doc.get("source_notes") or "")

    if has_local_scans(doc) and has_identified_pages(doc):
        return "verified"

    if scan_url and has_vkgy_issue:
        scan = doc["articles"][0].setdefault("scan", {})
        if not scan.get("available"):
            scan["available"] = True
            scan["quality"] = "medium"
            scan["url"] = scan_url
        if current in ("mention_only",):
            return "possible"

    if has_vkgy_issue and has_timeline and doc.get("issue_number") and doc.get("date_precision") == "month":
        if "cover" in roles:
            return "verified"
        if current == "mention_only":
            return "possible"

    if has_vkgy_issue and current == "mention_only":
        return "possible"

    return None


def pick_canonical_uv_files() -> dict[str, Path]:
    """issue_number -> preferred yaml path (month-dated over vol-*)."""
    files = list((ISSUES / "uv").glob("*.yaml"))
    by_num: dict[str, list[Path]] = {}
    for path in files:
        doc = load_yaml(path)
        num = doc.get("issue_number")
        if num is not None:
            key = str(int(num)) if str(num).isdigit() else str(num)
            by_num.setdefault(key, []).append(path)

    chosen: dict[str, Path] = {}
    for num, paths in by_num.items():
        dated = [p for p in paths if p.stem[:4].isdigit() and "-" in p.stem]
        chosen[num] = dated[0] if dated else paths[0]
    return chosen


def promote_uv(vkgy_map: dict[str, dict]) -> tuple[int, int, int]:
    promoted = merged = removed = 0
    canonical = pick_canonical_uv_files()

    for num, path in canonical.items():
        vkgy = vkgy_map.get(num)
        if not vkgy:
            continue
        doc = load_yaml(path)
        if merge_vkgy_into_issue(doc, vkgy):
            merged += 1
        new_status = decide_status(doc, vkgy, None)
        if new_status and new_status != doc.get("verification_status"):
            old = doc["verification_status"]
            doc["verification_status"] = new_status
            add_changelog(
                doc,
                "verified" if new_status == "verified" else "status_change",
                "vkgy",
                f"Promoted {old} → {new_status} via vk.gy per-issue TOC + artist timeline.",
            )
            promoted += 1
        dump_yaml(path, doc)

    # Remove duplicate vol-* when dated canonical exists
    for num, keep in canonical.items():
        if not keep.stem.startswith("vol-"):
            dup = ISSUES / "uv" / f"vol-{num}.yaml"
            if dup.exists() and dup != keep:
                dup.unlink()
                removed += 1

    return promoted, merged, removed


def promote_pop_beat(incomplete_scans: dict[str, str]) -> int:
    promoted = 0
    pub_dir = ISSUES / "pop-beat"
    if not pub_dir.exists():
        return 0

    for path in sorted(pub_dir.glob("*.yaml")):
        doc = load_yaml(path)
        date = doc.get("publication_date", "")[:7]
        scan_url = incomplete_scans.get(date)
        current = doc.get("verification_status")

        # Ensure timeline cross-ref in source notes
        notes = doc.get("source_notes") or ""
        if ARTIST_URL not in notes:
            doc["source_notes"] = f"POP BEAT {date}\n[vkgy-timeline] {ARTIST_URL}\n{notes}".strip()
            add_changelog(doc, "updated", "vkgy-timeline", "Added vk.gy artist timeline cross-reference.")

        if scan_url and not has_local_scans(doc):
            art = doc["articles"][0]
            scan = art.setdefault("scan", {})
            if not scan.get("available"):
                scan["available"] = True
                scan["quality"] = "medium"
                scan["url"] = scan_url
                if "[malice-archive-incomplete-mags]" not in (doc.get("source_notes") or ""):
                    doc["source_notes"] = (
                        (doc.get("source_notes") or "")
                        + "\n[malice-archive-incomplete-mags] https://malice-archive.neocities.org/Incompletemags/main"
                    ).strip()

        new_status = decide_status(doc, None, scan_url)
        if new_status and new_status != current and current != "verified":
            doc["verification_status"] = new_status
            add_changelog(
                doc,
                "status_change",
                "malice-archive" if scan_url else "vkgy-timeline",
                f"Promoted {current} → {new_status}.",
            )
            promoted += 1

        dump_yaml(path, doc)

    return promoted


def main() -> None:
    uv_map = load_vkgy_harvest("uv")
    pop_scans = load_incomplete_scans("pop-beat")

    uv_promoted, uv_merged, uv_removed = promote_uv(uv_map)
    pb_promoted = promote_pop_beat(pop_scans)

    print(f"uv: merged {uv_merged}, promoted {uv_promoted}, removed {uv_removed} duplicate vol stubs")
    print(f"pop-beat: promoted {pb_promoted} issues")


if __name__ == "__main__":
    main()
