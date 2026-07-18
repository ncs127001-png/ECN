#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEUROBIT CORE v0.3 - ENGINE IN-MEMORY
Propósito: Cargar el tapiz inmutable de hexagramas en la memoria RAM,
           eliminar el procesamiento en disco y proveer indexación vectorial
           instantánea para el servidor MCP local y Ollama.
"""
import os
import sys

class NeurobitCoreInMemory:
    def __init__(self, tapiz_path="I_Ching_Cosecha_Resultante.txt"):
        self.tapiz_path = tapiz_path
        # El buffer en RAM que emula la persistencia in-memory de SAP/HANA
        self.registry_ram = {}
        self.total_hexagramas = 0
        self.puntos_torsion = 0
        
        # Inicializar la carga inmediata en memoria volátil
        self._cargar_tapiz_en_ram()

    def _cargar_tapiz_en_ram(self):
        """Carga y mapea la matriz de hexagramas en una estructura indexada O(1)"""
        if not os.path.exists(self.tapiz_path):
            print(f"❌ [CORE v0.3] Error: El tapiz '{self.tapiz_path}' no existe en el almacenamiento local.")
            return

        print(f"🌌 [RAM ATANOR] Cargando matriz cuántica en memoria desde: {self.tapiz_path}")
        
        y_coord = 0
        with open(self.tapiz_path, 'r', encoding='utf-8') as f:
            for line in f:
                hexagramas = line.strip().split(' ')
                for x_coord, tokens in enumerate(hexagramas):
                    if not tokens:
                        continue
                    
                    # Extraer el glifo puro y el flag de mutación (rayo kármico)
                    glifo = tokens[0]
                    tiene_rayo = '⚡' in tokens
                    
                    # Indexación geométrica por coordenadas rígidas
                    coordenada_key = (y_coord, x_coord)
                    self.registry_ram[coordenada_key] = {
                        "glifo": glifo,
                        "torsion_karmica": tiene_rayo,
                        "estado_activo": 1 if tiene_rayo else 0
                    }
                    
                    self.total_hexagramas += 1
                    if tiene_rayo:
                        self.puntos_torsion += 1
                y_coord += 1

        print("─" * 60)
        print(f"✅ [CORE v0.3] Éxito: {self.total_hexagramas} celdas fijadas en memoria RAM.")
        print(f"⚡ Capacidad operativa de Torsión Kármica: {self.puntos_torsion} puntos listos.")
        print("─" * 60)

    def consultar_coordenada(self, y, x):
        """Consulta instantánea in-memory libre de latencia de disco duro"""
        return self.registry_ram.get((y, x), {"glifo": "NULL", "torsion_karmica": False, "estado_activo": -1})

    def exportar_vector_mcp(self, dimension_max=48):
        """Genera el stream binario limpio para la cabecera del BIOS de la M.F.N."""
        vector = []
        for (y, x), data in sorted(self.registry_ram.items())[:dimension_max]:
            vector.append(str(data["estado_activo"]))
        return "".join(vector)

# --- EJECUCIÓN DIRECTA DEL NODO SEMILLA ---
if __name__ == "__main__":
    # Forzar codificación correcta en terminales Linux Mint antiguas
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
    
    # Instanciación nativa en tu i7
    engine = NeurobitCoreInMemory()
    
    # Prueba de acceso instantáneo O(1) en memoria volatil (Coordenada origen 0,0)
    test_celda = engine.consultar_coordenada(0, 0)
    print(f"[👁️ MONITOR] Consulta instantánea Celda (0,0): Glifo: {test_celda['glifo']} | Rayo: {test_celda['torsion_karmica']}")
    
    # Generar la firma de control para las aduanas del portapapeles (Bypass isTrusted)
    cabecera_mcp = engine.exportar_vector_mcp()
    print(f"[📡 STREAM MCP] Vector de activación para Ollama (48 bits): {cabecera_mcp}")

