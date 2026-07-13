#!/usr/bin/env python3
import re
import os
import sys
import html
import quopri
from pathlib import Path

KNOWN_SPEAKERS = [
    'Qwen3-Max', 'Qwen', 'Qwen3', 'Qwen3-Max', 'Asistente', 'Assistant', 'Usuario', 'User', 'Tú', 'Tu', 'You', 'Coder', 'Proyectos', 'Neurobitronics', 'El Profe Domingo'
]


def normalize_name(n):
    # sanitize for filename
    n = re.sub(r"[\"'\\/:*?<>|]+", '', n)
    n = re.sub(r"\s+", '_', n.strip())
    return n if n else 'Unknown'


def detect_extension(code):
    txt = code.lower()
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
    if re.search(r'^[\s\-]*#!/bin/(?:ba)?sh', code, re.M) or re.search(r'\becho\s+"', code):
        return 'sh'
    if re.search(r'^[\s\S]*<style|color:|font-size|background', code):
        return 'css'
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


def strip_tags_keep_newlines(s):
    s = re.sub(r'<br\s*/?>', '\n', s, flags=re.I)
    s = re.sub(r'<(/)?(div|p|li|h[1-6]|section|article)[^>]*>', '\n', s, flags=re.I)
    s = re.sub(r'<[^>]+>', '', s)
    return s


def find_code_blocks_with_positions(html_text):
    patterns = [
        re.compile(r'<pre[^>]*?>(.*?)</pre>', re.I | re.S),
        re.compile(r'<code[^>]*?>(.*?)</code>', re.I | re.S),
        re.compile(r'<textarea[^>]*?>(.*?)</textarea>', re.I | re.S),
        re.compile(r'<div[^>]+class=["\']?[^"\'>]*(?:language-|lang-|prettyprint|hljs|code|source)[^"\'>]*["\']?[^>]*>(.*?)</div>', re.I | re.S),
    ]
    blocks = []
    for pat in patterns:
        for m in pat.finditer(html_text):
            inner = m.group(1)
            content = strip_tags_keep_newlines(inner)
            content = html.unescape(content)
            content = content.strip('\n')
            if content.strip():
                blocks.append({'pos': m.start(), 'code': content})

    # triple backtick
    for m in re.finditer(r'```(?:([a-zA-Z0-9_+-]+)\n)?(.*?)```', html_text, re.S):
        content = m.group(2)
        content = html.unescape(content).strip('\n')
        if content.strip():
            blocks.append({'pos': m.start(), 'code': content})

    blocks.sort(key=lambda x: x['pos'])

    # dedupe
    seen = set()
    unique = []
    for b in blocks:
        key = '\n'.join([ln.rstrip() for ln in b['code'].splitlines() if ln.strip()])
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        unique.append(b)
    return unique


def detect_speaker_around(html_text, pos):
    start = max(0, pos - 1000)
    context = html_text[start:pos]
    # 1) search for explicit sender class tags
    m = re.search(r'class=["\']?(?:sender|author|username|user-name|message-sender)["\']?[^>]*>\s*([^<\n]{1,60})', context, re.I)
    if m:
        name = m.group(1).strip()
        return name
    # 2) search for known speaker tokens, prefer last occurrence
    found = []
    for sp in KNOWN_SPEAKERS:
        idx = context.rfind(sp)
        if idx != -1:
            found.append((idx, sp))
    if found:
        found.sort()
        return found[-1][1]
    # 3) search for patterns like 'Name\nYYYY-MM-DD' or 'Name\nHH:MM'
    m = re.search(r'([A-Za-z0-9 _\-]{2,30})\s*\n\s*\d{4}-\d{2}-\d{2}', context)
    if m:
        return m.group(1).strip()
    m2 = re.search(r'([A-Za-z0-9 _\-]{2,30})\s*\n\s*\d{1,2}:\d{2}', context)
    if m2:
        return m2.group(1).strip()
    # 4) fallback: look for preceding strong/b tag
    m3 = re.search(r'(<(?:strong|b)[^>]*>([^<]{1,60})</(?:strong|b)>)', context, re.I)
    if m3:
        return m3.group(2).strip()
    return 'Unknown'


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: extract_code_blocks_with_speakers.py <archivo.mhtml>')
        sys.exit(2)
    infile = sys.argv[1]
    inp = Path(infile)
    if not inp.exists():
        print('Archivo no encontrado:', infile)
        sys.exit(2)

    outdir = inp.parent / 'code_snippets'
    outdir.mkdir(exist_ok=True)

    with open(infile, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    if '=20' in content or '=3D' in content or re.search(r'=\r?\n', content):
        try:
            content = quopri.decodestring(content.encode('utf-8', errors='replace')).decode('utf-8', errors='replace')
        except Exception:
            pass

    html_part = extract_body_from_mhtml(content)
    blocks = find_code_blocks_with_positions(html_part)

    aggregated_path = inp.parent / f"{inp.stem}_code_blocks_attributed.txt"
    hyph = '-' * 60

    with open(aggregated_path, 'w', encoding='utf-8') as agg:
        if not blocks:
            agg.write('# No se detectaron bloques de código.\n')
        for i, b in enumerate(blocks, start=1):
            code = b['code'].strip()
            pos = b['pos']
            speaker = detect_speaker_around(html_part, pos)
            speaker_safe = normalize_name(speaker)
            ext = detect_extension(code)
            filename = f"snippet_{i:03d}__{speaker_safe}.{ext}"
            file_path = outdir / filename
            # write individual file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code + '\n')
            # write aggregated
            agg.write(hyph + '\n')
            agg.write(f'Archivo "{filename}":\n\n')
            agg.write(code + '\n')
            agg.write(hyph + '\n')
    # create zip
    zip_path = inp.parent / f"{inp.stem}_code_snippets.zip"
    import zipfile
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(outdir.iterdir()):
            zf.write(p, arcname=p.name)

    print('Creado directorio:', outdir)
    print('Archivo agregado:', aggregated_path)
    print('ZIP creado:', zip_path)
    print('Snippets escritos:', len(list(outdir.iterdir())))
