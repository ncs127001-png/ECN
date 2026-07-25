#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core/bootstrap.py
Ritual de sincronización previa al despertar de la API.
Garantiza que el path_map.json refleje la realidad del workspace actual.
"""
import os
import sys
from pathlib import Path

# Asegurar que la raíz del workspace esté en el PATH
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

def sincronizar_rutas():
    """Fuerza la regeneración del mapa de rutas para evitar desincronización."""
    print("🔄 [BOOTSTRAP] Sincronizando mapa de rutas dinámico...")
    try:
        from tools.generate_path_map import generate_map
        map_file = WORKSPACE_ROOT / "data" / "path_map.json"
        # Asegurar que el directorio data exista
        map_file.parent.mkdir(parents=True, exist_ok=True)
        generate_map(WORKSPACE_ROOT, map_file)
        print("✅ [BOOTSTRAP] Mapa de rutas actualizado y cargado en memoria.")
        return True
    except Exception as e:
        print(f"❌ [BOOTSTRAP] Error al generar mapa de rutas: {e}")
        return False

def iniciar_api():
    """Lanza la API central una vez que las rutas están garantizadas."""
    print("🚀 [BOOTSTRAP] Iniciando Neurobit API...")
    try:
        # Importamos directamente el app o la función de arranque
        from core.neurobit_api import app, init_server
        init_server()
        
        # Obtener puertos de variables de entorno (inyectadas por start_ecn.sh)
        host = os.environ.get("NEUROBIT_HOST", "127.0.0.1")
        port = int(os.environ.get("API_PORT", 5000))
        
        print(f"📡 [BOOTSTRAP] Servidor escuchando en {host}:{port}")
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ [BOOTSTRAP] Fallo crítico al iniciar API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("═" * 60)
    print("🧠 ECN v0.2 - FASE DE SINCRONIZACIÓN DE RUTAS")
    print("═" * 60)
    
    if sincronizar_rutas():
        iniciar_api()
    else:
        sys.exit(1)