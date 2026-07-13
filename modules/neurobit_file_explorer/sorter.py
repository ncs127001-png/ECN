#!/usr/bin/env python3
# sorter.py

import sys
import re
from datetime import datetime
from pathlib import Path

ENTRY_SEP = ">" + "_"*73 + "<"

def parse_entries(text):
    parts = text.split(ENTRY_SEP)
    header = parts[0].strip()
    entries_raw = [p.strip() for p in parts[1:] if "Archivo:" in p]
    entries = []
    for raw in entries_raw:
        lines = raw.split("\n")
        meta = {}
        for line in lines:
            if line.startswith("Archivo:"):
                meta["archivo"] = line.replace("Archivo: ", "").strip()
            elif line.startswith("Carpeta:"):
                meta["carpeta"] = line.replace("Carpeta: ", "").strip()
            elif line.startswith("Fecha:"):
                meta["fecha_str"] = line.replace("Fecha: ", "").strip()
                meta["fecha_dt"] = datetime.strptime(meta["fecha_str"], "%d/%m/%Y")
        if "archivo" in meta:
            meta["raw"] = raw
            entries.append(meta)
    return header, entries

def main():
    input_path = Path("informe_bruto.txt")
    if not input_path.exists():
        print("[sorter] Error: informe_bruto.txt no encontrado.")
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    header, entries = parse_entries(content)
    entries.sort(key=lambda x: x["fecha_dt"], reverse=True)

    output_path = Path("informe_ordenado.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header + "\n\n")
        for e in entries:
            f.write(e["raw"] + "\n" + ENTRY_SEP + "\n\n")

    print(f"[sorter] Informe ordenado generado: {output_path}")

if __name__ == "__main__":
    main()
