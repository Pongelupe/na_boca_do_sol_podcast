#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Uso: $0 <arquivo_urls.txt>"
    echo "Exemplo: $0 urls.txt"
    exit 1
fi

URL_FILE="$1"

if [ ! -f "$URL_FILE" ]; then
    echo "❌ Arquivo não encontrado: $URL_FILE"
    exit 1
fi

# Get base name without extension
BASE_NAME="${URL_FILE%.txt}"
BASE_NAME=$(basename "$BASE_NAME")

# Create output directory
mkdir -p "$BASE_NAME"

# Extract index URL from first commented line
INDEX_URL=$(grep '^#' "$URL_FILE" | head -1 | sed 's/^#\s*//')

COUNTER=1

while IFS= read -r url || [ -n "$url" ]; do
    [ -z "$url" ] && continue
    [[ "$url" =~ ^#.* ]] && continue
    
    echo "🎙️ Processando [$COUNTER]: $url"
    docker run -v ./:/app --gpus all nbsp "$url"
    
    # Move the most recently created directory to BASE_NAME with counter prefix
    LAST_DIR=$(ls -td */ 2>/dev/null | grep -v "^$BASE_NAME/" | head -1)
    if [ -n "$LAST_DIR" ]; then
        sudo chown -R $(id -u):$(id -g) "$LAST_DIR"
        LAST_DIR_CLEAN="${LAST_DIR%/}"
        mv "$LAST_DIR" "$BASE_NAME/$(printf "%03d" $COUNTER)_$LAST_DIR_CLEAN"
        echo "📁 Movido para: $BASE_NAME/$(printf "%03d" $COUNTER)_$LAST_DIR_CLEAN"
    fi
    
    ((COUNTER++))
    
    echo "✅ Concluído: $url"
    echo "---"
done < "$URL_FILE"

cp "$URL_FILE" "$BASE_NAME/"

# Generate book.json from index URL
if [ -n "$INDEX_URL" ]; then
    echo "📚 Gerando book.json a partir de $INDEX_URL"
    html=$(curl -s "$INDEX_URL")

    title=$(echo "$html" | sed -n 's/.*<title>\([^<]*\)<\/title>.*/\1/p' | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    year=$(echo "$INDEX_URL" | grep -oE '/[0-9]{4}/' | tr -d '/' | head -1)
    # Extract first paragraph as description
    description=$(echo "$html" | lynx -stdin -dump -nolist -width=1000 -display_charset=utf-8 2>/dev/null | sed '/^$/d' | head -5 | tail -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    # Escape quotes for JSON
    title=$(echo "$title" | sed 's/"/\\"/g')
    description=$(echo "$description" | sed 's/"/\\"/g')

    cat > "$BASE_NAME/book.json" << EOF
{
  "title": "$title",
  "year": "$year",
  "image": "",
  "description": "$description"
}
EOF
    echo "✅ book.json gerado"
fi

echo "🎉 Todos os podcasts foram gerados em: $BASE_NAME/"
