#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOS CORE - Batch Executor para corrección de rutas
Función: Ejecuta un comando sobre una lista de archivos/directorios con delay controlado.
Principio: Tarea simple, trazabilidad completa.
"""
import os
import sys
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime

class SOSBatchExecutor:
    def __init__(self, workspace_root: Path):
        self.root = workspace_root
        self.log_file = self.root / "data" / "logs" / "batch_executor.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Lista de resultados
        self.results = []
    
    def log(self, message: str):
        """Registra en log con timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        print(log_entry.strip())
    
    def execute_on_file(self, command: str, file_path: Path, dry_run=False) -> dict:
        """Ejecuta un comando sobre un archivo específico"""
        result = {
            "file": str(file_path),
            "command": command,
            "status": "unknown",
            "return_code": None,
            "stdout": "",
            "stderr": "",
            "timestamp": datetime.now().isoformat()
        }
        
        if not file_path.exists():
            result["status"] = "error"
            result["stderr"] = f"Archivo no encontrado: {file_path}"
            self.log(f"❌ {file_path.name}: Archivo no encontrado")
            return result
        
        # Construir comando completo
        full_command = f"{command} {file_path}"
        
        if dry_run:
            result["status"] = "dry_run"
            self.log(f"🔍 [DRY-RUN] {file_path.name}: {full_command}")
            return result
        
        try:
            self.log(f"▶️  Ejecutando: {full_command}")
            
            proc = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(self.root),
                timeout=30  # Timeout de 30 segundos por archivo
            )
            
            result["return_code"] = proc.returncode
            result["stdout"] = proc.stdout.strip()
            result["stderr"] = proc.stderr.strip()
            
            if proc.returncode == 0:
                result["status"] = "success"
                self.log(f"✅ {file_path.name}: Éxito")
            else:
                result["status"] = "error"
                self.log(f"❌ {file_path.name}: Error (código {proc.returncode})")
                if proc.stderr:
                    self.log(f"   stderr: {proc.stderr[:200]}")
        
        except subprocess.TimeoutExpired:
            result["status"] = "timeout"
            self.log(f"⏱️  {file_path.name}: Timeout (30s)")
        except Exception as e:
            result["status"] = "error"
            result["stderr"] = str(e)
            self.log(f"❌ {file_path.name}: Excepción - {str(e)}")
        
        return result
    
    def execute_batch(self, command: str, file_list: list, delay_seconds=1, dry_run=False) -> list:
        """
        Ejecuta un comando sobre una lista de archivos con delay
        
        Args:
            command: Comando a ejecutar (ej: "python3 core/sos_path_fixer.py --apply")
            file_list: Lista de rutas de archivos
            delay_seconds: Segundos de espera entre cada ejecución
            dry_run: Si True, solo muestra qué haría sin ejecutar
        """
        total = len(file_list)
        self.log(f"\n{'='*60}")
        self.log(f"🚀 INICIANDO BATCH EXECUTOR")
        self.log(f"   Comando: {command}")
        self.log(f"   Total archivos: {total}")
        self.log(f"   Delay: {delay_seconds}s")
        self.log(f"   Modo: {'DRY-RUN' if dry_run else 'EJECUCIÓN REAL'}")
        self.log(f"{'='*60}\n")
        
        start_time = time.time()
        
        for idx, file_path in enumerate(file_list, 1):
            self.log(f"\n[{idx}/{total}] Procesando: {Path(file_path).name}")
            
            result = self.execute_on_file(command, Path(file_path), dry_run=dry_run)
            self.results.append(result)
            
            # Delay entre ejecuciones (excepto en el último)
            if idx < total and not dry_run:
                self.log(f"⏳ Esperando {delay_seconds}s...")
                time.sleep(delay_seconds)
        
        elapsed = time.time() - start_time
        
        self.log(f"\n{'='*60}")
        self.log(f"✅ BATCH COMPLETADO")
        self.log(f"   Tiempo total: {elapsed:.2f}s")
        self.log(f"   Exitosos: {sum(1 for r in self.results if r['status'] == 'success')}")
        self.log(f"   Errores: {sum(1 for r in self.results if r['status'] == 'error')}")
        self.log(f"   Timeouts: {sum(1 for r in self.results if r['status'] == 'timeout')}")
        self.log(f"{'='*60}\n")
        
        return self.results
    
    def generate_report(self, output_path: Path):
        """Genera reporte JSON de la ejecución"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(self.results),
            "success": sum(1 for r in self.results if r['status'] == 'success'),
            "errors": sum(1 for r in self.results if r['status'] == 'error'),
            "timeouts": sum(1 for r in self.results if r['status'] == 'timeout'),
            "results": self.results
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"📊 Reporte generado: {output_path}")
        return output_path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ejecutor batch de comandos sobre archivos")
    parser.add_argument("command", help="Comando a ejecutar (ej: 'python3 core/sos_path_fixer.py --apply')")
    parser.add_argument("--files", nargs='+', help="Lista de archivos a procesar")
    parser.add_argument("--file-list", help="Archivo de texto con lista de archivos (uno por línea)")
    parser.add_argument("--delay", type=int, default=1, help="Segundos de espera entre ejecuciones (default: 1)")
    parser.add_argument("--dry-run", action="store_true", help="Modo preview (no ejecuta)")
    parser.add_argument("--output", default="data/batch_executor_report.json", help="Ruta del reporte JSON")
    args = parser.parse_args()
    
    # Determinar raíz del workspace
    workspace = Path(__file__).resolve().parent
    
    executor = SOSBatchExecutor(workspace)
    
    # Obtener lista de archivos
    file_list = []
    if args.files:
        file_list = args.files
    elif args.file_list:
        with open(args.file_list, 'r') as f:
            file_list = [line.strip() for line in f if line.strip()]
    else:
        print("❌ Debes especificar --files o --file-list")
        parser.print_help()
        sys.exit(1)
    
    if not file_list:
        print("❌ Lista de archivos vacía")
        sys.exit(1)
    
    # Ejecutar batch
    executor.execute_batch(
        command=args.command,
        file_list=file_list,
        delay_seconds=args.delay,
        dry_run=args.dry_run
    )
    
    # Generar reporte
    report_path = executor.generate_report(workspace / args.output)
    
    print(f"\n✅ Ejecución completada. Reporte: {report_path}")
