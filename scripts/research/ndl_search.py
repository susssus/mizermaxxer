#!/usr/bin/env python3
"""Query the National Diet Library SRU API for magazine issue candidates."""

from __future__ import annotations

import argparse
import csv
import html
import sys
import xml.etree.ElementTree as ET

import requests

NDL_SRU = "https://ndlsearch.ndl.go.jp/api/sru"
SRW_NS = {"srw": "http://www.loc.gov/zing/srw/"}
RDF_NS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "dcterms": "http://purl.org/dc/terms/",
    "dcndl": "http://ndl.go.jp/dcndl/terms/",
}


def build_query(publication: str, year: int | None, month: int | None) -> str:
    parts = [f'title exact "{publication}"']
    if year and month:
        import calendar

        last_day = calendar.monthrange(year, month)[1]
        parts.append(f"from={year}-{month:02d}-01")
        parts.append(f"until={year}-{month:02d}-{last_day}")
    elif year:
        parts.append(f"from={year}-01-01")
        parts.append(f"until={year}-12-31")
    return " AND ".join(parts)


def text_or_none(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return (element.text or "").strip()


def parse_record(record: ET.Element) -> dict[str, str] | None:
    data = record.find("srw:recordData", SRW_NS)
    if data is None or not (data.text and data.text.strip()):
        return None

    inner = html.unescape(data.text.strip())
    try:
        root = ET.fromstring(inner)
    except ET.ParseError:
        return None

    description = text_or_none(root.find(".//dcterms:description", RDF_NS))
    if description == "type : title":
        return None

    title = text_or_none(root.find(".//dcterms:title", RDF_NS))
    volume = text_or_none(root.find(".//dcndl:volume/rdf:Description/rdf:value", RDF_NS))
    if not volume:
        volume = text_or_none(root.find(".//dcndl:volume", RDF_NS))

    ndl_id = ""
    for identifier in root.findall(".//dcterms:identifier", RDF_NS):
        datatype = identifier.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}datatype", "")
        if "NDLBibID" in datatype and identifier.text:
            ndl_id = identifier.text.strip()
            break

    about = ""
    for admin in root.findall(".//dcndl:BibAdminResource", RDF_NS):
        about = admin.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")
        if about:
            break

    url = about or (f"https://ndlsearch.ndl.go.jp/en/book/{ndl_id}" if ndl_id else "")
    date = volume.split()[-1] if volume else ""

    return {
        "title": title,
        "volume": volume,
        "date": date,
        "ndl_id": ndl_id,
        "url": url,
        "record_type": description.replace("type : ", ""),
    }


def search(publication: str, year: int | None, month: int | None, limit: int) -> list[dict[str, str]]:
    params = {
        "operation": "searchRetrieve",
        "query": build_query(publication, year, month),
        "recordSchema": "dcndl",
        "maximumRecords": str(limit),
    }
    response = requests.get(NDL_SRU, params=params, timeout=30)
    response.raise_for_status()
    root = ET.fromstring(response.text)

    records: list[dict[str, str]] = []
    seen: set[str] = set()
    for record in root.findall(".//srw:record", SRW_NS):
        parsed = parse_record(record)
        if not parsed:
            continue
        key = parsed["url"] or parsed["title"]
        if key in seen:
            continue
        seen.add(key)
        records.append(parsed)
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Search NDL for magazine issue candidates.")
    parser.add_argument("--publication", required=True, help='Magazine title, e.g. "FOOL\'S MATE"')
    parser.add_argument("--year", type=int, help="Publication year filter")
    parser.add_argument("--month", type=int, choices=range(1, 13), help="Optional month filter")
    parser.add_argument("--limit", type=int, default=50, help="Maximum records to retrieve")
    parser.add_argument("--csv", help="Optional CSV output path")
    args = parser.parse_args()

    try:
        records = search(args.publication, args.year, args.month, args.limit)
    except requests.RequestException as exc:
        print(f"NDL request failed: {exc}", file=sys.stderr)
        return 1

    if args.csv:
        with open(args.csv, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["title", "volume", "date", "ndl_id", "url", "record_type"],
            )
            writer.writeheader()
            writer.writerows(records)
        print(f"Wrote {len(records)} records to {args.csv}")
    else:
        if not records:
            print("No records found.")
            return 0
        for record in records:
            print(
                f"{record['date']}\t{record['volume']}\t{record['record_type']}\t{record['url']}"
            )
        print(f"\nTotal: {len(records)} records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
