#!/usr/bin/env python3
import subprocess
import os
import signal
import time

def kill_processes():
    """Mata todos los procesos python3 relacionados con neurobit_interceptor"""
    print("🔍 Buscando procesos de neurobit_interceptor...")
    
    # Método 1: Usar pkill
    try:
        result = subprocess.run(
            ['pkill', '-f', 'python3.*main.py'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Procesos terminados con pkill")
        else:
            print("⚠️  No se encontraron procesos activos")
    except Exception as e:
        print(f"❌ Error con pkill: {e}")
    
    # Método 2: Buscar y matar manualmente
    time.sleep(1)
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'python3.*main.py'],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"✅ Proceso {pid} terminado")
                except ProcessLookupError:
                    print(f"⚠️  Proceso {pid} ya no existe")
        else:
            print("✅ No hay procesos activos")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    kill_processes()
