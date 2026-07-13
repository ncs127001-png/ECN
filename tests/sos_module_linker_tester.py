#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOS CORE - Módulo de Auditoría y Vinculación Estática (Fase 1)
Función: Analizar imports, sintaxis y vinculación real con neurobit_api.py.
Principio: Observación no destructiva. Sin dependencias externas.
"""
import ast
import os
import sys
import json
import py_compile
from pathlib import Path

class SOSModuleLinkerTester:
    def __init__(self, workspace_root: Path):
        # Principio SINCERO: La raíz es el punto 1,1 de nuestro universo de archivos
        self.root = workspace_root
        self.api_file = self.root / "neurobit_api.py"
        
        # Estructura del reporte (Base para la GUI)
        self.report = {
            "api_imports": [],
            "modules_status": [],
            "orphans": [],
            "syntax_errors": []
        }

    def extract_api_imports(self):
        """Extrae los módulos que neurobit_api.py realmente necesita."""
        if not self.api_file.exists():
            print(f"❌ Error: No se encuentra {self.api_file}")
            return
        
        with open(self.api_file, 'r', encoding='utf-8') as f:
            try:
                tree = ast.parse(f.read(), filename=self.api_file.name)
            except SyntaxError as e:
                print(f"❌ Error de sintaxis en la API principal: {e}")
                return

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.report["api_imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self.report["api_imports"].append(node.module)
        
        print(f"✅ Extraídos {len(self.report['api_imports'])} imports de la API.")

    def check_syntax(self, py_file: Path):
        """Valida la sintaxis sin ejecutar el código."""
        try:
            py_compile.compile(str(py_file), doraise=True)
            return True
        except py_compile.PyCompileError as e:
            self.report["syntax_errors"].append({
                "file": str(py_file.relative_to(self.root)), 
                "error": str(e)
            })
            return False

    def scan_modules(self):
        """Recorre core/, modules/ y tools/ para cruzar datos."""
        dirs_to_scan = ["core", "modules", "tools"]
        api_imports_set = set(self.report["api_imports"])

        for d in dirs_to_scan:
            dir_path = self.root / d
            if not dir_path.exists(): 
                continue
                
            for py_file in dir_path.rglob("*.py"):
                # Ignorar entornos virtuales y caché
                if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                    continue

                rel_path = py_file.relative_to(self.root)
                # Convertir ruta a notación de módulo (ej: core/coherence_filter -> core.coherence_filter)
                module_name = str(rel_path.with_suffix('')).replace(os.sep, '.')

                # Verificar si la API lo importa (coincidencia parcial o total)
                is_linked = any(
                    module_name in imp or imp in module_name 
                    for imp in api_imports_set
                )
                
                syntax_ok = self.check_syntax(py_file)

                self.report["modules_status"].append({
                    "module": module_name,
                    "linked_to_api": is_linked,
                    "syntax_ok": syntax_ok,
                    "path": str(rel_path)
                })

                # Si no está linkeado y no tiene errores, es un módulo huérfano (candidato a integrar)
                if not is_linked and syntax_ok:
                    self.report["orphans"].append(module_name)

    def generate_report(self, output_path: Path):
        """Genera el JSON que alimentará al Gestor GUI."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        return output_path

if __name__ == "__main__":
    # Ajustar la ruta raíz según dónde se coloque este script
    # Si está en la raíz del workspace:
    ROOT_PATH = Path(__file__).resolve().parent 
    
    # Si está dentro de tools/ o SOS/, descomentar la siguiente línea:
    # ROOT_PATH = Path(__file__).resolve().parent.parent 

    tester = SOSModuleLinkerTester(ROOT_PATH)
    
    print("🔍 Iniciando Auditoría Estática SOS...")
    tester.extract_api_imports()
    tester.scan_modules()
    
    out_file = tester.generate_report(ROOT_PATH / "data" / "sos_linker_report.json")
    
    print(f"\n📊 Resumen:")
    print(f"   - Módulos escaneados: {len(tester.report['modules_status'])}")
    print(f"   - Errores de sintaxis: {len(tester.report['syntax_errors'])}")
    print(f"   - Módulos huérfanos (no linkeados): {len(tester.report['orphans'])}")
    print(f"\n✅ Reporte JSON generado en: {out_file}")
}<<'codigo'>

### Cómo opera este módulo en la arquitectura SOS:

1. **Lectura Ast (Abstract Syntax Tree):** No usa `grep` ni expresiones regulares frágiles. Lee el código exactamente como lo hace el intérprete de Python, identificando `import X` y `from Y import Z`.
2. **Validación de Sintaxis Pura:** Usa `py_compile` para detectar errores de tipeo (como el `fragto_actual` que mencionaste antes) sin riesgo de ejecutar código malicioso o con efectos secundarios.
3. **Generación de Mapa de Calor:** El JSON resultante (`sos_linker_report.json`) tendrá la estructura exacta para que tu `gestor_gui.py` lo lea y pinte la **Columna 1** (Módulos encontrados) y marque en rojo los que tienen `syntax_ok: false` o en amarillo los que tienen `linked_to_api: false`.

### Próximo paso (Fase 2):
Una vez que ejecutes este script y confirmes que el JSON se genera correctamente, el siguiente paso es modificar ligeramente tu `gestor_gui.py` para que, al abrir un archivo, no solo busque typos con la regex, sino que primero cargue este reporte base.

¿Ejecutas el script y me confirmas si el JSON refleja correctamente la realidad de tu workspace actual?

HOOK
