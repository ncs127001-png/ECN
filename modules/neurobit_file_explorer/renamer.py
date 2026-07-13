#!/usr/bin/env python3
# renamer.py

import re
import sys
from pathlib import Path

def sanitizar_nombre_carpeta(patron_sucio):
    """
    Limpia el patrón de búsqueda para que sea un nombre de carpeta válido.
    Ej: '*.md' -> 'md' | '*neurobit*.*' -> 'neurobit' | 'director' -> 'director'
    """
    # 1. Elimina caracteres ilegales en sistemas de archivos y comodines glob
    nombre_limpio = re.sub(r'[<>:"/\\|?*]', '', patron_sucio)
    
    # 2. Elimina puntos sobrantes (ej: el punto de '*.md' o '.*') y espacios
    nombre_limpio = nombre_limpio.strip('. ')
    
    # 3. Reemplaza espacios internos por guiones bajos para buenas prácticas
    nombre_limpio = nombre_limpio.replace(' ', '_')
    
    # 4. Si después de limpiar queda vacío (ej: el patrón era solo '*'), usa un fallback
    return nombre_limpio if nombre_limpio else "busqueda_sin_filtro"

def main():
    # El script asume que se ejecuta desde la raíz del proyecto
    ruta_base = Path.cwd() 
    
    # Buscamos solo carpetas que sigan estrictamente el patrón RESULTADOS_[NÚMERO]
    patron_regex = re.compile(r'^RESULTADOS_\d+$')
    carpetas_objetivo = sorted([
        d for d in ruta_base.iterdir() 
        if d.is_dir() and patron_regex.match(d.name)
    ])

    if not carpetas_objetivo:
        print("[renamer] No se encontraron carpetas 'RESULTADOS_N' en el directorio actual.")
        sys.exit(0)

    print(f"[renamer] Procesando {len(carpetas_objetivo)} carpetas...\n")
    nombres_usados = set() # Para evitar colisiones si hay búsquedas repetidas

    for carpeta in carpetas_objetivo:
        informe_path = carpeta / "informe_bruto.txt"
        
        if not informe_path.exists():
            print(f"  [!] {carpeta.name}: Saltada (No contiene informe_bruto.txt)")
            continue

        nuevo_nombre = None
        
        # Leemos solo el encabezado para ahorrar tiempo y memoria
        try:
            with open(informe_path, 'r', encoding='utf-8') as f:
                for linea in f:
                    if linea.startswith("Archivos:"):
                        # Extraemos todo lo que está después de "Archivos:"
                        patron_extraido = linea.split("Archivos:", 1)[1].strip()
                        nuevo_nombre = sanitizar_nombre_carpeta(patron_extraido)
                        break
                    
                    # Si llegamos al separador, ya pasamos el encabezado, detenemos la lectura
                    if ">___" in linea:
                        break
        except Exception as e:
            print(f"  [X] {carpeta.name}: Error leyendo informe ({e})")
            continue

        if not nuevo_nombre:
            print(f"  [!] {carpeta.name}: Saltada (No se encontró la línea 'Archivos:')")
            continue

        # --- MANEJO DE COLISIONES ---
        # Si ya existe una carpeta con ese nombre (o ya la renombramos en este loop), le añadimos un sufijo
        nombre_final = nuevo_nombre
        contador = 2
        while (ruta_base / nombre_final).exists() or nombre_final in nombres_usados:
            nombre_final = f"{nuevo_nombre}_{contador}"
            contador += 1

        nombres_usados.add(nombre_final)
        ruta_destino = ruta_base / nombre_final

        # --- RENOMBRADO ---
        try:
            carpeta.rename(ruta_destino)
            print(f"  [+] {carpeta.name}  =>  {nombre_final}")
        except Exception as e:
            print(f"  [X] Error al renombrar {carpeta.name}: {e}")

    print("\n[renamer] Proceso finalizado.")

if __name__ == "__main__":
    main()