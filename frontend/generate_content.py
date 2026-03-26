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
BASE_PATH = os.environ.get("BASE_PATH", "")  # Set BASE_PATH=/na_boca_do_sol_podcast for production
ARQUIVOS_DIR = os.path.join(os.path.dirname(__file__), "..", "arquivos")
AUTHORS_DIR = os.path.join(os.path.dirname(__file__), "src", "content", "authors")
BOOKS_DIR = os.path.join(os.path.dirname(__file__), "src", "content", "books")
EPISODES_DIR = os.path.join(os.path.dirname(__file__), "src", "content", "episodes")

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
            zip_url = f"{S3_BASE}/{author_slug}/{book_slug}.zip"
            return f'[📖 ver capítulos](/{author_slug}/{book_slug}/) [⬇️]({zip_url})'
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
    chapter_names = meta.get("chapters", {})
    mia_url = get_book_mia_url(author_slug, book_folder)
    book_slug = book_folder.replace('/', '_')

    # Build chapter table
    rows = []
    for ch in chapters:
        wav_name = re.sub(r'^\d+_', '', ch)
        ch_title = chapter_names.get(wav_name, get_chapter_title(ch))
        episode_url = f"{BASE_PATH}/{author_slug}/{book_slug}/{wav_name}/"
        rows.append(f"| [{ch_title}]({episode_url}) |")

    body = f"""| Capítulo |
|----------|
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

    # Generate episode pages for each chapter
    for i, ch in enumerate(chapters):
        ch_path = os.path.join(book_path, ch)
        wav_name = re.sub(r'^\d+_', '', ch)
        ch_title = chapter_names.get(wav_name)
        generate_episode(author_slug, author_name, wav_name, ch_path,
                         book_slug=book_slug, readme_content=None,
                         chapter_title=ch_title, order=i)

# --- Episode generation ---

def find_mia_url(readme_content, title):
    """Search author README for MIA link matching a title."""
    if not readme_content:
        return ""
    for line in readme_content.split('\n'):
        if title[:30] in line:
            m = re.search(r'\[🔗\]\(([^)]+)\)', line)
            if m:
                return m.group(1)
    return ""

def generate_episode(author_slug, author_name, episode_slug, episode_dir,
                     book_slug=None, readme_content=None,
                     chapter_title=None, order=None):
    txt_path = os.path.join(episode_dir, f"{episode_slug}.txt")
    if not os.path.exists(txt_path):
        return

    with open(txt_path, 'r') as f:
        text = f.read()

    lines = text.strip().split('\n')

    # For book chapters, prefer chapter_title from book.json, fallback to slug
    if book_slug:
        title = chapter_title or get_chapter_title(episode_slug)
    else:
        title = lines[0].strip() if lines else episode_slug.replace('_', ' ')

    # Extract year from early lines
    year = ""
    for line in lines[1:6]:
        m = re.match(r'^(\d{4})', line.strip())
        if m:
            year = m.group(1)
            break

    mia_url = find_mia_url(readme_content, title)

    if book_slug:
        audio_url = f"{S3_BASE}/{author_slug}/{book_slug}/{episode_slug}.mp3"
    else:
        audio_url = f"{S3_BASE}/{author_slug}/{episode_slug}.mp3"

    # Body: skip header metadata, start from actual content
    # Heuristic: find first numbered section or long paragraph
    body_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Numbered section like "1" or "I - Title"
        if re.match(r'^(\d+|[IVXLC]+ ?[-–—])$', stripped) and i > 3:
            body_start = i
            break
        # Long paragraph (actual content)
        if len(stripped) > 200 and i > 3:
            body_start = i
            break
    if body_start == 0:
        body_start = min(6, len(lines))

    body = '\n'.join(lines[body_start:]).strip()

    # Load timestamps
    ts_path = os.path.join(episode_dir, f"{episode_slug}_timestamps.json")
    if os.path.exists(ts_path):
        with open(ts_path, 'r') as f:
            ts_data = json.load(f)
        timestamps = ts_data.get("segments", [])
    else:
        timestamps = []

    # Escape quotes in frontmatter values
    safe_title = title.replace('"', '\\"')

    frontmatter = f'---\ntitle: "{safe_title}"\nauthor_name: "{author_name}"\nauthor_slug: "{author_slug}"\nepisode_slug: "{episode_slug}"\n'
    if book_slug:
        frontmatter += f'book_slug: "{book_slug}"\n'
    if order is not None:
        frontmatter += f'order: {order}\n'
    frontmatter += f'year: "{year}"\naudio_url: "{audio_url}"\nmia_url: "{mia_url}"\n'
    frontmatter += f'timestamps: {json.dumps(timestamps, ensure_ascii=False)}\n'
    frontmatter += '---\n\n'

    os.makedirs(EPISODES_DIR, exist_ok=True)
    prefix = f"{author_slug}_{book_slug}_" if book_slug else f"{author_slug}_"
    out_path = os.path.join(EPISODES_DIR, f"{prefix}{episode_slug}.md")
    with open(out_path, 'w') as f:
        f.write(frontmatter + body)

    print(f"  🎧 {title}")

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

    # Generate book + episode pages for this author
    for d in sorted(os.listdir(os.path.join(ARQUIVOS_DIR, slug))):
        full = os.path.join(ARQUIVOS_DIR, slug, d)
        if os.path.isdir(full):
            if is_book(slug, d):
                generate_book(slug, d, name)
            else:
                # Simple episode
                generate_episode(slug, name, d, full, readme_content=content)

if __name__ == '__main__':
    authors = [d for d in os.listdir(ARQUIVOS_DIR)
               if os.path.isdir(os.path.join(ARQUIVOS_DIR, d)) and d != '__pycache__']

    for slug in sorted(authors):
        process_author(slug)

    print(f"\n🎉 Concluído")
