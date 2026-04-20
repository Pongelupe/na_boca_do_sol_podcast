import argparse
import json
import re
import tempfile
import urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).parent

parser = argparse.ArgumentParser(description="Generate Instagram post image")
parser.add_argument("--episode", required=True, help="Path to episode folder")
parser.add_argument("--output", default=None)
parser.add_argument("--theme", choices=["dark", "light"], default="dark", help="Template theme")
parser.add_argument("--template", default=None)
args = parser.parse_args()

episode_path = Path(args.episode).resolve()
parent_path = episode_path.parent

# Resolve output filename
if args.output:
    output = args.output
else:
    output = f"instagram_{episode_path.name}.jpg"

# Resolve template
if args.template:
    template_path = args.template
else:
    suffix = "_light" if args.theme == "light" else ""
    template_path = str(SCRIPT_DIR / "templates" / f"post_instagram_back{suffix}.jpeg")

# Determine author dir: if parent has book.json, it's a book chapter
is_book = (parent_path / "book.json").exists()
author_dir = parent_path.parent if is_book else parent_path

# Read author.json
with open(author_dir / "author.json") as f:
    author_data = json.load(f)
author_name = author_data["name"]
photo_url = author_data["image"]

# Read README.md table to get year/month
readme = (author_dir / "README.md").read_text()
folder_to_match = parent_path.name if is_book else episode_path.name
year, month = "", ""
title_from_readme = ""
for line in readme.splitlines():
    if not line.strip().startswith("|") or "---" in line:
        continue
    if f"]({folder_to_match}/)" not in line:
        continue
    cols = [c.strip() for c in line.split("|")]
    # cols[0] is empty (before first |), cols[1]=Obra, cols[2]=Ano, cols[3]=Repo, cols[4]=MIA
    title_from_readme = cols[1]
    year_raw = cols[2]
    if " - " in year_raw:
        parts = year_raw.split(" - ", 1)
        year, month = parts[0].strip(), parts[1].strip()
    else:
        year, month = year_raw.strip(), ""
    break

# For book chapters, use book title + chapter subtitle
subtitle = ""
if is_book:
    with open(parent_path / "book.json") as f:
        book_data = json.load(f)
    title = book_data["title"]
    # Extract chapter number and name from folder prefix (e.g. 001_Chapter_Name)
    m = re.match(r"^(\d+)_(.*)", episode_path.name)
    if m:
        chapter_name = book_data["chapters"].get(m.group(2), m.group(2).replace("_", " "))
        subtitle = f"Cap. {int(m.group(1))} - {chapter_name}"
else:
    title = title_from_readme

# Download author photo to temp file
tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
req = urllib.request.Request(photo_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    tmp.write(resp.read())
tmp.close()

# --- Image generation (unchanged rendering logic) ---

FONT_PATH = str(SCRIPT_DIR / "fonts" / "BebasNeue-Regular.ttf")
YELLOW = (244, 191, 0)
RED = (200, 30, 15)
DARK = (40, 20, 5)
GOLD = (245, 192, 0)

# Open template and paint yellow bar
img = Image.open(template_path).convert("RGBA")
draw = ImageDraw.Draw(img)
draw.rectangle([0, 1253, 1600, 1600], fill=YELLOW)

# Composite author photo as circle with gold border
cx, cy = 806, 672
inner_r, outer_r = 443, 458
photo = Image.open(tmp.name).convert("RGBA").resize((inner_r * 2, inner_r * 2), Image.LANCZOS)
mask = Image.new("L", (inner_r * 2, inner_r * 2), 0)
ImageDraw.Draw(mask).ellipse([0, 0, inner_r * 2 - 1, inner_r * 2 - 1], fill=255)
img.paste(photo, (cx - inner_r, cy - inner_r), mask)
draw = ImageDraw.Draw(img)
draw.ellipse(
    [cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r],
    outline=GOLD, width=15,
)

# Auto-fit title in yellow bar
title_upper = title.upper()
font_size = 130
while font_size > 10:
    font = ImageFont.truetype(FONT_PATH, font_size)
    bbox = draw.textbbox((0, 0), title_upper, font=font)
    if bbox[2] - bbox[0] <= 1440:
        break
    font_size -= 5
tx = (1600 - (bbox[2] - bbox[0])) // 2
title_y = 1280
draw.text((tx, title_y), title_upper, fill=RED, font=font)

# Subtitle line for book chapters
info_y = 1460
if subtitle:
    title_bottom = title_y + (bbox[3] - bbox[1])
    sub_size = 55
    while sub_size > 10:
        sub_font = ImageFont.truetype(FONT_PATH, sub_size)
        sub_bbox = draw.textbbox((0, 0), subtitle.upper(), font=sub_font)
        if sub_bbox[2] - sub_bbox[0] <= 1440:
            break
        sub_size -= 5
    sx = (1600 - (sub_bbox[2] - sub_bbox[0])) // 2
    draw.text((sx, title_bottom + 5), subtitle.upper(), fill=RED, font=sub_font)
    info_y = title_bottom + 5 + (sub_bbox[3] - sub_bbox[1]) + 15

# Author name (left) and year-month (right)
info_font = ImageFont.truetype(FONT_PATH, 50)
draw.text((80, info_y), author_name, fill=DARK, font=info_font)
year_month = f"{year} - {month}" if month else year
ym_bbox = draw.textbbox((0, 0), year_month, font=info_font)
draw.text((1520 - (ym_bbox[2] - ym_bbox[0]), info_y), year_month, fill=DARK, font=info_font)

# Save
img.convert("RGB").save(output, "JPEG", quality=95)
print(f"✅ {output}")

# Cleanup temp file
Path(tmp.name).unlink(missing_ok=True)
