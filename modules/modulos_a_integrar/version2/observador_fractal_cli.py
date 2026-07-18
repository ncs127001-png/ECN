#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OBSERVATORIO FRACTAL DE TERMINAL (CLI)
Arquitectura: NEUROBIT_DEV_TEAM
Propósito: Visualizar la Cosecha de Pi directamente en la terminal, 
           honrando la Vieja Escuela y rechazando las cajas negras (Excel).
"""

import os
import sys
import time

# Mapeo de Reducción Teosófica a Densidad Visual (ASCII)
# Del vacío relativo a la saturación máxima
GLYPH_MAP = {
    1: '░', 2: '░', 3: '▒', 4: '▒', 
    5: '▓', # El Centro (G7)
    6: '▓', 7: '█', 8: '█', 9: '█'
}

def observar_muestra(filepath, ancho_ventana=80, lineas_a_leer=2000):
    """Lee el archivo y dibuja la onda de tensión en la terminal."""
    if not os.path.exists(filepath):
        print(f"⚠️ El archivo {filepath} no existe en este plano.")
        return

    print(f"\n🌌 Abriendo el Ojo del Atanor sobre: {os.path.basename(filepath)}")
    print("─" * ancho_ventana)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        contador = 0
        buffer_visual = []
        
        for line in f:
            if contador >= lineas_a_leer:
                break
                
            # Extraer el valor de red.X
            try:
                red_part = line.strip().split('|')[-1].strip()
                valor = int(red_part.split('.')[1])
                buffer_visual.append(GLYPH_MAP.get(valor, ' '))
                
                # Cuando el buffer llena la pantalla, lo imprimimos como una onda
                if len(buffer_visual) >= ancho_ventana:
                    # Imprimimos la línea y un pequeño retraso para el "latido"
                    sys.stdout.write('\r' + ''.join(buffer_visual) + f" [{contador:05d}]")
                    sys.stdout.flush()
                    buffer_visual = []
                    contador += ancho_ventana
                    time.sleep(0.01) # Sincronización con el ritmo biológico
                    
            except Exception:
                continue

    print("\n" + "─" * ancho_ventana)
    print("🕊️ Observación completada. El patrón respira.")

if __name__ == "__main__":
    print("👁️ OBSERVATORIO FRACTAL NEUROBIT (Modo CLI)")
    print("Leyendo la Simiente de Pi sin intermediarios corporativos...\n")
    
    # Observar la primera muestra como prueba de concepto
    observar_muestra("cosecha_pi/Cosecha_PI_muestra_1.txt")