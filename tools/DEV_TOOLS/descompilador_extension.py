#!/usr/bin/env python3
"""
Descompilador flexible para extension-eva.md
Extrae bloques de código de archivos markdown y reconstruye la estructura de carpetas.
"""

import os
import sys
import re
from pathlib import Path

def extract_code_blocks(markdown_file):
    """
    Extrae bloques de código del markdown.
    Retorna lista de (filename, filepath, lenguaje, contenido)
    """
    blocks = []
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón para encontrar bloques de código con lenguaje y comentarios de archivo
    # Busca: ## 1. Configuración VSCode (.vscode/settings.json)
    #        ```json
    #        {contenido}
    #        ```
    
    # Primero, buscar secciones como "## 1. Nombre (path)"
    pattern = r'##\s+\d+\.\s+([^\n(]+)\s*\(([^)]+)\)\s*\n```(\w+)?\s*\n(.*?)\n```'
    
    matches = re.finditer(pattern, content, re.DOTALL | re.MULTILINE)
    
    for match in matches:
        title = match.group(1).strip()
        filepath = match.group(2).strip()
        lang = match.group(3) or "text"
        code = match.group(4).strip()
        
        # Obtener nombre de archivo del path
        if '/' in filepath:
            filename = filepath.split('/')[-1]
        else:
            filename = filepath
        
        blocks.append({
            'title': title,
            'filepath': filepath,
            'filename': filename,
            'language': lang,
            'content': code
        })
    
    return blocks

def reconstruct_files(markdown_file, base_output_dir):
    """
    Reconstruye archivos desde bloques de código del markdown.
    """
    
    blocks = extract_code_blocks(markdown_file)
    
    if not blocks:
        print("❌ No se encontraron bloques de código en el archivo markdown.")
        return 0
    
    os.makedirs(base_output_dir, exist_ok=True)
    
    count = 0
    for block in blocks:
        # Construir ruta de salida
        filepath = block['filepath']
        
        # Manejar rutas relativas (~/... → base_output_dir)
        if filepath.startswith('~/'):
            filepath = filepath[2:]
        elif filepath.startswith('./'):
            filepath = filepath[2:]
        
        output_path = os.path.join(base_output_dir, filepath)
        output_dir = os.path.dirname(output_path)
        
        # Crear directorios
        os.makedirs(output_dir, exist_ok=True)
        
        # Escribir archivo
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(block['content'])
            print(f"✅ {block['title']:<40} → {output_path}")
            count += 1
        except Exception as e:
            print(f"❌ Error escribiendo {output_path}: {e}")
    
    return count

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 descompilador_extension.py <archivo.md> [carpeta_salida]")
        sys.exit(1)
    
    markdown_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './extension_reconstructed'
    
    if not os.path.isfile(markdown_file):
        print(f"❌ Archivo no encontrado: {markdown_file}")
        sys.exit(1)
    
    print(f"🔍 Analizando: {markdown_file}")
    print(f"📁 Salida: {output_dir}\n")
    
    count = reconstruct_files(markdown_file, output_dir)
    
    print(f"\n✅ Reconstrucción completada: {count} archivo(s) creado(s)")
    print(f"📂 Estructura disponible en: {output_dir}")

if __name__ == "__main__":
    main()
