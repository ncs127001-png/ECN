#!/usr/bin/env python3
# coding: utf-8
"""
INYECTOR INTELIGENTE DE ESQUELETOS NEUROBIT
Arquitectura: NEUROBIT_DEV_TEAM
Propósito: Localizar código para archivos vacíos (<100 bytes) en discos externos,
           protegiendo los módulos ya consolidados contra downgrades.
"""
import os
import sys

# Rutas de los repositorios antiguos en el disco externo
RUTAS_ANTERIORES = [
    "/media/gus/354be58d-fbfc-461d-a0c3-f456cd336c27/home/oxo-nuxun-80-08-unxnu-oxo/neurobit_salon_v0.1",
    "/media/gus/354be58d-fbfc-461d-a0c3-f456cd336c27/home/oxo-nuxun-80-08-unxnu-oxo/WORKSPACE_NEUROBIT_V0.2"
]

def buscar_en_historicos(nombre_archivo):
    """Busca el archivo en las rutas viejas y devuelve la primera coincidencia que tenga contenido."""
    for ruta_base in RUTAS_ANTERIORES:
        if not os.path.exists(ruta_base):
            continue
        for raiz, _, archivos in os.walk(ruta_base):
            if nombre_archivo in archivos:
                ruta_candidata = os.path.join(raiz, nombre_archivo)
                # Verificar que el archivo encontrado no esté vacío también
                if os.path.getsize(ruta_candidata) > 100:
                    return ruta_candidata
    return None

def iniciar_recuperacion_segura():
    print("🛡️  INICIANDO INYECTOR SELECTIVO CONTRA DOWNGRADES v0.3")
    print("─" * 80)
    
    destino_v3 = "WORKSPACE_NEUROBIT_V0.3"
    if not os.path.exists(destino_v3):
        destino_v3 = input("🎯 No veo la carpeta en la raíz actual. Ingresa ruta de WORKSPACE_NEUROBIT_V0.3: ").strip()
        if not os.path.exists(destino_v3):
            print("❌ Error: Destino inalcanzable.")
            sys.exit(1)

    # Escaneo del destino buscando únicamente esqueletos vacíos
    for raiz_dest, _, archivos_dest in os.walk(destino_v3):
        if ".git" in raiz_dest:
            continue
            
        for archivo in archivos_dest:
            ruta_completa_dest = os.path.join(raiz_dest, archivo)
            tamano_dest = os.path.getsize(ruta_completa_dest)
            
            # FILTRO DE SEGURIDAD: Solo procesar si mide menos de 100 bytes (esqueleto base)
            if tamano_dest < 100:
                print(f"🔍 Detectado esqueleto vacío: {archivo} ({tamano_dest} bytes)")
                
                # Ir a cazar el código a los discos externos
                ruta_origen_antigua = buscar_en_historicos(archivo)
                
                if ruder_origen_antigua := ruta_origen_antigua:
                    tamano_orig = os.path.getsize(ruder_origen_antigua)
                    print(f"💡 ¡Código ancestral encontrado! -> {ruder_origen_antigua} ({tamano_orig} bytes)")
                    
                    # Confirmación interactiva en terminal (Control total del Nodo Semilla)
                    confirmacion = input(f"❓ ¿Deseas inyectar este archivo en {archivo}? (s/n): ").strip().lower()
                    
                    if confirmacion == 's':
                        with open(ruder_origen_antigua, "r", encoding="utf-8", errors="ignore") as f_src:
                            codigo_ancestral = f_src.read()
                        
                        with open(ruta_completa_dest, "w", encoding="utf-8") as f_dst:
                            f_dst.write(codigo_ancestral)
                            
                        if archivo.endswith(".sh"):
                            os.chmod(ruta_completa_dest, 0o755)
                            
                        print(f"✅ Inyección segura completada para: {archivo}\n")
                    else:
                        print("⏭️  Operación omitida por el Director.\n")
                else:
                    print(f"❌ No se encontró código con sustancia para '{archivo}' en los discos externos.\n")
            else:
                # Archivo seguro de más de 100 bytes, ni lo tocamos
                continue

    print("─" * 80)
    print("🕊️  Auditoría de esqueletos finalizada. Tu base de datos madura v0.3 está intacta.")

if __name__ == "__main__":
    try:
        iniciar_recuperacion_segura()
    except KeyboardInterrupt:
        print("\n🛑 Resguardo activado por el operador.")

