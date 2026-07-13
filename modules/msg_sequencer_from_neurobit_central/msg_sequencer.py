#!/usr/bin/env python3
"""
msg_sequencer.py - Generador de mensajes secuenciales usando msg_builder.py
Permite convertir archivos .txt a formato YAML con numeración automática
"""

import os
import sys
import argparse
import subprocess
import re
from pathlib import Path

def get_next_message_number(output_dir):
    """Determina el próximo número de mensaje basado en archivos existentes"""
    if not output_dir.exists():
        return 1
    
    # Buscar archivos con formato mensaje_*.yaml
    existing_files = list(output_dir.glob("mensaje_*.yaml"))
    if not existing_files:
        return 1
    
    # Extraer números de los archivos existentes
    numbers = []
    for f in existing_files:
        match = re.search(r"mensaje_(\d+)\.yaml", f.name)
        if match:
            numbers.append(int(match.group(1)))
    
    return max(numbers) + 1 if numbers else 1

def create_output_directory(output_dir):
    """Crea el directorio de salida si no existe"""
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio creado: {output_dir}")
    return output_dir

def process_text_file(input_file, output_dir, node="TRON", session="SALA_01"):
    """Procesa un archivo .txt y genera el YAML correspondiente"""
    if not input_file.exists():
        print(f"❌ Error: El archivo {input_file} no existe")
        return False
    
    # Determinar el próximo número
    next_num = get_next_message_number(output_dir)
    output_file = output_dir / f"mensaje_{next_num}.yaml"
    
    print(f"📝 Procesando: {input_file.name}")
    print(f"🔢 Próximo número de mensaje: {next_num}")
    print(f"💾 Archivo de salida: {output_file.name}")
    
    try:
        # Ejecutar msg_builder.py con los parámetros adecuados
        cmd = [
            "python3", 
            str(Path(__file__).parent / "msg_builder.py"),
            "--source", str(input_file),
            "--node", node,
            "--session", session,
            "--out", str(output_file),
            "--fragment-index", str(next_num),
            "--fragment-total", "1"  # Podría actualizarse dinámicamente si es necesario
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Mensaje generado exitosamente: mensaje_{next_num}.yaml")
            print(f"📋 Contenido del mensaje:")
            with open(output_file, 'r') as f:
                print(f.read())
            return True
        else:
            print(f"❌ Error al generar el mensaje:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Excepción al procesar el archivo: {str(e)}")
        return False

def list_available_texts(input_dir):
    """Lista los archivos .txt disponibles para procesar"""
    if not input_dir.exists():
        print(f"⚠️  Directorio no encontrado: {input_dir}")
        return []
    
    text_files = list(input_dir.glob("*.txt"))
    return text_files

def interactive_mode(output_dir, input_dir):
    """Modo interactivo para seleccionar archivos"""
    print("\n" + "="*60)
    print("💬 GENERADOR DE MENSAJES SECUENCIALES - MODO INTERACTIVO")
    print("="*60)
    
    # Listar archivos disponibles
    text_files = list_available_texts(input_dir)
    
    if not text_files:
        print(f"❌ No se encontraron archivos .txt en {input_dir}")
        print(f"💡 Crea algunos archivos .txt en {input_dir} para procesarlos")
        return
    
    print(f"\n📁 Archivos disponibles en {input_dir}:")
    for i, file in enumerate(text_files, 1):
        print(f"  {i}. {file.name}")
    
    print(f"\n🎯 Próximo número de mensaje: {get_next_message_number(output_dir)}")
    
    try:
        selection = input("\n❓ Selecciona un archivo para procesar (número) o 'q' para salir: ")
        if selection.lower() == 'q':
            print("👋 Saliendo del modo interactivo")
            return True
        
        idx = int(selection) - 1
        if 0 <= idx < len(text_files):
            process_text_file(text_files[idx], output_dir)
            return False  # Continuar en modo interactivo
        else:
            print("❌ Selección inválida")
            return False
    except ValueError:
        print("❌ Por favor ingresa un número válido")
        return False

def main():
    parser = argparse.ArgumentParser(description='Generador de mensajes secuenciales usando msg_builder.py')
    parser.add_argument('--input', '-i', type=str, default='input_texts', 
                        help='Directorio con archivos .txt a procesar (default: input_texts)')
    parser.add_argument('--output', '-o', type=str, default='messages', 
                        help='Directorio de salida para mensajes YAML (default: messages)')
    parser.add_argument('--file', '-f', type=str, 
                        help='Archivo .txt específico a procesar (modo no interactivo)')
    parser.add_argument('--node', '-n', type=str, default='TRON',
                        help='Nodo origen (default: TRON)')
    parser.add_argument('--session', '-s', type=str, default='SALA_01',
                        help='ID de sesión (default: SALA_01)')
    parser.add_argument('--interactive', '-t', action='store_true',
                        help='Modo interactivo (default)')
    parser.add_argument('--non-interactive', action='store_true', help='Forzar modo no interactivo')
    parser.add_argument('--select', type=int, help='Seleccionar índice de archivo automáticamente (1-based)')
    
    args = parser.parse_args()
    
    # Configurar directorios
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    # Crear directorios necesarios
    input_dir.mkdir(exist_ok=True)
    create_output_directory(output_dir)
    
    print("\n" + "="*70)
    print("🧠 NEUROBIT - Generador de Mensajes Secuenciales")
    print("="*70)
    print(f"📊 Directorio de entrada: {input_dir}")
    print(f"📤 Directorio de salida: {output_dir}")
    print(f"🔢 Último mensaje generado: {get_next_message_number(output_dir) - 1}")
    print("="*70)
    
    # Decide mode: interactive only when explicitly requested and stdin is a TTY.
    # If --file, --select or --non-interactive are provided, run non-interactive flows.
    if args.interactive and not args.non_interactive and args.file is None and args.select is None and sys.stdin.isatty():
        print("\n💡 Instrucciones:")
        print("  - Coloca tus archivos .txt en el directorio de entrada")
        print("  - Selecciona el archivo que quieres convertir a mensaje")
        print("  - El sistema generará el YAML con numeración automática")
        print("  - Presiona 'q' para salir del modo interactivo")
        
        # Crear un ejemplo si no hay archivos
        if not list(input_dir.glob("*.txt")):
            example_file = input_dir / "ejemplo.txt"
            with open(example_file, 'w') as f:
                f.write("Este es un mensaje de ejemplo para la Sala de Reuniones.\n")
            print(f"\n✨ Creado archivo de ejemplo: {example_file}")
        
        while True:
            if interactive_mode(output_dir, input_dir):
                break
    # If a specific file was requested via --file or --select, or forced non-interactive
    elif args.file or args.select is not None or args.non_interactive:
        # prefer --file
        if args.file:
            input_file = Path(args.file)
            if not input_file.exists():
                print(f"❌ El archivo {input_file} no existe")
                sys.exit(1)
            success = process_text_file(input_file, output_dir, args.node, args.session)
            sys.exit(0 if success else 1)
        # select index provided
        if args.select is not None:
            files = list_available_texts(input_dir)
            idx = args.select - 1
            if 0 <= idx < len(files):
                success = process_text_file(files[idx], output_dir, args.node, args.session)
                sys.exit(0 if success else 1)
            else:
                print("❌ Selección fuera de rango")
                sys.exit(1)
    
    # If nothing selected and not interactive, process all .txt files in input_dir non-interactively
    else:
        files = list_available_texts(input_dir)
        if not files:
            print(f"❌ No se encontraron archivos .txt en {input_dir}")
            sys.exit(0)
        overall_ok = True
        for f in files:
            ok = process_text_file(f, output_dir, args.node, args.session)
            overall_ok = overall_ok and ok
        sys.exit(0 if overall_ok else 1)

if __name__ == "__main__":
    main()