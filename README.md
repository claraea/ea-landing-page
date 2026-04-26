# Clara/EA — Landing Page

Site institucional do **Clara/EA**, framework de Arquitetura Corporativa criado por Marcelo Andrade Clara.

## Stack

Site **estático puro** — HTML + CSS + JS vanilla, sem etapa de build.

- **Tipografia:** Inter (sans) + Source Serif 4 (serif), via Google Fonts.
- **Animação 3D:** Three.js r128 via CDN para o tesseract da home.
- **i18n:** trilíngue PT/EN/ES com switch client-side (dicionário embutido).
- **Hospedagem:** GitHub Pages — basta servir os arquivos.

## Estrutura

```
index.html              # home (era ClaraEA-Mockup.html)
ClaraEA-CMDB.html       # página da ferramenta EA/CMDB
ClaraEA-Autor.html      # página do autor
assets/
  styles.css            # CSS compartilhado entre as três páginas
  cubes.svg             # ilustração modular auxiliar
.nojekyll               # GitHub Pages: desliga o pipeline Jekyll
.planning/              # documentos fundacionais e fontes (não publicados)
.claude/                # skill + agente Clara/EA usados por Claude Code
```

## Rodar localmente

Como é estático puro, qualquer servidor estático serve:

```bash
python3 -m http.server 8000
# abrir http://localhost:8000/
```

ou

```bash
npx serve .
```

## Publicar no GitHub Pages

1. Commitar os arquivos da raiz na branch `main` (ou `gh-pages`).
2. Em **Settings → Pages**, apontar para a branch e o diretório raiz `/`.
3. O `.nojekyll` impede que o Pages tente processar o conteúdo via Jekyll.

Sem `basePath` ou prefixo: os links internos (`href="ClaraEA-CMDB.html"`, `href="assets/styles.css"`) são relativos e funcionam tanto em `username.github.io/<repo>/` quanto em domínio próprio.

## Idiomas

A troca de idioma é client-side, via os botões `PT / EN / ES` no header. O DOM é atualizado em tempo real lendo `data-i18n="..."` em cada elemento e buscando a chave no dicionário JS embutido em cada página.

> Toda nova string visível precisa de uma chave `data-i18n` e entradas equivalentes nos três blocos `pt`, `en`, `es` do `<script>`.

## Documentação interna

Decisões editoriais, fontes e mood board ficam em `.planning/claraea/`:

- `00-foundation.md` — documento fundacional consolidado.
- `sources/01-framework-overview.md` — texto inicial.
- `sources/02-livro-pdf-edicao-completa.md` — transcrição do PDF.
- `sources/03-livro-obsidian-em-progresso.md` — capítulos do livro.
- `sources/04-moodboard.md` — mood board do mockup atual.
