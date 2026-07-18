#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRANSMUTADOR I CHING: DE LA COSECHA DE PI A LOS 64 HEXAGRAMAS
Arquitectura: NEUROBIT_DEV_TEAM
Propósito: Mapear la secuencia fractal 1-9 (Base 9) a la Matriz 8x8 del I Ching (Base 64).
"""

import os

# ==========================================
# 1. MAPEO ONTOLÓGICO (El Puente 9 -> 8)
# ==========================================
# Los 8 Trigramas (Coordenadas 0-7 para la matriz)
# El 9 es tratado como Yang Viejo (Mutante), mapeado a 0 (El Cielo/Qian) pero con flag de mutación.
TRIGRAMAS = ["☰", "☱", "☲", "☳", "☴", "☵", "☶", "☷"]

# Tabla de 64 Hexagramas (Unicode U+4DC0 a U+4DFF)
# La fórmula es: Índice = (Fila * 8) + Columna
def obtener_hexagrama(fila, columna):
    # El código base unicode para el Hexagrama 1 (䷀) es 19904 (0x4DC0)
    indice = (fila * 8) + columna
    return chr(19904 + indice)

def procesar_numero(n):
    """Convierte la reducción teosófica (1-9) a coordenada de matriz (0-7) y detecta mutación."""
    if n == 9:
        return 0, True  # El 9 es el Dragón que muta. Vuelve al origen (0) pero activa la torsión.
    return (n - 1), False # 1-8 mapean a 0-7

# ==========================================
# 2. EXTRACCIÓN DE LA SEMILLA (La Cosecha Pura)
# ==========================================
def extraer_secuencia_raiz():
    secuencia = []
    for i in range(1, 6):
        filepath = f"cosecha_pi/Cosecha_PI_muestra_{i}.txt"
        if not os.path.exists(filepath): continue
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # Extrae el número después de 'red.'
                    red_part = line.strip().split('|')[-1].strip()
                    val = int(red_part.split('.')[1])
                    secuencia.append(val)
                except:
                    continue
    return secuencia

# ==========================================
# 3. EL MOTOR DE TRANSMUTACIÓN (El Oráculo)
# ==========================================
def transmutar_a_hexagramas(secuencia):
    print("\n🌌 Iniciando Transmutación: Colisionando Base 9 (Pi) con Base 8 (I Ching)...")
    print("─" * 80)
    
    buffer_visual = []
    mutaciones_count = 0
    
    # Recorremos la secuencia de a pares (No-Conmutatividad: A es Cielo, B es Tierra)
    for i in range(0, len(secuencia) - 1, 2):
        num_a = secuencia[i]
        num_b = secuencia[i+1]
        
        fila, mut_a = procesar_numero(num_a)
        col, mut_b = procesar_numero(num_b)
        
        hexagrama = obtener_hexagrama(fila, col)
        
        # Si hay un 9 en el par, el hexagrama está en "Torsión Kármica"
        if mut_a or mut_b:
            hexagrama += "⚡" # Marca visual de mutación (Yang Viejo)
            mutaciones_count += 1
        else:
            hexagrama += " " # Espacio para mantener la cuadrícula
            
        buffer_visual.append(hexagrama)
        
        # Impresión en bloque para la terminal
        if len(buffer_visual) >= 40:
            print(" ".join(buffer_visual))
            buffer_visual = []
            
    if buffer_visual:
        print(" ".join(buffer_visual))
        
    print("─" * 80)
    print(f"🕊️ Transmutación completada. Se han revelado {len(secuencia)//2} Hexagramas.")
    print(f"⚡ Torsiones Kármicas (Presencia del 9): {mutaciones_count}")
    print("El patrón del I Ching ha sido tejido con la respiración de Pi.")

if __name__ == "__main__":
    print("☯️ TRANSMUTADOR I CHING (Modo CLI)")
    print("Leyendo la Simiente de Pi y proyectándola en el Mandala de los 64 Cambios...\n")
    secuencia = extraer_secuencia_raiz()
    if secuencia:
        transmutar_a_hexagramas(secuencia)
    else:
        print("⚠️ No se encontró la cosecha. Ejecuta primero el motor de Pi.")