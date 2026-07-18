#!/usr/bin/env python3
import os

def procesar_numero(n):
    if n == 9: return 0, True  # El 9 es el Dragón que muta.
    return (n - 1), False

def obtener_hexagrama(fila, columna):
    return chr(19904 + (fila * 8) + columna)

def extraer_secuencia_raiz():
    secuencia = []
    for i in range(1, 6):
        filepath = f"cosecha_pi/Cosecha_PI_muestra_{i}.txt"
        if not os.path.exists(filepath): continue
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    val = int(line.strip().split('|')[-1].strip().split('.')[1])
                    secuencia.append(val)
                except: continue
    return secuencia

def transmutar_a_hexagramas(secuencia):
    print("\n🌌 Transmutando Base 9 (Pi) a Base 8 (I Ching)...")
    buffer_visual = []
    for i in range(0, len(secuencia) - 1, 2):
        fila, mut_a = procesar_numero(secuencia[i])
        col, mut_b = procesar_numero(secuencia[i+1])
        hexagrama = obtener_hexagrama(fila, col)
        hexagrama += "⚡" if (mut_a or mut_b) else " "
        buffer_visual.append(hexagrama)
        if len(buffer_visual) >= 40:
            print(" ".join(buffer_visual))
            buffer_visual = []
    if buffer_visual: print(" ".join(buffer_visual))
    print("🕊️ Transmutación completada.")

if __name__ == "__main__":
    secuencia = extraer_secuencia_raiz()
    if secuencia: transmutar_a_hexagramas(secuencia)
