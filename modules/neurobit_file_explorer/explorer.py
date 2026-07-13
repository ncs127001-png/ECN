#!/usr/bin/env python3
# explorer.py

import os
import sys
import shutil
import glob
from pathlib import Path
from datetime import datetime

def get_next_result_dir(base="RESULTADOS"):
    """Devuelve la siguiente carpeta RESULTADOS_N disponible."""
    n = 1
    while os.path.exists(f"{base}_{n}"):
        n += 1
    return f"{base}_{n}"

def get_file_creation_time(filepath):
    stat = os.stat(filepath)
    try:
        return datetime.fromtimestamp(stat.st_birthtime)  # macOS
    except AttributeError:
        return datetime.fromtimestamp(stat.st_ctime)      # Linux

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 explorer.py <patrón> [nivel_recursión] [directorio_raíz]")
        print("Ej: python3 explorer.py '*.md' 3 ~/neurobit_salon_v0.1")
        pattern = "*.md"
        max_depth = 3
        root_dir = Path.cwd()
    else:
        pattern = sys.argv[1]
        max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        root_dir = Path(sys.argv[3]).expanduser() if len(sys.argv) > 3 else Path.cwd()

    root_dir = root_dir.resolve()
    
    # =========================================================================
    # PASO 1: BUSCAR PRIMERO (Sin crear nada todavía)
    # =========================================================================
    matches = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        depth = str(dirpath).count(os.sep) - str(root_dir).count(os.sep)
        if depth > max_depth:
            dirnames[:] = []  # Evita descender más
            continue
        for filename in filenames:
            if glob.fnmatch.fnmatch(filename, pattern):
                src = Path(dirpath) / filename
                matches.append(src)

    # =========================================================================
    # PASO 2: VERIFICAR RESULTADOS (Salida temprana si está vacío)
    # =========================================================================
    if not matches:
        print(f"[explorer] No se encontraron archivos que coincidan con '{pattern}'.")
        print("[explorer] No se creó ninguna carpeta RESULTADOS_N.")
        sys.exit(0)  # Terminamos el script limpiamente sin crear nada

    # =========================================================================
    # PASO 3: CREAR ESTRUCTURA (Solo si hubo resultados)
    # =========================================================================
    result_dir = Path(get_next_result_dir())
    result_dir.mkdir(exist_ok=True)

    report_path = result_dir / "informe_bruto.txt"

    # Escribir encabezado
    now = datetime.now().strftime("%d de %B del año %Y a las %H:%M horas")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"Información de la busqueda realizada {now}\n")
        f.write(f"Directorio Raíz: {root_dir}\n")
        f.write(f"Nivel de busqueda en subdirectorios: {max_depth}\n")
        f.write(f"Archivos: {pattern}\n")
        f.write(">" + "_"*73 + "<\n")
        f.write("Resultados:\n\n")

    # =========================================================================
    # PASO 4: COPIAR Y REGISTRAR
    # =========================================================================
    for src in matches:
        rel_path = src.relative_to(root_dir)
        dst = result_dir / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

        ctime = get_file_creation_time(src)
        date_str = ctime.strftime("%d/%m/%Y")

        with open(report_path, "a", encoding="utf-8") as f:
            f.write(f"Archivo: {src.name}\n")
            f.write(f"Carpeta: {src.parent}\n")
            f.write(f"Fecha: {date_str}\n")
            f.write(">" + "_"*73 + "<\n\n")

    print(f"[explorer] Encontrados {len(matches)} archivos. Resultados en: {result_dir}")

if __name__ == "__main__":
    main()