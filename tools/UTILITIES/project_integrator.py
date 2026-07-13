#!/usr/bin/env python3
"""
modulo_integrador.py
Combina funcionalidad de buscador/recolector + compile_project en un flujo único.

Uso (resumen):
  python3 modulo_integrador.py --lista_archivos lista.txt --dir_busqueda /ruta/base \
    --dir_destino /ruta/destino --output_compilado compilado.txt --output_no_resueltas rutas_no_resueltas.txt
"""
import os
import sys
import argparse
import shutil
import datetime
from pathlib import Path
import subprocess

# --- Búsqueda recursiva (manejando permisos) ---
def buscar_archivo_recursivo(nombre_archivo, directorio_actual):
    nombre_l = nombre_archivo.lower()
    try:
        for elemento in os.listdir(directorio_actual):
            ruta = os.path.join(directorio_actual, elemento)
            try:
                if os.path.isfile(ruta) and elemento.lower() == nombre_l:
                    return ruta
                if os.path.isdir(ruta) and not os.path.islink(ruta):
                    resultado = buscar_archivo_recursivo(nombre_archivo, ruta)
                    if resultado:
                        return resultado
            except PermissionError:
                continue
    except PermissionError:
        return None
    except Exception:
        return None
    return None

# --- Búsqueda parcial (sugerencias) ---
def buscar_sugerencias(nombre_archivo, base_dir, max_sugerencias=5):
    nombre_l = nombre_archivo.lower()
    sugerencias = []
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if nombre_l in f.lower() or f.lower() in nombre_l:
                sugerencias.append(os.path.join(root, f))
                if len(sugerencias) >= max_sugerencias:
                    return sugerencias
    return sugerencias

# --- Copiar evitando sobrescribir (añade sufijo) ---
def copiar_evitar_sobrescribir(src, dst_dir):
    Path(dst_dir).mkdir(parents=True, exist_ok=True)
    base = os.path.basename(src)
    destino = os.path.join(dst_dir, base)
    contador = 1
    nombre_base, ext = os.path.splitext(base)
    while os.path.exists(destino):
        destino = os.path.join(dst_dir, f"{nombre_base}_{contador}{ext}")
        contador += 1
    shutil.copy2(src, destino)
    return destino

# --- Intento de usar compile_project directamente, con fallback a subprocess ---
def ejecutar_compile_project(proyecto_dir, output_file, script_dir):
    # Intentar importar la función si el módulo está en el mismo directorio
    try:
        sys.path.insert(0, str(script_dir))
        import compile_project as cp  # type: ignore
        if hasattr(cp, 'compile_project'):
            cnt = cp.compile_project(proyecto_dir, output_file)
            return True, cnt
    except Exception:
        pass

    # Fallback: ejecutar como script externo
    script_path = script_dir / 'compile_project.py'
    if script_path.exists():
        cmd = ['python3', str(script_path), '--project', str(proyecto_dir), '--output', str(output_file)]
        try:
            subprocess.check_call(cmd)
            return True, None
        except subprocess.CalledProcessError:
            return False, None

    return False, None

def generar_reporte_integracion(reporte_path, summary):
    with open(reporte_path, 'w', encoding='utf-8') as f:
        f.write(f"# Reporte de Integración\n\n")
        f.write(f"- Fecha: {datetime.datetime.utcnow().isoformat()}Z\n\n")
        for k, v in summary.items():
            f.write(f"## {k}\n\n")
            if isinstance(v, list):
                for item in v:
                    f.write(f"- {item}\n")
            else:
                f.write(f"{v}\n")
            f.write("\n")

