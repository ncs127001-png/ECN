#!/usr/bin/env python3
"""
simon_validator.py
Valida mensaje YAML mínimo para Sala Neurobit.
Uso: python3 simon_validator.py path/to/message.yaml
Sale con 0 (ok) o 1 (errores).
"""
import sys
import yaml
import hashlib
from datetime import datetime
from pathlib import Path
import argparse

REQUIRED_TOP = ["PROTOCOL_ID","VERSION","MESSAGE_ID","SESSION_ID","CREATED_AT","ORIGEN","FRAGMENT","CONTENT"]


def sha1_short(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def iso_ok(s):
    try:
        datetime.fromisoformat(s.replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description='simon_validator: valida un YAML de mensaje')
    parser.add_argument('positional', nargs='?', help='Ruta a message.yaml (posicional)')
    parser.add_argument('--message', '--file', '--input', dest='message', help='Ruta al YAML del mensaje', required=False)
    parser.add_argument('--stdin', action='store_true', help='Leer YAML desde stdin')
    args = parser.parse_args()

    path_arg = args.message or args.positional
    if args.stdin:
        try:
            doc = yaml.safe_load(sys.stdin.read())
        except Exception as e:
            print('ERROR: failed to read YAML from stdin', e)
            sys.exit(1)
    else:
        if not path_arg:
            print("Usage: simon_validator.py <message.yaml> or --message <file> or --stdin")
            sys.exit(1)
        p = Path(path_arg)
        if not p.exists():
            print("ERROR: file not found", p)
            sys.exit(1)
        doc = load_yaml(p)
    errors = []
    for k in REQUIRED_TOP:
        if k not in doc:
            errors.append(f"Missing top-level field: {k}")
    if "CREATED_AT" in doc and not iso_ok(doc["CREATED_AT"]):
        errors.append("CREATED_AT is not valid ISO8601")
    # FRAGMENT checks
    if "FRAGMENT" in doc:
        fr = doc["FRAGMENT"]
        if not isinstance(fr, dict) or "INDEX" not in fr or "TOTAL" not in fr:
            errors.append("FRAGMENT must be dict with INDEX and TOTAL")
    # CONTENT presence
    if "CONTENT" in doc:
        if not doc["CONTENT"]:
            errors.append("CONTENT is empty")
    # MESSAGE_HASH check (optional)
    if "MESSAGE_HASH" in doc:
        expected = doc["MESSAGE_HASH"]
        # compute hash of content + origin + created
        cnt = str(doc.get("CONTENT","")) + str(doc.get("ORIGEN","")) + str(doc.get("CREATED_AT",""))
        got = sha1_short(cnt)
        if got != expected:
            errors.append(f"MESSAGE_HASH mismatch (expected {expected} got {got})")
    else:
        errors.append("MESSAGE_HASH absent")
    if errors:
        print("SIMON VALIDATION FAILED:")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("SIMON: OK ✅")
    sys.exit(0)

if __name__ == "__main__":
    main()
