# modules/pid_monitor.py
"""
Monitor de procesos del navegador usando eBPF (Linux)
Captura eventos de teclado a nivel de proceso
"""

import subprocess
import json
from datetime import datetime

class BrowserPIDMonitor:
    def __init__(self, browser='firefox'):
        self.browser = browser
        self.pid_map = {}  # URL → PID
    
    def get_browser_pids(self):
        """Obtener todos los PIDs del navegador"""
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )
        pids = []
        for line in result.stdout.split('\n'):
            if self.browser in line.lower():
                parts = line.split()
                if len(parts) > 1:
                    pids.append({
                        'pid': parts[1],
                        'cpu': parts[2],
                        'memory': parts[3],
                        'command': ' '.join(parts[10:])
                    })
        return pids
    
    def map_pid_to_url(self, pid):
        """Mapear PID a URL (requiere acceso a /proc/[pid]/environ)"""
        try:
            with open(f'/proc/{pid}/environ', 'r') as f:
                environ = f.read().replace('\x00', '\n')
                for line in environ.split('\n'):
                    if 'URL' in line or 'url' in line:
                        return line.split('=')[1]
        except:
            pass
        return None
    
    def capture_keystrokes(self, pid):
        """
        Capturar pulsaciones de teclas para un PID específico
        Usando eBPF (requiere sudo)
        """
        # Esto requiere eBPF/bpftrace
        bpf_script = f"""
        tracepoint syscalls sys_enter_write /pid == {pid}/ {{
            printf("PID %d escribió %d bytes\\n", pid, args->count);
        }}
        """
        # Ejecutar con bpftrace
        subprocess.run(['sudo', 'bpftrace', '-e', bpf_script])
    
    def create_ghost_state(self, pid, url):
        """
        Crear estado ghost (réplica del frontend)
        """
        ghost_state = {
            'pid': pid,
            'url': url,
            'keystrokes': [],
            'clipboard': [],
            'dom_changes': [],
            'created_at': datetime.now().isoformat()
        }
        
        # Guardar en memoria_eva.jsonl
        with open('data/memoria_eva.jsonl', 'a') as f:
            f.write(json.dumps({
                'type': 'ghost_state_created',
                'state': ghost_state,
                'entity_id': 'PID_MONITOR',
                'perspective': 'audit'
            }) + '\n')
        
        return ghost_state