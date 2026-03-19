#!/usr/bin/env python3
"""Gera README.md com índice de obras a partir de uma página do MIA."""

import sys, os, re, json, html
from urllib.request import urlopen

if len(sys.argv) < 2:
    print("Uso: ./index_to_md.py <URL_index> [pasta_arquivos]")
    print("Exemplo: ./index_to_md.py https://www.marxists.org/portugues/mao/index.htm arquivos/mao_zedong")
    sys.exit(1)

url = sys.argv[1]
arquivos = sys.argv[2] if len(sys.argv) > 2 else "."
base_url = url.rsplit("/", 1)[0]

page = urlopen(url).read().decode("utf-8", errors="replace")

# Author name from <h1>
m = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.DOTALL)
author = re.sub(r"<[^>]+>", "", m.group(1)).split("\n")[0].strip() if m else "Autor"

# Image
m = re.search(r'<img src="([^"]+)"[^>]*class="bordafoto"', page)
img = f"{base_url}/{m.group(1)}" if m else ""

# Bio
bios = re.findall(r'<p class="texto-sem-espaco">(.*?)</p>', page, re.DOTALL)
bio = "\n".join(re.sub(r"<[^>]+>", "", b).strip() for b in bios)

# Generate author.json
if os.path.isdir(arquivos):
    with open(os.path.join(arquivos, "author.json"), "w") as f:
        json.dump({"name": author, "image": img}, f, ensure_ascii=False)
    print(f"✅ author.json gerado em {arquivos}/", file=sys.stderr)

# Build markdown
lines = [f"# {author}", ""]
if img:
    lines.append(f'<p align="center"><img src="{img}" alt="{author}"></p>')
    lines.append("")
if bio:
    lines.append(bio)
    lines.append("")
lines += ["## Obras", "", "| Obra | Ano | Repo | MIA |", "|------|-----|:----:|:---:|"]

# Extract works from <tr> rows
for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", page, re.DOTALL):
    link = re.search(r'<a href="([^"]+)">([^<]+)</a>', tr)
    if not link:
        continue
    href, title = link.group(1), html.unescape(link.group(2).strip())
    tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.DOTALL)
    date = re.sub(r"<[^>]+>", "", tds[0]).strip() if tds else ""

    folder = title.replace(" ", "_")
    repo = f"[📁]({folder}/)" if os.path.isdir(os.path.join(arquivos, folder)) else ""

    if not href.startswith("http"):
        href = f"{base_url}/{href}"

    lines.append(f"| {title} | {date} | {repo} | [🔗]({href}) |")

print("\n".join(lines))
