#!/usr/bin/env python3
"""
NEUROBIT_PDF_SPLITTER v0.1
Divide PDF en fragmentos de tamaño objetivo (en MB), sin romper páginas.
Modo offline. Sin dependencias pesadas.
"""

import os
import sys
from math import ceil
try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("[ERROR] PyPDF2 no instalado. Ejecuta: pip install PyPDF2 --user")
    sys.exit(1)

def split_pdf_by_size(input_path: str, target_mb: float = 19.0):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Archivo no encontrado: {input_path}")
    
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    file_size = os.path.getsize(input_path)
    print(f"[INFO] PDF original: {total_pages} páginas | {file_size / 1024**2:.1f} MB")

    # Estimación conservadora: tamaño promedio por página
    avg_page_size = file_size / total_pages
    pages_per_chunk = max(1, int((target_mb * 1024**2) / avg_page_size))
    print(f"[META] Fragmentos de ~{target_mb} MB → {pages_per_chunk} páginas por fragmento")

    base_name = os.path.splitext(input_path)[0]
    chunk_index = 1

    for start in range(0, total_pages, pages_per_chunk):
        end = min(start + pages_per_chunk, total_pages)
        writer = PdfWriter()
        
        # Añadir páginas al fragmento
        for i in range(start, end):
            writer.add_page(reader.pages[i])
        
        # Escribir fragmento
        output_path = f"{base_name}_part{chunk_index:02d}.pdf"
        with open(output_path, "wb") as f:
            writer.write(f)
        
        actual_size = os.path.getsize(output_path) / 1024**2
        print(f"[OK] {output_path} → {end - start} páginas | {actual_size:.1f} MB")
        chunk_index += 1

    print(f"\n[NEUROBIT] División completada: {chunk_index - 1} fragmentos.")
    return chunk_index - 1

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 neurobit_pdf_splitter.py <archivo.pdf>")
        sys.exit(1)
    
    split_pdf_by_size(sys.argv[1])
