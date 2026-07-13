#!/usr/bin/env python3
"""
Merge `fragments/parte_N.txt` parts (sorted numerically) into
`texto_completo/bitacora_eva_full.txt`. Optionally create a zip of parts.

Usage:
  python3 scripts/merge_parts.py           # produce combined file
  python3 scripts/merge_parts.py --zip     # also create bitacora_eva_parts.zip
  python3 scripts/merge_parts.py --out FILE  # custom output path
"""

import argparse
import os
import re
import sys
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAG_DIR = os.path.join(ROOT, 'fragments')
OUT_DIR = os.path.join(ROOT, 'texto_completo')
DEFAULT_OUT = os.path.join(OUT_DIR, 'bitacora_eva_full.txt')
ZIP_NAME = os.path.join(ROOT, 'bitacora_eva_parts.zip')

PAT = re.compile(r'^parte_(\d+)\.txt$')


def find_parts():
    try:
        names = os.listdir(FRAG_DIR)
    except FileNotFoundError:
        print(f"fragments directory not found at {FRAG_DIR}")
        sys.exit(1)
    parts = []
    for n in names:
        m = PAT.match(n)
        if m:
            parts.append((int(m.group(1)), n))
    parts.sort()
    return [fname for _, fname in parts]


def ensure_out_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def merge_parts(outpath):
    parts = find_parts()
    if not parts:
        print('No parts found matching parte_*.txt in fragments/.')
        return 1
    ensure_out_dir(outpath)
    written = 0
    with open(outpath, 'w', encoding='utf-8') as outf:
        for fname in parts:
            fpath = os.path.join(FRAG_DIR, fname)
            # write a small header to help identify parts (optional)
            outf.write(f"\n\n--- {fname} ---\n\n")
            with open(fpath, 'r', encoding='utf-8', errors='replace') as inf:
                for line in inf:
                    outf.write(line)
            written += 1
    print(f"Merged {written} parts into {outpath}")
    return 0


def make_zip(zipname):
    parts = find_parts()
    if not parts:
        print('No parts found to zip.')
        return 1
    with ZipFile(zipname, 'w', ZIP_DEFLATED) as zf:
        for fname in parts:
            zf.write(os.path.join(FRAG_DIR, fname), arcname=fname)
    print(f"Created zip archive {zipname} with {len(parts)} files")
    return 0


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Merge fragments/parte_*.txt into one file')
    p.add_argument('--out', '-o', default=DEFAULT_OUT, help='output combined file path')
    p.add_argument('--zip', action='store_true', help='also create a zip archive of parts')
    args = p.parse_args()

    code = merge_parts(args.out)
    if code != 0:
        sys.exit(code)
    if args.zip:
        zcode = make_zip(ZIP_NAME)
        if zcode != 0:
            sys.exit(zcode)

    print('Done.')
