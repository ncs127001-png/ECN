import os
import re
from pathlib import Path

def limpiar_nombre_carpeta(nombre_sucio):
    """
    Elimina caracteres no válidos para nombres de carpetas en Windows/Linux
    y limpia asteriscos o puntos sobrantes de los patrones de búsqueda.
    """
    # Elimina caracteres prohibidos en sistemas de archivos
    caracteres_invalidos = r'[<>:"/\\|?*]'
    nombre_limpio = re.sub(caracteres_invalidos, '', nombre_sucio)
    # Elimina puntos y espacios al inicio y final (ej: "neurobit.." -> "neurobit")
    nombre_limpio = nombre_limpio.strip('. ') 
    return nombre_limpio

def renombrar_carpetas_resultados(directorio_raiz, modo_simulacion=False):
    """
    Busca carpetas RESULTADOS_N, lee su informe_bruto.txt y las renombra.
    
    :param directorio_raiz: Ruta donde están las carpetas RESULTADOS_
    :param modo_simulacion: Si es True, solo muestra lo que haría sin renombrar (Recomendado)
    """
    ruta_base = Path(directorio_raiz)
    
    if not ruta_base.is_dir():
        print(f"❌ Error: El directorio '{directorio_raiz}' no existe o no es válido.")
        return

    # Busca solo carpetas que empiecen con "RESULTADOS_" y tengan números
    patron_carpeta = re.compile(r'^RESULTADOS_\d+$')
    carpetas_objetivo = [d for d in ruta_base.iterdir() if d.is_dir() and patron_carpeta.match(d.name)]

    if not carpetas_objetivo:
        print("⚠️ No se encontraron carpetas con el patrón 'RESULTADOS_[N]'.")
        return

    print(f"🔍 Se encontraron {len(carpetas_objetivo)} carpetas para procesar.\n")
    if modo_simulacion:
        print("⚠️ MODO SIMULACIÓN ACTIVADO (No se aplicarán los cambios reales)\n")

    for carpeta in carpetas_objetivo:
        archivo_informe = carpeta / "informe_bruto.txt"
        
        if not archivo_informe.exists():
            print(f"⚠️ [SALTADO] '{carpeta.name}': No contiene 'informe_bruto.txt'.")
            continue

        nuevo_nombre = None
        
        # Leer las primeras líneas del informe para encontrar el patrón
        try:
            with open(archivo_informe, 'r', encoding='utf-8') as f:
                for linea in f:
                    # Busca la línea que empieza con "Archivos:"
                    match = re.match(r'^Archivos:\s*(.*)', linea)
                    if match:
                        nombre_extraido = match.group(1).strip()
                        nuevo_nombre = limpiar_nombre_carpeta(nombre_extraido)
                        break
                    
                    # Seguridad: no leer el archivo entero si es muy grande
                    if f.tell() > 2000: 
                        break
        except Exception as e:
            print(f"❌ Error leyendo '{archivo_informe}': {e}")
            continue

        if not nuevo_nombre:
            print(f"⚠️ [SALTADO] '{carpeta.name}': No se encontró el patrón 'Archivos:' en el encabezado.")
            continue

        ruta_nueva = carpeta.parent / nuevo_nombre

        # Verificar si la carpeta de destino ya existe para evitar sobrescrituras
        if ruta_nueva.exists():
            print(f"⚠️ [SALTADO] '{carpeta.name}': La carpeta destino '{nuevo_nombre}' ya existe.")
            continue

        # Ejecutar o simular el renombrado
        if modo_simulacion:
            print(f"✅ [SIMULACIÓN] '{carpeta.name}'  --->  '{nuevo_nombre}'")
        else:
            try:
                carpeta.rename(ruta_nueva)
                print(f"✅ [RENOMBRADO] '{carpeta.name}'  --->  '{nuevo_nombre}'")
            except Exception as e:
                print(f"❌ Error al renombrar '{carpeta.name}': {e}")

# ==========================================
# EJECUCIÓN DEL MÓDULO
# ==========================================
if __name__ == "__main__":
    # Cambia esta ruta por tu directorio real
    RUTA_DE_TRABAJO = "neurobit_file_explorer" 
    
    # PASO 1: Ejecutar en modo simulación (True) para revisar que todo esté bien
    renombrar_carpetas_resultados(RUTA_DE_TRABAJO, modo_simulacion=True)
    
    # PASO 2: Si los resultados de arriba te convencen, cambia a False para aplicar
    # renombrar_carpetas_resultados(RUTA_DE_TRABAJO, modo_simulacion=False)
