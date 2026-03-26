#!/usr/bin/env python3
"""
Generates book.json from a book's txt file containing chapter URLs.
Fetches <title> from each chapter page for proper names with diacritics.

Usage: python3 generate_book_json.py <BOOK_DIR>
  BOOK_DIR must contain a .txt file with the index URL and chapter URLs.
"""
import html as html_mod
import json
import os
import re
import sys
import urllib.request


def fetch_title(url):
    """Fetch a URL and extract the <title> content."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        text = r.read().decode("utf-8", errors="replace")
    m = re.search(r'<title>([^<]+)</title>', text, re.IGNORECASE)
    if m:
        return html_mod.unescape(m.group(1)).strip()
    return ""


def strip_roman_prefix(title):
    """'IX - Crítica do Imperialismo' -> 'Crítica do Imperialismo'"""
    return re.sub(r'^[IVXLC]+[\.\s\-–—:]+\s*', '', title).strip()


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 generate_book_json.py <BOOK_DIR>")
        sys.exit(1)

    book_dir = sys.argv[1]

    # Find the .txt file with URLs
    txt_files = [f for f in os.listdir(book_dir)
                 if f.endswith('.txt') and os.path.isfile(os.path.join(book_dir, f))]
    if not txt_files:
        print("❌ Nenhum .txt encontrado em", book_dir)
        sys.exit(1)

    txt_path = os.path.join(book_dir, txt_files[0])
    with open(txt_path) as f:
        lines = f.read().strip().split('\n')

    # Parse index URL and chapter URLs
    index_url = ""
    chapter_urls = []
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            m = re.search(r'(https?://\S+)', line)
            if m:
                index_url = m.group(1)
        elif line.startswith('http'):
            chapter_urls.append(line)

    # Book title from index page
    book_title = ""
    if index_url:
        book_title = fetch_title(index_url)

    # Year from URL
    m = re.search(r'/(\d{4})/', index_url or (chapter_urls[0] if chapter_urls else ""))
    year = m.group(1) if m else ""

    # Chapter folders sorted
    chapter_dirs = sorted([
        d for d in os.listdir(book_dir)
        if os.path.isdir(os.path.join(book_dir, d))
    ])

    # Fetch title from each chapter URL, map to folder slug
    chapters = {}
    for i, ch_dir in enumerate(chapter_dirs):
        slug = re.sub(r'^\d+_', '', ch_dir)
        if i < len(chapter_urls):
            raw_title = fetch_title(chapter_urls[i])
            chapters[slug] = strip_roman_prefix(raw_title) if raw_title else slug.replace('_', ' ')
            print(f"   {slug} → {chapters[slug]}")
        else:
            chapters[slug] = slug.replace('_', ' ')

    out = {
        "title": book_title,
        "year": year,
        "image": "",
        "description": "",
        "chapters": chapters,
    }

    out_path = os.path.join(book_dir, "book.json")
    with open(out_path, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"📚 {book_title} — {len(chapters)} capítulos")


if __name__ == "__main__":
    main()
