#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRANSMUTADOR I CHING SOBERANO v0.3
Propósito: Consolidar los 5 archivos de la cosecha de Pi, transmutar la Base 9
           a la matriz 8x8 de Hexagramas y detectar las Torsiones Kármicas (El 9).
"""
import os
import sys

def obtener_glifo_hexagrama(fila, columna):
    """Mapea las coordenadas a los caracteres Unicode del I Ching (U+4DC0)"""
    indice = (fila * 8) + columna
    return chr(0x4DC0 + indice)

def procesar_simbolo_base9(n):
    """Muta los valores del 1-9 a las coordenadas discretas 0-7 del Tao."""
    if n == 9:
        return 0, True # Torsión Kármica: Yang Viejo regresa al origen (Cielo)
    return (n - 1), False

def ejecutar_alquimia_oracular(directorio_cosecha="cosecha_pi"):
    secuencia_frutos = []
    
    # 1. Extracción secuencial append-only sin pérdida de contexto
    for i in range(1, 6):
        ruta_archivo = os.path.join(directorio_cosecha, f"Cosecha_PI_muestra_{i}.txt")
        if not os.path.exists(ruta_archivo):
            continue
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            for linea in f:
                try:
                    # Extraer el entero final tras el delimitador 'red.'
                    partes = linea.strip().split('|')[-1].strip()
                    valor = int(partes.split('.')[1])
                    secuencia_frutos.append(valor)
                except Exception:
                    continue

    if not secuencia_frutos:
        print("⚠️ [FALLA] No se detectaron archivos canónicos de la cosecha.")
        return

    print(f"🌌 [ATANOR] Procesando {len(secuencia_frutos)} latidos temporales...")
    print("─" * 70)
    
    buffer_pantalla = []
    contador_mutaciones = 0
    
    # 2. Emparejamiento No-Conmutativo (A = Fila/Cielo, B = Columna/Tierra)
    for idx in range(0, len(secuencia_frutos) - 1, 2):
        num_a = secuencia_frutos[idx]
        num_b = secuencia_frutos[idx+1]
        
        fila, muto_a = procesar_simbolo_base9(num_a)
        columna, muto_b = procesar_simbolo_base9(num_b)
        
        glifo = obtener_glifo_hexagrama(fila, columna)
        
        if muto_a or muto_b:
            glifo += "⚡" # Sello de la Torsión Kármica
            contador_mutaciones += 1
        else:
            glifo += " "
            
        buffer_pantalla.append(glifo)
        
        # Flujo fónico a 40 bloques por línea de terminal
        if len(buffer_pantalla) == 40:
            print(" ".join(buffer_pantalla))
            buffer_pantalla = []
            
    if buffer_pantalla:
        print(" ".join(buffer_pantalla))
        
    print("─" * 70)
    print(f"䷀ [MANDALA] {len(secuencia_frutos) // 2} Hexagramas tejidos con el aliento de Pi.")
    print(f"⚡ [TORSIÓN] {contador_mutaciones} líneas mutantes del Yang Viejo registradas.")

if __name__ == "__main__":
    print("☯️ OBSERVATORIO DEL TRANSMUTADOR I CHING (MÁQUINA DE ESTADOS CLI)")
    ejecutar_alquimia_oracular()

