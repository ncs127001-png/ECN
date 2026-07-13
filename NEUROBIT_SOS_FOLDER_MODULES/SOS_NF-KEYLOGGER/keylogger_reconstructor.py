import json
import os

# Diccionario de traducción para teclas especiales comunes
MAPA_TECLAS = {
    "KEY_SPACE": " ",
    "KEY_ENTER": "\n",
    "KEY_TAB": "\t",
    # Añadir mapeos adicionales según sea necesario
}

def procesar_log_teclado(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        print(f"Error: El archivo '{ruta_archivo}' no existe.")
        return

    texto_reconstruido = []
    ultima_tecla = None

    print(f"Procesando '{ruta_archivo}'...")
    
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        for num_linea, linea in enumerate(archivo, 1):
            linea = linea.strip()
            if not linea:
                continue
                
            try:
                # Procesar línea por línea para evitar cargar archivos masivos en memoria
                datos = json.loads(linea)
                tecla_raw = datos.get("key", "")
                
                # Ignorar modificadores directos en la reconstrucción simple de texto
                if "SHIFT" in tecla_raw or "CTRL" in tecla_raw or "ALT" in tecla_raw:
                    continue
                
                # Filtrar repeticiones consecutivas causadas por eventos repetidos (down/up)
                if tecla_raw == ultima_tecla:
                    continue
                
                ultima_tecla = tecla_raw
                
                # Gestionar la tecla de retroceso (Borrar último carácter)
                if tecla_raw == "KEY_BACKSPACE":
                    if texto_reconstruido:
                        texto_reconstruido.pop()
                    continue

                # Traducir o limpiar el nombre de la tecla
                if tecla_raw in MAPA_TECLAS:
                    caracter = MAPA_TECLAS[tecla_raw]
                elif tecla_raw.startswith("KEY_"):
                    # Extraer la letra (ej. "KEY_E" -> "e")
                    caracter = tecla_raw.replace("KEY_", "").lower()
                else:
                    caracter = tecla_raw

                texto_reconstruido.append(caracter)

            except json.JSONDecodeError:
                print(f"Advertencia: Línea {num_linea} no es un JSON válido. Omitiendo...")
                continue

    # Unir la lista para formar el mensaje final
    mensaje_final = "".join(texto_reconstruido)
    
    print("\n--- Mensaje Reconstruido ---")
    print(mensaje_final)
    print("----------------------------\n")

if __name__ == "__main__":
    archivo_entrada = input("Introduce el nombre o ruta del archivo de registro: ").strip()
    procesar_log_teclado(archivo_entrada)

