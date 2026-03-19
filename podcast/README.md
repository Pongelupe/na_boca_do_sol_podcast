# Na Boca do Sol Podcast 🎙️

Gerador automático de podcasts com síntese de voz por IA para leitura de textos marxistas.

## Sobre

O **Na Boca do Sol** é um podcast que divulga textos marxistas de domínio público disponibilizados pelo [Marxists Internet Archive (MIA)](https://www.marxists.org/). O projeto utiliza a voz sintetizada "Alex" através do [Kokoro TTS](https://github.com/hexgrad/kokoro) para gerar os episódios automaticamente.

## Funcionalidades

- Extração automática de artigos de URLs do Marxists.org
- Limpeza e formatação de HTML para texto
- Extração de biografia do autor
- Síntese de voz em português com Kokoro TTS
- Inserção de vinhetas de áudio (intro, pausas)
- Template personalizável para episódios

## Requisitos

- Python 3
- lynx
- curl
- GPU NVIDIA (recomendado para Kokoro TTS)

## Instalação

```bash
pip install -r requirements.txt
```

### Com Docker [PREFERIDO]

```bash
docker build -t nabocadosol .
docker run --gpus all nabocadosol <URL>
```

## Uso

### Com Docker [PREFERIDO]

```bash
docker build -t nabocadosol .
docker run --gpus all nabocadosol <URL>
```

### Gerar podcast a partir de URL

```bash
./podcast.sh https://www.marxists.org/portugues/autor/ano/texto.htm
```

Os arquivos gerados serão salvos em uma pasta com o título do artigo:
- `Titulo.html` - HTML limpo
- `Titulo.txt` - Texto extraído
- `Titulo_podcast.txt` - Script completo do episódio
- `Titulo.wav` - Áudio final

### Gerar áudio de script existente

```bash
./podcast.sh -p arquivo_podcast.txt
```

### Gerar livro (múltiplos capítulos)

```bash
./batch_podcast.sh urls.txt
```

O arquivo `urls.txt` deve conter uma URL por linha. A primeira linha comentada (`# URL`) é usada como índice do livro para gerar o `book.json`.

### Gerar índice de obras em Markdown

Movido para `tools/index_to_md.py`. Ver [tools/README.md](../tools/README.md).

## Estrutura

```
├── podcast.sh            # Script principal
├── batch_podcast.sh      # Geração em lote (livros)
├── kokoro_tts.py         # Síntese de voz com Kokoro
├── clean_html_article.py # Limpeza de HTML do artigo
├── clean_html_author.py  # Limpeza de HTML do autor
├── process_author_info.py # Extração de biografia
├── process_template.py   # Processamento do template
├── script.txt            # Template do episódio
├── Dockerfile            # Imagem Docker com GPU
├── requirements.txt      # Dependências Python
└── sounds/               # Vinhetas de áudio
    ├── intro.wav
    └── virgula.wav
```

## Template

O arquivo `script.txt` define a estrutura do episódio com variáveis:

- `{{TITLE}}` - Título do texto
- `{{AUTHOR}}` - Nome do autor
- `{{YEAR}}` - Ano de publicação
- `{{LINE_COUNT}}` - Número de linhas
- `{{CONTENT}}` - Conteúdo do texto
- `{{BIOGRAFY}}` - Biografia do autor

Marcadores especiais:
- `|SOUND:arquivo.wav|` - Insere áudio
- `|PAUSE:segundos|` - Insere pausa

## Redes Sociais

- Instagram: [@nabocadosolpodcast](https://instagram.com/nabocadosolpodcast)

## Licença

Código aberto. Textos são de domínio público via Marxists Internet Archive.
