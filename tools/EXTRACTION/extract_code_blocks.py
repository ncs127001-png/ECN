#!/usr/bin/env python3
import re
import sys
import os
import html
import quopri

# Heurística simple para detectar extensión a partir del contenido
def detect_extension(code):
    txt = code.lower()
    # common markers
    if '<?php' in txt or txt.strip().startswith('<?php'):
        return 'php'
    if re.search(r'\bdef\s+\w+\(|\bimport\s+\w+|if\s+__name__', code):
        return 'py'
    if re.search(r'\bpublic\s+class\b|\bpackage\b|\bSystem\.out\.println\b', code):
        return 'java'
    if '<!doctype html' in txt or '<html' in txt:
        return 'html'
    if 'console.log(' in txt or re.search(r'function\s+\w+\s*\(', code) or 'document.getElementById' in txt:
        return 'js'
    if re.search(r"#include\s+<|int\s+main\(|std::", code):
        return 'cpp'
    if re.search(r"\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bCREATE\b", txt, re.I):
        return 'sql'
    if re.search(r'\{\s*"[a-zA-Z0-9_\-]+"\s*:', code.strip()[:200]):
        return 'json'
    if re.search(r'^[\s\-]*#!/bin/(?:ba)?sh', code) or re.search(r'\becho\s+"', code):
        return 'sh'
    if re.search(r':[\s\n]*#[ \t]*', code) and re.search(r'color:|font-size|background', code):
        return 'css'
    # fallback
    return 'txt'


def extract_body_from_mhtml(text):
    m = re.search(r"<html[\s\S]*?</html>", text, flags=re.I)
    if m:
        return m.group(0)
    m = re.search(r"<body[\s\S]*?</body>", text, flags=re.I)
    if m:
        return m.group(0)
    idx = text.find("Content-Type: text/html")
    if idx != -1:
        m = re.search(r"<html[\s\S]*?</html>", text[idx:], flags=re.I)
        if m:
            return m.group(0)
    return text


def strip_inner_tags(s):
    # remove tags but keep text (use naive regex)
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    return s


def find_code_blocks(html_text):
    blocks = []  # list of tuples (start_pos, code_text)

    # Patterns to capture HTML code containers
    patterns = [
        re.compile(r'<pre[^>]*?>(.*?)</pre>', re.I|re.S),
        re.compile(r'<code[^>]*?>(.*?)</code>', re.I|re.S),
        re.compile(r'<div[^>]+class=["\']?[^"\'>]*(?:language-|lang-|prettyprint|hljs|code|source)[^"\'>]*["\']?[^>]*>(.*?)</div>', re.I|re.S),
        re.compile(r'<textarea[^>]*?>(.*?)</textarea>', re.I|re.S),
    ]

    for pat in patterns:
        for m in pat.finditer(html_text):
            inner = m.group(1)
            # strip inner tags
            content = strip_inner_tags(inner)
            content = html.unescape(content)
            content = content.strip('\n')
            if content.strip():
                blocks.append((m.start(), content))

    # Also search for triple-backtick blocks in the raw HTML (they may appear inside text nodes)
    for m in re.finditer(r'```(?:([a-zA-Z0-9_+\-]+)\n)?(.*?)```', html_text, re.S):
        lang = m.group(1) or ''
        content = m.group(2)
        content = html.unescape(content)
        content = content.strip('\n')
        if content.strip():
            blocks.append((m.start(), content))

    # Sort by appearance
    blocks.sort(key=lambda x: x[0])

    # Deduplicate by normalized content while preserving order
    seen = set()
    unique_blocks = []
    for pos, code in blocks:
        key = '\n'.join([ln.rstrip() for ln in code.splitlines() if ln.strip()])
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        unique_blocks.append(code)
    return unique_blocks


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: extract_code_blocks.py <archivo.mhtml>')
        sys.exit(2)
    infile = sys.argv[1]
    if not os.path.exists(infile):
        print('Archivo no encontrado:', infile)
        sys.exit(2)

    with open(infile, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # decode quoted-printable if present
    if '=20' in content or '=3D' in content or re.search(r'=\r?\n', content):
        try:
            content = quopri.decodestring(content.encode('utf-8', errors='replace')).decode('utf-8', errors='replace')
        except Exception:
            pass

    html_part = extract_body_from_mhtml(content)

    code_blocks = find_code_blocks(html_part)

    # output file path
    base = os.path.basename(infile)
    name, _ = os.path.splitext(base)
    outpath = os.path.join(os.path.dirname(infile), f"{name}_code_blocks.txt")

    hyph = '-' * 60

    with open(outpath, 'w', encoding='utf-8') as out:
        if not code_blocks:
            out.write('# No se detectaron bloques de código mediante heurísticas simples.\n')
        for i, code in enumerate(code_blocks, start=1):
            ext = detect_extension(code)
            filename = f'snippet_{i:03d}.{ext}'
            out.write(hyph + '\n')
            out.write(f'Archivo "{filename}":\n\n')
            out.write(code.strip() + '\n\n')
            out.write(hyph + '\n')

    print('Archivo de bloques de código creado:', outpath)
    print('Bloques detectados:', len(code_blocks))
