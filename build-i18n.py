#!/usr/bin/env python3
"""
Pre-render PT/EN/ES versions of each HTML page in /en/ and /es/.

For each non-PT language:
  - Extract dictionary from JS at the bottom of the file.
  - Walk every element with data-i18n attribute and replace text/HTML with translation.
  - Walk every element with data-i18n-attr to translate attribute values (placeholders, etc.).
  - Update <html lang>, data-lang, page <title>, meta description, OG / Twitter meta,
    canonical, JSON-LD URLs, currentLang in JS, language switcher hrefs and active state.
  - Save to <lang>/<page>.

PT files (in place):
  - Replace <button data-lang="..."> with <a href="..."> in the language switcher.
  - Add hreflang alternates to <head>.
"""

from __future__ import annotations
import re
import json
from pathlib import Path

ROOT = Path(__file__).parent
PAGES = ['index.html', 'ClaraEA-CMDB.html', 'ClaraEA-Autor.html']
LANGS_OTHER = ['en', 'es']  # PT is the canonical default at root
ALL_LANGS = ['pt', 'en', 'es']

LANG_HTML_ATTR = {'pt': 'pt-BR', 'en': 'en', 'es': 'es'}
LANG_OG_LOCALE = {'pt': 'pt_BR', 'en': 'en_US', 'es': 'es_ES'}

DOMAIN = 'https://www.claraea.com.br'


def extract_dict(html: str, lang: str) -> dict:
    """Extract translation dictionary for `lang` from a JS object literal."""
    # Match `<lang>: { ... },` block in the translations object.
    pattern = re.compile(
        rf"\b{lang}:\s*\{{(.*?)\}}\s*(?:,|\}};?)",
        re.DOTALL,
    )
    m = pattern.search(html)
    if not m:
        return {}
    body = m.group(1)
    # Parse 'key': 'value' pairs (single-quoted strings, no nested objects expected here).
    # Handles escaped \' and \\.
    pair_re = re.compile(
        r"'([^']+?)'\s*:\s*'((?:\\.|[^'\\])*)'",
        re.DOTALL,
    )
    out = {}
    for k, v in pair_re.findall(body):
        # Unescape minimally: \' -> ', \\ -> \.
        v = v.replace(r"\'", "'").replace(r'\\', '\\')
        out[k] = v
    return out


def translate_data_i18n(html: str, dict_lang: dict) -> str:
    """Replace innerHTML/textContent of every element with `data-i18n="key"`."""
    # Match <tag ... data-i18n="key" ...>content</tag>
    # Allow self-closing not relevant — we only translate text content.
    # Use DOTALL so multi-line content (rare) works.
    def repl(m: re.Match) -> str:
        tag = m.group(1)
        attrs = m.group(2)
        old_inner = m.group(3)
        key_match = re.search(r'data-i18n="([^"]+)"', attrs)
        if not key_match:
            return m.group(0)
        key = key_match.group(1)
        if key not in dict_lang:
            return m.group(0)
        new_inner = dict_lang[key]
        return f"<{tag}{attrs}>{new_inner}</{tag}>"

    pattern = re.compile(
        r'<(\w+)((?:[^<>"]|"[^"]*")*?\bdata-i18n="[^"]+"(?:[^<>"]|"[^"]*")*?)>(.*?)</\1>',
        re.DOTALL,
    )
    return pattern.sub(repl, html)


def translate_data_i18n_attr(html: str, dict_lang: dict) -> str:
    """Translate attribute values for elements with both data-i18n and data-i18n-attr."""
    # The runtime JS does: if data-i18n-attr is set, set that attribute = dict[data-i18n].
    # We pre-render that statically.
    def repl_input(m: re.Match) -> str:
        full = m.group(0)
        i18n_match = re.search(r'data-i18n="([^"]+)"', full)
        attr_match = re.search(r'data-i18n-attr="([^"]+)"', full)
        if not i18n_match or not attr_match:
            return full
        key = i18n_match.group(1)
        attr_name = attr_match.group(1)
        if key not in dict_lang:
            return full
        value = dict_lang[key]
        # Replace existing attribute or add it.
        attr_pattern = re.compile(rf'\s+{re.escape(attr_name)}="[^"]*"')
        if attr_pattern.search(full):
            return attr_pattern.sub(f' {attr_name}="{value}"', full)
        # Otherwise insert before the closing > / />.
        return re.sub(r'(/?>)$', f' {attr_name}="{value}"\\1', full)

    # Match self-closing or open-tag elements that contain data-i18n-attr.
    pattern = re.compile(
        r'<\w+[^>]*\bdata-i18n-attr="[^"]+"[^>]*/?>',
        re.DOTALL,
    )
    return pattern.sub(repl_input, html)


