#!/usr/bin/env python3
"""Run NDL searches for needs_verification issue stubs and update YAML with results."""

from __future__ import annotations

import calendar
import html
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[2]
ISSUES = ROOT / "data" / "issues"
TODAY = "2026-07-06"

NDL_SRU = "https://ndlsearch.ndl.go.jp/api/sru"
SRW_NS = {"srw": "http://www.loc.gov/zing/srw/"}
RDF_NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "dcterms": "http://purl.org/dc/terms/",
    "dcndl": "http://ndl.go.jp/dcndl/terms/",
}

NDL_PUB_NAMES = {
    "fools-mate": "FOOL'S MATE",
    "shoxx": "SHOXX",
    "arena37": "Arena37",
}


def build_query(publication: str, year: int, month: int) -> str:
    last_day = calendar.monthrange(year, month)[1]
    return (
        f'title exact "{publication}" AND '
        f"from={year}-{month:02d}-01 AND until={year}-{month:02d}-{last_day}"
    )


def parse_records(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    records = []
    for record in root.findall(".//srw:record", SRW_NS):
        data = record.find("srw:recordData", SRW_NS)
        if data is None or not (data.text and data.text.strip()):
            continue
        inner = html.unescape(data.text.strip())
        try:
            inner_root = ET.fromstring(inner)
        except ET.ParseError:
            continue
        title = (inner_root.findtext(".//dcterms:title", default="", namespaces=RDF_NS) or "").strip()
        volume = (
            inner_root.findtext(".//dcndl:volume/rdf:Description/rdf:value", default="", namespaces=RDF_NS)
            or inner_root.findtext(".//dcndl:volume", default="", namespaces=RDF_NS)
            or ""
        ).strip()
        url = ""
        for admin in inner_root.findall(".//dcndl:BibAdminResource", RDF_NS):
            url = admin.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")
            if url:
                break
        if title or volume:
            records.append({"title": title, "volume": volume, "url": url})
    return records


def ndl_search(pub_name: str, year: int, month: int) -> list[dict]:
    params = {
        "operation": "searchRetrieve",
        "query": build_query(pub_name, year, month),
        "recordSchema": "dcndl",
        "maximumRecords": 5,
    }
    resp = requests.get(NDL_SRU, params=params, timeout=30)
    resp.raise_for_status()
    return parse_records(resp.text)


def parse_date(publication_date: str) -> tuple[int, int] | None:
    m = re.match(r"(\d{4})-(\d{2})", publication_date)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def main() -> None:
    paths = sorted(ISSUES.rglob("*.yaml"))
    updated = 0
    for path in paths:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        if doc.get("verification_status") != "needs_verification":
            continue
        pub = doc.get("publication")
        pub_name = NDL_PUB_NAMES.get(pub)
        if not pub_name:
            continue
        parsed = parse_date(doc.get("publication_date", ""))
        if not parsed:
            continue
        year, month = parsed
        print(f"NDL: {pub} {year}-{month:02d} …", end="", flush=True)
        try:
            records = ndl_search(pub_name, year, month)
        except Exception as exc:  # noqa: BLE001
            print(f" error: {exc}")
            continue
        time.sleep(0.5)
        if not records:
            print(" no records")
            continue
        rec = records[0]
        note = f"NDL candidate ({year}-{month:02d}): {rec.get('volume') or rec.get('title')}"
        if rec.get("url"):
            note += f" — {rec['url']}"
        existing = doc.get("source_notes") or ""
        if "NDL candidate" not in existing:
            doc["source_notes"] = (existing + "\n" + note).strip()
        doc["verification_status"] = "possible"
        changelog = doc.setdefault("changelog", [])
        changelog.append(
            {
                "date": TODAY,
                "action": "status_change",
                "source": "ndl",
                "notes": note,
            }
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
        updated += 1
        print(f" → possible ({len(records)} hit(s))")

    print(f"\nUpdated {updated} issue stubs with NDL results.")


if __name__ == "__main__":
    main()
