import os
import shutil
import argparse
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
    parser = argparse.ArgumentParser(description='Busca archivos desde una lista y los copia a un destino')
    parser.add_argument('--list', required=True, help='Archivo .txt con lista de archivos a buscar')
    parser.add_argument('--source', required=True, help='Directorio origen para búsqueda recursiva')
    parser.add_argument('--dest', required=True, help='Directorio destino para archivos encontrados')
    
    args = parser.parse_args()
    
    # Verificar que los directorios existen
    if not os.path.exists(args.source):
        print(f"❌ Error: El directorio de origen no existe: {args.source}")
        return
    
    # Crear carpeta destino si no existe
    Path(args.dest).mkdir(parents=True, exist_ok=True)
    
    # Leer lista de archivos
    try:
        with open(args.list, 'r', encoding='utf-8') as f:
            archivos_a_buscar = [linea.strip() for linea in f if linea.strip()]
        print(f"\n📋 Archivos a buscar ({len(archivos_a_buscar)}):")
        for i, archivo in enumerate(archivos_a_buscar, 1):
            print(f"  {i}. {archivo}")
    except Exception as e:
        print(f"\n❌ Error al leer el archivo de lista: {str(e)}")
        return
    
    # Buscar y copiar archivos
    print("\n" + "="*50)
    print("🚀 INICIANDO BÚSQUEDA Y COPIA")
    print("="*50)
    
    encontrados = 0
    no_encontrados = []
    
    for nombre_archivo in archivos_a_buscar:
        print(f"\n🔎 Buscando: '{nombre_archivo}'")
        ruta_encontrada = buscar_archivo_recursivo(nombre_archivo, args.source)
        
        if ruta_encontrada:
            try:
                destino = os.path.join(args.dest, os.path.basename(ruta_encontrada))
                # Evitar sobrescritura añadiendo sufijo numérico si existe
                contador = 1
                while os.path.exists(destino):
                    nombre_base, extension = os.path.splitext(os.path.basename(ruta_encontrada))
                    destino = os.path.join(args.dest, f"{nombre_base}_{contador}{extension}")
                    contador += 1
                
                shutil.copy2(ruta_encontrada, destino)
                print(f"✅ ¡Encontrado! Copiado a: {destino}")
                encontrados += 1
            except Exception as e:
                print(f"❌ Error al copiar '{ruta_encontrada}': {str(e)}")
        else:
            print(f"❌ No encontrado en {args.source}")
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
    
    print(f"\n🎉 ¡Proceso completado! Todos los archivos recolectados en:\n   {args.dest}")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operación cancelada por el usuario.")
    except Exception as e:
        print(f"\n❌ Error crítico no manejado: {str(e)}")
