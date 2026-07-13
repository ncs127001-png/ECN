import os
import shutil
import sys
from pathlib import Path

def buscar_archivo_recursivo(nombre_archivo, directorio_actual):
    """
    Función recursiva que busca un archivo en un directorio y sus subdirectorios.
    Devuelve la ruta completa si lo encuentra, None si no.
    """
    try:
        # Listar contenido del directorio actual
        for elemento in os.listdir(directorio_actual):
            ruta_completa = os.path.join(directorio_actual, elemento)
            
            # Si es un archivo y coincide el nombre (case-insensitive)
            if os.path.isfile(ruta_completa) and elemento.lower() == nombre_archivo.lower():
                return ruta_completa
            
            # Si es un directorio (y no un enlace simbólico), buscar recursivamente
            elif os.path.isdir(ruta_completa) and not os.path.islink(ruta_completa):
                resultado = buscar_archivo_recursivo(nombre_archivo, ruta_completa)
                if resultado:
                    return resultado
    except PermissionError:
        print(f"⚠️  Permiso denegado al acceder: {directorio_actual}")
    except Exception as e:
        print(f"❌ Error inesperado en {directorio_actual}: {str(e)}")
    
    return None

def main():
    print("="*50)
    print("🔍 BUSCADOR Y RECOLECTOR DE ARCHIVOS")
    print("="*50)
    
    # Obtener directorio raíz donde se ejecuta el script
    directorio_raiz = os.path.dirname(os.path.abspath(__file__))
    print(f"\n📁 Directorio raíz actual: {directorio_raiz}")
    
    # 1. Cargar lista de archivos a localizar
    while True:
        lista_archivos = input("\n📄 Ingresa la ruta del archivo .txt con la lista de nombres (o 'salir' para terminar): ").strip()
        
        if lista_archivos.lower() == 'salir':
            print("\n👋 ¡Hasta luego!")
            sys.exit(0)
        
        # Ruta relativa al directorio raíz si no es absoluta
        if not os.path.isabs(lista_archivos):
            lista_archivos = os.path.join(directorio_raiz, lista_archivos)
        
        if os.path.isfile(lista_archivos):
            break
        print(f"\n❌ Error: El archivo '{lista_archivos}' no existe. Verifica la ruta.")
    
    # 2. Nombre de la carpeta de destino
    while True:
        carpeta_destino = input("\n📂 Ingresa el nombre para la carpeta de destino: ").strip()
        if carpeta_destino:
            break
        print("❌ El nombre no puede estar vacío.")
    
    ruta_destino = os.path.join(directorio_raiz, carpeta_destino)
    
    # 3. Directorio base para búsqueda
    directorio_busqueda = input("\n🔍 Ingresa el directorio base para búsqueda (dejar en blanco para usar el raíz actual): ").strip()
    if not directorio_busqueda:
        directorio_busqueda = directorio_raiz
    elif not os.path.isabs(directorio_busqueda):
        directorio_busqueda = os.path.join(directorio_raiz, directorio_busqueda)
    
    if not os.path.isdir(directorio_busqueda):
        print(f"\n❌ Error: El directorio '{directorio_busqueda}' no existe.")
        sys.exit(1)
    
    print("\n" + "="*50)
    print(f"⚙️  Configuración final:")
    print(f"• Archivo lista: {lista_archivos}")
    print(f"• Directorio búsqueda: {directorio_busqueda}")
    print(f"• Carpeta destino: {ruta_destino}")
    print("="*50)
    
    # Crear carpeta destino si no existe
    try:
        Path(ruta_destino).mkdir(parents=True, exist_ok=True)
        print(f"\n✅ Carpeta destino creada/verificada: {ruta_destino}")
    except Exception as e:
        print(f"\n❌ Error al crear carpeta destino: {str(e)}")
        sys.exit(1)
    
    # Leer lista de archivos
    try:
        with open(lista_archivos, 'r', encoding='utf-8') as f:
            archivos_a_buscar = [linea.strip() for linea in f if linea.strip()]
        print(f"\n📋 Archivos a buscar ({len(archivos_a_buscar)}):")
        for i, archivo in enumerate(archivos_a_buscar, 1):
            print(f"  {i}. {archivo}")
    except Exception as e:
        print(f"\n❌ Error al leer el archivo de lista: {str(e)}")
        sys.exit(1)
    
    # Buscar y copiar archivos
    print("\n" + "="*50)
    print("🚀 INICIANDO BÚSQUEDA Y COPIA")
    print("="*50)
    
    encontrados = 0
    no_encontrados = []
    
    for nombre_archivo in archivos_a_buscar:
        print(f"\n🔎 Buscando: '{nombre_archivo}'")
        ruta_encontrada = buscar_archivo_recursivo(nombre_archivo, directorio_busqueda)
        
        if ruta_encontrada:
            try:
                destino = os.path.join(ruta_destino, os.path.basename(ruta_encontrada))
                # Evitar sobrescritura añadiendo sufijo numérico si existe
                contador = 1
                while os.path.exists(destino):
                    nombre_base, extension = os.path.splitext(os.path.basename(ruta_encontrada))
                    destino = os.path.join(ruta_destino, f"{nombre_base}_{contador}{extension}")
                    contador += 1
                
                shutil.copy2(ruta_encontrada, destino)
                print(f"✅ ¡Encontrado! Copiado a: {destino}")
                encontrados += 1
            except Exception as e:
                print(f"❌ Error al copiar '{ruta_encontrada}': {str(e)}")
        else:
            print(f"❌ No encontrado en {directorio_busqueda}")
            no_encontrados.append(nombre_archivo)
    
    # Resumen final
    print("\n" + "="*50)
    print("📊 RESUMEN FINAL")
    print("="*50)
    print(f"✓ Archivos encontrados y copiados: {encontrados}")
    print(f"✗ Archivos no encontrados: {len(no_encontrados)}")
    
    if no_encontrados:
        print("\n📝 Archivos no encontrados:")
        for archivo in no_encontrados:
            print(f"  • {archivo}")
        print(f"\n💡 Sugerencia: Verifica nombres de archivos en '{lista_archivos}'")
    
    print(f"\n🎉 ¡Proceso completado! Todos los archivos recolectados en:\n   {ruta_destino}")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operación cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error crítico no manejado: {str(e)}")
        sys.exit(1)