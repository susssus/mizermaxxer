#!/usr/bin/env python3
"""Trace direct image URLs for scan sources in the print archive.

Reads scripts/research/scan_sources_catalog.yaml and related research files,
fetches gallery pages / metadata, and writes scripts/research/image_urls_catalog.yaml.

Sources:
  - Cantavanda WordPress galleries (fg-thumb full-size hrefs)
  - scape.sc Cher de memoire pamphlet (cherdememoireNN.jpg)
  - Internet Archive item metadata (image/* files)
  - Reddit gallery posts via PullPush (i.redd.it originals)
  - vk.gy FOOL'S MATE cover scans (optional --vkgy)
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCAN_CATALOG = ROOT / "scripts/research/scan_sources_catalog.yaml"
REDDIT_CATALOG = ROOT / "scripts/research/reddit_scan_sources.yaml"
VKGY_CATALOG = ROOT / "scripts/research/vkgy_fools_mate_malice_mizer.yaml"
OUT = ROOT / "scripts/research/image_urls_catalog.yaml"

USER_AGENT = "Mozilla/5.0 (compatible; malice-mizer-print-archive/1.0; image-url-tracer)"


def fetch(url: str, timeout: int = 45) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def fetch_json(url: str, timeout: int = 45) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def cantavanda_scan_urls(html: str) -> list[str]:
    """Full-size JPGs from FooGallery fg-thumb links; scan filenames only."""
    urls: list[str] = []
    for m in re.finditer(
        r'class="fg-thumb"[^>]*href="(https://cantavanda\.com/malice-mizer/wp-content/uploads/sites/4/[^"]+\.(?:jpg|jpeg|png|webp))"',
        html,
        re.I,
    ):
        url = m.group(1)
        if "MALICE-MIZER-Scans" in url or "ma-cherie" in url.lower() or "Ma-Cherie" in url:
            urls.append(url)
    # Fallback: any fg-thumb upload not matching site chrome
    if not urls:
        for m in re.finditer(
            r'href="(https://cantavanda\.com/malice-mizer/wp-content/uploads/sites/4/[^"]+\.(?:jpg|jpeg|png|webp))"',
            html,
            re.I,
        ):
            url = m.group(1)
            if any(
                skip in url
                for skip in (
                    "Logo",
                    "Banner",
                    "Background",
                    "Site-Icon",
                    "Cantavanda-Logo",
                    "LAREINE",
                    "VELVET-EDEN",
                    "Logo-New",
                    "banner-1",
                )
            ):
                continue
            if url not in urls:
                urls.append(url)
    return sorted(set(urls))


def scape_pamphlet_urls(page_count: int = 33) -> list[dict[str, Any]]:
    base = "http://www.scape.sc/pamphlets/cherdememoire"
    images: list[dict[str, Any]] = []
    for page in range(page_count + 1):
        nn = f"{page:02d}"
        images.append(
            {
                "index": page + 1,
                "page": page,
                "url": f"{base}/cherdememoire{nn}.jpg",
                "variant": "full",
            }
        )
        images.append(
            {
                "index": page + 1,
                "page": page,
                "url": f"{base}/cherdememoire{nn}med.jpg",
                "variant": "medium",
            }
        )
        images.append(
            {
                "index": page + 1,
                "page": page,
                "url": f"{base}/cherdememoire{nn}thumb.jpg",
                "variant": "thumb",
            }
        )
    return images


def ia_image_urls(identifier: str) -> list[dict[str, Any]]:
    meta = fetch_json(f"https://archive.org/metadata/{identifier}")
    files = meta.get("files") or []
    images: list[dict[str, Any]] = []
    for idx, f in enumerate(files, start=1):
        name = f.get("name") or ""
        fmt = (f.get("format") or "").lower()
        if fmt not in ("jpeg", "jpg", "png", "gif", "webp", "item tile") and not re.search(
            r"\.(jpe?g|png|gif|webp)$", name, re.I
        ):
            continue
        if name.endswith("_thumb.jpg") or name.endswith("_thumb.gif"):
            variant = "thumb"
        elif "thumb" in name.lower():
            variant = "thumb"
        else:
            variant = "full"
        url = f"https://archive.org/download/{identifier}/{urllib.parse.quote(name)}"
        images.append({"index": idx, "url": url, "variant": variant, "filename": name})
    return images


def reddit_post_images(post_id: str) -> list[dict[str, Any]]:
    """Resolve i.redd.it URLs from PullPush submission media_metadata."""
    data = fetch_json(f"https://api.pullpush.io/reddit/search/submission/?ids={post_id}")
    posts = data.get("data") or []
    if not posts:
        return []
    post = posts[0]
    md = post.get("media_metadata") or {}
    images: list[dict[str, Any]] = []
    gallery = post.get("gallery_data") or {}
    order = [item.get("media_id") for item in (gallery.get("items") or []) if item.get("media_id")]
    keys = order or list(md.keys())
    for idx, key in enumerate(keys, start=1):
        item = md.get(key) or {}
        preview = (item.get("s") or {}).get("u", "").replace("&amp;", "&")
        media_id = key
        direct = f"https://i.redd.it/{media_id}.jpg"
        images.append(
            {
                "index": idx,
                "url": direct,
                "variant": "full",
                "preview_url": preview or None,
            }
        )
    return images


def vkgy_cover_urls(html: str) -> dict[str, str | None]:
    out: dict[str, str | None] = {"cover_full": None, "cover_medium": None}
    m = re.search(r'href="(/images/[^"]+-release\.jpg)"', html)
    if m:
        out["cover_full"] = f"https://vk.gy{m.group(1)}"
    mm = re.search(r'data-src="(/images/[^"]+release[^"]+\.jpg)"', html)
    if mm:
        out["cover_medium"] = f"https://vk.gy{mm.group(1)}"
    return out


def entry_key(item: dict[str, Any]) -> str:
    pub = item.get("publication", "unknown")
    date = item.get("issue_date") or item.get("title", "unknown")
    num = item.get("issue_number")
    if num:
        return f"{pub}-{num}"
    return f"{pub}-{date}".replace(" ", "-").lower()


def trace_scan_catalog(include_vkgy: bool = False, vkgy_delay: float = 0.4) -> dict[str, Any]:
    catalog = yaml.safe_load(SCAN_CATALOG.read_text(encoding="utf-8"))
    entries: list[dict[str, Any]] = []

    for item in catalog.get("items") or []:
        scan_url = item.get("scan_url")
        if not scan_url:
            continue
        source = item.get("source", "")
        key = entry_key(item)
        entry: dict[str, Any] = {
            "key": key,
            "title": item.get("title"),
            "project_path": item.get("project_path"),
            "gallery_url": scan_url,
            "source": source,
            "images": [],
        }

        try:
            if source == "cantavanda-magazine-appearances" or source == "cantavanda-fan-club-mags":
                html = fetch(scan_url)
                urls = cantavanda_scan_urls(html)
                entry["images"] = [
                    {"index": i, "url": u, "variant": "full"} for i, u in enumerate(urls, start=1)
                ]
                print(f"  cantavanda {key}: {len(urls)} images")
            elif source == "scape-cher-de-memoire":
                entry["images"] = scape_pamphlet_urls(item.get("page_count") or 33)
                # Keep only full-size in primary list; store variants separately
                full_only = [img for img in entry["images"] if img["variant"] == "full"]
                entry["images"] = full_only
                entry["image_variants"] = scape_pamphlet_urls(item.get("page_count") or 33)
                print(f"  scape {key}: {len(full_only)} full pages")
            elif source == "internet-archive":
                ident = scan_url.rstrip("/").split("/")[-1]
                imgs = ia_image_urls(ident)
                entry["images"] = imgs
                entry["archive_identifier"] = ident
                print(f"  ia {key} ({ident}): {len(imgs)} files")
            else:
                print(f"  skip {key}: unknown source {source}")
                continue
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            entry["error"] = str(exc)
            print(f"  error {key}: {exc}", flush=True)

        entries.append(entry)
        time.sleep(0.3)

    if include_vkgy and VKGY_CATALOG.exists():
        vkgy = yaml.safe_load(VKGY_CATALOG.read_text(encoding="utf-8"))
        for issue in vkgy.get("entries") or []:
            url = issue.get("url")
            if not url:
                continue
            num = issue.get("issue_number")
            try:
                html = fetch(url)
                covers = vkgy_cover_urls(html)
                if not covers.get("cover_full") and not covers.get("cover_medium"):
                    continue
                entries.append(
                    {
                        "key": f"vkgy-fools-mate-{num}",
                        "title": f"FOOL'S MATE #{num} cover (vk.gy)",
                        "project_path": None,
                        "gallery_url": url,
                        "source": "vkgy-fools-mate",
                        "issue_number": num,
                        "cover_image_url": covers.get("cover_full"),
                        "cover_image_medium_url": covers.get("cover_medium"),
                        "images": [
                            img
                            for img in (
                                {"index": 1, "url": covers["cover_full"], "variant": "full"}
                                if covers.get("cover_full")
                                else None,
                                {"index": 2, "url": covers["cover_medium"], "variant": "medium"}
                                if covers.get("cover_medium")
                                else None,
                            )
                            if img
                        ],
                    }
                )
                print(f"  vkgy #{num}: cover traced")
            except (urllib.error.URLError, TimeoutError) as exc:
                print(f"  vkgy #{num} error: {exc}")
            time.sleep(vkgy_delay)

    return {
        "generated": datetime.now(UTC).strftime("%Y-%m-%d"),
        "source_notes": (
            "Direct image URLs traced from gallery pages and archive metadata. "
            "Images are linked externally (not mirrored) per docs/RESEARCH.md."
        ),
        "entries": entries,
    }


def trace_reddit_entries() -> list[dict[str, Any]]:
    if not REDDIT_CATALOG.exists():
        return []
    reddit = yaml.safe_load(REDDIT_CATALOG.read_text(encoding="utf-8"))
    entries: list[dict[str, Any]] = []
    for thread in reddit.get("threads") or []:
        if thread.get("type") != "scan_identification":
            continue
        tid = thread.get("id", "").replace("reddit-", "")
        if not tid:
            m = re.search(r"/comments/([a-z0-9]+)/", thread.get("url") or "")
            tid = m.group(1) if m else ""
        if not tid:
            continue
        try:
            images = reddit_post_images(tid)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            entries.append(
                {
                    "key": thread.get("id"),
                    "gallery_url": thread.get("url"),
                    "source": "reddit",
                    "error": str(exc),
                    "images": [],
                }
            )
            continue
        if not images:
            continue
        ident = (thread.get("identifications") or [{}])[0]
        entries.append(
            {
                "key": thread.get("id"),
                "title": thread.get("title"),
                "gallery_url": thread.get("url"),
                "source": "reddit",
                "publication": ident.get("publication"),
                "issue_number": ident.get("issue_number"),
                "issue_date": ident.get("issue_date"),
                "project_links": ident.get("project_links"),
                "notes": "Reposted crops; original scan host unknown.",
                "images": images,
            }
        )
        print(f"  reddit {thread.get('id')}: {len(images)} images")
        time.sleep(0.5)
    return entries


def patch_scan_sources_catalog(catalog_out: dict[str, Any]) -> int:
    """Add image_urls / image_url_count to scan_sources_catalog items in-place."""
    if not SCAN_CATALOG.exists():
        return 0
    text = SCAN_CATALOG.read_text(encoding="utf-8")
    scan = yaml.safe_load(text)
    by_path: dict[str, dict[str, Any]] = {}
    for entry in catalog_out.get("entries") or []:
        path = entry.get("project_path")
        if path:
            by_path[path] = entry

    changed = 0
    for item in scan.get("items") or []:
        path = item.get("project_path")
        if path not in by_path:
            continue
        entry = by_path[path]
        imgs = entry.get("images") or []
        full_urls = [i["url"] for i in imgs if i.get("variant") in (None, "full")]
        if not full_urls:
            continue
        item["image_urls"] = full_urls
        item["image_url_count"] = len(full_urls)
        changed += 1

    if not changed:
        return 0

    header_match = re.match(r"(#.*?\n\n)", text, re.S)
    header = header_match.group(1) if header_match else ""
    body = yaml.dump(scan, allow_unicode=True, sort_keys=False, default_flow_style=False)
    # yaml.dump includes sources: at top; strip duplicate if header already had structure
    if body.startswith("sources:"):
        SCAN_CATALOG.write_text(header + body, encoding="utf-8")
    else:
        SCAN_CATALOG.write_text(header + body, encoding="utf-8")
    return changed


def patch_reddit_catalog(reddit_entries: list[dict[str, Any]]) -> int:
    """Add image_urls to reddit threads without rewriting the whole file."""
    if not REDDIT_CATALOG.exists() or not reddit_entries:
        return 0
    text = REDDIT_CATALOG.read_text(encoding="utf-8")
    changed = 0
    for entry in reddit_entries:
        thread_id = entry.get("key")
        urls = [i["url"] for i in entry.get("images") or [] if i.get("url")]
        if not thread_id or not urls:
            continue
        block = yaml.dump(
            {"image_urls": urls},
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        ).rstrip()
        pattern = rf"(- id: {re.escape(thread_id)}\n(?:  .+\n)*?)(  image_urls:\n(?:  - .+\n)*)?"
        if not re.search(pattern, text):
            continue
        replacement = rf"\1{block}\n"
        new_text = re.sub(pattern, replacement, text, count=1)
        if new_text != text:
            text = new_text
            changed += 1
    if changed:
        REDDIT_CATALOG.write_text(text, encoding="utf-8")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Trace direct image URLs for scan sources.")
    parser.add_argument(
        "--vkgy",
        action="store_true",
        help="Also fetch vk.gy FOOL'S MATE cover images (~2 min).",
    )
    parser.add_argument(
        "--patch-catalogs",
        action="store_true",
        help="Update scan_sources_catalog.yaml and reddit_scan_sources.yaml with traced URLs.",
    )
    args = parser.parse_args()

    print("Tracing image URLs…")
    catalog_out = trace_scan_catalog(include_vkgy=args.vkgy)
    reddit_entries = trace_reddit_entries()
    if reddit_entries:
        catalog_out["reddit_entries"] = reddit_entries

    OUT.write_text(
        yaml.dump(catalog_out, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    total = sum(len(e.get("images") or []) for e in catalog_out.get("entries") or [])
    total += sum(len(e.get("images") or []) for e in reddit_entries)
    print(f"Wrote {OUT} ({len(catalog_out.get('entries', []))} scan entries, {total} image URLs)")

    if args.patch_catalogs:
        n = patch_scan_sources_catalog(catalog_out)
        r = patch_reddit_catalog(reddit_entries)
        print(f"Patched scan_sources_catalog ({n} items), reddit_scan_sources ({r} threads)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
