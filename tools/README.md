# Ferramentas

Scripts para gerenciamento de conteúdo do site.

## Scripts

### `index_to_md.py`
Gera o `README.md` de um autor a partir da página de índice do Marxists Internet Archive. Também cria o `author.json` com nome e imagem.

```bash
python3 tools/index_to_md.py <URL_INDEX> <PASTA_AUTOR> > <PASTA_AUTOR>/README.md
# ou
make index URL=https://www.marxists.org/portugues/mao/index.htm DIR=arquivos/mao_zedong
```

### `add_episode.sh`
Move uma pasta de episódio gerado para o autor correto usando `fzf` para seleção interativa, e atualiza o README com o link `📁`.

```bash
./tools/add_episode.sh <PASTA_EPISODIO>
# ou
make add FOLDER=./Titulo_do_Episodio
```

### `update_readme.sh`
Varre as pastas de episódios existentes e adiciona links `📁` faltantes nos READMEs dos autores.

```bash
./tools/update_readme.sh arquivos
# ou
make update
```

### `index_to_md.sh`
Versão antiga em bash do `index_to_md.py`. Mantido por referência.
