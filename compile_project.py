#!/usr/bin/env python3
"""
compile_project.py - Compila todos los archivos de un proyecto en un único documento de texto
con formato claro para análisis de equipo y documentación histórica.
"""

import os
import sys
import argparse
import datetime
import fnmatch
from pathlib import Path

def get_directory_tree(startpath, ignore_patterns=None):
    """Genera una representación en texto del árbol de directorios"""
    if ignore_patterns is None:
        ignore_patterns = ['.git', '__pycache__', '*.pyc', '*.egg-info', '.venv', 'venv', 'build', 'dist']
    
    tree = []
    startpath = Path(startpath)
    
    for root, dirs, files in os.walk(startpath):
        # Filtrar directorios ignorados
        dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in ignore_patterns)]
        
        level = root.replace(str(startpath), '').count(os.sep)
        indent = ' ' * 4 * level
        tree.append(f'{indent}{os.path.basename(root)}/')
        
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            if not any(fnmatch.fnmatch(f, pattern) for pattern in ignore_patterns):
                tree.append(f'{subindent}{f}')
                
    return '\n'.join(tree)

def should_ignore(path, ignore_patterns):
    """Verifica si un archivo o directorio debe ser ignorado"""
    path_str = str(path)
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(os.path.basename(path_str), pattern):
            return True
    return False

def compile_project(root_dir, output_file, ignore_patterns=None):
    """Compila todos los archivos del proyecto en un único documento"""
    if ignore_patterns is None:
        ignore_patterns = [
            '.git', '.gitignore', '__pycache__', '*.pyc', '*.egg-info', 
            '.venv', 'venv', 'build', 'dist', '*.log', '*.tmp', '*.bak',
            '*.sqlite', '*.db', '.env', '*.env', '*.env.*', '*.md~', 
            '.idea', '.vscode', '.DS_Store', '*.png', '*.jpg', '*.jpeg', 
            '*.gif', '*.ico', '*.pdf', '*.zip', '*.tar.gz', '*.tar.bz2'
        ]
    
    root_path = Path(root_dir).resolve()
    all_files = []
    
    # Recopilar todos los archivos relevantes
    for root, dirs, files in os.walk(root_path):
        # Filtrar directorios ignorados
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), ignore_patterns)]
        
        for file in files:
            file_path = Path(root) / file
            if not should_ignore(file_path, ignore_patterns):
                all_files.append(file_path)
    
    # Ordenar archivos por ruta
    all_files.sort()
    
    # Preparar el contenido del archivo de compilado
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    project_name = root_path.name
    
    content = []
    content.append(f"Compendio de Archivos del proyecto: '{project_name}';")
    content.append(f"Analisis_Date: ('{current_time}')")
    content.append(f"N_Archivos_Actuales: ({len(all_files)})")
    content.append("-" * 76)
    content.append("Arbol de directorios:")
    content.append(get_directory_tree(root_dir, ignore_patterns))
    content.append("-" * 76)
    content.append("----------------------LISTA DE ARCHIVOS-----------------------")
    
    # Añadir cada archivo con su contenido
    for idx, file_path in enumerate(all_files, 1):
        relative_path = file_path.relative_to(root_path)
        file_dir = file_path.parent.relative_to(root_path) if file_path.parent != root_path else "."
        
        content.append("_" * 60)
        content.append(f"ARCHIVO NRO. : ({idx})")
        content.append(f"Archivo: ('{file_path.name}');")
        content.append(f"Carpeta de ubicación: ('~/{project_name}/{file_dir}');")
        
        # Determinar función del archivo basado en su extensión y nombre
        file_ext = file_path.suffix.lower()
        function_desc = get_file_function(file_path.name, file_ext)
        content.append(f"función: ('{function_desc}')")
        
        # Variables de entorno relevantes (esto sería más complejo en un sistema real)
        env_vars = get_env_vars_for_file(file_path)
        if env_vars:
            content.append(f"Variables del entorno: ({', '.join(env_vars)})")
        else:
            content.append("Variables del entorno: (ninguna)")
            
        content.append("-" * 65 + "Inicio:")
        content.append("")
        
        # Leer contenido del archivo
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                content.append(file_content)
        except Exception as e:
            content.append(f"ERROR AL LEER EL ARCHIVO: {str(e)}")
            
        content.append("")
        content.append("FINAL" + "-" * 63)
    
    # Escribir el contenido compilado al archivo de salida
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    return len(all_files)

