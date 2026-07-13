#!/usr/bin/env python3
"""Ingesta del directorio 'trabajo final compendio'.

Genera `data/compendio_index.jsonl` con una línea por archivo.

Reglas:
- calcula size y sha256
- intenta leer como UTF-8; si falla, marca como binary y no incluye contenido
- incluye path relativo, mtime y los metadatos básicos
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
COMP_DIR = Path.home() / 'Documentos' / 'trabajo final compendio'
OUT_DIR = ROOT / 'data'
OUT_FILE = OUT_DIR / 'compendio_index.jsonl'


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def try_read_text(path: Path) -> tuple[bool, str]:
    try:
        with path.open('r', encoding='utf-8') as f:
            return True, f.read()
    except Exception:
        return False, ''


def ingest():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    with OUT_FILE.open('w', encoding='utf-8') as out:
        if not COMP_DIR.exists():
            raise SystemExit(f"Compendium dir not found: {COMP_DIR}")
        for entry in sorted(COMP_DIR.iterdir()):
            if not entry.is_file():
                continue
            stat = entry.stat()
            size = stat.st_size
            mtime = datetime.utcfromtimestamp(stat.st_mtime).isoformat() + 'Z'
            sha = sha256_of_file(entry)
            is_text, content = try_read_text(entry)
            item = {
                'filename': entry.name,
                'path': str(entry.resolve()),
                'size': size,
                'sha256': sha,
                'mtime': mtime,
                'is_text': is_text,
            }
            if is_text:
                item['content'] = content
            out.write(json.dumps(item, ensure_ascii=False) + '\n')
            count += 1
    print(f"Ingested {count} files -> {OUT_FILE}")


if __name__ == '__main__':
    ingest()
