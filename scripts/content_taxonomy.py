#!/usr/bin/env python3
"""Content classification helpers for bibliography articles."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = ROOT / "data" / "content_taxonomy.yaml"

EDITORIAL_TYPES = frozenset(
    {
        "interview",
        "live_report",
        "review",
        "photo_spread",
        "instrument_interview",
        "cover",
        "newsletter",
        "release_calendar",
    }
)
PROMOTIONAL_TYPES = frozenset(
    {"advertisement", "flyer", "live_listing", "poster", "pamphlet"}
)
VKGY_ROLE_PATTERN = re.compile(r"vkgy roles:\s*([^\n]+)", re.IGNORECASE)
VKGY_ROLE_MAP = {
    "large_feature": "large_feature",
    "other_appearance": "other_appearance",
    "flyer": "flyer",
    "cover": "cover",
    "poster": "poster",
    "mention": "mention",
}


def load_taxonomy() -> dict[str, Any]:
    with TAXONOMY_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def parse_vkgy_roles(notes: str | None) -> list[str]:
    if not notes:
        return []
    match = VKGY_ROLE_PATTERN.search(notes)
    if not match:
        return []
    roles: list[str] = []
    for token in match.group(1).split(","):
        normalized = token.strip().lower().replace(" ", "_")
        if normalized in VKGY_ROLE_MAP:
            roles.append(VKGY_ROLE_MAP[normalized])
    return roles


def infer_promotional_subtype(article: dict[str, Any], issue_publication: str | None = None) -> str | None:
    if article.get("promotional_subtype"):
        return article["promotional_subtype"]

    article_type = article.get("type") or article.get("article_type")
    taxonomy = load_taxonomy()
    defaults = taxonomy.get("promotional_type_defaults", {})
    if article_type in defaults:
        return defaults[article_type]

    title = f"{article.get('title_en') or ''} {article.get('title_ja') or ''}".lower()
    if isinstance(article.get("title"), dict):
        title = f"{article['title'].get('romanized', '')} {article['title'].get('original', '')}".lower()
    notes = (article.get("notes") or "").lower()
    combined = f"{title} {notes}"

    vkgy_roles = article.get("vkgy_roles") or parse_vkgy_roles(article.get("notes"))
    if "flyer" in vkgy_roles and issue_publication and issue_publication != "flyers":
        return "magazine_inset"

    if article_type == "advertisement":
        if any(token in combined for token in ("tour", "standing tour", "oneman", "ライブ", "schedule", "sold out")):
            return "tour_ad"
        if any(token in combined for token in ("single", "album", "release", "debut", "vhs", "dvd", "発売", "デビュー")):
            return "release_ad"
        return "release_ad"

    if article_type == "flyer" or issue_publication == "flyers":
        if "demo" in combined:
            return "demo_flyer"
        if any(token in combined for token in ("live flyer", "upcoming lives", "upcoming live", "gig", "ライブ")):
            return "gig_flyer"
        if any(
            token in combined
            for token in (
                "release flyer",
                "single",
                "vhs",
                "dvd",
                "book",
                "release",
                "発売",
                "シングル",
            )
        ):
            return "release_flyer"
        if any(token in combined for token in ("photobook", "goods", "グッズ")):
            return "goods_ad"
        return "other"

    return None


def infer_content_nature(article: dict[str, Any]) -> str | None:
    if article.get("content_nature"):
        return article["content_nature"]

    article_type = article.get("type") or article.get("article_type")
    taxonomy = load_taxonomy()
    defaults = taxonomy.get("article_type_defaults", {})

    if article_type in EDITORIAL_TYPES:
        return "editorial"
    if article_type in PROMOTIONAL_TYPES:
        return "promotional"
    if article_type in defaults and defaults[article_type]:
        return defaults[article_type]

    vkgy_roles = article.get("vkgy_roles") or parse_vkgy_roles(article.get("notes"))
    if "flyer" in vkgy_roles and article_type == "mention":
        return "promotional"

    return None


def infer_promotional_carrier(
    article: dict[str, Any], issue_publication: str | None = None
) -> str | None:
    if article.get("promotional_carrier"):
        return article["promotional_carrier"]

    subtype = infer_promotional_subtype(article, issue_publication)
    if not subtype:
        return None

    taxonomy = load_taxonomy()
    meta = taxonomy.get("promotional_subtypes", {}).get(subtype, {})
    return meta.get("carrier")


def enrich_article(article: dict[str, Any], issue_publication: str | None = None) -> dict[str, Any]:
    enriched = dict(article)
    if not enriched.get("vkgy_roles"):
        roles = parse_vkgy_roles(enriched.get("notes"))
        if roles:
            enriched["vkgy_roles"] = roles

    nature = infer_content_nature(enriched)
    if nature:
        enriched["content_nature"] = nature

    if enriched.get("content_nature") == "promotional":
        subtype = infer_promotional_subtype(enriched, issue_publication)
        if subtype:
            enriched["promotional_subtype"] = subtype
        carrier = infer_promotional_carrier(enriched, issue_publication)
        if carrier:
            enriched["promotional_carrier"] = carrier

    return enriched


def subtype_label(subtype: str | None) -> str | None:
    if not subtype:
        return None
    taxonomy = load_taxonomy()
    return taxonomy.get("promotional_subtypes", {}).get(subtype, {}).get("label", subtype)
