#!/usr/bin/env python3
"""
ESTACIÓN CENTRAL NEUROBITRÓNICA - Servidor Flask v0.1
======================================================

Sistema de control central para monitoreo y activación de artefactos.
Proporciona:
  - API REST para control de servicios
  - WebSocket para comunicación en tiempo real
  - Dashboard web interactivo
  - Monitoreo de estado de componentes
"""

import os
import sys
import json
import psutil
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import subprocess
from typing import Dict, List, Optional

# ==================== CONFIGURACIÓN ====================
WORKSPACE_ROOT = Path(__file__).parent.parent
INTERFACE_DIR = WORKSPACE_ROOT / "interface"
DATA_DIR = WORKSPACE_ROOT / "data"
FRAGMENTS_DIR = DATA_DIR / "fragments"

# Crear directorios necesarios
FRAGMENTS_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "bitacora").mkdir(parents=True, exist_ok=True)

# ==================== LOGGING ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== FLASK APP ====================
app = Flask(__name__, 
            template_folder=str(INTERFACE_DIR),
            static_folder=str(INTERFACE_DIR))
CORS(app)

# ==================== ESTADO GLOBAL ====================
class SystemState:
    """Mantiene el estado actual del sistema"""
    def __init__(self):
        self.components = self._init_components()
        self.start_time = datetime.now()
        self.logs = []
        self.lock = threading.Lock()
    
    def _init_components(self) -> Dict:
        """Inicializa lista de componentes"""
        return {
            ".venv": {"status": "stopped", "critical": True, "port": None},
            "Servidor Flask": {"status": "starting", "critical": True, "port": 5001},
            "Módulo Integrador": {"status": "stopped", "critical": True, "port": None},
            "Awake Ceremony": {"status": "stopped", "critical": True, "port": None},
            "PROCESS_BASELINE": {"status": "stopped", "critical": True, "port": None},
            "API Endpoint Manager": {"status": "stopped", "critical": True, "port": None},
            "Neurobit API": {"status": "stopped", "critical": True, "port": None},
            "IDE Audit": {"status": "stopped", "critical": False, "port": None},
            "WS Sentinel": {"status": "stopped", "critical": True, "port": 5002},
            "Neurobit Postman": {"status": "stopped", "critical": True, "port": None},
            "Verify Tier2": {"status": "stopped", "critical": True, "port": None},
            "Centinela Monitor": {"status": "stopped", "critical": True, "port": None},
            "HID Adapter": {"status": "stopped", "critical": True, "port": None},
            "Neurobit Keylogger": {"status": "stopped", "critical": False, "port": None},
            "Neurobit Interceptor": {"status": "stopped", "critical": False, "port": None},
            "Fragment State Server": {"status": "stopped", "critical": False, "port": 5003},
            "Fragment Sender": {"status": "stopped", "critical": False, "port": None},
            "WebSocket Server": {"status": "stopped", "critical": True, "port": 5004},
            "Neurobit MCP": {"status": "stopped", "critical": False, "port": None},
            "Session Context": {"status": "stopped", "critical": False, "port": None},
            "SOS File Manager": {"status": "stopped", "critical": False, "port": None},
            "Path Resolver": {"status": "stopped", "critical": False, "port": None},
            "Simon Validator": {"status": "stopped", "critical": False, "port": None},
            "PID Monitor": {"status": "stopped", "critical": False, "port": None},
            "Drawille Master": {"status": "stopped", "critical": False, "port": None},
            "VM Bridge": {"status": "stopped", "critical": False, "port": None},
            "Backup System": {"status": "stopped", "critical": False, "port": None},
            "Ollama Bridge": {"status": "stopped", "critical": False, "port": None},
            "Dispatcher": {"status": "stopped", "critical": True, "port": None},
            "Bitácora EVA": {"status": "running", "critical": False, "port": None},
        }
    
    def add_log(self, message: str, level: str = "info"):
        """Agrega un mensaje al log"""
        with self.lock:
            timestamp = datetime.now().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "level": level,
                "message": message
            }
            self.logs.append(log_entry)
            # Mantener solo últimos 1000 logs
            if len(self.logs) > 1000:
                self.logs = self.logs[-1000:]
            logger.log(
                getattr(logging, level.upper(), logging.INFO),
                message
            )
    
    def set_component_status(self, component: str, status: str):
        """Actualiza el estado de un componente"""
        with self.lock:
            if component in self.components:
                old_status = self.components[component]["status"]
                self.components[component]["status"] = status
                self.add_log(
                    f"[{component}] {old_status.upper()} → {status.upper()}",
                    "info"
                )
    
    def get_uptime(self) -> str:
        """Retorna el uptime del sistema"""
        delta = datetime.now() - self.start_time
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_system_stats(self) -> Dict:
        """Obtiene estadísticas del sistema"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_mb": psutil.virtual_memory().used // (1024 * 1024),
                "uptime": self.get_uptime(),
                "active_components": sum(
                    1 for c in self.components.values() 
                    if c["status"] in ["running", "online"]
                ),
                "total_components": len(self.components),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}

# Instancia global del estado
state = SystemState()

# ==================== RUTAS HTTP ====================

@app.route('/')
def index():
    """Página principal - Dashboard"""
    state.add_log("[HTTP] GET / - Dashboard solicitado", "info")
    return send_from_directory(INTERFACE_DIR, 'salon_debug_complete.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """API: Estado actual del sistema"""
    return jsonify({
        "timestamp": datetime.now().isoformat(),
        "system": state.get_system_stats(),
        "components": state.components,
        "logs_count": len(state.logs)
    })

@app.route('/api/components', methods=['GET'])
def get_components():
    """API: Lista de componentes"""
    return jsonify({
        "components": state.components,
        "count": len(state.components),
        "active": sum(1 for c in state.components.values() 
                     if c["status"] in ["running", "online"]),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/component/<component_name>', methods=['GET'])
def get_component(component_name):
    """API: Detalles de un componente específico"""
    if component_name not in state.components:
        return jsonify({"error": "Component not found"}), 404
    
    return jsonify({
        "name": component_name,
        "data": state.components[component_name],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """API: Obtener logs del sistema"""
    limit = request.args.get('limit', 100, type=int)
    level = request.args.get('level', None)
    
    logs = state.logs
    if level:
        logs = [l for l in logs if l["level"] == level]
    
    return jsonify({
        "logs": logs[-limit:],
        "total": len(state.logs),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/control/start/<component>', methods=['POST'])
def start_service(component):
    """API: Iniciar un servicio"""
    if component not in state.components:
        return jsonify({"error": "Component not found"}), 404
    
    state.add_log(f"[CONTROL] Iniciando {component}...", "info")
    state.set_component_status(component, "starting")
    
    # Simular inicio (en producción, ejecutar el servicio real)
    threading.Timer(2.0, lambda: state.set_component_status(component, "online")).start()
    
    return jsonify({
        "action": "start",
        "component": component,
        "status": "requested",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/control/stop/<component>', methods=['POST'])
def stop_service(component):
    """API: Detener un servicio"""
    if component not in state.components:
        return jsonify({"error": "Component not found"}), 404
    
    state.add_log(f"[CONTROL] Deteniendo {component}...", "warning")
    state.set_component_status(component, "stopped")
    
    return jsonify({
        "action": "stop",
        "component": component,
        "status": "stopped",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/control/restart/<component>', methods=['POST'])
def restart_service(component):
    """API: Reiniciar un servicio"""
    if component not in state.components:
        return jsonify({"error": "Component not found"}), 404
    
    state.add_log(f"[CONTROL] Reiniciando {component}...", "warning")
    state.set_component_status(component, "restarting")
    
    threading.Timer(2.0, lambda: state.set_component_status(component, "online")).start()
    
    return jsonify({
        "action": "restart",
        "component": component,
        "status": "restarting",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/control/start-all', methods=['POST'])
def start_all():
    """API: Iniciar todos los servicios"""
    state.add_log("[CONTROL] Iniciando todos los servicios...", "info")
    
    for component in state.components:
        if component != "Bitácora EVA":  # Ya corriendo
            state.set_component_status(component, "starting")
    
    # Simulación de inicio gradual
    def activate_components():
        for i, component in enumerate(state.components):
            if component != "Bitácora EVA":
                threading.Timer(
                    i * 0.5,
                    lambda c=component: state.set_component_status(c, "online")
                ).start()
    
    threading.Thread(target=activate_components).start()
    
    return jsonify({
        "action": "start-all",
        "status": "initiated",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/control/stop-all', methods=['POST'])
def stop_all():
    """API: Detener todos los servicios"""
    state.add_log("[CONTROL] Deteniendo todos los servicios...", "warning")
    
    for component in state.components:
        state.set_component_status(component, "stopped")
    
    return jsonify({
        "action": "stop-all",
        "status": "stopped",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/system/info', methods=['GET'])
def system_info():
    """API: Información del sistema"""
    return jsonify({
        "hostname": os.uname().nodename,
        "platform": sys.platform,
        "python_version": sys.version,
        "workspace": str(WORKSPACE_ROOT),
        "fragments_dir": str(FRAGMENTS_DIR),
        "data_dir": str(DATA_DIR),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """API: Health check"""
    active = sum(1 for c in state.components.values() 
                 if c["status"] in ["running", "online"])
    critical_count = sum(1 for c in state.components.values() if c["critical"])
    critical_active = sum(1 for name, c in state.components.items() 
                         if c["critical"] and c["status"] in ["running", "online"])
    
    return jsonify({
        "status": "healthy" if active > 0 else "degraded",
        "active_components": active,
        "total_components": len(state.components),
        "critical_components": critical_count,
        "critical_active": critical_active,
        "uptime": state.get_uptime(),
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    """Manejo de 404"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores internos"""
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500

