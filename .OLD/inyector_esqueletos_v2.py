#!/usr/bin/env python3
# coding: utf-8
"""
INYECTOR SELECTIVO E INFALIBLE NEUROBIT v0.3
Arquitectura: NEUROBIT_DEV_TEAM
Propósito: Rescatar esqueletos vacíos combinando rutas rápidas con un 'find'
           global indexado en archivo .log. Evita downgrades y ruido de permisos.
"""
import os
import sys
import subprocess

# Configuración de persistencia inmutable de auditoría
LOG_FILE = "migracion_busqueda.log"

RUTAS_RAPIDAS = [
    "/media/gus/354be58d-fbfc-461d-a0c3-f456cd336c27/home/oxo-nuxun-80-08-unxnu-oxo/neurobit_salon_v0.1",
    "/media/gus/354be58d-fbfc-461d-a0c3-f456cd336c27/home/oxo-nuxun-80-08-unxnu-oxo/WORKSPACE_NEUROBIT_V0.2"
]

def registrar_log(mensaje):
    """Guarda la traza forense de la búsqueda en modo append-only."""
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(mensaje + "\n")

def buscar_find_total(nombre_archivo):
    """Opción infalible: Ejecuta un find total redirigiendo errores a /dev/null."""
    registrar_log(f"🔍 Activando Opción Infalible: find global para '{nombre_archivo}'...")
    try:
        # Busca en /home y en /media para cubrir el sistema y discos externos
        comando = f"find /home /media -name '{nombre_archivo}' 2>/dev/null"
        resultado = subprocess.check_output(comando, shell=True, text=True)
        lineas = [l.strip() for l in resultado.split("\n") if l.strip()]
        
        # Filtrar candidatos que tengan sustancia (>100 bytes)
        for candidato in lineas:
            if os.path.exists(candidato) and os.path.getsize(candidato) > 100:
                # Evitar que se encuentre a sí mismo en la carpeta v0.3
                if "WORKSPACE_NEUROBIT_V0.3" not in candidato:
                    return candidato
    except Exception as e:
        registrar_log(f"❌ Error en find total para {nombre_archivo}: {str(e)}")
    return None

def buscar_codigo_ancestro(nombre_archivo):
    """Busca primero en rutas rápidas; si falla, ejecuta el find total."""
    # 1. Intento en rutas conocidas
    for ruta_base in RUTAS_RAPIDAS:
        if os.path.exists(ruta_base):
            for raiz, _, archivos in os.walk(ruta_base):
                if nombre_archivo in archivos:
                    ruta = os.path.join(raiz, nombre_archivo)
                    if os.path.getsize(ruta) > 100:
                        registrar_log(f"🎯 Localizado en ruta rápida: {ruta}")
                        return ruta
                        
    # 2. Segunda opción infalible si la primera falla
    return buscar_find_total(nombre_archivo)

def iniciar_inyeccion_infalible():
    print("🛡️  INYECTOR INFALIBLE CON LOG DE AUDITORÍA v0.3")
    print(f"📝 Registrando traza forense en: {LOG_FILE}")
    print("─" * 80)
    
    with open(LOG_FILE, "w", encoding="utf-8") as log:
        log.write("=== LOG DE AUDITORÍA MIGRACIÓN NEUROBIT v0.3 ===\n")
        
    destino_v3 = "WORKSPACE_NEUROBIT_V0.3"
    if not os.path.exists(destino_v3):
        print("❌ No se detecta 'WORKSPACE_NEUROBIT_V0.3' en la raíz actual.")
        sys.exit(1)

    for raiz_dest, _, archivos_dest in os.walk(destino_v3):
        if ".git" in raiz_dest or "data/logs" in raiz_dest:
            continue
            
        for archivo in archivos_dest:
            # Saltarse archivos de persistencia que el operador ya controló
            if archivo in ["memoria_eva.jsonl", "tareas_pendientes.jsonl"]:
                continue
                
            ruta_completa_dest = os.path.join(raiz_dest, archivo)
            tamano_dest = os.path.getsize(ruta_completa_dest)
            
            # FILTRO: Solo procesar plantillas o esqueletos (< 100 bytes)
            if tamano_dest < 100:
                print(f"📦 Analizando esqueleto vacío: {archivo}")
                registrar_log(f"\n--- Procesando: {archivo} ({tamano_dest} bytes) ---")
                
                ruta_ancestro = buscar_codigo_ancestro(archivo)
                
                if ruta_ancestro:
                    tamano_orig = os.path.getsize(ruta_ancestro)
                    print(f"⚡ ¡Código localizado en el sistema!")
                    print(f"   -> {ruta_ancestro} ({tamano_orig} bytes)")
                    
                    confirmar = input(f"❓ ¿Inyectar código en {archivo}? (s/n): ").strip().lower()
                    if confirmar == 's':
                        with open(ruta_ancestro, "r", encoding="utf-8", errors="ignore") as f_src:
                            codigo = f_src.read()
                        with open(ruta_completa_dest, "w", encoding="utf-8") as f_dst:
                            f_dst.write(codigo)
                        if archivo.endswith(".sh"):
                            os.chmod(ruta_completa_dest, 0o755)
                        print(f"✅ Sustitución exitosa.\n")
                        registrar_log(f"✅ Inyectado con éxito desde: {ruta_ancestro}")
                    else:
                        print("⏭️  Omitido por el Director.\n")
                        registrar_log("⏭️ Omitido por decisión del operador.")
                else:
                    print(f"❌ Archivo inalcanzable en el almacenamiento histórico.\n")
                    registrar_log(f"❌ No se encontró coincidencia útil para {archivo}")

    print("─" * 80)
    print("🕊️  Búsqueda total completada. Tu base de datos madura v0.3 está a salvo.")

if __name__ == "__main__":
    try:
        iniciar_inyeccion_infalible()
    except KeyboardInterrupt:
        print("\n🛑 Resguardo activado por el operador Nodo Semilla.")

