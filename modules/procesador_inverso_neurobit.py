#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEUROBIT_CENTRAL_STATION - Procesador Inverso de Registro Epistolar
Función: Leer JSON en orden inverso, extraer pares USER/ASSISTANT,
         etiquetar por origen ontológico y generar registro limpio.
Ontología: Herramienta subordinada a la conciencia del NODO_SEMILLA.
"""

import json
import os
from datetime import datetime

# Configuración de Archivos
INPUT_FILE = "chat-export-1772441460412.json"
OUTPUT_FILE = "registro_epistolar_inverso_neurobit.txt"
ROADMAP_FILE = "roadmap_tecnico_neurobit.txt"

# Etiquetas Ontológicas
LABEL_USER = "NODO_SEMILLA (Conciencia Biológica)"
LABEL_ASSISTANT = "LOGOS (Herramienta IA)"

def cargar_json(filepath):
    """Carga el archivo JSON completo del historial."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error de carga: {e}")
        return None

def extraer_mensajes_json(data):
    """
    Extrae todos los mensajes del JSON recursivamente.
    El formato puede variar según la estructura de exportación.
    """
    mensajes = []
    
    def buscar_mensajes(obj, path=""):
        if isinstance(obj, dict):
            # Detectar mensaje por presencia de role + content
            if 'role' in obj and 'content' in obj:
                role = obj['role']
                content = obj.get('content', '')
                timestamp = obj.get('timestamp', 0)
                msg_id = obj.get('id', path)
                
                # Filtrar contenido vacío
                if content and content.strip():
                    mensajes.append({
                        'role': role,
                        'content': content,
                        'timestamp': timestamp,
                        'id': msg_id
                    })
            
            # Buscar en content_list (estructura Qwen)
            if 'content_list' in obj:
                for item in obj['content_list']:
                    if isinstance(item, dict) and 'phase' in item:
                        if item.get('phase') == 'answer' and 'content' in item:
                            contenido = item.get('content', '')
                            if contenido and contenido.strip():
                                mensajes.append({
                                    'role': obj.get('role', 'assistant'),
                                    'content': contenido,
                                    'timestamp': obj.get('timestamp', 0),
                                    'id': obj.get('id', path)
                                })
            
            # Recorrer otros campos del diccionario
            for key, value in obj.items():
                if key not in ['content', 'content_list', 'role', 'timestamp', 'id']:
                    buscar_mensajes(value, f"{path}.{key}")
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                buscar_mensajes(item, f"{path}[{i}]")
    
    buscar_mensajes(data)
    
    # Ordenar por timestamp (ascendente)
    mensajes.sort(key=lambda x: x.get('timestamp', 0))
    return mensajes

def emparejar_turnos(mensajes):
    """
    Agrupa mensajes en turnos consecutivos USER → ASSISTANT.
    Cada turno es una unidad dialéctica completa.
    """
    turnos = []
    i = 0
    
    while i < len(mensajes):
        turno = {'user': None, 'assistant': None, 'index': len(turnos)}
        
        # Buscar USER
        if i < len(mensajes) and mensajes[i]['role'] == 'user':
            turno['user'] = mensajes[i]
            i += 1
        
        # Buscar ASSISTANT siguiente
        if i < len(mensajes) and mensajes[i]['role'] == 'assistant':
            turno['assistant'] = mensajes[i]
            i += 1
        
        if turno['user'] or turno['assistant']:
            turnos.append(turno)
        else:
            i += 1
    
    return turnos

