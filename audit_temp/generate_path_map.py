#!/usr/bin/env python3
"""Genera el mapa de paths del workspace."""
import os
import json
from pathlib import Path

def generate_map(root_dir: Path, output_file: Path):
    path_map = {}
    for root, dirs, files in os.walk(root_dir):
        # Ignorar directorios ruidosos
        dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.venv', 'node_modules'}]
        
        for file in files:
            if file.endswith(('.py', '.js', '.yaml', '.json', '.md', '.sh')):
                abs_path = str(Path(root) / file)
                path_map[file] = abs_path  # nombre → ruta absoluta
    
    with open(output_file, 'w') as f:
        json.dump(path_map, f, indent=2)
    
    print(f"✅ Mapa generado: {len(path_map)} archivos indexados")

if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent  # raíz del workspace
    generate_map(root, root / "path_map.json")
