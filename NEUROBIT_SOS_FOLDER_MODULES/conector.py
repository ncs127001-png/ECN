#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# conector.py 
import os
import sys
from pathlib import Path
from core.path_resolver import PathResolver

class SOSConector:
    def __init__(self):
        self.root_path = Path(__file__).resolve().parent
        self.path_resolver = PathResolver(self.root_path)
        self.yaml_path = self.path_resolver.resolve("architecture.yaml")
        self.trazabilidad_log = self.path_resolver.resolve("data") / ("logs") / ("trazabilidad_arquitectura.jsonl")
        
        # Ahora en lugar de hardcodear:
        # self.modules_dir = self.root_path / "NEUROBIT_SOS_FOLDER_MODULES"        
        # Usamos el resolver:

        self.modules_dir = self.path_resolver.resolve("NEUROBIT_SOS_FOLDER_MODULES")
        self.trazabilidad_log.parent.mkdir(parents=True, exist_ok=True)
        self._verificar_o_crear_yaml()

    def _verificar_o_crear_yaml(self):
        """Asegura que el archivo de arquitectura exista con la estructura correcta."""
        import yaml
        if not self.yaml_path.exists():
            estructura_base = {
                "sos_project": {"name": "Sovereign Order Sentinels", "version": "0.3b"},
                "modules": [
                    {"id": "SOS_NF-HID", "path": "NEUROBIT_SOS_FOLDER_MODULES", "description": "Módulos core HID"}
                ]
            }
            with open(self.yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(estructura_base, f, default_flow_style=False)

    def registrar_trazabilidad(self, modulo: str, archivo: str, cambio: str, comentario: str):
        """Inyección Append-Only inmutable para auditoría externa."""
        import json
        from datetime import datetime
        
        registro = {
            "timestamp": datetime.now().isoformat(),
            "modulo": modulo,
            "archivo": archivo,
            "cambio": cambio,
            "comentario": comentario if comentario.strip() else "Sin comentario."
        }
        with open(self.trazabilidad_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(registro, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    c = SOSConector()
    print(f"[✓] Conector SOS V0.3 online. Raíz: {c.root_path}")

