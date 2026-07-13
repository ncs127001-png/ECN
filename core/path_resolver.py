#!/usr/bin/env python3
"""Resuelve paths consultando el mapa dinámico."""
import json
from pathlib import Path

class PathResolver:
    def __init__(self, workspace_root: Path):
        self.map_file = workspace_root / "path_map.json"
        self.path_map = self._load_map()
    
    def _load_map(self) -> dict:
        if self.map_file.exists():
            with open(self.map_file, 'r') as f:
                return json.load(f)
        return {}
    
    def resolve(self, filename: str) -> Path:
        """Devuelve la ruta absoluta de un archivo por su nombre."""
        if filename in self.path_map:
            return Path(self.path_map[filename])
        
        # Si no está en el mapa, regenerar y reintentar
        print(f"⚠️ {filename} no encontrado en mapa. Regenerando...")
        from tools.generate_path_map import generate_map
        generate_map(self.map_file.parent, self.map_file)
        self.path_map = self._load_map()
        
        if filename in self.path_map:
            return Path(self.path_map[filename])
        
        raise FileNotFoundError(f"Archivo no encontrado: {filename}")
    
    def refresh(self):
        """Fuerza regeneración del mapa."""
        from tools.generate_path_map import generate_map
        generate_map(self.map_file.parent, self.map_file)
        self.path_map = self._load_map()
