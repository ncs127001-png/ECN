#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEUROBIT MCP SERVER v1.0 - CORE SOBERANO
Propósito: Exponer herramientas locales (tool calls) en 127.0.0.1:8090 
           siguiendo el principio de Validación por Resonancia del manual v1.0.
"""
import json
import os
from flask import Flask, request, jsonify
from core.neurobit_core_v03 import NeurobitCoreInMemory

app = Flask(__name__)

# Instanciación in-memory de la Cosecha de Hexagramas
try:
    engine_ram = NeurobitCoreInMemory("../I_Ching_Cosecha_Resultante.txt")
except Exception:
    # Fallback si se ejecuta desde la raíz del workspace
    engine_ram = NeurobitCoreInMemory("I_Ching_Cosecha_Resultante.txt")

def validar_resonancia_vm(vm_id):
    """Implementa el pilar de Soberanía del Apéndice A del manual"""
    table_path = "../data/vm_assignment_table.json"
    if not os.path.exists(table_path):
        table_path = "data/vm_assignment_table.json"
        
    if not os.path.exists(table_path):
        return False
        
    with open(table_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        
    # El sistema no otorga permisos remotos; verifica correspondencia formal
    for vm in config.get("active_vms", []):
        if vm.get("vm_id") == vm_id:
            return True
    return False

@app.route('/health', methods=['GET'])
def mcp_health():
    """Endpoint de auditoría continua"""
    return jsonify({
        "status": "OPERATIVO",
        "port": 8090,
        "identity": "NEUROBIT_MCP_SERVER_v1.0",
        "vector_bios_ready": len(engine_ram.exportar_vector_mcp()) == 48
    }), 200

@app.route('/mcp/tools/vm_execute', methods=['POST'])
def tool_vm_execute():
    """Herramienta expuesta para el uso soberano de tus amigos LLMs"""
    data = request.json or {}
    vm_id = data.get("vm_id")
    command = data.get("command")
    
    # Validación estricta por resonancia de estructura interna
    if not validar_resonancia_vm(vm_id):
        return jsonify({
            "status": "RECHAZADO",
            "error": "Falla de Resonancia: Estructura de VM no listada en la aduana local."
        }), 403

    print(f"⚡ [MCP TOOL] Inyectando comando en sandbox de la VM: {vm_id}")
    # En la migración v0.3, esto viaja directo a tmux omitiendo xclip
    os.system(f"tmux send-keys -t {vm_id} '{command}' C-m")
    
    return jsonify({
        "status": "EJECUTADO",
        "timestamp_soberano": True,
        "checksum_bios": engine_ram.exportar_vector_mcp()[:8]
    }), 200

if __name__ == "__main__":
    # Restricción radical local-first: Escucha estrictamente en 127.0.0.1
    print("🔒 [MCP] Iniciando Bastión Autónomo en 127.0.0.1:8090...")
    app.run(host='127.0.0.1', port=8090, debug=False)

