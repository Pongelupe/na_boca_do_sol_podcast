#!/bin/bash

TYPE="article"

while getopts "t:" opt; do
    case $opt in
        t) TYPE="$OPTARG";;
    esac
done
shift $((OPTIND-1))

if [ $# -eq 0 ]; then
    echo "Uso: $0 [-t article|author] <URL>"
    echo "Exemplo: $0 https://exemplo.com"
    echo "Exemplo: $0 -t author https://exemplo.com"
    exit 1
fi

URL=$1

raw_html=$(curl -s "$URL")
echo "$raw_html" | python "clean_html_${TYPE}.py" > artigo.tmp.html

# Process author info
echo "$raw_html" | python process_author_info.py "$URL" > autor.tmp.html 2>/dev/null

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
    python process_template.py script.txt autor.tmp.txt "$clean_title.txt" "$clean_title.html" > "${clean_title}_podcast.txt"
    INPUT_FILE="${clean_title}_podcast.txt"
else
    INPUT_FILE="$clean_title.txt"
fi

echo "🔊 Convertendo com Kokoro:"

python kokoro_tts.py "$INPUT_FILE" "$clean_title.wav" &

# Barra de progresso simples
while jobs %% > /dev/null 2>&1; do
    echo -n "█"
    sleep 1
done


# Verificar se funcionou
if [ -f "$clean_title.wav" ] && [ -s "$clean_title.wav" ]; then
    tamanho=$(wc -c < "$clean_title.wav")
    echo -n "✅ Áudio criado: $clean_title.wav ($tamanho bytes)"
else
    echo "❌ Piper falhou, tentando método alternativo..."
    exit 1
fi

# Limpar arquivos temporários
rm -f artigo_limpo.txt autor.tmp* 
