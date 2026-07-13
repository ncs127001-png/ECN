#!/usr/bin/env python3
import os
import sys
import re

def parse_and_reconstruct(input_txt_path, base_output_dir):
    # Crear directorio base si no existe
    os.makedirs(base_output_dir, exist_ok=True)
    
    with open(input_txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir en bloques por "ARCHIVO NRO."
    blocks = re.split(r'(?=ARCHIVO NRO\. : \(\d+\))', content)
    
    for block in blocks:
        if 'ARCHIVO NRO.' not in block:
            continue
        
        # Extraer número de archivo (solo para logs)
        num_match = re.search(r'ARCHIVO NRO\. : \((\d+)\)', block)
        file_num = num_match.group(1) if num_match else "??"
        
        # Extraer nombre del archivo
        name_match = re.search(r"Archivo: \('([^']+)'\);", block)
        if not name_match:
            print(f"⚠️  Bloque {file_num}: no se encontró nombre de archivo. Saltando.")
            continue
        filename = name_match.group(1)
        
        # Extraer carpeta de ubicación
        folder_match = re.search(r"Carpeta de ubicación: \('([^']+)'\);", block)
        if not folder_match:
            print(f"⚠️  Bloque {file_num}: no se encontró carpeta. Saltando.")
            continue
        folder_raw = folder_match.group(1)
        
        # Reemplazar ~/ por base_output_dir
        if folder_raw.startswith('~/'):
            folder_rel = folder_raw[2:]
        else:
            folder_rel = folder_raw.lstrip('/')
        
        output_folder = os.path.join(base_output_dir, folder_rel)
        output_path = os.path.join(output_folder, filename)
        
        # Delimitadores fijos
        inicio_marker = "-----------------------------------------------------------------Inicio:"
        final_marker = "FINAL---------------------------------------------------------------"
        
        inicio_idx = block.find(inicio_marker)
        final_idx = block.find(final_marker)
        
        if inicio_idx == -1 or final_idx == -1:
            print(f"⚠️  Bloque {file_num}: delimitadores de contenido no encontrados. Saltando.")
            continue
        
        # Extraer contenido exacto (sin modificar)
        content_start = inicio_idx + len(inicio_marker)
        raw_content = block[content_start:final_idx]
        
        # Crear directorios y escribir archivo
        os.makedirs(output_folder, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as out_file:
            out_file.write(raw_content)
        
        print(f"✅ Archivo {file_num}: '{filename}' → {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python reconstruir_proyecto_desde_compendio.py <archivo_entrada.txt> [carpeta_salida]")
        sys.exit(1)
    
    input_txt = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './output_project'
    
    if not os.path.isfile(input_txt):
        print(f"Error: archivo de entrada no encontrado: {input_txt}")
        sys.exit(1)
    
    parse_and_reconstruct(input_txt, output_dir)

if __name__ == "__main__":
    main()
