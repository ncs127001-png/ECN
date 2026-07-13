#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOS CORE - Corrector de Rutas para Scripts .sh
Función: Reemplaza rutas hardcodeadas usando path_map.json
Principio: Observación no destructiva. Backup automático antes de modificar.
"""
import json
import re
import shutil
from pathlib import Path
from datetime import datetime

class SOSPathFixer:
    def __init__(self, workspace_root: Path):
        self.root = workspace_root
        self.map_file = self.root / "path_map.json"
        self.path_map = self._load_map()
        
        # Patrones de rutas hardcodeadas comunes
        self.workspace_patterns = [
            r'~/WORKSPACE_NEUROBIT_V0\.2(/[^"\']\s*)',
            r'/home/[^/]+/WORKSPACE_NEUROBIT_V0\.2(/[^"\']\s*)',
            r'\$HOME/WORKSPACE_NEUROBIT_V0\.2(/[^"\']\s*)',
            r'~/WORKSPACE_NEUROBIT_V0\.3(/[^"\']\s*)',
            r'/home/[^/]+/WORKSPACE_NEUROBIT_V0\.3(/[^"\']\s*)',
        ]
    
    def _load_map(self) -> dict:
        """Carga el mapa de paths generado por generate_path_map.py"""
        if self.map_file.exists():
            with open(self.map_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        print(f"⚠️ {self.map_file} no encontrado. Ejecuta primero generate_path_map.py")
        return {}
    
    def backup_script(self, script_path: Path) -> Path:
        """Crea backup con timestamp antes de modificar"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = script_path.with_suffix(f'.backup_{timestamp}.sh')
        shutil.copy2(script_path, backup_path)
        return backup_path
    
    def find_best_match(self, relative_path: str) -> str:
        """Busca la mejor coincidencia en el mapa de paths"""
        # Limpiar la ruta relativa
        clean_path = relative_path.strip().strip('"').strip("'")
        
        # Buscar coincidencia exacta
        if clean_path in self.path_map:
            return self.path_map[clean_path]
        
        # Buscar por nombre de archivo
        filename = clean_path.split('/')[-1]
        if filename in self.path_map:
            return self.path_map[filename]
        
        # Buscar coincidencia parcial
        for key, value in self.path_map.items():
            if clean_path in key or key in clean_path:
                return value
        
        return None
    
    def fix_script(self, script_path: Path, dry_run=True) -> dict:
        """
        Corrige rutas en un script .sh
        
        Args:
            script_path: Ruta al script
            dry_run: Si True, solo muestra cambios sin aplicar
        
        Returns:
            Diccionario con estadísticas de cambios
        """
        if not script_path.exists():
            return {"error": f"Script no encontrado: {script_path}"}
        
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = []
        stats = {
            "file": str(script_path),
            "changes": [],
            "backup": None,
            "applied": False
        }
        
        # Buscar y reemplazar rutas hardcodeadas
        for pattern in self.workspace_patterns:
            matches = list(re.finditer(pattern, content))
            for match in matches:
                old_path = match.group(0)
                relative_part = match.group(1)
                
                # Buscar en el mapa
                new_path = self.find_best_match(relative_part)
                
                if new_path:
                    # Preservar comillas si las había
                    if old_path.startswith('"') or old_path.startswith("'"):
                        replacement = f'"{new_path}"'
                    else:
                        replacement = new_path
                    
                    changes.append({
                        "old": old_path,
                        "new": replacement,
                        "line": content[:match.start()].count('\n') + 1
                    })
                    
                    content = content.replace(old_path, replacement, 1)
        
        # Verificar si hubo cambios
        if changes:
            stats["changes"] = changes
            
            if not dry_run:
                # Crear backup
                backup_path = self.backup_script(script_path)
                stats["backup"] = str(backup_path)
                
                # Aplicar cambios
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                stats["applied"] = True
        
        return stats
    
    def fix_all_scripts(self, scripts_dir: Path, dry_run=True) -> list:
        """Corrige todos los scripts .sh en un directorio"""
        results = []
        
        for script_path in scripts_dir.glob("*.sh"):
            stats = self.fix_script(script_path, dry_run=dry_run)
            results.append(stats)
        
        return results
    
    def generate_report(self, results: list, output_path: Path):
        """Genera reporte JSON de los cambios"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_scripts": len(results),
            "scripts_with_changes": sum(1 for r in results if r.get("changes")),
            "total_changes": sum(len(r.get("changes", [])) for r in results),
            "details": results
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return output_path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Corregir rutas en scripts .sh usando path_map.json")
    parser.add_argument("script", nargs='?', help="Ruta al script .sh (o directorio con --all)")
    parser.add_argument("--all", action="store_true", help="Corregir todos los scripts en el directorio")
    parser.add_argument("--apply", action="store_true", help="Aplicar cambios (por defecto es dry-run)")
    parser.add_argument("--output", default="data/sos_path_fixer_report.json", help="Ruta del reporte JSON")
    args = parser.parse_args()
    
    # Determinar raíz del workspace
    workspace = Path(__file__).resolve().parent.parent
    
    fixer = SOSPathFixer(workspace)
    
    if not fixer.path_map:
        print("❌ No se pudo cargar path_map.json")
        print("   Ejecuta primero: python3 tools/generate_path_map.py")
        exit(1)
    
    print(f"\n SOS PATH FIXER - Corrector de Rutas")
    print("=" * 50)
    print(f"Mapa cargado: {len(fixer.path_map)} archivos indexados")
    print(f"Modo: {'APLICAR' if args.apply else 'DRY-RUN (preview)'}")
    print()
    
    if args.all:
        # Corregir todos los scripts en el directorio actual
        scripts_dir = Path.cwd()
        results = fixer.fix_all_scripts(scripts_dir, dry_run=not args.apply)
    elif args.script:
        # Corregir un script específico
        script_path = Path(args.script)
        results = [fixer.fix_script(script_path, dry_run=not args.apply)]
    else:
        print("❌ Debes especificar un script o usar --all")
        parser.print_help()
        exit(1)
    
    # Mostrar resultados
    for result in results:
        if "error" in result:
            print(f"❌ {result['error']}")
            continue
        
        if result.get("changes"):
            print(f"\n📝 {Path(result['file']).name}:")
            for change in result["changes"]:
                print(f"   Línea {change['line']}:")
                print(f"      - {change['old']}")
                print(f"      + {change['new']}")
            
            if result.get("applied"):
                print(f"   ✅ Cambios aplicados. Backup: {result['backup']}")
            else:
                print(f"   ⚠️  Usa --apply para aplicar estos cambios")
        else:
            print(f"✅ {Path(result['file']).name}: Sin rutas hardcodeadas")
    
    # Generar reporte
    report_path = fixer.generate_report(results, workspace / args.output)
    print(f"\n📊 Reporte generado: {report_path}")
    
    if not args.apply and any(r.get("changes") for r in results):
        print(f"\n💡 Para aplicar los cambios, ejecuta:")
        print(f"   python3 {Path(__file__).name} {' '.join(sys.argv[1:])} --apply")
