import os
import json
import shutil

def ejecutar_migracion():
    config_ruta = "integrador_control/config_ws.json"
    archivo_revision = "integrador_control/lista_revision_manual_DEPURADA.txt"
    destino_base = "workspaces_integrated"

    if not os.path.exists(config_ruta) or not os.path.exists(archivo_revision):
        print("❌ Faltan archivos esenciales. Asegúrese de haber corrido las fases 1 y 2.")
        return

    with open(config_ruta, "r", encoding="utf-8") as f:
        workspaces = json.load(f)

    print("🚀 Iniciando lectura de la lista depurada manualmente...")
    
    # Crear la carpeta final si no existe
    os.makedirs(destino_base, exist_ok=True)

    conteo_migrados = 0
    conteo_errores = 0

    with open(archivo_revision, "r", encoding="utf-8") as f_rev:
        for num_linea, linea in enumerate(f_rev, 1):
            linea = linea.strip()
            
            # Ignorar encabezados, instrucciones, comentarios o líneas en blanco
            if not linea or linea.startswith("==") or linea.startswith("INSTRUCCIONES") or linea.startswith("---") or linea.startswith("1.") or linea.startswith("2.") or linea.startswith("3.") or linea.startswith("4."):
                continue

            partes = [p.strip() for p in linea.split("|")]
            
            # Validar formato esperado de línea de datos
            if len(partes) < 6:
                continue

            tipo_registro = partes[0]      # MIGRACION_DIRECTA o CONFLICTO
            ws_id = partes[1]              # WS_V[nro.]
            # partes[2] es la ruta_virtual con prefijo (no la usamos para copiar)
            # partes[3] es TAM, partes[4] es MOD
            ruta_original_rel = partes[5].replace("ORIGINAL:", "").strip() # Ruta limpia real

            # Obtener la ruta absoluta del Workspace de origen
            ruta_ws_origen = workspaces.get(ws_id)
            if not ruta_ws_origen:
                print(f"⚠️ Advertencia en línea {num_linea}: No se reconoció el Workspace '{ws_id}'")
                conteo_errores += 1
                continue

            # Construir rutas físicas finales en disco
            origen_fisico = os.path.join(ruta_ws_origen, ruta_original_rel)
            destino_fisico = os.path.join(destino_base, ruta_original_rel)

            # Verificar que el archivo de origen realmente exista en el disco antes de copiar
            if not os.path.exists(origen_fisico):
                print(f"❌ Archivo no encontrado físicamente: {origen_fisico}")
                conteo_errores += 1
                continue

            try:
                # Asegurar que la subcarpeta destino exista (Manejo automático de subcarpetas unificadas)
                os.makedirs(os.path.dirname(destino_fisico), exist_ok=True)
                
                # Copiar archivo preservando metadatos originales (fecha de mod/creación)
                shutil.copy2(origen_fisico, destino_fisico)
                conteo_migrados += 1
            except Exception as e:
                print(f"❌ Error al copiar {ruta_original_rel}: {e}")
                conteo_errores += 1

    print("\n==========================================")
    print("===      INTEGRACIÓN FINALIZADA        ===")
    print("==========================================")
    print(f"Archivos copiados con éxito: {conteo_migrados}")
    print(f"Errores encontrados durante la copia: {conteo_errores}")
    print(f"📂 Revisa tu nuevo espacio limpio en la carpeta: '{destino_base}'")

if __name__ == "__main__":
    ejecutar_migracion()

