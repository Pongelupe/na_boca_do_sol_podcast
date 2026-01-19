#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Uso: $0 <URL_index>"
    echo "Exemplo: $0 https://www.marxists.org/portugues/mao/index.htm"
    exit 1
fi

URL="$1"
BASE_URL="${URL%/*}"

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

# Extract works: date and links
echo "$html" | tr '\n' ' ' | sed 's/<tr/\n<tr/g' | \
grep '<td>.*<a href=' | \
sed 's/.*<td>\([^<]*\)<\/td>.*<a href="\([^"]*\)">\([^<]*\)<\/a>.*/- [\3](\2) (\1)/' | \
sed "s|](\([^)]*\))|]($BASE_URL/\1)|g"
