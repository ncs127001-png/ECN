#!/usr/bin/env python3
"""
centinela_monitor.py
NEUROBIT Salón v0.1 — Monitor Local de Clipboard

El Centinela es un vigilante soberano que:
1. Monitorea el clipboard del sistema LOCAL (SIN enviar a servidores externos)
2. Registra cambios en memoria_eva.jsonl con MESSAGE_ID y TIMESTAMP
3. Valida coherencia básica de contenido
4. Implementa "pulso" configurable (por defecto 2 segundos)

Soberanía técnica garantizada: Logs locales solamente, zero remote transmission.

Uso:
  python3 core/centinela_monitor.py --start           # Inicia en background
  python3 core/centinela_monitor.py --stop            # Detiene
  python3 core/centinela_monitor.py --status          # Muestra estado
  
O desde API:
  POST /api/start_centinela
  POST /api/stop_centinela
  GET /api/centinela_status
"""

import os
import sys
import time
import subprocess
import json
import hashlib
import uuid
from pathlib import Path
from datetime import datetime
import threading
import signal

# Configuración
MEMORIA_EVA_PATH = "data/memoria_eva.jsonl"
LOG_FILE = "data/centinela_resguardo.jsonl"
CENTINELA_STATE_FILE = "data/.centinela_state"
CLIPBOARD_PULSE = 2  # segundos entre chequeos

# Estado global
centinela_running = False
centinela_thread = None

def check_clipboard_available():
    """Verifica si el clipboard está disponible en el sistema."""
    try:
        # Test xclip con un comando que no sea destructivo
        result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                               capture_output=True, timeout=1, text=True)
        # Si retorna 0, xclip está disponible
        return result.returncode == 0 or (result.returncode != 0 and "target STRING" not in result.stderr)
    except FileNotFoundError:
        try:
            # Test xsel
            result = subprocess.run(['xsel', '--clipboard', '--output'],
                                   capture_output=True, timeout=1, text=True)
            return result.returncode == 0 or (result.returncode != 0 and "target STRING" not in result.stderr)
        except FileNotFoundError:
            return False
    except:
        return False

def get_clipboard():
    """Extrae contenido del clipboard del sistema LOCAL."""
    try:
        # Intenta xclip (Linux)
        result = subprocess.check_output(['xclip', '-selection', 'clipboard', '-o'], 
                                        timeout=2, stderr=subprocess.DEVNULL).decode('utf-8')
        return result
    except:
        try:
            # Intenta xsel (Linux alternativa)
            result = subprocess.check_output(['xsel', '--clipboard', '--output'],
                                            timeout=2, stderr=subprocess.DEVNULL).decode('utf-8')
            return result
        except:
            return ""  # Sin clipboard disponible (OK en headless)