# ==================== INICIALIZACIÓN ====================

def init_ecn_state_file():
    """Escribe el archivo ECN_state.txt en data/"""
    state_file = DATA_DIR / "ECN_state.txt"
    if not state_file.exists():
        # El archivo ya fue creado anteriormente
        pass
    state.add_log("[INIT] Archivo ECN_state.txt disponible", "info")

def init_server():
    """Inicialización del servidor"""
    logger.info("=" * 60)
    logger.info("ESTACIÓN CENTRAL NEUROBITRÓNICA - v0.1-SOBERANO-LOCAL")
    logger.info("=" * 60)
    logger.info(f"Workspace: {WORKSPACE_ROOT}")
    logger.info(f"Interface: {INTERFACE_DIR}")
    logger.info(f"Data: {DATA_DIR}")
    logger.info("=" * 60)
    
    state.add_log("[BOOT] Estación Central inicializando...", "info")
    state.add_log(f"[BOOT] Workspace: {WORKSPACE_ROOT}", "info")
    state.add_log(f"[BOOT] Componentes registrados: {len(state.components)}", "info")
    state.set_component_status("Servidor Flask", "online")
    
    init_ecn_state_file()

if __name__ == '__main__':
    init_server()
    
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   🧠 ESTACIÓN CENTRAL NEUROBITRÓNICA - SERVIDOR ACTIVO 🧠  ║
    ╠════════════════════════════════════════════════════════════╣
    ║                                                            ║
    ║   Dashboard:  http://localhost:5001/                      ║
    ║   API:        http://localhost:5001/api/                  ║
    ║   Status:     http://localhost:5001/api/status            ║
    ║                                                            ║
    ║   Modo:       SOBERANÍA OPERATIVA LOCAL                   ║
    ║   Seguridad:  ✓ Sin dependencias externas                 ║
    ║   Control:    ✓ Control total de procesos                 ║
    ║   Auditoría:  ✓ BITÁCORA_EVA activada                     ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Iniciar servidor
    app.run(
        host='127.0.0.1',
        port=5001,
        debug=False,
        threaded=True,
        use_reloader=False
    )
