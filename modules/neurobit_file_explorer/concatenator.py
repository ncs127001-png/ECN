#!/usr/bin/env python3
# concatenator.py

import sys
import re
from pathlib import Path

def extract_metadata_blocks(report_text):
    blocks = []
    entries = report_text.split(">" + "_"*73 + "<")
    for entry in entries:
        if "Archivo:" in entry and "Carpeta:" in entry:
            archivo = re.search(r"Archivo:\s*(.+)", entry)
            carpeta = re.search(r"Carpeta:\s*(.+)", entry)
            fecha = re.search(r"Fecha:\s*(\d{2}/\d{2}/\d{4})", entry)
            if archivo and carpeta:
                blocks.append({
                    "archivo": archivo.group(1).strip(),
                    "carpeta": carpeta.group(1).strip(),
                    "fecha_str": fecha.group(1) if fecha else "01/01/1970"
                })
    return blocks

def main():
    report_path = Path("informe_ordenado.txt")
    if not report_path.exists():
        print("[concatenator] Error: informe_ordenado.txt no encontrado.")
        sys.exit(1)

    with open(report_path, "r", encoding="utf-8") as f:
        report = f.read()

    blocks = extract_metadata_blocks(report)
    output_file = Path("resultado_concatenado.txt")

    with open(output_file, "w", encoding="utf-8") as out:
        for block in blocks:
            # Ruta relativa desde la carpeta RESULTADOS_N
            rel_path = Path(block["carpeta"]).relative_to(Path(block["carpeta"]).anchor)
            src_file = Path(".") / rel_path / block["archivo"]

            # Buscar archivo en subdirectorios actuales (asumiendo estamos en RESULTADOS_N/)
            found = None
            for candidate in Path(".").rglob(block["archivo"]):
                if str(candidate).endswith(str(rel_path / block["archivo"])):
                    found = candidate
                    break
            if not found:
                # fallback: buscar solo por nombre (riesgoso, pero robusto)
                candidates = list(Path(".").rglob(block["archivo"]))
                found = candidates[0] if candidates else None

            content = ""
            if found and found.exists():
                try:
                    with open(found, "r", encoding="utf-8") as f:
                        content = f.read()
                    # Renombrar archivo: añadir '>>' al inicio del nombre
                    new_name = f">>{found.name}"
                    found.rename(found.parent / new_name)
                except Exception as e:
                    content = f"[ERROR al leer {found}: {e}]"

            out.write("-" * 50 + "\n")
            out.write(f"ARCHIVO: {block['archivo']}\n")
            out.write(f"CARPETA: {block['carpeta']}\n")
            out.write("-" * 50 + "\n")
            out.write(f"Date: ['{block['fecha_str']}']\n\n")
            out.write("INICIO__________________________________________\n\n")
            out.write(content + "\n")
            out.write("_____________________________________________EOF\n\n")

    print(f"[concatenator] Concatenación finalizada: {output_file}")

if __name__ == "__main__":
    main()
