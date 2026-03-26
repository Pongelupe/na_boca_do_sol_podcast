#!/bin/bash
# Moves a generated episode/book folder to the right author, updates README.
# Usage: ./add_episode.sh <folder>

set -e

if [ $# -eq 0 ]; then
    echo "Uso: $0 <pasta_episódio>"
    exit 1
fi

EPISODE="$1"
ARQUIVOS_DIR="arquivos"

if [ ! -d "$EPISODE" ]; then
    echo "❌ Pasta não encontrada: $EPISODE"
    exit 1
fi

# Pick author with fzf
AUTHOR=$(ls -d "$ARQUIVOS_DIR"/*/ | xargs -I{} basename {} | fzf --prompt="Autor: ")

if [ -z "$AUTHOR" ]; then
    echo "❌ Nenhum autor selecionado"
    exit 1
fi

# Pick title from README with fzf (rows without 📁)
DEST_DIR="$ARQUIVOS_DIR/$AUTHOR"
LINE=$(grep '^|' "$DEST_DIR/README.md" | grep -v '📁' | grep -v '^| Obra ' | grep -v '^|---' | fzf --prompt="Obra: ")

if [ -z "$LINE" ]; then
    echo "❌ Nenhuma obra selecionada"
    exit 1
fi

# Extract title from selected line
TITLE=$(echo "$LINE" | awk -F'|' '{print $2}' | sed 's/^ *//;s/ *$//')
FOLDER_NAME=$(echo "$TITLE" | tr ' ' '_')

# Move
sudo mv "$EPISODE" "$DEST_DIR/$FOLDER_NAME"
echo "📁 Movido para: $DEST_DIR/$FOLDER_NAME"

# Rename files inside to match folder name
EPISODE_BASENAME=$(basename "$EPISODE")
if [ "$EPISODE_BASENAME" != "$FOLDER_NAME" ]; then
    echo "🔄 Renomeando arquivos de '$EPISODE_BASENAME' para '$FOLDER_NAME'..."
    cd "$DEST_DIR/$FOLDER_NAME"
    for file in *"$EPISODE_BASENAME"*; do
        [ -e "$file" ] || continue
        newname="${file//$EPISODE_BASENAME/$FOLDER_NAME}"
        sudo mv "$file" "$newname"
    done
    cd - > /dev/null
fi

# Update README — add 📁 link
python3 -c "
lines = open('$DEST_DIR/README.md').readlines()
for i, line in enumerate(lines):
    if '| $TITLE |' in line and '|  |' in line:
        lines[i] = line.replace('|  |', '| [📁]($FOLDER_NAME/) |', 1)
        break
open('$DEST_DIR/README.md', 'w').writelines(lines)
"
echo "✅ README atualizado"