def main():
    parser = argparse.ArgumentParser(description='Integrador: busqueda + compilado sobre carpeta destino')
    parser.add_argument('--lista_archivos', required=True, help='Ruta al .txt con nombres de archivos a buscar')
    parser.add_argument('--dir_busqueda', required=True, help='Directorio base para búsqueda recursiva')
    parser.add_argument('--dir_destino', required=True, help='Carpeta destino para archivos encontrados')
    parser.add_argument('--output_compilado', default='compilado_integrado.txt', help='Nombre archivo compilado final')
    parser.add_argument('--output_no_resueltas', default='rutas_no_resueltas.txt', help='Nombre archivo con rutas no resueltas')
    parser.add_argument('--reporte_final', default='reporte_integracion.md', help='Reporte final (markdown)')
    args = parser.parse_args()

    lista_path = Path(args.lista_archivos)
    base_busqueda = Path(args.dir_busqueda)
    destino = Path(args.dir_destino)
    output_compilado = Path(args.output_compilado)
    output_no_resueltas = Path(args.output_no_resueltas)
    reporte_final = Path(args.reporte_final)

    if not lista_path.is_file():
        print(f"Error: archivo de lista no encontrado: {lista_path}", file=sys.stderr)
        sys.exit(1)
    if not base_busqueda.is_dir():
        print(f"Error: directorio de búsqueda no válido: {base_busqueda}", file=sys.stderr)
        sys.exit(1)

    destino.mkdir(parents=True, exist_ok=True)

    with open(lista_path, 'r', encoding='utf-8') as f:
        items = [l.strip() for l in f if l.strip()]

    encontrados = []
    no_encontrados = []
    sugerencias_map = {}

    for nombre in items:
        print(f"Buscando: {nombre}")
        ruta = buscar_archivo_recursivo(nombre, str(base_busqueda))
        if ruta:
            try:
                dst = copiar_evitar_sobrescribir(ruta, str(destino))
                encontrados.append(f"{nombre} -> {dst}")
                print(f"  Encontrado y copiado: {dst}")
            except Exception as e:
                print(f"  Error copiando {ruta}: {e}", file=sys.stderr)
                no_encontrados.append(nombre)
                sugerencias_map[nombre] = buscar_sugerencias(nombre, str(base_busqueda))
        else:
            print(f"  No encontrado: {nombre}")
            no_encontrados.append(nombre)
            sugerencias_map[nombre] = buscar_sugerencias(nombre, str(base_busqueda))

    # Escribir rutas_no_resueltas con formato requerido
    with open(output_no_resueltas, 'w', encoding='utf-8') as f:
        f.write(f"# Rutas no resueltas\n")
        f.write(f"Fecha: {datetime.datetime.utcnow().isoformat()}Z\n\n")
        if not no_encontrados:
            f.write("Todos los archivos fueron encontrados.\n")
        else:
            for nombre in no_encontrados:
                f.write(f"## {nombre}\n\n")
                f.write("Estado: NO ENCONTRADO\n\n")
                sugerencias = sugerencias_map.get(nombre, [])
                if sugerencias:
                    f.write("Sugerencias (posibles rutas parcial match):\n")
                    for s in sugerencias:
                        f.write(f"- {s}\n")
                else:
                    f.write("Sugerencias: Ninguna encontrada por búsqueda parcial.\n")
                f.write("\n")
            # Comando sugerido para reintentar búsqueda
            cmd_sugerido = (
                f"python3 {Path(__file__).name} --lista_archivos {lista_path} "
                f"--dir_busqueda {base_busqueda} --dir_destino {destino} "
                f"--output_compilado {output_compilado} --output_no_resueltas {output_no_resueltas}"
            )
            f.write("Comando sugerido para reintentar la búsqueda:\n")
            f.write(f"`{cmd_sugerido}`\n")

    # Ejecutar compile_project.py sobre la carpeta destino
    script_dir = Path(__file__).parent.resolve()
    ok, count = ejecutar_compile_project(str(destino.resolve()), str(output_compilado.resolve()), script_dir)
    compile_status = "OK" if ok else "FAIL"

    # Generar reporte_final (markdown)
    summary = {
        "Directorio destino": str(destino.resolve()),
        "Archivos solicitados (n)": len(items),
        "Archivos encontrados (n)": len(encontrados),
        "Archivos copiados": encontrados,
        "Archivos no encontrados (n)": len(no_encontrados),
        "Archivo rutas no resueltas": str(output_no_resueltas.resolve()),
        "Compile_project status": compile_status,
        "Archivo compilado salida": str(output_compilado.resolve()) if ok else "No generado"
    }
    generar_reporte_integracion(reporte_final, summary)

    # Resumen por consola
    print("\n--- Resumen ---")
    print(f"Encontrados: {len(encontrados)}")
    print(f"No encontrados: {len(no_encontrados)}")
    print(f"Compile_project: {compile_status}")
    print(f"Reporte final: {reporte_final.resolve()}")
    print(f"Rutas no resueltas: {output_no_resueltas.resolve()}")

if __name__ == "__main__":
    main()