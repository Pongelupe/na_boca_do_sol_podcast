#!/bin/bash
# Updates README.md repo links (📁) based on existing episode folders.
# Usage: ./update_readme.sh [arquivos_dir]

ARQUIVOS_DIR="${1:-arquivos}"

for author_dir in "$ARQUIVOS_DIR"/*/; do
    readme="$author_dir/README.md"
    [ -f "$readme" ] || continue
    author=$(basename "$author_dir")

    python3 -c "
import os

readme = '$readme'
author_dir = '$author_dir'
lines = open(readme).readlines()
folders = {f for f in os.listdir(author_dir) if os.path.isdir(os.path.join(author_dir, f))}
changed = False

for folder in folders:
    if any('[📁](' + folder + '/)' in l for l in lines):
        continue
    title = folder.replace('_', ' ')
    for i, line in enumerate(lines):
        if '| ' + title + ' |' in line and '|  |' in line:
            lines[i] = line.replace('|  |', '| [📁](' + folder + '/) |', 1)
            changed = True
            break

if changed:
    open(readme, 'w').writelines(lines)
    print('✅ $author')
else:
    print('— $author (sem alterações)')
"
done
