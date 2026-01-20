#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Uso: $0 <URL_index> [pasta_arquivos]"
    echo "Exemplo: $0 https://www.marxists.org/portugues/mao/index.htm arquivos/mao_zedong"
    exit 1
fi

URL="$1"
BASE_URL="${URL%/*}"
ARQUIVOS_DIR="${2:-.}"

html=$(curl -s "$URL")

# Extract author name from h1
author=$(echo "$html" | sed -n 's/.*<h1>\([^<]*\)<\/h1>.*/\1/p' | head -1)

# Extract image
img=$(echo "$html" | sed -n 's/.*<img src="\([^"]*\)".*class="bordafoto".*/\1/p' | head -1)

# Extract biography paragraphs
bio=$(echo "$html" | sed -n 's/.*<p class="texto-sem-espaco">\(.*\)<\/p>.*/\1/p' | sed 's/<[^>]*>//g')

echo "# $author"
echo ""
[ -n "$img" ] && echo "<p align=\"center\"><img src=\"$BASE_URL/$img\" alt=\"$author\"></p>"
echo ""
echo "$bio"
echo ""
echo "## Obras"
echo ""
echo "| Obra | Ano | Repo | MIA |"
echo "|------|-----|:----:|:---:|"

# Extract works and check if folder exists in repo
echo "$html" | tr '\n' ' ' | sed 's/<tr/\n<tr/g' | \
grep '<td>.*<a href=' | \
while read -r line; do
    date=$(echo "$line" | sed 's/.*<td>\([^<]*\)<\/td>.*/\1/')
    href=$(echo "$line" | sed 's/.*<a href="\([^"]*\)".*/\1/')
    title=$(echo "$line" | sed 's/.*<a href="[^"]*">\([^<]*\)<\/a>.*/\1/')
    
    # Clean title for folder name (same logic as podcast.sh)
    clean_title=$(echo "$title" | tr -cd '[:alnum:][:space:]' | tr ' ' '_' | tr -s '_')
    
    # Check if folder exists
    if [ -d "$ARQUIVOS_DIR/$clean_title" ]; then
        repo_link="[📁]($clean_title/)"
    else
        repo_link=""
    fi
    
    echo "| $title | $date | $repo_link | [🔗]($BASE_URL/$href) |"
done
