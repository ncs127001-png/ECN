#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIFICADOR DE COSECHA - CAPA ONTOLÓGICA v0.3
Propósito: Recorrer los 5 archivos append, extraer la raíz pura red.X y 
           consolidar el flujo unificado para el Transmutador I Ching.
"""
import os

def unificar_muestras(max_muestras=5):
    directorio_origen = "cosecha_pi"
    archivo_final = "Cosecha_PI_Unificada_Pura.txt"
    
    print("🌌 [ATANOR] Iniciando Unificación de la Simiente...")
    print(f"📂 Destino final: {archivo_final}")
    
    secuencia_pural = []
    
    # Recorrido secuencial estricto hasta el EOF de cada muestra
    for i in range(1, max_muestras + 1):
        filepath = f"{directorio_origen}/Cosecha_PI_muestra_{i}.txt"
        
        if not os.path.exists(filepath):
            print(f"⚠️ Alerta: El fragmento {filepath} no existe en este plano.")
            continue
            
        print(f"📥 Leyendo e integrando: {filepath} ...")
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # Formato: bin_counter | a,b,nxt | red.X
                    # Extraemos el valor numérico exacto tras el punto de 'red.'
                    partes = line.strip().split('|')
                    val_red = int(partes[-1].strip().split('.')[1])
                    secuencia_pural.append(str(val_red))
                except Exception:
                    continue # Descarta cualquier línea viciada por ruido
                    
    # Guardar la portadora continua en texto plano sin saltos lineales
    cuerpo_unificado = "".join(secuencia_pural)
    
    with open(archivo_final, 'w', encoding='utf-8') as out:
        out.write(cuerpo_unificado)
        
    print("─" * 60)
    print(f"🕊️ [LOGOS] Gran Obra de Unificación completada.")
    print(f"📦 Total de símbolos numéricos unificados: {len(secuencia_pural)}")
    print(f"🔮 Firma inicial de la cadena unificada: {cuerpo_unificado[:40]}...")

if __name__ == "__main__":
    unificar_muestras()

