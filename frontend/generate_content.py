#!/usr/bin/env python3
"""
Converts arquivos/*/README.md into Astro content collection entries.
Transforms 📁 repo links into audio player + download buttons pointing to S3.
Also generates book pages for multi-chapter works.
"""
import os
import re
import sys
import json
import html as html_mod

S3_BASE = "https://nbds-podcast.s3.us-east-2.amazonaws.com"
ARQUIVOS_DIR = os.path.join(os.path.dirname(__file__), "..", "arquivos")
AUTHORS_DIR = os.path.join(os.path.dirname(__file__), "src", "content", "authors")
BOOKS_DIR = os.path.join(os.path.dirname(__file__), "src", "content", "books")

ORDER = {
    "marx": 1,
    "lenin": 2,
    "mao_zedong": 3,
    "jorge_amado": 4,
    "gonzalo_abimael_guzman": 5,
}

def load_author_meta(slug):
    json_path = os.path.join(ARQUIVOS_DIR, slug, "author.json")
    if os.path.exists(json_path):
        with open(json_path) as f:
            return json.load(f)
    return {}

def fix_broken_table_rows(content):
    def replace_tr(match):
        raw = match.group(0)
        title_match = re.search(r'<a href="[^"]*">(.+?)</a>', raw, re.DOTALL)
        title = title_match.group(1) if title_match else ""
        title = re.sub(r'<[^>]+>', '', title).strip()
        title = html_mod.unescape(title)
        date_match = re.search(r'<td>([^<]+)</td>', raw)
        date = date_match.group(1).strip() if date_match else ""
        mia_match = re.search(r'(\[🔗\]\([^)]+\))', raw)
        mia = mia_match.group(1) if mia_match else ""
        return f"| {title} | {date} |  | {mia} |"
    return re.sub(r'\| <tr>.*?\| \[🔗\]\([^)]+\) \|', replace_tr, content, flags=re.DOTALL)

def is_book(author_slug, folder_path):
    full = os.path.join(ARQUIVOS_DIR, author_slug, folder_path)
    if not os.path.isdir(full):
        return False
    return any(os.path.isdir(os.path.join(full, d)) for d in os.listdir(full))

def transform_repo_links(content, author_slug):
    def replace_link(match):
        folder_path = match.group(1).rstrip('/')
        if is_book(author_slug, folder_path):
            book_slug = folder_path.replace('/', '_')
            return f'[📖 ver capítulos](/{author_slug}/{book_slug}/)'
        filename = os.path.basename(folder_path)
        s3_url = f"{S3_BASE}/{author_slug}/{filename}.mp3"
        return f'[⬇️]({s3_url}) <audio controls preload="none" src="{s3_url}"></audio>'
    return re.sub(r'\[📁\]\(([^)]+)\)', replace_link, content)

# --- Book generation ---

def get_book_mia_url(author_slug, book_folder):
    """Extract MIA URL from the book's txt file."""
    txt_path = os.path.join(ARQUIVOS_DIR, author_slug, book_folder, f"{book_folder}.txt")
    if not os.path.exists(txt_path):
        return ""
    with open(txt_path) as f:
        first_line = f.readline().strip()
    # Lines like "# https://..." or "# url base do livro https://..."
    url_match = re.search(r'(https?://\S+)', first_line)
    return url_match.group(1) if url_match else ""

def get_chapter_title(chapter_dir_name):
    """Convert folder name like '003_A_Experincia_da_Comuna' to readable title."""
    # Strip numeric prefix
    name = re.sub(r'^\d+_', '', chapter_dir_name)
    # Also strip roman numeral prefix like "I.", "XIV."
    name = re.sub(r'^[IVXLC]+\.', '', name)
    return name.replace('_', ' ').strip()

def generate_book(author_slug, book_folder, author_name):
    book_path = os.path.join(ARQUIVOS_DIR, author_slug, book_folder)
    chapters = sorted([
        d for d in os.listdir(book_path)
        if os.path.isdir(os.path.join(book_path, d))
    ])

    if not chapters:
        return

    # Load book metadata
    book_json = os.path.join(book_path, "book.json")
    if os.path.exists(book_json):
        with open(book_json) as f:
            meta = json.load(f)
    else:
        meta = {}

    book_title = meta.get("title", book_folder.replace('_', ' '))
    year = meta.get("year", "")
    description = meta.get("description", "")
    image = meta.get("image", "")
    mia_url = get_book_mia_url(author_slug, book_folder)
    book_slug = book_folder.replace('/', '_')

    # Build chapter table
    rows = []
    for ch in chapters:
        ch_title = get_chapter_title(ch)
        # The wav filename is the part after the numeric prefix
        wav_name = re.sub(r'^\d+_', '', ch)
        s3_url = f"{S3_BASE}/{author_slug}/{book_folder}/{wav_name}.mp3"
        rows.append(
            f"| {ch_title} | "
            f'[⬇️]({s3_url}) <audio controls preload="none" src="{s3_url}"></audio> |'
        )

    body = f"""| Capítulo | Áudio |
|----------|-------|
""" + "\n".join(rows)

    frontmatter = f"""---
title: "{book_title}"
author_name: "{author_name}"
author_slug: "{author_slug}"
book_slug: "{book_slug}"
year: "{year}"
description: "{description}"
image: "{image}"
mia_url: "{mia_url}"
---

"""
    os.makedirs(BOOKS_DIR, exist_ok=True)
    out_path = os.path.join(BOOKS_DIR, f"{author_slug}_{book_slug}.md")
    with open(out_path, 'w') as f:
        f.write(frontmatter + body)

    print(f"  📖 {book_title} ({len(chapters)} capítulos)")

# --- Author generation ---

def process_author(slug):
    readme = os.path.join(ARQUIVOS_DIR, slug, "README.md")
    if not os.path.exists(readme):
        return

    with open(readme, 'r') as f:
        content = f.read()

    meta = load_author_meta(slug)
    name = meta.get("name", "")
    image = meta.get("image", "")

    if not name:
        m = re.search(r'^# (.+)$', content, re.MULTILINE)
        name = m.group(1).strip() if m else slug
    if not image:
        m = re.search(r'<img src="([^"]+)"', content)
        image = m.group(1) if m else ""

    body = re.sub(r'^# .*\n+', '', content)
    body = re.sub(r'<p align="center">.*?</p>\n*', '', body, flags=re.DOTALL)
    body = transform_repo_links(body, slug)
    body = fix_broken_table_rows(body)

    frontmatter = f"""---
name: "{name}"
slug: "{slug}"
image: "{image}"
order: {ORDER.get(slug, 99)}
---

"""
    os.makedirs(AUTHORS_DIR, exist_ok=True)
    out_path = os.path.join(AUTHORS_DIR, f"{slug}.md")
    with open(out_path, 'w') as f:
        f.write(frontmatter + body)

    print(f"✅ {name}")

    # Generate book pages for this author
    for d in sorted(os.listdir(os.path.join(ARQUIVOS_DIR, slug))):
        full = os.path.join(ARQUIVOS_DIR, slug, d)
        if os.path.isdir(full) and is_book(slug, d):
            generate_book(slug, d, name)

if __name__ == '__main__':
    authors = [d for d in os.listdir(ARQUIVOS_DIR)
               if os.path.isdir(os.path.join(ARQUIVOS_DIR, d)) and d != '__pycache__']

    for slug in sorted(authors):
        process_author(slug)

    print(f"\n🎉 Concluído")
