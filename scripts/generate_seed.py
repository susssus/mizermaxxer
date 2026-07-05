#!/usr/bin/env python3
"""Generate Phase 1 seed issue stubs."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ISSUES = ROOT / "data" / "issues"
TODAY = "2026-07-06"


def article(issue_id: str, index: int, article_type: str, **kwargs) -> dict:
    base = {
        "id": f"{issue_id}-{index:03d}",
        "title_ja": None,
        "title_en": None,
        "type": article_type,
        "pages": None,
        "members": [],
        "photographer": None,
        "writer": None,
        "cover": False,
        "poster": False,
        "foldout": False,
        "scan": {"available": False, "quality": None, "url": None},
        "translation": {"available": False, "url": None},
        "purchase_links": [],
        "notes": "",
    }
    base.update(kwargs)
    return base


def changelog(notes: str, action: str = "created") -> list[dict]:
    return [
        {
            "date": TODAY,
            "action": action,
            "source": "user_bibliography",
            "notes": notes,
        }
    ]


def write_issue(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main() -> None:
    # 1992 specific entries
    write_issue(
        ISSUES / "flyers" / "1992-08.yaml",
        {
            "id": "flyers-1992-08",
            "publication": "flyers",
            "issue_number": None,
            "volume": None,
            "publication_date": "1992-08",
            "date_precision": "month",
            "verification_status": "needs_verification",
            "source_notes": "Earliest promotional material. Band formation period.",
            "research_targets": [
                "earliest artist photo",
                "first advertisement",
            ],
            "articles": [
                article("flyers-1992-08", 1, "flyer", notes="Earliest known live flyer.")
            ],
            "changelog": changelog("Initial stub from Phase 1 master bibliography"),
        },
    )

    write_issue(
        ISSUES / "fools-mate" / "1992-09.yaml",
        {
            "id": "fools-mate-1992-09",
            "publication": "fools-mate",
            "issue_number": None,
            "volume": None,
            "publication_date": "1992-09",
            "date_precision": "month",
            "verification_status": "mention_only",
            "source_notes": "Live listings likely.",
            "articles": [
                article(
                    "fools-mate-1992-09",
                    1,
                    "live_listing",
                    notes="Suspected indie live listing mention.",
                )
            ],
            "changelog": changelog("Initial stub from Phase 1 master bibliography"),
        },
    )

    write_issue(
        ISSUES / "arena37" / "1992-10.yaml",
        {
            "id": "arena37-1992-10",
            "publication": "arena37",
            "issue_number": None,
            "volume": None,
            "publication_date": "1992-10",
            "date_precision": "month",
            "verification_status": "mention_only",
            "source_notes": "Indies concert listings.",
            "articles": [
                article("arena37-1992-10", 1, "live_listing", notes="Indies concert listing mention.")
            ],
            "changelog": changelog("Initial stub from Phase 1 master bibliography"),
        },
    )

    write_issue(
        ISSUES / "shoxx" / "1992-11.yaml",
        {
            "id": "shoxx-1992-11",
            "publication": "shoxx",
            "issue_number": None,
            "volume": None,
            "publication_date": "1992-11",
            "date_precision": "month",
            "verification_status": "possible",
            "source_notes": "Small introduction possible.",
            "articles": [
                article("shoxx-1992-11", 1, "mention", notes="Possible small introduction.")
            ],
            "changelog": changelog("Initial stub from Phase 1 master bibliography"),
        },
    )

    write_issue(
        ISSUES / "fools-mate" / "1992-12.yaml",
        {
            "id": "fools-mate-1992-12",
            "publication": "fools-mate",
            "issue_number": None,
            "volume": None,
            "publication_date": "1992-12",
            "date_precision": "month",
            "verification_status": "possible",
            "source_notes": "Possible live report.",
            "articles": [
                article("fools-mate-1992-12", 1, "live_report", notes="Possible live report.")
            ],
            "changelog": changelog("Initial stub from Phase 1 master bibliography"),
        },
    )

    # 1993 monthly FOOL'S MATE placeholders
    research_1993 = [
        "exact issue numbers",
        "page numbers",
        "photographers",
        "interviewer",
        "scan availability",
    ]
    for month in range(1, 13):
        slug = f"1993-{month:02d}"
        issue_id = f"fools-mate-{slug}"
        write_issue(
            ISSUES / "fools-mate" / f"{slug}.yaml",
            {
                "id": issue_id,
                "publication": "fools-mate",
                "issue_number": None,
                "volume": None,
                "publication_date": slug,
                "date_precision": "month",
                "verification_status": "needs_verification",
                "source_notes": "1993 research placeholder; editors began noticing the band.",
                "research_targets": research_1993,
                "articles": [
                    article(
                        issue_id,
                        1,
                        "mention",
                        notes="Placeholder for any 1993 FOOL'S MATE coverage.",
                    )
                ],
                "changelog": changelog("1993 placeholder stub"),
            },
        )

    # 1993 quarterly SHOXX / Arena37
    for pub in ("shoxx", "arena37"):
        for month in (3, 6, 9, 12):
            slug = f"1993-{month:02d}"
            issue_id = f"{pub}-{slug}"
            write_issue(
                ISSUES / pub / f"{slug}.yaml",
                {
                    "id": issue_id,
                    "publication": pub,
                    "issue_number": None,
                    "volume": None,
                    "publication_date": slug,
                    "date_precision": "month",
                    "verification_status": "needs_verification",
                    "source_notes": f"1993 quarterly research placeholder for {pub.upper()}.",
                    "research_targets": research_1993,
                    "articles": [
                        article(
                            issue_id,
                            1,
                            "mention",
                            notes="Placeholder for suspected 1993 coverage.",
                        )
                    ],
                    "changelog": changelog("1993 placeholder stub"),
                },
            )

    # 1994 Memoire era
    memoire_targets = [
        "cover",
        "poster",
        "review",
        "interview",
        "advertisement",
        "release calendar",
    ]
    for pub in ("fools-mate", "shoxx", "arena37"):
        for month in range(1, 13):
            slug = f"1994-{month:02d}"
            issue_id = f"{pub}-{slug}"
            write_issue(
                ISSUES / pub / f"{slug}.yaml",
                {
                    "id": issue_id,
                    "publication": pub,
                    "issue_number": None,
                    "volume": None,
                    "publication_date": slug,
                    "date_precision": "month",
                    "verification_status": "possible",
                    "source_notes": "1994 Memoire era research stub.",
                    "research_targets": memoire_targets,
                    "articles": [
                        article(
                            issue_id,
                            1,
                            "mention",
                            notes="Placeholder for Memoire-era coverage.",
                        )
                    ],
                    "changelog": changelog("1994 Memoire-era placeholder stub"),
                },
            )

    for month in (3, 6, 9, 12):
        slug = f"1994-{month:02d}"
        issue_id = f"vicious-{slug}"
        write_issue(
            ISSUES / "vicious" / f"{slug}.yaml",
            {
                "id": issue_id,
                "publication": "vicious",
                "issue_number": None,
                "volume": None,
                "publication_date": slug,
                "date_precision": "month",
                "verification_status": "possible",
                "source_notes": "Vicious coverage needs confirmation.",
                "research_targets": memoire_targets,
                "articles": [
                    article(
                        issue_id,
                        1,
                        "mention",
                        notes="Possible Vicious mention during Memoire era.",
                    )
                ],
                "changelog": changelog("1994 Vicious placeholder stub"),
            },
        )

    # 1995 transition period
    transition_targets = [
        "major label coverage",
        "advertisements",
        "instrument interviews",
        "concert reports",
    ]
    for pub in ("fools-mate", "shoxx", "arena37"):
        for month in (3, 6, 9, 12):
            slug = f"1995-{month:02d}"
            issue_id = f"{pub}-{slug}"
            write_issue(
                ISSUES / pub / f"{slug}.yaml",
                {
                    "id": issue_id,
                    "publication": pub,
                    "issue_number": None,
                    "volume": None,
                    "publication_date": slug,
                    "date_precision": "month",
                    "verification_status": "needs_verification",
                    "source_notes": "1995 transition period research stub.",
                    "research_targets": transition_targets,
                    "articles": [
                        article(
                            issue_id,
                            1,
                            "mention",
                            notes="Placeholder for 1995 transition coverage.",
                        )
                    ],
                    "changelog": changelog("1995 transition placeholder stub"),
                },
            )

    count = len(list(ISSUES.rglob("*.yaml")))
    print(f"Generated {count} issue files.")


if __name__ == "__main__":
    main()
