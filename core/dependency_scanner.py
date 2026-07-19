#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MFN_LOCATION: core/
MFN_LEVEL: 1

DEPENDENCY SCANNER - SISTEMA INMUNOLÓGICO ECN
Propósito: Leer contratos module_*.yaml, detectar dependencias faltantes
           y generar requirements_dynamic.txt para instalación segura.
Co-Creación: NODO_SEMILLA & NODO_REFLEJO
"""

import os
import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Set

class DependencyScanner:
    def __init__(self, workspace_root: str):
        self.workspace = Path(workspace_root).expanduser()
        self.python_deps: Set[str] = set()
        self.system_deps: Set[str] = set()
        self.modules_scanned: List[str] = []
        
    def scan_workspace(self) -> Dict:
        """Escanea recursivamente buscando module_*.yaml"""
        print(f"🔍 Escaneando workspace: {self.workspace}")
        
        # Ignorar carpetas ruidosas
        ignore_dirs = {'.git', '.venv', '__pycache__', 'node_modules', '.backups'}
        
        for root, dirs, files in os.walk(self.workspace):
            # Filtrar directorios ignorados
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file.startswith('module_') and file.endswith('.yaml'):
                    self._parse_contract(Path(root) / file)
                    
        return {
            'python': sorted(list(self.python_deps)),
            'system': sorted(list(self.system_deps)),
            'modules': self.modules_scanned
        }
    
    def _parse_contract(self, yaml_path: Path):
        """Extrae dependencias de un contrato YAML"""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                contract = yaml.safe_load(f)
                
            module_id = contract.get('module', {}).get('id', 'unknown')
            self.modules_scanned.append(module_id)
            
            # Extraer dependencias Python
            deps = contract.get('dependencies', {})
            if 'python' in deps:
                for pkg in deps['python']:
                    self.python_deps.add(pkg)
                    
            # Extraer dependencias de Sistema
            if 'system' in deps:
                for tool in deps['system']:
                    self.system_deps.add(tool)
                    
            print(f"  ✅ [{module_id}] -> {len(deps.get('python', []))} py, {len(deps.get('system', []))} sys")
            
        except Exception as e:
            print(f"  ⚠️ Error leyendo {yaml_path}: {e}")
    
    def generate_requirements_files(self, output_dir: str = "."):
        """Genera archivos de requisitos para instalación"""
        output_path = Path(output_dir).expanduser()
        
        # 1. requirements_dynamic.txt (Python)
        req_file = output_path / "requirements_dynamic.txt"
        with open(req_file, 'w', encoding='utf-8') as f:
            f.write("# ECN Dynamic Requirements - Generado automáticamente\n")
            f.write("# Basado en contratos module_*.yaml\n\n")
            for dep in sorted(self.python_deps):
                f.write(f"{dep}\n")
        print(f"💾 Python deps guardadas en: {req_file}")
        
        # 2. system_deps_check.txt (Herramientas Linux)
        sys_file = output_path / "system_deps_check.txt"
        with open(sys_file, 'w', encoding='utf-8') as f:
            f.write("# ECN System Dependencies - Herramientas de Sistema\n")
            f.write("# Instalar con: sudo apt install <paquete>\n\n")
            for dep in sorted(self.system_deps):
                # Mapeo simple de nombres comunes
                f.write(f"{dep}\n")
        print(f"💾 System deps guardadas en: {sys_file}")
        
    def check_missing_system_deps(self) -> List[str]:
        """Verifica qué herramientas de sistema faltan (Linux)"""
        missing = []
        import shutil
        
        for tool in self.system_deps:
            if shutil.which(tool) is None:
                missing.append(tool)
                
        if missing:
            print(f"\n⚠️ FALTAN HERRAMIENTAS DE SISTEMA: {missing}")
            print("   Ejecute: sudo apt install " + " ".join(missing))
        else:
            print("\n✅ Todas las dependencias de sistema están presentes.")
            
        return missing

def main():
    workspace = os.getenv('ECN_WORKSPACE', '~/ECN')
    scanner = DependencyScanner(workspace)
    
    results = scanner.scan_workspace()
    scanner.generate_requirements_files()
    scanner.check_missing_system_deps()
    
    print(f"\n📊 RESUMEN: {len(results['modules'])} módulos escaneados.")
    print(f"   - Python packages: {len(results['python'])}")
    print(f"   - System tools: {len(results['system'])}")

if __name__ == "__main__":
    main()
