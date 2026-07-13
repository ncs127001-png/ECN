#!/usr/bin/env python3
"""
MFN File Manager - CLI para mover archivos con auto-actualización
"""
import sys
from pathlib import Path
from core.mfn_file_registry import MFNFileRegistry

def main():
    workspace = Path(__file__).resolve().parent.parent
    registry = MFNFileRegistry(workspace)
    
    if len(sys.argv) < 2:
        print("Uso: python3 mfn_file_manager.py <comando> [args]")
        print("Comandos:")
        print("  scan              - Escanear y mostrar índice MFN")
        print("  move <archivo> <nueva_ubicación> - Mover archivo")
        print("  regenerate        - Regenerar path_map.json")
        return
    
    comando = sys.argv[1]
    
    if comando == "scan":
        index = registry.scan_and_index()
        print(f"\n📋 ÍNDICE MFN ({len(index)} archivos):")
        for path, meta in sorted(index.items(), key=lambda x: x[1]['level']):
            print(f"  Nivel {meta['level']}: {meta['location']} → {Path(path).name}")
    
    elif comando == "move":
        if len(sys.argv) < 4:
            print("❌ Uso: move <archivo.py> <nueva_carpeta>")
            return
        
        src = workspace / sys.argv[2]
        new_loc = sys.argv[3]
        
        if not src.exists():
            print(f"❌ Archivo no encontrado: {src}")
            return
        
        print(f"🔄 Moviendo {src.name} → {new_loc}/")
        dest = registry.move_file(src, new_loc)
        print(f"✅ Movido a: {dest}")
    
    elif comando == "regenerate":
        from tools.generate_path_map import generate_map
        print("🔄 Regenerando path_map.json...")
        generate_map(workspace, workspace / "path_map.json")
        print("✅ path_map.json regenerado")

if __name__ == "__main__":
    main()
