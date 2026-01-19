#!/bin/bash

run_tts() {
    local input_file="$1"
    local output_file="$2"
    echo "🔊 Convertendo com Kokoro:"
    python3 kokoro_tts.py "$input_file" "$output_file" &
    while jobs %% > /dev/null 2>&1; do
        echo -n "█"
        sleep 1
    done
    if [ -f "$output_file" ] && [ -s "$output_file" ]; then
        tamanho=$(wc -c < "$output_file")
        echo "✅ Áudio criado: $output_file ($tamanho bytes)"
    else
        echo "❌ Kokoro falhou"
        exit 1
    fi
}

if [ "$1" = "-p" ] || [ "$1" = "--podcast" ]; then
    INPUT_FILE="$2"
    clean_title="${INPUT_FILE%_podcast.txt}"
    run_tts "$INPUT_FILE" "$clean_title.wav"
    exit 0
fi

if [ $# -eq 0 ]; then
    echo "Uso: $0 <URL>"
    echo "       $0 -p <arquivo_podcast.txt>"
    echo "Exemplo: $0 https://exemplo.com"
    echo "Exemplo: $0 -p Titulo_podcast.txt"
    echo "Artefatos gerados serão salvos em uma pasta com o título do artigo."
    exit 1
fi

URL=$1

raw_html=$(curl -s "$URL")
echo "$raw_html" | python3 clean_html_article.py > artigo.tmp.html

# Process author info
echo "$raw_html" | python3 process_author_info.py "$URL" > autor.tmp.html 2>/dev/null

title=$(awk -F'<title>|</title>' '/<title>/ {print $2}' artigo.tmp.html)
echo -e "\n📖 Título: $title"

# Limpar o título para nome de arquivo
clean_title=$(echo "$title" | tr -cd '[:alnum:][:space:]' | tr ' ' '_' | tr -s '_')

lynx -dump -nolist -width=1000 -display_charset=utf-8 artigo.tmp.html |
sed 's/^[[:space:]]*//' |
# Juntar linhas que não começam com espaço (continuam o parágrafo)
awk '!/^[[:space:]]/ && NR>1 {print ""} {printf "%s", $0} END {print ""}' |
sed 's/  */ /g' > artigo_limpo.txt
#lynx -dump -nolist -width=1000 -display_charset=utf-8 artigo.tmp.html | sed 's/^[[:space:]]*//' | tr '\n' ' ' | sed 's/  */\n\n/g' > artigo_limpo.txt
lynx -dump -nolist -width=1000 -display_charset=utf-8 autor.tmp.html > autor.tmp.txt
mv artigo.tmp.html "$clean_title.html"

# Clean encoding issues
iconv -f UTF-8 -t UTF-8 -c artigo_limpo.txt > artigo_limpo_fixed.txt 2>/dev/null || cp artigo_limpo.txt artigo_limpo_fixed.txt
mv artigo_limpo_fixed.txt "$clean_title.txt"

echo "📄 Texto extraído: $(wc -l < "$clean_title.txt") linhas"

# Process template if script.txt exists
if [ -f "script.txt" ]; then
    echo "📝 Processando template..."
    python3 process_template.py script.txt autor.tmp.txt "$clean_title.txt" "$clean_title.html" > "${clean_title}_podcast.txt"
    INPUT_FILE="${clean_title}_podcast.txt"
else
    INPUT_FILE="$clean_title.txt"
fi

run_tts "$INPUT_FILE" "$clean_title.wav"

# Limpar arquivos temporários
rm -f artigo_limpo.txt autor.tmp* 

# Move artifacts to folder
mkdir -p "$clean_title"
mv "$clean_title.html" "$clean_title.txt" "$clean_title.wav" "${clean_title}_podcast.txt" "$clean_title/" 2>/dev/null
