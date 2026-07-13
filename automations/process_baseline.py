# modules/process_baseline.py
#!/usr/bin/env python3
"""
Process Baseline Capture — Captura estado inicial del sistema
Se ejecuta al inicio de GNOME (autostart)
"""

import psutil
import json
import time
from datetime import datetime
from pathlib import Path

class ProcessBaseline:
    def __init__(self):
        self.baseline_file = Path.home() / '.config' / 'neurobit' / 'baseline_processes.json'
        self.baseline_file.parent.mkdir(parents=True, exist_ok=True)
        
    def capture(self):
        """Captura todos los procesos activos al inicio"""
        baseline = {
            'timestamp': datetime.now().isoformat(),
            'session': 'gnome_startup',
            'processes': []
        }
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'cpu_percent']):
            try:
                baseline['processes'].append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': ' '.join(proc.info['cmdline'] or []),
                    'memory_mb': proc.info['memory_info'].rss / 1024 / 1024,
                    'cpu_percent': proc.info['cpu_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Guardar baseline
        with open(self.baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)
        
        print(f"✅ Baseline capturado: {len(baseline['processes'])} procesos")
        return baseline
    
    def load(self):
        """Carga el baseline guardado"""
        if self.baseline_file.exists():
            with open(self.baseline_file, 'r') as f:
                return json.load(f)
        return None

# Ejecutar al inicio
if __name__ == '__main__':
    baseline = ProcessBaseline()
    baseline.capture()