def update_html_lang(html: str, lang: str) -> str:
    html = re.sub(
        r'<html lang="[^"]*"',
        f'<html lang="{LANG_HTML_ATTR[lang]}"',
        html,
        count=1,
    )
    html = re.sub(
        r'data-lang="[^"]*"',
        f'data-lang="{lang}"',
        html,
        count=1,
    )
    return html


def update_canonical_and_og(html: str, page: str, lang: str) -> str:
    """Point canonical, og:url and twitter URL to the correct localized URL."""
    page_path = '' if page == 'index.html' else page
    if lang == 'pt':
        url = f'{DOMAIN}/{page_path}'
    else:
        url = f'{DOMAIN}/{lang}/{page_path}'

    html = re.sub(
        r'(<link rel="canonical" href=")[^"]+(")',
        rf'\g<1>{url}\g<2>',
        html,
    )
    html = re.sub(
        r'(<meta property="og:url" content=")[^"]+(")',
        rf'\g<1>{url}\g<2>',
        html,
    )
    # og:locale
    html = re.sub(
        r'(<meta property="og:locale" content=")[^"]+(")',
        rf'\g<1>{LANG_OG_LOCALE[lang]}\g<2>',
        html,
    )
    return html


def insert_hreflang(html: str, page: str) -> str:
    """Insert <link rel="alternate" hreflang> tags after the canonical link."""
    page_path = '' if page == 'index.html' else page
    tags = []
    tags.append(f'<link rel="alternate" hreflang="pt-BR" href="{DOMAIN}/{page_path}">')
    tags.append(f'<link rel="alternate" hreflang="en" href="{DOMAIN}/en/{page_path}">')
    tags.append(f'<link rel="alternate" hreflang="es" href="{DOMAIN}/es/{page_path}">')
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}/{page_path}">')
    block = '\n'.join(tags)
    # Insert right after canonical line.
    pattern = re.compile(r'(<link rel="canonical" href="[^"]+">)')
    if not pattern.search(html):
        return html
    if 'rel="alternate" hreflang=' in html:
        # Already has hreflang — replace existing block by removing then re-adding.
        html = re.sub(
            r'(<link rel="alternate" hreflang="[^"]+" href="[^"]+">\s*)+',
            '',
            html,
        )
    html = pattern.sub(rf'\1\n{block}', html, count=1)
    return html


def update_lang_switcher(html: str, page: str, lang: str) -> str:
    """Replace <button data-lang="..."> with <a href="..."> pointing to localized URL."""
    page_path = '' if page == 'index.html' else page

    def url_for(target_lang: str) -> str:
        if target_lang == 'pt':
            return f'/{page_path}'
        return f'/{target_lang}/{page_path}'

    def repl(m: re.Match) -> str:
        block = m.group(0)
        # Iterate each button in the block.
        def repl_btn(bm: re.Match) -> str:
            target = bm.group(1)
            text = bm.group(2)
            href = url_for(target)
            cls = ' class="active"' if target == lang else ''
            return f'<a href="{href}" data-lang="{target}"{cls}>{text}</a>'
        block = re.sub(
            r'<button\s+data-lang="(\w+)"(?:\s+class="active")?>(.*?)</button>',
            repl_btn,
            block,
            flags=re.DOTALL,
        )
        return block

    return re.sub(
        r'<div class="lang-switch"[^>]*>.*?</div>',
        repl,
        html,
        count=1,
        flags=re.DOTALL,
    )


def update_currentlang_init(html: str, lang: str) -> str:
    """Set `let currentLang = '<lang>'` so on-page interactivity uses correct dict."""
    return re.sub(
        r"let currentLang = '\w+';",
        f"let currentLang = '{lang}';",
        html,
        count=1,
    )


def process_page(page: str) -> None:
    pt_path = ROOT / page
    html_pt_orig = pt_path.read_text(encoding='utf-8')

    # --- Update PT in place: lang switcher → anchors, hreflang in head ---
    html_pt = update_lang_switcher(html_pt_orig, page, 'pt')
    html_pt = insert_hreflang(html_pt, page)
    pt_path.write_text(html_pt, encoding='utf-8')

    # --- Generate /en/ and /es/ versions ---
    for lang in LANGS_OTHER:
        dict_lang = extract_dict(html_pt_orig, lang)
        if not dict_lang:
            print(f"WARN: no dict for lang={lang} in {page}")
            continue

        out = html_pt_orig
        out = translate_data_i18n_attr(out, dict_lang)
        out = translate_data_i18n(out, dict_lang)
        out = update_html_lang(out, lang)
        out = update_canonical_and_og(out, page, lang)
        out = insert_hreflang(out, page)
        out = update_lang_switcher(out, page, lang)
        out = update_currentlang_init(out, lang)

        out_dir = ROOT / lang
        out_dir.mkdir(exist_ok=True)
        (out_dir / page).write_text(out, encoding='utf-8')
        print(f"wrote {lang}/{page} ({len(out):,} bytes)")


if __name__ == '__main__':
    for p in PAGES:
        process_page(p)
    print("done.")
