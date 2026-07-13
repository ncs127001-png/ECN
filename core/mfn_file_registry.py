#!/usr/bin/env python3
"""
MFN File Registry - Sistema de auto-organización
Cada archivo se auto-declara y el sistema mantiene el índice actualizado
"""
import re
from pathlib import Path
from datetime import datetime

class MFNFileRegistry:
    def __init__(self, workspace_root: Path):
        self.root = workspace_root
        self.mfn_pattern = re.compile(
            r'MFN_LOCATION:\s*(\S+)\n.*?MFN_LEVEL:\s*(\d+)',
            re.MULTILINE
        )
    
    def scan_and_index(self):
        """Escanea todos los .py y genera índice MFN"""
        index = {}
        for py_file in self.root.rglob("*.py"):
            metadata = self.extract_mfn_metadata(py_file)
            if metadata:
                index[str(py_file)] = metadata
        return index
    
    def extract_mfn_metadata(self, file_path: Path) -> dict:
        """Extrae metadatos MFN del header del archivo"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(500)  # Primeros 500 caracteres
        
        match = self.mfn_pattern.search(content)
        if match:
            return {
                "location": match.group(1),
                "level": int(match.group(2)),
                "path": str(file_path),
                "updated": datetime.now().isoformat()
            }
        return None
    
    def move_file(self, src_path: Path, new_location: str):
        """Mueve un archivo y actualiza sus metadatos"""
        # 1. Calcular nueva ruta
        dest_path = self.root / new_location / src_path.name
        
        # 2. Mover archivo físico
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        src_path.rename(dest_path)
        
        # 3. Actualizar metadatos en el archivo movido
        self.update_mfn_header(dest_path, new_location)
        
        # 4. Regenerar path_map.json
        from tools.generate_path_map import generate_map
        generate_map(self.root, self.root / "path_map.json")
        
        return dest_path
    
    def update_mfn_header(self, file_path: Path, new_location: str):
        """Actualiza el header MFN del archivo"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar MFN_LOCATION
        updated = re.sub(
            r'MFN_LOCATION:\s*\S+',
            f'MFN_LOCATION: {new_location}',
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated)	
