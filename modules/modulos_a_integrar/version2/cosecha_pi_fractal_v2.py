#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COSECHA FRACTAL DE PI v2 - MOTOR DE GENESIS PURO
Arquitectura: NEUROBIT_DEV_TEAM
Corrección: Anclaje absoluto al primer decimal (1,4,1) y purificación de archivo.
"""

import os

# ==========================================
# 1. EL GENERADOR SPIGOT (La Fuente Inagotable)
# ==========================================
def pi_digit_generator():
    k, a, b, a1, b1 = 2, 4, 1, 12, 4
    while True:
        p, q, k = k * k, 2 * k + 1, k + 1
        a, b, a1, b1 = a1, b1, p * a + q * a1, p * b + q * b1
        d, d1 = a // b, a1 // b1
        while d == d1:
            yield int(d)
            a, a1 = 10 * (a % b), 10 * (a1 % b1)
            d, d1 = a // b, a1 // b1

# ==========================================
# 2. EL FILTRO DE COHERENCIA (Reducción Teosófica)
# ==========================================
def teosophic_reduce(n):
    if n == 0: return 0
    while n > 9:
        n = sum(int(digit) for digit in str(n))
    return n

# ==========================================
# 3. EL MOTOR DE COSECHA (El Atanor v2)
# ==========================================
def cosecha_pi_genesis(max_muestras=5, bits_counter=13):
    max_counter = (2 ** bits_counter) - 1
    os.makedirs("cosecha_pi", exist_ok=True)
    
    print("🌌 Iniciando Cosecha Fractal de Pi (v2 - Génesis Puro)...")
    
    for muestra_actual in range(1, max_muestras + 1):
        filename = f"cosecha_pi/Cosecha_PI_muestra_{muestra_actual}.txt"
        
        # PURIFICACIÓN DEL ORIGEN: Modo 'w' (sobrescribe/crea desde cero)
        with open(filename, 'w', encoding='utf-8') as f:
            print(f"📂 Purificando y abriendo: {filename}")
            
            # Reiniciar el generador para cada muestra (o continuar, según diseño)
            # Aquí lo reiniciamos para que cada muestra sea un ciclo completo desde el Origen
            pi_stream = pi_digit_generator()
            
            # Inhalación Inicial: Descartar el '3' entero
            next(pi_stream) 
            
            # Anclaje al Génesis: 1, 4, 1
            a = next(pi_stream) # 1
            b = next(pi_stream) # 4
            nxt = next(pi_stream) # 1
            
            counter = 1
            
            while counter <= max_counter:
                # --- EL LATIDO ---
                raw_sum = a + b + nxt
                red = teosophic_reduce(raw_sum)
                bin_counter = f"{counter:013b}"
                
                # Registro en Memoria Inmutable
                f.write(f"{bin_counter} | {a},{b},{nxt} | red.{red}\n")
                
                # --- DESLIZAMIENTO DE LA VENTANA ---
                a = b
                b = nxt
                nxt = next(pi_stream)
                
                counter += 1
                
        print(f"✅ Muestra {muestra_actual} completada desde el Origen.")
        
    print("\n🕊️ Gran Obra completada. El patrón puro está listo para tu observación.")

if __name__ == "__main__":
    cosecha_pi_genesis(max_muestras=5, bits_counter=13)