def calculate_content_hash(content):
    """Calcula hash SHA256 del contenido."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def validate_content(content):
    """Valida que el contenido sea significativo."""
    stripped = content.strip()
    # Al menos 10 caracteres y sin ser repetición simple
    if len(stripped) < 10:
        return False
    
    # No registrar si es solo espacios/saltos de línea
    if len(stripped.replace('\n', '').replace(' ', '')) < 5:
        return False
    
    return True

def generate_message_id():
    """Genera MESSAGE_ID único con timestamp."""
    timestamp = datetime.now().isoformat()
    unique_id = str(uuid.uuid4())[:8]
    return f"CLIP-{timestamp.replace(':', '-').replace('.', '-')}-{unique_id}"

def store_clipboard_entry(content):
    """Almacena entrada de clipboard en memoria_eva.jsonl."""
    try:
        Path(MEMORIA_EVA_PATH).parent.mkdir(parents=True, exist_ok=True)
        
        message_id = generate_message_id()
        content_hash = calculate_content_hash(content)
        timestamp = datetime.now().isoformat()
        
        envelope = {
            "MESSAGE_ID": message_id,
            "TIMESTAMP": timestamp,
            "source": "CENTINELA_CLIPBOARD",
            "content": content[:5000],  # Limitar a 5000 caracteres
            "content_hash": content_hash,
            "content_length": len(content),
            "validated": validate_content(content)
        }
        
        # Append-only a memoria_eva.jsonl
        with open(MEMORIA_EVA_PATH, 'a') as f:
            f.write(json.dumps(envelope, ensure_ascii=False) + '\n')
        
        return message_id
        
    except Exception as e:
        print(f"❌ Error guardando entrada: {e}")
        return None

def centinela_loop(pulse=CLIPBOARD_PULSE):
    """Loop principal del Centinela."""
    global centinela_running
    
    print(f"[CENTINELA] Iniciando monitoreo con pulso de {pulse}s...")
    print(f"[CENTINELA] Registrando en: {MEMORIA_EVA_PATH}")
    print("[CENTINELA] ✓ SOBERANÍA: Logs locales solamente\n")
    
    last_hash = ""
    
    try:
        while centinela_running:
            try:
                current_content = get_clipboard()
                
                if current_content and validate_content(current_content):
                    current_hash = calculate_content_hash(current_content)
                    
                    # Solo guardar si cambió desde última vez
                    if current_hash != last_hash:
                        message_id = store_clipboard_entry(current_content)
                        if message_id:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            content_preview = current_content[:50].replace('\n', ' ')
                            print(f"[✅ {timestamp}] Fractal Resguardado: {message_id}")
                            print(f"               > {content_preview}...")
                            last_hash = current_hash
                
                time.sleep(pulse)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[⚠️ ] Error en pulso: {e}")
                time.sleep(pulse)
    
    except Exception as e:
        print(f"[❌] Error crítico: {e}")
    
    finally:
        centinela_running = False
        print("\n[CENTINELA] En reposo.")

def start_centinela(background=True):
    """Inicia el Centinela."""
    global centinela_running, centinela_thread
    
    if centinela_running:
        return {"status": "error", "message": "Centinela ya está corriendo"}
    
    # ✅ FIX: Verificar si clipboard está disponible
    if not check_clipboard_available():
        return {
            "status": "error", 
            "message": "Clipboard no disponible: instala 'xclip' o 'xsel' (apt install xclip)",
            "suggestion": "sudo apt install xclip"
        }
    
    centinela_running = True
    
    if background:
        centinela_thread = threading.Thread(target=centinela_loop, daemon=True)
        centinela_thread.start()
        
        # Guardar estado
        try:
            with open(CENTINELA_STATE_FILE, 'w') as f:
                f.write(json.dumps({
                    "status": "running",
                    "started": datetime.now().isoformat()
                }))
        except:
            pass
        
        return {"status": "success", "message": "Centinela iniciado en background"}
    else:
        centinela_loop()
        return {"status": "success", "message": "Centinela completado"}

def stop_centinela():
    """Detiene el Centinela."""
    global centinela_running
    
    centinela_running = False
    
    try:
        with open(CENTINELA_STATE_FILE, 'w') as f:
            f.write(json.dumps({
                "status": "stopped",
                "stopped": datetime.now().isoformat()
            }))
    except:
        pass
    
    return {"status": "success", "message": "Centinela detenido"}

def get_status():
    """Retorna estado actual del Centinela."""
    try:
        if CENTINELA_STATE_FILE.endswith('*') or Path(CENTINELA_STATE_FILE).exists():
            with open(CENTINELA_STATE_FILE, 'r') as f:
                state = json.load(f)
        else:
            state = {"status": "unknown"}
    except:
        state = {"status": "unknown"}
    
    return {
        "global_status": "running" if centinela_running else "stopped",
        "saved_state": state,
        "memoria_eva_size": os.path.getsize(MEMORIA_EVA_PATH) if Path(MEMORIA_EVA_PATH).exists() else 0
    }

if __name__ == "__main__":
    if "--start" in sys.argv:
        result = start_centinela(background="--foreground" not in sys.argv)
        print(json.dumps(result))
    elif "--stop" in sys.argv:
        result = stop_centinela()
        print(json.dumps(result))
    elif "--status" in sys.argv:
        result = get_status()
        print(json.dumps(result, indent=2))
    else:
        # Ejecución directa: background mode
        start_centinela(background=False)
