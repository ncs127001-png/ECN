#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOS CORE - Gestor de Archivos para Estación Central
Función: Localizar sh_archives y mover archivos automáticamente
Principio: Sin consola, todo desde GUI o comandos simples
"""
import os
import shutil
from pathlib import Path
from datetime import datetime

class SOSFileManager:
    def __init__(self, workspace_root: Path):
        self.root = workspace_root
        self.sh_archives_dir = self.root / "sh_archives"
        self.data_dir = self.root / "data"
        
    def ensure_sh_archives(self) -> Path:
        """Crea sh_archives si no existe"""
        self.sh_archives_dir.mkdir(exist_ok=True)
        return self.sh_archives_dir
    
    def find_sh_archives(self) -> Path:
        """Busca sh_archives en el workspace"""
        # Primero intenta en la raíz
        if self.sh_archives_dir.exists():
            return self.sh_archives_dir
        
        # Busca recursivamente
        for item in self.root.rglob("sh_archives"):
            if item.is_dir():
                return item
        
        # Si no existe, lo crea
        return self.ensure_sh_archives()
    
    def move_files_to_archives(self, file_list: list, description: str = "") -> dict:
        """
        Mueve archivos a sh_archives con organización automática
        
        Args:
            file_list: Lista de rutas de archivos a mover
            description: Descripción opcional del lote
            
        Returns:
            Diccionario con resultados
        """
        archives_dir = self.ensure_sh_archives()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Crear subcarpeta con timestamp
        if description:
            batch_dir = archives_dir / f"{timestamp}_{description.replace(' ', '_')}"
        else:
            batch_dir = archives_dir / f"batch_{timestamp}"
        
        batch_dir.mkdir(exist_ok=True)
        
        results = {
            "moved": [],
            "errors": [],
            "destination": str(batch_dir)
        }
        
        for file_path in file_list:
            src = Path(file_path)
            if not src.exists():
                results["errors"].append(f"{file_path}: No existe")
                continue
            
            try:
                dst = batch_dir / src.name
                shutil.copy2(src, dst)
                results["moved"].append(str(dst))
            except Exception as e:
                results["errors"].append(f"{file_path}: {str(e)}")
        
        return results
    
    def list_archives(self) -> list:
        """Lista todos los archivos en sh_archives"""
        archives_dir = self.find_sh_archives()
        files = []
        
        for root, dirs, filenames in os.walk(archives_dir):
            for filename in filenames:
                files.append({
                    "name": filename,
                    "path": str(Path(root) / filename),
                    "size": os.path.getsize(Path(root) / filename),
                    "modified": datetime.fromtimestamp(
                        os.path.getmtime(Path(root) / filename)
                    ).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return files
    
    def create_manifest(self, output_path: Path = None):
        """Crea un manifiesto JSON de sh_archives"""
        if output_path is None:
            output_path = self.sh_archives_dir / "manifest.json"
        
        manifest = {
            "created": datetime.now().isoformat(),
            "workspace": str(self.root),
            "archives_path": str(self.find_sh_archives()),
            "files": self.list_archives()
        }
        
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        return output_path

if __name__ == "__main__":
    import sys
    
    workspace = Path(__file__).resolve().parent.parent
    manager = SOSFileManager(workspace)
    
    print(" SOS FILE MANAGER")
    print("=" * 50)
    print(f"Workspace: {workspace}")
    print(f"sh_archives: {manager.find_sh_archives()}")
    print()
    
    # Ejemplo de uso: mover los 2 archivos del batch executor
    if len(sys.argv) > 1 and sys.argv[1] == "--move-batch":
        files_to_move = [
            workspace / "core" / "sos_batch_executor.py",
            workspace / "core" / "data" / "batch_executor_report.json"
        ]
        
        print("📦 Moviendo archivos del batch executor...")
        result = manager.move_files_to_archives(files_to_move, "batch_executor")
        
        print(f"✅ Movidos: {len(result['moved'])}")
        for f in result['moved']:
            print(f"   → {f}")
        
        if result['errors']:
            print(f"❌ Errores: {len(result['errors'])}")
            for e in result['errors']:
                print(f"   → {e}")
        
        print(f"\n📂 Destino: {result['destination']}")
    
    # Listar archivos
    elif len(sys.argv) > 1 and sys.argv[1] == "--list":
        files = manager.list_archives()
        print(f"📄 Archivos en sh_archives: {len(files)}")
        for f in files[:10]:  # Mostrar primeros 10
            print(f"   {f['name']} ({f['size']} bytes)")
        if len(files) > 10:
            print(f"   ... y {len(files) - 10} más")
    
    # Crear manifiesto
    else:
        manifest_path = manager.create_manifest()
        print(f"✅ Manifiesto creado: {manifest_path}")
        print()
        print("Usa:")
        print("  python3 core/sos_file_manager.py --move-batch  # Mover batch executor")
        print("  python3 core/sos_file_manager.py --list         # Listar archivos")