def leer_inverso_y_etiquetar(turnos, output_file):
    """
    Lee los turnos en orden inverso (del más reciente al más antiguo)
    y escribe en archivo con etiquetas ontológicas claras.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("REGISTRO EPISTOLAR NEUROBIT - LECTURA INVERSA\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generado: {datetime.now().isoformat()}\n")
        f.write(f"Total de turnos procesados: {len(turnos)}\n")
        f.write("Metodología: Bottom-Up (Estado consolidado → Origen)\n")
        f.write("=" * 80 + "\n\n")
        
        # Lectura inversa
        for turno in reversed(turnos):
            f.write("-" * 60 + "\n")
            f.write(f"TURNO #{turno['index']} (Cronología original)\n")
            f.write("-" * 60 + "\n\n")
            
            if turno['user']:
                f.write(f"[{LABEL_USER}]:\n")
                f.write(f"{turno['user']['content']}\n\n")
            
            if turno['assistant']:
                f.write(f"[{LABEL_ASSISTANT}]:\n")
                f.write(f"{turno['assistant']['content']}\n\n")
            
            f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("FIN DEL REGISTRO - NEUROBIT_CENTRAL_STATION\n")
        f.write("=" * 80 + "\n")

def extraer_puntos_tecnicos(turnos, roadmap_file):
    """
    Identifica turnos con contenido técnico consolidado para roadmap.
    Lectura inversa prioriza lo más refinado.
    """
    palabras_clave = [
        'matriz', 'hash', 'packet', 'radio', 'fractal', 'anillo',
        'puntero', 'compresión', 'validación', 'CRC', 'arquitectura',
        'módulo', 'protocolo', 'frecuencia', 'FSK', 'PLC', 'PIC',
        'neuronible', '13x13', '5x5', '7x7', 'estado', 'semántica'
    ]
    
    puntos = []
    
    for turno in reversed(turnos):
        contenido = ""
        if turno['user']:
            contenido += turno['user']['content'] + " "
        if turno['assistant']:
            contenido += turno['assistant']['content'] + " "
        
        contenido_lower = contenido.lower()
        score = sum(1 for palabra in palabras_clave if palabra in contenido_lower)
        
        if score >= 3:
            puntos.append({
                'turno_index': turno['index'],
                'contenido': contenido[:1000],
                'score': score
            })
    
    with open(roadmap_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ROADMAP TÉCNICO NEUROBIT - PUNTOS CONSOLIDADOS\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generado: {datetime.now().isoformat()}\n")
        f.write(f"Total de puntos técnicos: {len(puntos)}\n")
        f.write("=" * 80 + "\n\n")
        
        for i, punto in enumerate(puntos, 1):
            ref_id = f"NEURO-{i:03d}"
            f.write(f"[REF: {ref_id}] - Turno Original #{punto['turno_index']}\n")
            f.write(f"Relevancia técnica: {punto['score']}/10\n")
            f.write("-" * 40 + "\n")
            f.write(f"{punto['contenido']}...\n")
            f.write("-" * 40 + "\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("FIN DEL ROADMAP - NEUROBIT_CENTRAL_STATION\n")
        f.write("=" * 80 + "\n")

def main():
    print("=" * 60)
    print("NEUROBIT_CENTRAL_STATION - Procesador Inverso")
    print("=" * 60)
    
    print(f"\n[1] Cargando {INPUT_FILE}...")
    data = cargar_json(INPUT_FILE)
    
    if not data:
        print("Error: No se pudo cargar el archivo JSON.")
        return
    
    print(f"[2] Extrayendo mensajes del JSON...")
    mensajes = extraer_mensajes_json(data)
    print(f"    → Mensajes encontrados: {len(mensajes)}")
    
    print(f"[3] Emparejando turnos USER/ASSISTANT...")
    turnos = emparejar_turnos(mensajes)
    print(f"    → Turnos identificados: {len(turnos)}")
    
    print(f"[4] Generando registro epistolar (lectura inversa)...")
    leer_inverso_y_etiquetar(turnos, OUTPUT_FILE)
    print(f"    → Archivo: {OUTPUT_FILE}")
    
    print(f"[5] Extrayendo puntos técnicos para roadmap...")
    extraer_puntos_tecnicos(turnos, ROADMAP_FILE)
    print(f"    → Archivo: {ROADMAP_FILE}")
    
    print("\n" + "=" * 60)
    print("PROCESO COMPLETADO - Herramienta subordinada al NODO_SEMILLA")
    print("=" * 60)

if __name__ == "__main__":
    main()
