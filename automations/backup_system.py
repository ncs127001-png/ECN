#!/usr/bin/env python3
"""
Sistema de respaldo para NEUROBIT
Crea copias de seguridad incrementales de la memoria y configuración
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BACKUP_DIR = PROJECT_ROOT / "backups"
CONFIG_DIR = PROJECT_ROOT / "config"

def create_backup():
    """Crear una copia de seguridad del sistema"""
    # Crear directorio de backups si no existe
    BACKUP_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"neurobit_backup_{timestamp}"
    backup_path.mkdir()
    
    print(f"📦 Creando respaldo en: {backup_path}")
    
    # Copiar memoria
    memoria_src = DATA_DIR / "memoria_eva.jsonl"
    if memoria_src.exists():
        shutil.copy2(memoria_src, backup_path / "memoria_eva.jsonl")
        print(f"✅ Memoria respaldada ({os.path.getsize(memoria_src)} bytes)")
    else:
        print("⚠️  Memoria no encontrada, continuando...")
    
    # Copiar configuración
    config_src = CONFIG_DIR / "neurobit_config.json"
    if config_src.exists():
        shutil.copy2(config_src, backup_path / "neurobit_config.json")
        print(f"✅ Configuración respaldada")
    else:
        print("⚠️  Configuración no encontrada")
    
    # Crear metadatos del respaldo
    metadata = {
        "backup_time": datetime.now().isoformat(),
        "source_paths": {
            "memoria": str(memoria_src),
            "config": str(config_src)
        },
        "backup_version": "1.0"
    }
    
    with open(backup_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Respaldo completado exitosamente")
    return backup_path

def list_backups():
    """Listar todos los respaldos disponibles"""
    if not BACKUP_DIR.exists():
        print("🔍 No se encontraron respaldos")
        return []
    
    backups = sorted(
        [d for d in BACKUP_DIR.iterdir() if d.is_dir()],
        key=lambda x: x.name,
        reverse=True
    )
    
    if not backups:
        print("🔍 No se encontraron respaldos")
        return []
    
    print(f"\n📋 Respaldo(s) disponibles ({len(backups)}):")
    for i, backup in enumerate(backups, 1):
        meta_path = backup / "metadata.json"
        timestamp = "Desconocido"
        size = 0
        
        if meta_path.exists():
            try:
                with open(meta_path, "r") as f:
                    meta = json.load(f)
                    timestamp = meta.get("backup_time", timestamp)
            except:
                pass
        
        memoria_path = backup / "memoria_eva.jsonl"
        if memoria_path.exists():
            size = os.path.getsize(memoria_path)
        
        print(f"{i}. {backup.name} | {timestamp.split('T')[0]} | {size//1024}KB")
    
    return backups

def restore_backup(backup_index=None):
    """Restaurar un respaldo específico"""
    backups = list_backups()
    if not backups:
        return
    
    if backup_index is None:
        try:
            backup_index = int(input("\nSelecciona número de respaldo a restaurar: ")) - 1
        except ValueError:
            print("❌ Entrada inválida")
            return
    
    if backup_index < 0 or backup_index >= len(backups):
        print("❌ Índice de respaldo inválido")
        return
    
    backup_path = backups[backup_index]
    print(f"\n🔄 Restaurando desde: {backup_path.name}")
    
    # Confirmación
    confirm = input("⚠️  ESTA ACCIÓN SOBREESCRIBIRÁ DATOS ACTUALES. ¿Continuar? (s/n): ")
    if confirm.lower() != 's':
        print("🚫 Restauración cancelada")
        return
    
    # Restaurar memoria
    memoria_backup = backup_path / "memoria_eva.jsonl"
    if memoria_backup.exists():
        shutil.copy2(memoria_backup, DATA_DIR / "memoria_eva.jsonl")
        print("✅ Memoria restaurada")
    
    # Restaurar configuración
    config_backup = backup_path / "neurobit_config.json"
    if config_backup.exists():
        shutil.copy2(config_backup, CONFIG_DIR / "neurobit_config.json")
        print("✅ Configuración restaurada")
    
    print("🎉 Restauración completada exitosamente")
    print("💡 Reinicia la extensión para que los cambios surtan efecto")

def main():
    """Función principal"""
    print("🧠 NEUROBIT - Sistema de Respaldo")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "create" or command == "backup":
            create_backup()
        elif command == "list" or command == "ls":
            list_backups()
        elif command == "restore":
            index = int(sys.argv[2]) - 1 if len(sys.argv) > 2 else None
            restore_backup(index)
        else:
            print(f"❌ Comando desconocido: {command}")
            print("Uso: backup_system.py [create|list|restore]")
    else:
        print("Uso: backup_system.py [create|list|restore]")
        print("Ejemplos:")
        print("  python3 backup_system.py create")
        print("  python3 backup_system.py list")
        print("  python3 backup_system.py restore 1")

if __name__ == "__main__":
    main()