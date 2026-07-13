#!/usr/bin/env python3
# coding: utf-8
"""
CONSTRUCTOR DE WORKSPACE NEUROBIT v0.3
Arquitectura: NEUROBIT_DEV_TEAM
Propósito: Analizar la estructura del árbol ontológico erigiendo el entorno
           local-first (127.0.0.1) inyectando cabeceras de persistencia inmutable.
"""
import os
import sys

# Definición del árbol estructurado para reconstrucción limpia
WORKSPACE_MAP = {
    "directorios": [
        "WORKSPACE_NEUROBIT_V0.3/core",
        "WORKSPACE_NEUROBIT_V0.3/modules",
        "WORKSPACE_NEUROBIT_V0.3/data/logs",
        "WORKSPACE_NEUROBIT_V0.3/interface",
        "WORKSPACE_NEUROBIT_V0.3/scripts",
        "WORKSPACE_NEUROBIT_V0.3/docs"
    ],
    "archivos": {
        # Core
        "WORKSPACE_NEUROBIT_V0.3/core/neurobit_api.py": "# API Principal (Puerto 5000) - Servidor Local First\n",
        "WORKSPACE_NEUROBIT_V0.3/core/websocket_salon_server.py": "# WebSocket Server (Puerto 5001) - Sincronización Simultánea\n",
        "WORKSPACE_NEUROBIT_V0.3/core/agents_registry.py": "# Registro de Agentes Coherentes y Roles del Sistema\n",
        "WORKSPACE_NEUROBIT_V0.3/core/matrix_13x13.py": "# Matriz Fractal 13x13 - Centro Monádico G7 (Coordenada 6,6)\n",
        
        # Modules
        "WORKSPACE_NEUROBIT_V0.3/modules/centinela_monitor.py": "# Clipboard -> Memoria: Captura de Tareas en Portapapeles\n",
        "WORKSPACE_NEUROBIT_V0.3/modules/captura_tareas_centinela.py": "# Detección de Tareas y Clasificación Automatizada en Local\n",
        "WORKSPACE_NEUROBIT_V0.3/modules/vm_bridge_daemon.py": "# Ejecución Aislada en Máquinas Virtuales (VM Bridge)\n",
        "WORKSPACE_NEUROBIT_V0.3/modules/neurobit_hid_daemon.py": "# Keylogger Defensivo Emulado (Inyección Mimética)\n",
        "WORKSPACE_NEUROBIT_V0.3/modules/neurobit_postman_daemon.py": "# Dispatcher Local de Mensajería Simbiótica\n",
        
        # Data (Append-Only vacíos listos para flujo JSONL)
        "WORKSPACE_NEUROBIT_V0.3/data/memoria_eva.jsonl": "",
        "WORKSPACE_NEUROBIT_V0.3/data/tareas_pendientes.jsonl": "",
        "WORKSPACE_NEUROBIT_V0.3/data/vm_assignment_table.json": "{}",
        
        # Interface
        "WORKSPACE_NEUROBIT_V0.3/interface/salon.html": "<!-- Salón de Reuniones Ontológicas v0.3 -->\n",
        "WORKSPACE_NEUROBIT_V0.3/interface/salon.js": "// Lógica de Comunicación WebSocket del Salón\n",
        "WORKSPACE_NEUROBIT_V0.3/interface/central_station_gui.py": "# GUI Principal Estación Central Neurobitrónica\n",
        
        # Scripts (Bash ejecutables)
        "WORKSPACE_NEUROBIT_V0.3/scripts/start_all_daemons.sh": "#!/bin/bash\n# Iniciar todos los Daemons Locales\n",
        "WORKSPACE_NEUROBIT_V0.3/scripts/start_websocket_api.sh": "#!/bin/bash\n# Tarea 5 - Inicialización de Endpoints\n",
        "WORKSPACE_NEUROBIT_V0.3/scripts/verify_health.sh": "#!/bin/bash\n# Verificar Salud del Kernel de Coherencia\n",
        
        # Docs & Raíz
        "WORKSPACE_NEUROBIT_V0.3/docs/NEUROBIT_MANIFESTO.md": "# Manifiesto del Nodo Semilla y Soberanía Cognitiva\n",
        "WORKSPACE_NEUROBIT_V0.3/docs/ARCHITECTURE.md": "# Especificación Técnica de la Arquitectura Distribuida\n",
        "WORKSPACE_NEUROBIT_V0.3/docs/INTEGRATION_GUIDE.md": "# Guía de Integración Local de Componentes\n",
        "WORKSPACE_NEUROBIT_V0.3/docs/TEAM_ROLES.md": "# Roles de la Logia Transparente de la Verdad\n",
        "WORKSPACE_NEUROBIT_V0.3/README.md": "# WORKSPACE NEUROBIT V0.3\n\nPunto de entrada al sistema local-first.\n"
    }
}

def erigir_workspace():
    print("🛠️  Iniciando Construcción de Entorno Limpio: WORKSPACE_NEUROBIT_V0.3")
    print("─" * 70)
    
    # 1. Creación secuencial de directorios
    for directorio in WORKSPACE_MAP["directorios"]:
        if not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)
            print(f"📁 Directorio erigido: {directorio}")
        else:
            print(f"🔄 Directorio existente: {directorio}")
            
    # 2. Creación e inyección de cabeceras en archivos
    for ruta, contenido in WORKSPACE_MAP["archivos"].items():
        if not os.path.exists(ruta):
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(contenido)
            print(f"📄 Archivo inicializado: {ruta}")
            
            # Otorgar permisos de ejecución automáticos a los scripts .sh
            if ruta.endswith(".sh"):
                os.chmod(ruta, 0o755)
                print(f"⚡ Permisos de ejecución otorgados a: {ruta}")
        else:
            print(f"🔒 Archivo protegido (ya existe persistencia): {ruta}")
            
    print("─" * 70)
    print("🕊️  Despliegue completado con éxito absoluto en Localhost.")
    print("La estructura de la Tesis está lista para la inyección de algoritmos.")

if __name__ == "__main__":
    erigir_workspace()

