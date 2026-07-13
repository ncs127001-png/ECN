#!/usr/bin/env python3
"""
compile_selector.py — Compilador selectivo para NEUROBIT
Uso: python3 compile_selector.py --list LISTA_OBTENIDA.txt --output resultado.txt
"""
import argparse, shutil, sys, os, subprocess, tempfile
from pathlib import Path
from datetime import datetime

def parse_file_list(list_path: str) -> list:
    """Lee lista de archivos desde .txt (formato find output)"""
    files = []
    with open(list_path, 'r', encoding='utf-8') as f:
        for line in f:
            path = line.strip()
            if path and Path(path).exists():
                files.append(path)
            elif path:
                print(f"⚠️  Archivo no encontrado: {path}", file=sys.stderr)
    return files

def copy_to_temp(files: list, temp_dir: Path) -> bool:
    """Copia archivos preservando estructura relativa"""
    workspace = Path.home() / "WORKSPACE_NEUROBIT_V0.2"
    for src in files:
        src_path = Path(src)
        # Calcular ruta relativa al workspace
        try:
            rel_path = src_path.relative_to(workspace)
            dest = temp_dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest)
            print(f"✓ Copiado: {rel_path}")
        except ValueError:
            # Fuera del workspace, copiar nombre plano
            shutil.copy2(src_path, temp_dir / src_path.name)
            print(f"✓ Copiado (plano): {src_path.name}")
    return True

def run_compiler(temp_dir: Path, output_name: str) -> bool:
    """Ejecuta compile_project.py sobre la carpeta temporal"""
    cmd = [
        sys.executable,
        str(Path.home() / "WORKSPACE_NEUROBIT_V0.2" / "compile_project.py"),
        "--project", str(temp_dir),
        "--output", output_name
    ]
    print(f"🔄 Ejecutando: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=temp_dir.parent)
    if result.returncode != 0:
        print(f"❌ Error en compile_project.py:\n{result.stderr}", file=sys.stderr)
        return False
    print(f"✅ compile_project.py completado")
    return True

def main():
    parser = argparse.ArgumentParser(description="Compilador selectivo NEUROBIT")
    parser.add_argument("--list", required=True, help="Archivo .txt con lista de archivos (find output)")
    parser.add_argument("--output", default=None, help="Nombre del archivo de salida")
    parser.add_argument("--keep-temp", action="store_true", help="No eliminar carpeta temporal tras éxito")
    args = parser.parse_args()
    
    # Validar lista de entrada
    list_path = Path(args.list)
    if not list_path.exists():
        print(f"❌ Lista no encontrada: {list_path}", file=sys.stderr)
        sys.exit(1)
    
    files = parse_file_list(str(list_path))
    if not files:
        print("❌ No se encontraron archivos válidos en la lista", file=sys.stderr)
        sys.exit(1)
    
    print(f"✓ {len(files)} archivos para compilar")
    
    # Crear carpeta temporal
    temp_dir = Path(tempfile.mkdtemp(prefix="neurobit_compile_"))
    print(f"📁 Temp: {temp_dir}")
    
    try:
        # Copiar archivos
        if not copy_to_temp(files, temp_dir):
            raise RuntimeError("Fallo al copiar archivos")
        
        # Determinar nombre de output
        output_name = args.output or f"Compilacion_{list_path.stem}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        output_path = Path.cwd() / output_name
        
        # Ejecutar compilador
        if not run_compiler(temp_dir, output_name):
            raise RuntimeError("Fallo en compile_project.py")
        
        # Verificar output
        if not output_path.exists():
            # Buscar en temp_dir si compile_project.py escribió allí
            alt_output = temp_dir / output_name
            if alt_output.exists():
                shutil.move(alt_output, output_path)
            else:
                raise FileNotFoundError(f"Output no generado: {output_name}")
        
        print(f"🎉 Éxito: {output_path.resolve()} ({output_path.stat().st_size} bytes)")
        
        # Cleanup
        if not args.keep_temp:
            shutil.rmtree(temp_dir)
            print(f"🧹 Temp eliminado")
        else:
            print(f"💾 Temp preservado: {temp_dir}")
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        # No eliminar temp en caso de error para debug
        print(f"🔍 Temp para debug: {temp_dir}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()