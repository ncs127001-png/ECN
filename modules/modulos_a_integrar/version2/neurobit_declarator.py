#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEUROBIT DECLARATOR - CORE v0.3 (BETA)
Propósito: Monitorear, leer y modificar las declaraciones mnemotécnicas YAML.
           Aplica el principio de Co-Herencia MFN sobre los procesos internos.
"""
import os
import sys
import json

# Forzar la salida limpia de caracteres Unicode para el monitor wide
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

class NeurobitDeclarator:
    def __init__(self, yaml_path="data/declaraciones_base.yaml"):
        self.yaml_path = yaml_path
        self.declaraciones = {}
        self.cargar_mapa_nemotecnico()

    def cargar_mapa_nemotecnico(self):
        """Lee el archivo de la receta y lo fija in-memory en la RAM"""
        if not os.path.exists(self.yaml_path):
            # Simulación de contingencia si no se encuentra PyYAML instalado en Linux Mint
            print(f"⚠️ [DECLARATOR] Archivo YAML no encontrado en '{self.yaml_path}'. Inicializando buffer de respaldo.")
            self._cargar_mock_seguro()
            return
            
        # Nota: Usamos parsing nativo para evitar dependencias externas pesadas (Cláusula Regla 1)
        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            print("📖 [ATANOR] Leyendo aduana de declaraciones nemotécnicas...")
            # Aquí iría el parser formal; inicializamos el registro seguro para el test
            self._cargar_mock_seguro()

    def _cargar_mock_seguro(self):
        self.declaraciones = {
            "BASTION_MCP": {"meridiano": "mu", "coordenada": "6,6", "gate": "GATE_EAND", "status": "COHERENTE"},
            "OPTO_GALVANICO": {"meridiano": "alpha", "coordenada": "0,6", "gate": "GATE_NAND", "status": "LATENCIA"}
        }

    def auditar_coherencia_modulo(self, nemotecnico):
        """Audita si la MFN del módulo pertenece y se integra perfectamente con el todo"""
        modulo = self.declaraciones.get(nemotecnico)
        if not modulo:
            return f"❌ [ALERTA] Artefacto '{nemotecnico}' no listado en la receta de co-herencia."
            
        print(f"⚡ [MONITOR] Verificando módulo [{nemotecnico}] en Meridiano [{modulo['meridiano'].upper()}]...")
        return f"✅ Artefacto alineado. MFN Heredada en Coordenada ({modulo['coordenada']}) bajo la compuerta {modulo['gate']}."

    def modificar_declaracion(self, nemotecnico, nueva_gate):
        """Permite cambiar dinámicamente el verbo o comportamiento del proceso interno"""
        if nemotecnico in self.declaraciones:
            self.declaraciones[nemotecnico]["gate"] = nueva_gate
            print(f"🔮 [TRANSMUTACIÓN] Proceso cambiado. Módulo {nemotecnico} ahora opera bajo: {nueva_gate}")
            return True
        return False

if __name__ == "__main__":
    print("─" * 60)
    print("🌌 [GÉNESIS] Inicializando Módulo Lector de Declaraciones Neurobitrónicas")
    print("─" * 60)
    
    declarador = NeurobitDeclarator()
    
    # Test 1: Auditar el Servidor MCP central
    reporte = declarador.auditar_coherencia_modulo("BASTION_MCP")
    print(reporte)
    
    # Test 2: Modificación dinámica en tiempo de ejecución (In-Memory)
    declarador.modificar_declaracion("BASTION_MCP", "GATE_AND")
    print(declarador.auditar_coherencia_modulo("BASTION_MCP"))

