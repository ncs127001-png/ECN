import os
import json
from datetime import datetime

def obtener_extensiones():
    ext_nativas = ['.md', '.jsonl', '.json', '.js', '.c', '.sh', '.py', '.html', '.h', '.yaml', '.log']
    print("\n=== CONFIGURACIÓN DE EXTENSIONES ===")
    print("Extensiones soportadas:", ", ".join(ext_nativas))
    print("1) Elegir un conjunto personalizado (ej: .py, .json)")
    print("2) Responder Sí/No para cada una de las extensiones de la lista")
    
    opcion = input("Seleccione una opción (1 o 2): ").strip()
    ext_seleccionadas = []
    
    if opcion == "1":
        entrada = input("Ingrese las extensiones separadas por coma (ej: .py, .md): ")
        ext_seleccionadas = [e.strip().lower() for e in entrada.split(",") if e.strip()]
    else:
        for ext in ext_nativas:
            resp = input(f"¿Incluir [{ext}]? (s/n): ").strip().lower()
            if resp == 's':
                ext_seleccionadas.append(ext)
                
    return ext_seleccionadas

def mapear_workspaces():
    os.makedirs("integrador_control", exist_ok=True)
    
    try:
        cant_ws = int(input("¿Cuántos espacios de trabajo (Workspaces) va a integrar?: "))
    except ValueError:
        print("Por favor, ingrese un número válido.")
        return

    workspaces = {}
    ext_filtro = obtener_extensiones()
    print(f"\nExtensiones activas para el análisis: {ext_filtro}\n")

    for i in range(1, cant_ws + 1):
        while True:
            ruta = input(f"Ingrese la ubicación exacta (Ruta absoluta) del WS #{i}: ").strip()
            if os.path.exists(ruta) and os.path.isdir(ruta):
                workspaces[f"WS_V[{i}]"] = os.path.abspath(ruta)
                break
            print("❌ La ruta no existe o no es una carpeta válida. Intente de nuevo.")

    with open("integrador_control/config_ws.json", "w", encoding="utf-8") as f:
        json.dump(workspaces, f, indent=4, ensure_ascii=False)

    for ws_id, ruta_base in workspaces.items():
        archivo_mapa = f"integrador_control/mapa_bruto_{ws_id.replace('[','').replace(']','')}.txt"
        print(f"Mapeando {ws_id} -> {ruta_base}...")
        
        conteo_archivos = 0
        conteo_omitidos = 0
        
        with open(archivo_mapa, "w", encoding="utf-8") as f_out:
            f_out.write(f"WORKSPACE ID: {ws_id}\n")
            f_out.write(f"RUTA REAL: {ruta_base}\n")
            f_out.write("-" * 60 + "\n")
            
            for raiz, carpetas, archivos in os.walk(ruta_base):
                for archivo in archivos:
                    _, ext = os.path.splitext(archivo)
                    if ext.lower() in ext_filtro:
                        ruta_completa = os.path.join(raiz, archivo)
                        ruta_relativa = os.path.relpath(ruta_completa, ruta_base)
                        
                        try:
                            # Validar que no sea un enlace roto antes de procesar
                            if os.path.islink(ruta_completa) and not os.path.exists(os.path.realpath(ruta_completa)):
                                conteo_omitidos += 1
                                continue
                                
                            stats = os.stat(ruta_completa)
                            tamano = stats.st_size
                            fecha_mod = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                            
                            f_out.write(f"{ruta_relativa} | TAM: {tamano} bytes | MOD: {fecha_mod}\n")
                            conteo_archivos += 1
                        except (FileNotFoundError, PermissionError):
                            # Captura enlaces rotos fantasmas o archivos sin permisos de lectura
                            conteo_omitidos += 1
                            continue
                        
        print(f"   ✅ Creado {archivo_mapa} ({conteo_archivos} válidos, {conteo_omitidos} omitidos por enlaces rotos/errores).")

    print("\n=== FASE 1 COMPLETADA ===")
    print("Se han generado los mapas brutos de forma segura en 'integrador_control'.")

if __name__ == "__main__":
    mapear_workspaces()

