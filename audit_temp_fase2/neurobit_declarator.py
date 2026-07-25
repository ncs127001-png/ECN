#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEUROBIT DECLARATOR v0.3 - BETA
Propósito: Leer el mapa nemotécnico YAML nativamente, auditar la correspondencia
           con el eje G-7 (7,7) y generar los módulos inyectando la firma de co-herencia.
"""
import os
import sys
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class NeurobitDeclarator:
    def __init__(self, yaml_path="data/declaraciones_base.yaml"):
        self.yaml_path = yaml_path
        self.declaraciones = {}
        self.pivote_g7 = (7, 7)  # Centro absoluto indexado en Base 1 (Principio SINCERO)
        self.cargar_receta_nativa()

    def cargar_receta_nativa(self):
        """Parser nativo por expresiones regulares para evitar dependencias externas."""
        if not os.path.exists(self.yaml_path):
            # Fallback de inicialización segura e in-memory para el Atanor
            self.declaraciones = {
                "BASTION_MCP": {"meridiano": "mu", "col": 7, "row": 7, "gate": "GATE_EAND", "path": "mcp_server/neurobit_mcp_server.py"},
                "OPTO_GALVANICO": {"meridiano": "alpha", "col": 1, "row": 7, "gate": "GATE_NAND", "path": "core/neurobit_pic_com.py"},
                "MIMESIS_HID": {"meridiano": "alpha", "col": 2, "row": 7, "gate": "GATE_XOR", "path": "daemons/neurobit_hid_daemon.py"}
            }
            return

        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            current_mod = None
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): 
                    continue
                if line.endswith(":"):
                    current_mod = line[:-1].strip()
                    if current_mod not in ["estacion_central", "modulos_heredados"]:
                        self.declaraciones[current_mod] = {}
                elif ":" in line and current_mod and current_mod in self.declaraciones:
                    k, v = line.split(":", 1)
                    self.declaraciones[current_mod][k.strip()] = v.strip().replace('"', '').replace('[', '').replace(']', '')

    def auditar_coherencia_modulo(self, nemotecnico):
        """Audita si la sub-MFN del módulo se integra perfectamente al orden central."""
        modulo = self.declaraciones.get(nemotecnico)
        if not modulo:
            return f"❌ [ALERTA] Artefacto '{nemotecnico}' no listado en la receta central."
        
        # Principio SINCERO: El cero queda expulsado de las coordenadas locales
        if modulo.get('col') == '0' or modulo.get('row') == '0':
            return f"❌ [RECHAZO] Violación del Principio SINCERO: Índice 0 detectado en [{nemotecnico}]."
            
        print(f"⚡ [MONITOR] Verificando módulo [{nemotecnico}] en Meridiano [{modulo.get('meridiano')}]")
        return f"✅ Artefacto alineado. MFN Heredada bajo el anclaje ético del centro G-7."

    def recrear_modulo_instalable(self, nemotecnico, codigo_base_remoto):
        """Toma el código limpio que entrega Haiku e inyecta la cabecera rígida de Co-Herencia."""
        modulo = self.declaraciones.get(nemotecnico)
        if not modulo:
            print(f"❌ [ALERTA] El nemotécnico '{nemotecnico}' no pertenece al todo.")
            return False

        cabecera_ontologica = f"""# ##NB::CO-HERENCIA_FRACTAL::v0.3##
# ARTEFACTO: {nemotecnico}
# MERIDIANO DE RECONEXIÓN: {str(modulo.get('meridiano')).upper()}
# COMPUERTA LOGICIAL ASIGNADA: {modulo.get('opcode_gate', 'GATE_AND')}
# ANCLAJE DE COORDENADA CENTRAL: G-7 (7,7) - PRINCIPIO SINCERO
# ─────────────────────────────────────────────────────────────────────
"""
        codigo_final = cabecera_ontologica + codigo_base_remoto
        target_path = modulo.get('path', f"core/{nemotecnico.lower()}.py")
        
        if os.path.dirname(target_path):
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
        with open(target_path, 'w', encoding='utf-8') as out:
            out.write(codigo_final)
            
        print(f"📦 [MIGRACIÓN] Módulo '{nemotecnico}' recreado de forma instalable en {target_path}.")
        return True

if __name__ == "__main__":
    print("─" * 60)
    print("🚀 [GÉNESIS] Inicializando Workspace v0.3 - Lector de Co-Herencia")
    print("─" * 60)
    
    declarator = NeurobitDeclarator()
    print(declarator.auditar_coherencia_modulo("BASTION_MCP"))

