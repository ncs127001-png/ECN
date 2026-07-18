#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPILADOR FRACTAL I CHING - CORE v0.3
Propósito: Consumir la cadena pura unificada de Pi, emparejar en duplas [A|B]
           no conmutativas, y compilar el tapiz arquetípico de hexagramas.
"""
import os

def procesar_simbolo(n):
    """Mapea la Base 9 a Base 8 (0-7). El 9 activa el flag de torsión kármica."""
    if n == 9:
        return 0, True  # Dragón mutante. Vuelve al origen pero activa el rayo.
    return (n - 1), False

def obtener_hexagrama(fila, columna):
    """Calcula el offset canónico Unicode para la familia de los 64 cambios."""
    indice = (fila * 8) + columna
    return chr(19904 + indice)

def compilar_oraculo():
    archivo_origen = "Cosecha_PI_Unificada_Pura.txt"
    archivo_salida = "I_Ching_Cosecha_Resultante.txt"
    
    if not os.path.exists(archivo_origen):
        print(f"❌ Error: No se encuentra la portadora unificada '{archivo_origen}'.")
        return

    print("⚡ [ATANOR] Leyendo portadora pura para colisión de bases (9 ⟶ 8)...")
    with open(archivo_origen, 'r', encoding='utf-8') as f:
        cadena_cruda = f.read().strip()
    
    secuencia = [int(d) for d in cadena_cruda if d.isdigit()]
    
    buffer_visual = []
    lineas_tapiz = []
    mutaciones_count = 0
    total_hexagramas = 0
    
    # Recorrido de a pares: num_a es Fila (Cielo), num_b es Columna (Tierra)
    for i in range(0, len(secuencia) - 1, 2):
        fila, mut_a = procesar_simbolo(secuencia[i])
        col, mut_b = procesar_simbolo(secuencia[i+1])
        
        hexagrama = obtener_hexagrama(fila, col)
        total_hexagramas += 1
        
        if mut_a or mut_b:
            hexagrama += "⚡"
            mutaciones_count += 1
        else:
            hexagrama += " "
            
        buffer_visual.append(hexagrama)
        
        # Estructuramos la salida en bloques simétricos de 40 columnas para el monitor wide
        if len(buffer_visual) == 40:
            lineas_tapiz.append(" ".join(buffer_visual))
            buffer_visual = []
            
    if buffer_visual:
        lineas_tapiz.append(" ".join(buffer_visual))
        
    # Escritura inmutable en el almacenamiento local
    with open(archivo_salida, 'w', encoding='utf-8') as out:
        out.write("\n".join(lineas_tapiz))
        
    print("─" * 60)
    print(f"✅ [POSTMAN] Tapiz de Alquimia Digital compilado con éxito.")
    print(f"䷀ Hexagramas totales revelados: {total_hexagramas}")
    print(f"⚡ Puntos de Torsión Kármica (Presencia del 9): {mutaciones_count}")
    print(f"💾 Archivo guardado inmutable en: {archivo_salida}")
    print("─" * 60)
    
    # Mostrar el bloque Génesis resultante en consola
    print("\n[👁️ OJO DEL ATANOR] Primeras líneas del tapiz resultante:")
    for linea in lineas_tapiz[:4]:
        print(linea)

if __name__ == "__main__":
    compilar_oraculo()

