#!/usr/bin/env python3
# reconstruir_desde_especificacion.py
# 
# NEUROBIT v2.1 - Módulo de Reconstrucción desde Especificación
# Reconstruye proyecto Neurobit desde una especificación técnica en Markdown
#
# Función: Spec → Archivos (inversa a descompilador_extension.py)
# Uso: python3 reconstruir_desde_especificacion.py spec.md [--dry-run] [--root proyecto_name]
#
# Autor: NEUROBIT Restoration Protocol v2.1
# Fecha: enero 2026
# Soberanía: Restauración del Logos - Sin dependencias corporativas

import os
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

class ReconstructorFromSpec:
    """
    Reconstruye estructura de proyecto desde especificación Markdown.
    
    Patrón esperado en el .md:
    
    ## 1. Nombre del Archivo (ruta/relativa/archivo.ext)
    ```lenguaje
    contenido del archivo
    ```
    
    Esta clase es el GEMELO INVERSO de descompilador_extension.py
    """
    
    def __init__(self, project_root: str = "neurobit"):
        self.project_root = Path(project_root)
        self.file_entries = []
        self.errors = []
        self.warnings = []
    
    def extract_code_blocks_with_paths(self, md_content: str):
        """
        Extrae pares (ruta, contenido) basados en encabezados del tipo:
        ## N. Título (ruta/relativa/archivo.ext)
        ```lenguaje
        contenido
        ```
        
        Retorna: lista de tuplas (filepath, contenido)
        """
        # Patrón: ## N. Título (ruta) + bloque de código
        pattern = r"##\s+\d+\.\s+[^\n]*\(([^)]+?)\)\s*$(?:.*?)```(?:[a-z]*)\n(.*?)\n```"
        
        matches = re.findall(pattern, md_content, re.DOTALL | re.MULTILINE)
        
        files = []
        for filepath, content in matches:
            # Normalizar ruta
            filepath = filepath.strip()
            content = content.rstrip('\n')
            
            # Validación básica
            if not filepath:
                self.warnings.append("Ruta vacía detectada - ignorando")
                continue
            
            files.append((filepath, content))
        
        return files
    
    def validate_filepaths(self, file_list):
        """
        Valida que las rutas sean seguras (sin traversal attacks, etc.)
        """
        for filepath, _ in file_list:
            # Rechazar rutas con ..
            if ".." in filepath:
                self.errors.append(f"❌ Path traversal detectado: {filepath}")
                continue
            
            # Rechazar rutas absolutas
            if os.path.isabs(filepath):
                self.errors.append(f"❌ Ruta absoluta no permitida: {filepath}")
                continue
        
        return len(self.errors) == 0
    
    def load_specification(self, spec_path: str) -> bool:
        """Carga especificación desde archivo .md"""
        spec_file = Path(spec_path)
        
        if not spec_file.exists():
            self.errors.append(f"❌ Especificación no encontrada: {spec_path}")
            return False
        
        try:
            with open(spec_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.file_entries = self.extract_code_blocks_with_paths(content)
            
            if not self.file_entries:
                self.warnings.append("⚠️  No se detectaron bloques de código con rutas")
                return False
            
            if not self.validate_filepaths(self.file_entries):
                return False
            
            return True
        
        except Exception as e:
            self.errors.append(f"❌ Error leyendo especificación: {str(e)}")
            return False
    
    def get_summary(self):
        """Retorna resumen de lo que se va a reconstruir"""
        return {
            'total_files': len(self.file_entries),
            'files': [fp for fp, _ in self.file_entries],
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def reconstruct_dry_run(self):
        """Simulación sin escritura en disco"""
        print(f"\n🔍 [DRY-RUN] Especificación contiene {len(self.file_entries)} archivos:\n")
        
        total_size = 0
        for filepath, content in self.file_entries:
            size = len(content)
            total_size += size
            print(f"  📄 {filepath:40} ({size:5} bytes)")
        
        print(f"\n  Total: {total_size} bytes en {len(self.file_entries)} archivos")
        return True
    
    def reconstruct(self):
        """Reconstruye todos los archivos en disco"""
        if not self.file_entries:
            print("⚠️  No hay archivos para reconstruir")
            return False
        
        # Crear raíz del proyecto
        try:
            self.project_root.mkdir(exist_ok=True, parents=True)
        except Exception as e:
            self.errors.append(f"❌ No se pudo crear directorio raíz: {str(e)}")
            return False
        
        print(f"\n🛠️  Escribiendo {len(self.file_entries)} archivos en '{self.project_root}'...\n")
        
        successful = 0
        for filepath, content in self.file_entries:
            full_path = self.project_root / filepath
            
            try:
                # Crear directorios padres si es necesario
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Escribir archivo
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"  ✅ {filepath}")
                successful += 1
            
            except Exception as e:
                error_msg = f"❌ Error escribiendo {filepath}: {str(e)}"
                self.errors.append(error_msg)
                print(f"  {error_msg}")
        
        print(f"\n✨ Reconstrucción completada: {successful}/{len(self.file_entries)} archivos escritos")
        
        if self.warnings:
            print(f"\n⚠️  Advertencias ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  {w}")
        
        return successful == len(self.file_entries)


def main():
    parser = argparse.ArgumentParser(
        description="NEUROBIT v2.1 - Reconstructor desde Especificación",
        epilog="Ejemplo: python3 reconstruir_desde_especificacion.py spec.md --root proyecto"
    )
    parser.add_argument("spec_file", help="Archivo .md con la especificación")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar acciones sin ejecutar")
    parser.add_argument("--root", default="neurobit", help="Nombre del directorio raíz (default: neurobit)")
    parser.add_argument("--verbose", action="store_true", help="Modo verbose")
    
    args = parser.parse_args()
    
    # Crear reconstructor
    reconstructor = ReconstructorFromSpec(project_root=args.root)
    
    # Cargar especificación
    if not reconstructor.load_specification(args.spec_file):
        print("\n❌ No se pudo cargar la especificación:")
        for error in reconstructor.errors:
            print(f"  {error}")
        sys.exit(1)
    
    # Mostrar resumen
    summary = reconstructor.get_summary()
    print(f"\n📦 Especificación: {args.spec_file}")
    print(f"📁 Proyecto: {args.root}")
    print(f"📄 Archivos detectados: {summary['total_files']}")
    
    if args.verbose:
        for f in summary['files']:
            print(f"  → {f}")
    
    # Dry-run o reconstrucción real
    if args.dry_run:
        reconstructor.reconstruct_dry_run()
    else:
        if not reconstructor.reconstruct():
            if reconstructor.errors:
                print(f"\n❌ Errores durante la reconstrucción:")
                for error in reconstructor.errors:
                    print(f"  {error}")
            sys.exit(1)
    
    print(f"\n✨ Operación completada exitosamente.")
    print(f"💡 Próximo paso: Validar archivos y ejecutar tests.")


if __name__ == "__main__":
    main()
