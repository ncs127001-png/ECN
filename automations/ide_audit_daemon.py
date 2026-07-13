#!/usr/bin/env python3
"""
ide_audit_daemon.py
Auditoría de procesos IDE — Captura estado ANTES y DESPUÉS del cierre

Propósito:
- Detectar cuando se cierra VSCode/Antigravity/JetBrains
- Capturar snapshot de procesos ANTES del cierre
- Esperar cierre
- Capturar snapshot DESPUÉS
- Identificar procesos huérfanos (que deberían haberse cerrado)
- Generar informe en .log
- Opcional: hacer kill automático de procesos no deseados
"""

import psutil
import time
import json
from datetime import datetime
from pathlib import Path
import subprocess

class IDEAuditDaemon:
    def __init__(self, log_path="data/logs/ide_audit.log"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # IDEs a monitorear
        self.ide_processes = {
            'code': 'VSCode',
            'antigravity': 'Antigravity',
            'pycharm': 'PyCharm',
            'idea': 'IntelliJ',
            'webstorm': 'WebStorm'
        }
        
        # Procesos que DEBEN cerrarse con el IDE
        self.child_patterns = [
            'node',           # Language servers
            'python',         # Python extensions
            'rg',             # Ripgrep (búsqueda)
            'git',            # Git operations
        ]
        
    def get_snapshot(self):
        """Captura snapshot de procesos actuales"""
        snapshot = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                info = {
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': ' '.join(proc.info['cmdline'] or []),
                    'create_time': proc.info['create_time'],
                    'timestamp': datetime.now().isoformat()
                }
                snapshot.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return snapshot
    
    def find_ide_processes(self):
        """Encuentra procesos IDE activos"""
        active_ides = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info['name'].lower()
                for ide_key, ide_name in self.ide_processes.items():
                    if ide_key in name:
                        active_ides.append({
                            'pid': proc.info['pid'],
                            'name': ide_name,
                            'process_name': proc.info['name']
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return active_ides
    
    def find_orphan_processes(self, before_snapshot, after_snapshot, ide_name):
        """Compara snapshots y encuentra procesos huérfanos"""
        before_pids = {p['pid'] for p in before_snapshot}
        after_pids = {p['pid'] for p in after_snapshot}
        
        # Procesos que aparecieron DESPUÉS del cierre (sospechosos)
        new_processes = []
        for proc in after_snapshot:
            if proc['pid'] not in before_pids:
                # Verificar si coincide con patrones sospechosos
                for pattern in self.child_patterns:
                    if pattern in proc['name'].lower() or pattern in proc['cmdline'].lower():
                        new_processes.append(proc)
                        break
        
        return new_processes
    
    def log_audit(self, message, level="INFO"):
        """Escribe en log"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.log_path, 'a') as f:
            f.write(log_line)
        
        print(log_line.strip())
    
    def kill_orphan_processes(self, processes, force=False):
        """Mata procesos huérfanos"""
        killed = []
        for proc in processes:
            try:
                p = psutil.Process(proc['pid'])
                if force:
                    p.kill()
                else:
                    p.terminate()
                killed.append(proc)
                self.log_audit(f"✅ Proceso {proc['name']} (PID {proc['pid']}) terminado", "ACTION")
            except psutil.NoSuchProcess:
                self.log_audit(f"⚠️ Proceso {proc['pid']} ya no existe", "WARN")
            except psutil.AccessDenied:
                self.log_audit(f"❌ Permiso denegado para PID {proc['pid']}", "ERROR")
        
        return killed
    
    def run_daemon(self, check_interval=5, auto_kill=False):
        """Bucle principal del daemon"""
        self.log_audit("🚀 IDE Audit Daemon iniciado", "START")
        self.log_audit(f"📝 Log: {self.log_path}")
        self.log_audit(f"🔍 Monitoreando IDEs: {list(self.ide_processes.values())}")
        self.log_audit(f"⏱ Intervalo: {check_interval}s")
        self.log_audit(f"🔨 Auto-kill: {'ACTIVO' if auto_kill else 'INACTIVO'}")
        
        last_ide_state = {}
        
        try:
            while True:
                # Verificar IDEs activos
                active_ides = self.find_ide_processes()
                
                for ide in active_ides:
                    ide_key = ide['name'].lower()
                    pid = ide['pid']
                    
                    # Detectar si el IDE se cerró
                    if ide_key in last_ide_state and last_ide_state[ide_key] != pid:
                        # IDE se cerró!
                        self.log_audit(f"🔴 {ide['name']} cerrado (PID {pid})", "EVENT")
                        
                        # Capturar snapshot ANTES
                        before_snapshot = self.get_snapshot()
                        
                        # Esperar un momento para que cierren procesos hijos
                        time.sleep(2)
                        
                        # Capturar snapshot DESPUÉS
                        after_snapshot = self.get_snapshot()
                        
                        # Encontrar huérfanos
                        orphans = self.find_orphan_processes(before_snapshot, after_snapshot, ide['name'])
                        
                        if orphans:
                            self.log_audit(f"⚠️ {len(orphans)} procesos huérfanos detectados", "WARN")
                            for orphan in orphans:
                                self.log_audit(f"   - {orphan['name']} (PID {orphan['pid']})", "DETAIL")
                            
                            # Auto-kill si está activado
                            if auto_kill and orphans:
                                self.kill_orphan_processes(orphans, force=False)
                        else:
                            self.log_audit("✅ No hay procesos huérfanos", "OK")
                    
                    last_ide_state[ide_key] = pid
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            self.log_audit("🛑 Daemon detenido por usuario", "STOP")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='IDE Audit Daemon')
    parser.add_argument('--interval', type=int, default=5, help='Intervalo de verificación (segundos)')
    parser.add_argument('--auto-kill', action='store_true', help='Matar procesos huérfanos automáticamente')
    parser.add_argument('--log', type=str, default='data/logs/ide_audit.log', help='Ruta del log')
    
    args = parser.parse_args()
    
    daemon = IDEAuditDaemon(log_path=args.log)
    daemon.run_daemon(check_interval=args.interval, auto_kill=args.auto_kill)