import os
import json
import re

def cargar_mapa_bruto(archivo_ruta):
    """Lee un archivo de mapa bruto y extrae los datos de los archivos."""
    archivos_datos = {}
    if not os.path.exists(archivo_ruta):
        return archivos_datos
        
    linea_regex = re.compile(r'^(.*?) \| TAM: (\d+) bytes \| MOD: (.*?)$')
    
    with open(archivo_ruta, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            match = linea_regex.match(linea)
            if match:
                ruta_relativa, tamano, fecha_mod = match.groups()
                archivos_datos[ruta_relativa] = {
                    "tamano": int(tamano),
                    "fecha": fecha_mod
                }
    return archivos_datos

def procesar_colisiones():
    config_ruta = "integrador_control/config_ws.json"
    if not os.path.exists(config_ruta):
        print("❌ No se encontró la configuración de la Fase 1. Ejecute 1_descubrimiento.py primero.")
        return

    with open(config_ruta, "r", encoding="utf-8") as f:
        workspaces = json.load(f)

    # Diccionario maestro para agrupar por ruta relativa de archivo
    # Clave: ruta_relativa -> Valor: { ws_id: {tamano, fecha}, ... }
    universo_archivos = {}

    # Cargar todos los mapas brutos en memoria
    for ws_id in workspaces.keys():
        ws_limpio = ws_id.replace('[','').replace(']','')
        archivo_mapa = f"integrador_control/mapa_bruto_{ws_limpio}.txt"
        
        print(f"Cargando datos de {ws_id}...")
        datos_ws = cargar_mapa_bruto(archivo_mapa)
        
        for ruta_rel, metadatos in datos_ws.items():
            if ruta_rel not in universo_archivos:
                universo_archivos[ruta_rel] = {}
            universo_archivos[ruta_rel][ws_id] = metadatos

    # Generar el archivo de texto para revisión manual
    archivo_revision = "integrador_control/lista_revision_manual.txt"
    print(f"\nAnalizando colisiones y escribiendo listado limpio en '{archivo_revision}'...")
    
    conteo_unicos = 0
    conteo_conflictos = 0

    with open(archivo_revision, "w", encoding="utf-8") as f_out:
        f_out.write("=== LISTA DE REVISIÓN MANUAL DE MIGRACIÓN ===\n")
        f_out.write("INSTRUCCIONES:\n")
        f_out.write("1. Revisa los bloques de archivos repetidos (CONFLICTO).\n")
        f_out.write("2. Deja ÚNICAMENTE la línea del archivo que deseas mantener.\n")
        f_out.write("3. BORRA por completo las líneas de los archivos que desees descartar.\n")
        f_out.write("4. Las carpetas únicas y archivos sin conflicto se migrarán automáticamente si no los borras.\n")
        f_out.write("=" * 80 + "\n\n")

        # Ordenar las rutas relativas alfabéticamente para mantener un orden de carpetas
        for ruta_rel in sorted(universo_archivos.keys()):
            origenes = universo_archivos[ruta_rel]
            
            # Caso 1: El archivo existe en un solo Workspace (Sin conflicto)
            if len(origenes) == 1:
                ws_id = list(origenes.keys())[0]
                meta = origenes[ws_id]
                # Prefijado lógico sugerido: WS_V[nro.]_nombre
                nombre_dir, nombre_archivo = os.path.split(ruta_rel)
                prefijo_virtual = f"{ws_id}_{nombre_archivo}"
                ruta_virtual = os.path.join(nombre_dir, prefijo_virtual) if nombre_dir else prefijo_virtual
                
                f_out.write(f"MIGRACION_DIRECTA | {ws_id} | {ruta_virtual} | TAM: {meta['tamano']} bytes | MOD: {meta['fecha']} | ORIGINAL: {ruta_rel}\n")
                conteo_unicos += 1
                
            # Caso 2: El archivo se repite en varios Workspaces (Conflicto / Colisión)
            else:
                f_out.write(f"--- CONFLICTO DETECTADO EN: {ruta_rel} ---\n")
                conteo_conflictos += 1
                for ws_id, meta in origenes.items():
                    nombre_dir, nombre_archivo = os.path.split(ruta_rel)
                    prefijo_virtual = f"{ws_id}_{nombre_archivo}"
                    ruta_virtual = os.path.join(nombre_dir, prefijo_virtual) if nombre_dir else prefijo_virtual
                    
                    f_out.write(f"CONFLICTO | {ws_id} | {ruta_virtual} | TAM: {meta['tamano']} bytes | MOD: {meta['fecha']} | ORIGINAL: {ruta_rel}\n")
                f_out.write(f"--- FIN CONFLICTO ---\n\n")

    print(f"\n=== FASE 2 COMPLETADA ===")
    print(f"Archivos sin conflicto (Migración directa): {conteo_unicos}")
    print(f"Archivos en conflicto (Requieren tu decisión): {conteo_conflictos}")
    print(f"👉 Por favor, abre y edita: '{archivo_revision}' antes de continuar.")

if __name__ == "__main__":
    procesar_colisiones()

