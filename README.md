# Na Boca do Sol Podcast 🎙️

Gerador automático de podcasts com síntese de voz por IA para leitura de textos marxistas, com site estático para publicação.

## Sobre

O **Na Boca do Sol** é um podcast que divulga textos marxistas de domínio público disponibilizados pelo [Marxists Internet Archive (MIA)](https://www.marxists.org/). O projeto utiliza a voz sintetizada "Alex" através do [Kokoro TTS](https://github.com/hexgrad/kokoro) para gerar os episódios automaticamente.

## Estrutura

```
├── podcast/       # Geração de episódios (TTS, Docker, scripts)
├── frontend/      # Site estático (Astro + GitHub Pages)
├── tools/         # Gerenciamento de conteúdo (índice, episódios, README)
├── arquivos/      # Dados dos autores e episódios
├── Makefile       # Orquestração de tarefas
└── DEPLOY.md      # Instruções de deploy (S3, GitHub Pages)
```

## Início Rápido

```bash
# Gerar episódio
make podcast URL=https://www.marxists.org/portugues/autor/ano/texto.htm

# Mover episódio para autor (interativo com fzf)
make add FOLDER=./Titulo_do_Episodio

# Converter wav→mp3 e enviar para S3
make deploy

# Gerar/atualizar índice de autor
make index URL=https://www.marxists.org/portugues/autor/index.htm DIR=arquivos/autor

# Atualizar links nos READMEs
make update

# Build local do site
make build

# Dev server
make dev
```

## Requisitos

- Python 3
- Node.js 20+
- ffmpeg (conversão wav→mp3)
- fzf (seleção interativa)
- GPU NVIDIA (recomendado para Kokoro TTS)
- AWS CLI (upload para S3)

## Redes Sociais

- Instagram: [@nabocadosolpodcast](https://instagram.com/nabocadosolpodcast)

## Licença

Código aberto. Textos são de domínio público via Marxists Internet Archive.
