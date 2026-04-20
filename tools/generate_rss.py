#!/usr/bin/env python3
"""Generate podcast RSS 2.0 feed with iTunes namespace from arquivos/ data."""

import argparse
import json
import os
import re
import subprocess
import sys
import xml.dom.minidom
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

S3_BASE = "https://nbds-podcast.s3.us-east-2.amazonaws.com"
SITE_URL = "https://pongelupe.github.io/na_boca_do_sol_podcast"
ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
ROOT = Path(__file__).resolve().parent.parent
ARQUIVOS = ROOT / "arquivos"


def seconds_to_hms(total):
    h = int(total) // 3600
    m = (int(total) % 3600) // 60
    s = int(total) % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def get_pub_date(timestamps_path):
    rel = os.path.relpath(timestamps_path, ROOT)
    try:
        result = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%aI", "--", rel],
            capture_output=True, text=True, cwd=ROOT
        )
        iso = result.stdout.strip().splitlines()
        if iso:
            return datetime.fromisoformat(iso[-1])
    except Exception:
        pass
    # fallback to file mtime
    mtime = os.path.getmtime(timestamps_path)
    return datetime.fromtimestamp(mtime, tz=timezone.utc)


def discover_episodes():
    episodes = []
    for ts_path in sorted(ARQUIVOS.rglob("*_timestamps.json")):
        ep_dir = ts_path.parent
        author_dir = None
        book_json_path = None
        is_book = False

        # Check if grandparent has book.json (book chapter)
        grandparent = ep_dir.parent
        if (grandparent / "book.json").exists() and grandparent != ARQUIVOS:
            is_book = True
            book_dir = grandparent
            author_dir = book_dir.parent
            book_json_path = grandparent / "book.json"
        else:
            author_dir = ep_dir.parent

        # Read author
        author_json = author_dir / "author.json"
        if not author_json.exists():
            continue
        with open(author_json) as f:
            author_name = json.load(f)["name"]

        # Read timestamps for duration
        with open(ts_path) as f:
            segments = json.load(f)["segments"]
        duration = seconds_to_hms(segments[-1]["end"])

        author_slug = author_dir.name
        chapter_slug = ts_path.stem.replace("_timestamps", "")

        if is_book:
            with open(book_json_path) as f:
                book_data = json.load(f)
            book_title = book_data["title"]
            folder_name = ep_dir.name
            # Extract numeric prefix: "001_Something" -> 1
            match = re.match(r"^(\d+)_(.+)$", folder_name)
            if match:
                n = int(match.group(1))
                chapter_key = match.group(2)
            else:
                continue
            chapter_title = book_data.get("chapters", {}).get(chapter_key, folder_name.replace("_", " "))
            title = f"{book_title} - Cap. {n}: {chapter_title}"
            mp3_url = f"{S3_BASE}/{author_slug}/{grandparent.name}/{folder_name}/{chapter_slug}.mp3"
        else:
            title = ep_dir.name.replace("_", " ")
            mp3_url = f"{S3_BASE}/{author_slug}/{ep_dir.name}/{ep_dir.name}.mp3"

        description = f"{title}, por {author_name}. Leitura com voz sintetizada por IA."
        pub_date = get_pub_date(ts_path)

        episodes.append({
            "title": title,
            "description": description,
            "mp3_url": mp3_url,
            "duration": duration,
            "pub_date": pub_date,
            "author_name": author_name,
        })

    # Sort newest first
    episodes.sort(key=lambda e: e["pub_date"], reverse=True)
    return episodes


def build_feed(episodes):
    ET.register_namespace("itunes", ITUNES_NS)
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Na Boca do Sol Podcast"
    ET.SubElement(channel, "link").text = SITE_URL
    ET.SubElement(channel, "description").text = (
        "Podcast de leitura de textos marxistas de domínio público, "
        "disponibilizados pelo Marxists Internet Archive. "
        "Episódios gerados com voz sintetizada por IA."
    )
    ET.SubElement(channel, "language").text = "pt-br"

    ns = f"{{{ITUNES_NS}}}"
    ET.SubElement(channel, f"{ns}author").text = "Na Boca do Sol"

    owner = ET.SubElement(channel, f"{ns}owner")
    ET.SubElement(owner, f"{ns}name").text = "Na Boca do Sol"
    ET.SubElement(owner, f"{ns}email").text = "nabocadosolpodcast@gmail.com"

    ET.SubElement(channel, f"{ns}image").set("href", f"{SITE_URL}/favicon.svg")
    ET.SubElement(channel, f"{ns}category").set("text", "Education")
    ET.SubElement(channel, f"{ns}explicit").text = "false"

    for ep in episodes:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = ep["title"]
        ET.SubElement(item, "description").text = ep["description"]
        enc = ET.SubElement(item, "enclosure")
        enc.set("url", ep["mp3_url"])
        enc.set("length", "0")
        enc.set("type", "audio/mpeg")
        guid = ET.SubElement(item, "guid")
        guid.set("isPermaLink", "false")
        guid.text = ep["mp3_url"]
        ET.SubElement(item, "pubDate").text = format_datetime(ep["pub_date"])
        ET.SubElement(item, f"{ns}author").text = ep["author_name"]
        ET.SubElement(item, f"{ns}duration").text = ep["duration"]
        ET.SubElement(item, f"{ns}explicit").text = "false"

    rough = ET.tostring(rss, encoding="unicode", xml_declaration=False)
    dom = xml.dom.minidom.parseString(rough)
    return dom.toprettyxml(indent="  ", encoding=None)


def main():
    parser = argparse.ArgumentParser(description="Generate podcast RSS feed")
    parser.add_argument("--output", help="Output file (default: stdout)")
    args = parser.parse_args()

    episodes = discover_episodes()
    xml_str = build_feed(episodes)

    # Replace minidom's default XML declaration with UTF-8 one
    xml_str = xml_str.replace(
        '<?xml version="1.0" ?>',
        '<?xml version="1.0" encoding="UTF-8"?>'
    )

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(xml_str)
    else:
        sys.stdout.write(xml_str)


if __name__ == "__main__":
    main()
