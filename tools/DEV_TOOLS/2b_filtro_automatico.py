import os
import re
from datetime import datetime

def parsear_linea(linea):
    """Extrae metadatos clave de una línea del listado."""
    partes = [p.strip() for p in linea.split("|")]
    if len(partes) < 6:
        return None
    
    ws_id = partes[1]
    tamano = int(re.search(r'TAM: (\d+) bytes', partes[3]).group(1))
    fecha_str = re.search(r'MOD: (.*?)$', partes[4]).group(1)
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d %H:%M:%S')
    ruta_original = partes[5].replace("ORIGINAL:", "").strip()
    
    return {
        "linea_original": linea,
        "ws_id": ws_id,
        "tamano": tamano,
        "fecha": fecha,
        "ruta_original": ruta_original
    }

def filtrar_listado():
    archivo_entrada = "integrador_control/lista_revision_manual.txt"
    archivo_salida = "integrador_control/lista_revision_manual_DEPURADA.txt"
    
    if not os.path.exists(archivo_entrada):
        print(f"❌ No se encuentra el archivo {archivo_entrada}")
        return

    print("扫 Iniciando pre-procesamiento automático de la lista de revisión...")
    
    lineas_salida = []
    conteo_omitidos_venv = 0
    conteo_conflictos_resueltos = 0
    
    with open(archivo_entrada, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    i = 0
    total_lineas = len(lineas)
    
    # Copiar encabezados iniciales hasta encontrar datos
    while i < total_lineas:
        linea = lineas[i].strip()
        if linea.startswith("MIGRACION_DIRECTA") or linea.startswith("--- CONFLICTO"):
            break
        lineas_salida.append(lineas[i])
        i += 1

    # Procesar el cuerpo del listado
    while i < total_lineas:
        linea = lineas[i].strip()
        
        if not linea:
            lineas_salida.append(lineas[i])
            i += 1
            continue

        # 1. FILTRO DE EXCLUSIÓN: Descartar entornos virtuales y dependencias dispersas
        if ".venv/" in linea or "/venv/" in linea or "/python3" in linea:
            conteo_omitidos_venv += 1
            i += 1
            continue

        # 2. PROCESAMIENTO DE BLOQUES DE CONFLICTO
        if linea.startswith("--- CONFLICTO DETECTADO EN:"):
            bloque_conflictos = []
            i += 1
            
            # Recolectar todas las líneas dentro de este bloque de conflicto específico
            while i < total_lineas and not lineas[i].strip().startswith("--- FIN CONFLICTO ---"):
                lin_interna = lineas[i].strip()
                if ".venv/" in lin_interna or "/venv/" in lin_interna or "/python3" in lin_interna:
                    conteo_omitidos_venv += 1
                elif lin_interna.startswith("CONFLICTO"):
                    datos = parsear_linea(lin_interna)
                    if datos:
                        bloque_conflictos.append(datos)
                i += 1
            
            # Saltarse la línea de '--- FIN CONFLICTO ---'
            if i < total_lineas:
                i += 1 

            # Resolver el bloque de conflicto recolectado
            if not bloque_conflictos:
                continue
                
            if len(bloque_conflictos) == 1:
                item = bloque_conflictos[0]
                nueva_linea = item["linea_original"].replace("CONFLICTO", "MIGRACION_DIRECTA")
                lineas_salida.append(nueva_linea + "\n")
                conteo_conflictos_resueltos += 1
            else:
                # Ordenar: Más reciente primero, luego por tamaño (evitando el doble de tamaño artificial)
                # y priorizando los WS más avanzados (V0.3 / WS_V[4])
                bloque_conflictos.sort(key=lambda x: (x["fecha"], x["ws_id"], -x["tamano"]), reverse=True)
                
                ganador = bloque_conflictos[0]
                nueva_linea = ganador["linea_original"].replace("CONFLICTO", "MIGRACION_DIRECTA")
                
                lineas_salida.append(f"MIGRACION_DIRECTA | {ganador['ws_id']} | {ganador['ruta_original']} (Auto-Resuelto)\n")
                conteo_conflictos_resueltos += 1

        # 3. PROCESAMIENTO DE MIGRACIONES DIRECTAS COMUNES
        elif linea.startswith("MIGRACION_DIRECTA"):
            lineas_salida.append(lineas[i])
            i += 1
        else:
            i += 1

    # Escribir los resultados en el archivo depurado final
    with open(archivo_salida, "w", encoding="utf-8") as f_out:
        f_out.writelines(lineas_salida)

    print("\n=== FASE INTERMEDIA COMPLETADA ===")
    print(f"Líneas de entornos virtuales (.venv/python3) eliminadas: {conteo_omitidos_venv}")
    print(f"Bloques de conflicto resueltos algorítmicamente: {conteo_conflictos_resueltos}")
    print(f"👉 Archivo optimizado generado en: '{archivo_salida}'")

if __name__ == "__main__":
    filtrar_listado()