def get_file_function(filename, extension):
    """Devuelve una descripción de la función del archivo basada en su nombre y extensión"""
    # Reglas básicas para determinar la función del archivo
    if 'dispatcher' in filename.lower() and extension == '.py':
        return "Script para distribución de mensajes entre nodos (Postman automático)"
    elif 'validator' in filename.lower() and extension == '.py':
        return "Validación de mensajes y estructuras YAML/JSON"
    elif 'builder' in filename.lower() and extension == '.py':
        return "Construcción de mensajes según protocolo NEUROBIT"
    elif 'schema' in filename.lower() or extension == '.json':
        return "Definición de esquemas y contratos de mensajes"
    elif extension == '.md':
        return "Documentación del proyecto y protocolos"
    elif extension == '.yaml' or extension == '.yml':
        return "Configuración de metadatos y parámetros del sistema"
    elif extension == '.html':
        return "Interfaz de usuario para la bitácora y estación central"
    elif extension == '.js':
        return "Lógica de frontend y comunicación con el backend"
    elif extension == '.css':
        return "Estilos para la interfaz de usuario"
    elif 'requirements' in filename.lower() or 'pipfile' in filename.lower():
        return "Dependencias del proyecto Python"
    else:
        return "Archivo de propósito general - requiere revisión manual"

def get_env_vars_for_file(file_path):
    """Devuelve variables de entorno relevantes para el archivo (simulado para este ejemplo)"""
    filename = file_path.name.lower()
    
    if 'dispatcher' in filename:
        return ["NEUROBIT_BROKER_URL", "DISPATCHER_TIMEOUT", "MAX_RETRIES"]
    elif 'validator' in filename:
        return ["VALIDATION_SCHEMA_PATH"]
    elif 'builder' in filename:
        return ["MESSAGE_BUILDER_DEFAULT_NODE", "MESSAGE_BUILDER_SESSION_ID"]
    elif 'msg' in filename or 'message' in filename:
        return ["MESSAGE_PROTOCOL_VERSION"]
    else:
        return []

def main():
    parser = argparse.ArgumentParser(description='Compila todos los archivos de un proyecto en un único documento de texto')
    parser.add_argument('--project', '-p', required=True, help='Ruta al directorio raíz del proyecto')
    parser.add_argument('--output', '-o', default='compilado_proyecto.txt', help='Nombre del archivo de salida')
    parser.add_argument('--ignore', '-i', nargs='*', help='Patrones de archivos/directorios a ignorar')
    
    args = parser.parse_args()
    
    # Configurar patrones de ignorado
    ignore_patterns = [
        '.git', '.gitignore', '__pycache__', '*.pyc', '*.egg-info', 
        '.venv', 'venv', 'build', 'dist', '*.log', '*.tmp', '*.bak',
        '*.sqlite', '*.db', '.env', '*.env', '*.env.*', '*.md~', 
        '.idea', '.vscode', '.DS_Store', '*.png', '*.jpg', '*.jpeg', 
        '*.gif', '*.ico', '*.pdf', '*.zip', '*.tar.gz', '*.tar.bz2'
    ]
    
    if args.ignore:
        ignore_patterns.extend(args.ignore)
    
    # Verificar que el directorio del proyecto existe
    if not os.path.isdir(args.project):
        print(f"Error: El directorio '{args.project}' no existe o no es un directorio.")
        sys.exit(1)
    
    # Realizar la compilación
    try:
        num_files = compile_project(args.project, args.output, ignore_patterns)
        print(f"✅ Compilación completada exitosamente!")
        print(f"📊 Archivos procesados: {num_files}")
        print(f"💾 Archivo de salida: {os.path.abspath(args.output)}")
    except Exception as e:
        print(f"❌ Error durante la compilación: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()