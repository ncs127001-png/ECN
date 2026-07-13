#!/usr/bin/env python3
"""
capture_before_send.py
Captura respuesta ANTES de enviar nuevo prompt
Integración: Central Station → Capture → Send → Loop
"""

import subprocess
import time
import requests
import sys
from pathlib import Path
from datetime import datetime

# Importar el daemon HID
sys.path.insert(0, str(Path(__file__).parent))
from neurobit_hid_daemon import NeurobitHIDDaemon


def log_to_flask_server(event_type, platform, content, char_count):
    """Registra evento en Flask server"""
    try:
        payload = {
            'event_type': event_type,
            'platform': platform,
            'char_count': char_count,
            'timestamp': datetime.now().isoformat()
        }
        requests.post('http://127.0.0.1:5000/log_event', json=payload, timeout=2)
        print(f"✅ Evento registrado en Flask server")
    except Exception as e:
        print(f"⚠️ Flask server no disponible: {e}")

class ConversationRecorder:
    def __init__(self):
        self.fragments_dir = Path("~/WORKSPACE_NEUROBIT_V0.2/data/fragments").expanduser()
        self.fragments_dir.mkdir(parents=True, exist_ok=True)
        self.history_log = Path("~/WORKSPACE_NEUROBIT_V0.2/data/logs/conversation_history.jsonl").expanduser()
        self.history_log.parent.mkdir(parents=True, exist_ok=True)
        
    def capture_last_response(self, platform="gemini"):
        """Captura última respuesta antes de enviar nuevo prompt"""
        print(f"\n📸 CAPTURANDO RESPUESTA DE {platform.upper()}")
        print("=" * 50)
        
        daemon = NeurobitHIDDaemon()
        
        if not daemon.create_virtual_device():
            print("❌ Error creando dispositivo virtual")
            return None
        
        # Ejecutar captura
        content = daemon.capture_from_platform(platform)
        daemon.shutdown()
        
        if content and len(content) > 0:
            # Guardar como fragmento
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"response_{timestamp}.txt"
            filepath = self.fragments_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"[CAPTURED_FROM]: {platform}\n")
                f.write(f"[TIMESTAMP]: {datetime.now().isoformat()}\n")
                f.write(f"[CONTENT]:\n{content}")
            
            # Registrar en historial
            self._log_to_history(platform, filename, len(content))
            
            print(f"✅ Respuesta capturada: {filename} ({len(content)} chars)")
            return filepath
        else:
            print("⚠️ No se pudo capturar contenido (clipboard vacío)")
            return None
    
    def _log_to_history(self, platform, filename, char_count):
        """Registra captura en historial JSONL"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "platform": platform,
            "filename": filename,
            "char_count": char_count,
            "type": "LLM_RESPONSE"
        }
        
        with open(self.history_log, 'a', encoding='utf-8') as f:
            import json
            f.write(json.dumps(entry) + "\n")
    
    def send_prompt_with_context(self, prompt_text, platform="gemini"):
        """Envía prompt después de capturar respuesta anterior"""
        print(f"\n🚀 ENVIANDO PROMPT A {platform.upper()}")
        print("=" * 50)
        
        daemon = NeurobitHIDDaemon()
        
        if not daemon.create_virtual_device():
            print("❌ Error creando dispositivo virtual")
            return False
        
        # Focalizar ventana
        daemon.focus_window("Google Gemini")
        time.sleep(0.5)
        
        # Inyectar texto
        daemon.type_string(prompt_text)
        time.sleep(0.3)
        
        # Presionar ENTER para enviar
        daemon.press_key(28)  # KEY_ENTER
        time.sleep(0.3)
        
        daemon.shutdown()
        
        # Registrar en historial
        self._log_to_history(platform, "prompt_sent", len(prompt_text))
        
        print(f"✅ Prompt enviado ({len(prompt_text)} chars)")
        return True

# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Conversation Recorder')
    parser.add_argument('--capture', action='store_true', help='Capturar última respuesta')
    parser.add_argument('--send', type=str, help='Enviar prompt específico')
    parser.add_argument('--platform', type=str, default='gemini', help='Plataforma (gemini/chatgpt)')
    
    args = parser.parse_args()
    
    recorder = ConversationRecorder()
    
    if args.capture:
        recorder.capture_last_response(args.platform)
    elif args.send:
        recorder.send_prompt_with_context(args.send, args.platform)
    else:
        parser.print_help()