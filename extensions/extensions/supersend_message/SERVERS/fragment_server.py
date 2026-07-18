#!/usr/bin/env python3
"""Lightweight HTTP server (no external deps) that accepts a multipart POST
to /fragment and writes fragments into ./fragments/ directory.

Usage:
  python3 scripts/fragment_server_simple.py

Then POST multipart form to http://127.0.0.1:8001/fragment with fields:
  file=@<file>, title, author, max_chars
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import re
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
FRAGMENTS_DIR = BASE_DIR / 'fragments'
FRAGMENTS_DIR.mkdir(parents=True, exist_ok=True)


def split_paragraphs(text):
    parts = re.split(r'\n\s*\n+', text)
    return [p.strip() for p in parts if p.strip()]


def split_long_paragraph(p, max_chars):
    words = re.split(r'\s+', p)
    chunks = []
    cur = ''
    for w in words:
        candidate = (cur + ' ' + w).strip() if cur else w
        if len(candidate) > max_chars:
            if cur:
                chunks.append(cur)
            if len(w) > max_chars:
                for i in range(0, len(w), max_chars):
                    chunks.append(w[i:i+max_chars])
                cur = ''
            else:
                cur = w
        else:
            cur = candidate
    if cur:
        chunks.append(cur)
    return chunks


def build_header(idx, title, author, source):
    return (f"[FRAGMENT_ID]: {idx}\n"
            f"[TITLE]: \"{title or ''}\"\n"
            f"[AUTHOR]: {author or ''}\n"
            f"[SOURCE]: {source}\n"
            f"[CONTENT]:\n")


def next_index(prefix='parte_'):
    max_n = 0
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)\.txt$")
    for p in FRAGMENTS_DIR.iterdir():
        if p.is_file():
            m = pattern.match(p.name)
            if m:
                try:
                    n = int(m.group(1))
                    if n > max_n:
                        max_n = n
                except ValueError:
                    pass
    return max_n + 1


class FragHandler(BaseHTTPRequestHandler):
    def _send_json(self, dct, code=200):
        data = json.dumps(dct, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != '/fragment':
            self.send_error(404)
            return
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        if ctype != 'multipart/form-data':
            self._send_json({'error': 'expected multipart/form-data'}, 400)
            return
        pdict['boundary'] = pdict['boundary'].encode('utf-8')
        fs = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST'}, keep_blank_values=True)
        if 'file' not in fs:
            self._send_json({'error': 'no file provided'}, 400)
            return
        fileitem = fs['file']
        filename = getattr(fileitem, 'filename', 'uploaded.txt')
        raw = fileitem.file.read()
        try:
            text = raw.decode('utf-8')
        except Exception:
            text = raw.decode('latin-1')

        title = fs.getvalue('title', '')
        author = fs.getvalue('author', '')
        try:
            max_chars = int(fs.getvalue('max_chars') or 5000)
        except Exception:
            max_chars = 5000
        prefix = fs.getvalue('prefix') or 'parte_'

        paragraphs = split_paragraphs(text)
        fragments = []
        current = ''
        for p in paragraphs:
            if len(p) > max_chars:
                pieces = split_long_paragraph(p, max_chars)
                for piece in pieces:
                    if current:
                        fragments.append(current)
                        current = ''
                    fragments.append(piece)
            else:
                if current:
                    if len(current) + 2 + len(p) <= max_chars:
                        current = current + '\n\n' + p
                    else:
                        fragments.append(current)
                        current = p
                else:
                    current = p
        if current:
            fragments.append(current)

        start = next_index(prefix=prefix)
        created = []
        pad = max(3, len(str(start + len(fragments))))
        for i, piece in enumerate(fragments, start=start):
            idx = str(i).zfill(pad)
            name = f"{prefix}{idx}.txt"
            header = build_header(idx, title, author, filename)
            path = FRAGMENTS_DIR / name
            with open(path, 'w', encoding='utf-8') as out:
                out.write(header + '\n' + piece + '\n')
            created.append(name)

        self._send_json({'created': len(created), 'files': created})


def run(server_class=HTTPServer, handler_class=FragHandler, port=8001):
    server_address = ('127.0.0.1', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting fragment server on http://127.0.0.1:{port}/fragment")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Stopping')
        httpd.server_close()


if __name__ == '__main__':
    run()
