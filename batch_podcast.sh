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

cp $URL_FILE $BASE_NAME/

echo "🎉 Todos os podcasts foram gerados em: $BASE_NAME/"
