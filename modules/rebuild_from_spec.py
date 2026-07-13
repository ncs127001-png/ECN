#!/usr/bin/env python3
# rebuild_from_spec.py
# Reconstruye proyecto Neurobit desde una especificación técnica en markdown

import os
import re
import sys
import argparse
from pathlib import Path

def extract_code_blocks_with_paths(md_content: str):
    """
    Extrae pares (ruta, contenido) basados en encabezados del tipo:
    ## N. Título (ruta/relativa/archivo.ext)
    ```lenguaje
    contenido
    ```
    """
    # Patrón: encabezado con ruta entre paréntesis + bloque de código siguiente
    pattern = r"##\s+\d+\.\s+[^\n]*$\s*\(([^)]+?)\)\s*$(?:.*?)(?:```(?:[a-z]*)\n(.*?)\n```)"
    matches = re.findall(pattern, md_content, re.DOTALL | re.MULTILINE)
    
    files = []
    for filepath, content in matches:
        # Normalizar ruta (eliminar espacios finales, asegurar relativo)
        filepath = filepath.strip()
        content = content.rstrip('\n')
        files.append((filepath, content))
    return files

def validate_against_tree(file_paths, tree_root="neurobit"):
    """
    Opcional: validar que las rutas estén dentro del árbol esperado.
    Aquí asumimos que todo bajo 'neurobit/' es válido.
    """
    invalid = []
    for fp in file_paths:
        if not fp.startswith(f"{tree_root}/") and fp != tree_root:
            # Permitir rutas relativas si no incluyen 'neurobit/' explícito
            pass
    return invalid

def main():
    parser = argparse.ArgumentParser(description="Reconstruye Neurobit desde especificación técnica")
    parser.add_argument("spec_file", help="Archivo .md con la especificación")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar acciones sin ejecutar")
    parser.add_argument("--root", default="neurobit", help="Nombre de la raíz del proyecto (default: neurobit)")
    args = parser.parse_args()

    spec_path = Path(args.spec_file)
    if not spec_path.exists():
        print(f"❌ Especificación no encontrada: {spec_path}")
        sys.exit(1)

    with open(spec_path, 'r', encoding='utf-8') as f:
        content = f.read()

    file_entries = extract_code_blocks_with_paths(content)

    if not file_entries:
        print("⚠️  No se detectaron bloques de código con rutas en la especificación.")
        return

    print(f"📦 Detectados {len(file_entries)} archivos para reconstruir:")

    for relpath, _ in file_entries:
        print(f"  → {relpath}")

    if args.dry_run:
        print("\n🔍 Modo dry-run: ninguna escritura realizada.")
        return

    # Crear raíz del proyecto
    project_root = Path(args.root)
    project_root.mkdir(exist_ok=True)

    print(f"\n🛠️  Escribiendo archivos en '{project_root}'...")

    for relpath, body in file_entries:
        full_path = project_root / relpath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(body)
        print(f"✅ {relpath}")

    print(f"\n✨ Especificación implementada en '{project_root}'.")
    print("Siguiente: ejecutar ./automations/init_workspace.sh desde la raíz.")

if __name__ == "__main__":
    main()