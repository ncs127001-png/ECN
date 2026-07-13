#!/usr/bin/env python3
# coding: utf-8
"""
MOTOR MIGRADOR E INTEGRADOR NEUROBIT
Arquitectura: NEUROBIT_DEV_TEAM
Propósito: Extraer código verificado del entorno masivo V0.2 e integrarlo
           mediante flujos limpios en el nuevo Workspace V0.3.
"""
import os

# Mapeo exacto basado en el reporte de auditoría estructural del backend
MIGRATION_MAP = {
    # Destino en V0.3 : [Posibles rutas de origen en la estructura caótica]
    "WORKSPACE_NEUROBIT_V0.3/core/matrix_13x13.py": [
        "CLASIFICACION_PREDICTIVA/05_MFN_MATRIX_13x13/matrix_13x13.py",
        "core/matrix_13x13.py"
    ],
    "WORKSPACE_NEUROBIT_V0.3/core/neurobit_api.py": [
        "CLASIFICACION_PREDICTIVA/01_PROYECTO_NEUROBIT/neurobit_api.py",
        "neurobit_api.py"
    ],
    "WORKSPACE_NEUROBIT_V0.3/core/websocket_salon_server.py": [
        "core/websocket_salon_server.py"
    ],
    "WORKSPACE_NEUROBIT_V0.3/core/agents_registry.py": [
        "core/agents_registry.py"
    ],
    "WORKSPACE_NEUROBIT_V0.3/modules/centinela_monitor.py": [
        "centinela-compilado/centinela_monitor.py",
        "core/centinela_monitor.py"
    ],
    "WORKSPACE_NEUROBIT_V0.3/modules/captura_tareas_centinela.py": [
        "centinela-compilado/captura_tareas_centinela.py"
    ],
    "WORKSPACE_NEUROBIT_V0.3/modules/vm_bridge_daemon.py": [
        "modules/vm_bridge_daemon.py"
    ],
    "WORKSPACE_NEUROBIT_V0.3/modules/neurobit_hid_daemon.py": [
        "modules/neurobit_hid_daemon/neurobit_hid_daemon.py"
    ],
    "WORKSPACE_NEUROBIT_V0.3/modules/neurobit_postman_daemon.py": [
        "modules/neurobit_postman_daemon.py"
    ],
    "WORKSPACE_NEUROBIT_V0.3/interface/salon.html": [
        "interface/salon.html"
    ],
    "WORKSPACE_NEUROBIT_V0.3/interface/salon.js": [
        "interface/salon.js"
    ]
}

def ejecutar_migracion():
    print("🚀 Iniciando Secuencia de Migración y Consolidación de Código Base")
    print("─" * 80)
    
    archivos_migrados = 0
    
    for destino, origenes in MIGRATION_MAP.items():
        codigo_encontrado = None
        ruta_origen_real = None
        
        # Buscar el archivo en las posibles ubicaciones del entorno caótico
        for origen in origenes:
            if os.path.exists(origen):
                ruta_origen_real = origen
                with open(origen, "r", encoding="utf-8") as f:
                    codigo_encontrado = f.read()
                break  # Encontrado, salir del bucle de búsqueda
        
        if codigo_encontrado:
            # Si el destino no existe, el constructor previo falló o cambió de ruta
            if not os.path.exists(os.path.dirname(destino)):
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                
            # Realizar el append o escritura limpia protegiendo el destino
            print(f"📥 Extrayendo código de: {ruta_origen_real}")
            with open(destino, "a", encoding="utf-8") as f_dest:
                f_dest.write("\n# =========================================================\n")
                f_dest.write(f"# BLOQUE MIGRADO AUTOMÁTICAMENTE DESDE: {ruta_origen_real}\n")
                f_dest.write("# =========================================================\n\n")
                f_dest.write(codigo_encontrado)
                
            print(f"✅ Inyección completada en: {destino}\n")
            archivos_migrados += 1
        else:
            print(f"⚠️ No se encontró el origen para: {destino} (Revisar rutas relativas)\n")
            
    print("─" * 80)
    print(f"🕊️  Fase de Consolidación Terminada. {archivos_migrados} módulos bases integrados.")
    print("Tu estación central v0.3 ha recuperado sus funciones lógicas en localhost.")

if __name__ == "__main__":
    ejecutar_migracion()

