#!/usr/bin/env python3
"""
neurobit_hid_daemon.py
Daemon soberano que genera eventos HID a nivel de kernel
Bypass total del sandbox del navegador - isTrusted: TRUE
"""

import evdev
from evdev import UInput, ecodes as e, UInputError
import subprocess
import time
import json
import yaml
from pathlib import Path
from datetime import datetime
from collections import deque
import threading
import queue

class NeurobitHIDDaemon:
    def __init__(self, config_path="config/hid_daemon.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()

        self.event_queue = queue.Queue()
        self.ui = None  # Dispositivo UInput virtual
        self.running = False

        # Mapeo de plataformas (selectores + secuencias)
        self.platforms = self.load_platform_map()

        # Buffer de teclas para recovery (keylogger soberano)
        self.key_buffer = deque(maxlen=1000)
        self.log_path = Path("~/neurobit/data/logs/keylog").expanduser()
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def load_config(self):
        """Carga configuración desde YAML"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {
            'char_delay_ms': 30,
            'tab_delay_ms': 150,
            'enter_delay_ms': 200,
            'enable_keylog': True,
            'virtual_device_name': 'neurobit-hid-virtual'
        }

    def load_platform_map(self):
        """Carga mapa de plataformas desde config/"""
        platform_dir = Path("config/platforms")
        platforms = {}

        if platform_dir.exists():
            for f in platform_dir.glob("*.yaml"):
                with open(f, 'r', encoding='utf-8') as file:
                    platforms[f.stem] = yaml.safe_load(file)

        return platforms

    def create_virtual_device(self):
        """Crea dispositivo de entrada virtual vía uinput"""
        try:
            # Capacidades del teclado virtual
            capabilities = {
                e.EV_KEY: list(range(e.KEY_RESERVED, e.KEY_MAX + 1)),
                e.EV_SYN: []
            }

            self.ui = UInput(
                capabilities,
                name=self.config.get('virtual_device_name', 'neurobit-hid-virtual'),
                vendor=0x0123,
                product=0x4567,
                version=0x0100
            )

            print(f"✅ Dispositivo virtual creado: {self.ui.name}")
        # ✅ CORREGIDO
            print(f"   Device: {self.ui.name}")
            print(f"   Capabilities: {len(self.ui.capabilities())} keys")
            return True

        except UInputError as err:
            print(f"❌ Error creando dispositivo virtual: {err}")
            print("   Solución: sudo modprobe uinput && sudo usermod -aG uinput $USER")
            return False

    def press_key(self, keycode):
        """Presiona una tecla (press + release)"""
        if not self.ui:
            raise RuntimeError("Dispositivo virtual no inicializado")

        # Press
        self.ui.write(e.EV_KEY, keycode, 1)
        self.ui.syn()
        time.sleep(0.02)

        # Release
        self.ui.write(e.EV_KEY, keycode, 0)
        self.ui.syn()
        time.sleep(0.02)

        # Log para recovery
        if self.config.get('enable_keylog', True):
            self.log_keypress(keycode)

    def log_keypress(self, keycode):
        """Registra tecla presionada para recovery"""
        key_name = e.ecodes.get(keycode, f"UNKNOWN_{keycode}")
        timestamp = datetime.now().isoformat()

        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} | {keycode} | {key_name}\n")

    def type_string(self, text):
        """Escribe string completo caracter por caracter"""
        char_map = {
            'a': e.KEY_A, 'b': e.KEY_B, 'c': e.KEY_C, 'd': e.KEY_D,
            'e': e.KEY_E, 'f': e.KEY_F, 'g': e.KEY_G, 'h': e.KEY_H,
            'i': e.KEY_I, 'j': e.KEY_J, 'k': e.KEY_K, 'l': e.KEY_L,
            'm': e.KEY_M, 'n': e.KEY_N, 'o': e.KEY_O, 'p': e.KEY_P,
            'q': e.KEY_Q, 'r': e.KEY_R, 's': e.KEY_S, 't': e.KEY_T,
            'u': e.KEY_U, 'v': e.KEY_V, 'w': e.KEY_W, 'x': e.KEY_X,
            'y': e.KEY_Y, 'z': e.KEY_Z,
            '0': e.KEY_0, '1': e.KEY_1, '2': e.KEY_2, '3': e.KEY_3,
            '4': e.KEY_4, '5': e.KEY_5, '6': e.KEY_6, '7': e.KEY_7,
            '8': e.KEY_8, '9': e.KEY_9,
            ' ': e.KEY_SPACE,
            '\n': e.KEY_ENTER,
            '\t': e.KEY_TAB,
        }

        for char in text.lower():
            keycode = char_map.get(char)
            if keycode:
                self.press_key(keycode)
                time.sleep(self.config.get('char_delay_ms', 30) / 1000)

    def tab_sequence(self, count=1, shift=False):
        """Secuencia de TAB con SHIFT hold correcto"""
        if shift:
            # SHIFT PRESS (mantener presionado)
            self.ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
            self.ui.syn()
            time.sleep(0.05)
            print(f"   [SHIFT HOLD] iniciando {count} TABs")
        
        for i in range(count):
            # TAB PRESS
            self.ui.write(e.EV_KEY, e.KEY_TAB, 1)
            self.ui.syn()
            time.sleep(0.05)
            # TAB RELEASE (SHIFT sigue presionado)
            self.ui.write(e.EV_KEY, e.KEY_TAB, 0)
            self.ui.syn()
            time.sleep(self.config.get('tab_delay_ms', 150) / 1000)
            print(f"   [TAB {i+1}/{count}] completado")
        
        if shift:
            # SHIFT RELEASE (al final de todos los TABs)
            self.ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
            self.ui.syn()
            time.sleep(0.05)
            print(f"   [SHIFT RELEASE] secuencia completada")

    def execute_sequence(self, platform, sequence_name):
        """Ejecuta secuencia predefinida para plataforma"""
        if platform not in self.platforms:
            raise ValueError(f"Plataforma no encontrada: {platform}")

        seq = self.platforms[platform].get('sequences', {}).get(sequence_name)
        if not seq:
            raise ValueError(f"Secuencia no encontrada: {sequence_name}")

        for action in seq:
            action_type = action.get('type')

            if action_type == 'key':
                keycode = getattr(e, action.get('keycode', 'KEY_ENTER'))
                self.press_key(keycode)

            elif action_type == 'string':
                self.type_string(action.get('text', ''))

            elif action_type == 'delay':
                time.sleep(action.get('ms', 100) / 1000)

            elif action_type == 'clipboard_read':
                content = self.get_clipboard()
                return content

        return True
    
    def focus_window(self, window_name):
        """Focaliza ventana en Wayland o X11"""
        session = subprocess.check_output(['echo', '$XDG_SESSION_TYPE'], shell=True, text=True).strip()
        
        if session == 'wayland':
            try:
                subprocess.run(['wlopt', '--focus', window_name])
            except FileNotFoundError:
                subprocess.run(['xdotool', 'search', '--name', window_name, 'windowactivate'])
        else:
            subprocess.run(['xdotool', 'search', '--name', window_name, 'windowactivate'])
        
        time.sleep(0.5)

    def get_clipboard(self):
        """Lee contenido del portapapeles"""
        try:
            return subprocess.check_output(['wl-paste']).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            return ""

    def capture_from_platform(self, platform):
        """
        Flujo completo: Focus → Navigate → Copy → Capture
        isTrusted: TRUE en todo el proceso
        """
        print(f"\n🎯 CAPTURE_FROM_PLATFORM: {platform}")
        print("=" * 50)
        
        platform_config = self.platforms.get(platform, {})
        
        # 1. Focalizar ventana
        window_name = platform_config.get('window_name', platform)
        print(f"📍 Ventana: {window_name}")
        self.focus_window(window_name)
        
        # 2. Navegar al botón copiar
        tab_seq = platform_config.get('copy_navigation', {})
        tabs = tab_seq.get('tabs', 2)
        shift = tab_seq.get('shift', False)
        print(f"🔀 Navegación: {tabs} TABs, shift={shift}")
        self.tab_sequence(count=tabs, shift=shift)
        
        # 3. Trigger copiar
        print("⏎ Presionando ENTER...")
        self.press_key(e.KEY_ENTER)
        time.sleep(0.5)
        
        # 4. Capturar clipboard
        print("📋 Leyendo clipboard...")
        content = self.get_clipboard()
        
        print("=" * 50)
        print(f"✅ CAPTURE COMPLETADO: {len(content)} chars")
        
        return content

    def run_daemon(self):
        """Bucle principal del daemon"""
        self.running = True
        print("🚀 NEUROBIT_HID_DAEMON iniciado")
        print(f"   Log de teclas: {self.log_path}")
        print(f"   Plataformas cargadas: {list(self.platforms.keys())}")

        while self.running:
            try:
                # Procesar cola de eventos
                try:
                    event = self.event_queue.get(timeout=0.5)
                    self.process_event(event)
                except queue.Empty:
                    pass

            except KeyboardInterrupt:
                print("\n⏹ Daemon detenido por usuario")
                break
            except Exception as e:
                print(f"❌ Error en daemon: {e}")
                time.sleep(1)

        self.shutdown()

    def process_event(self, event):
        """Procesa evento de la cola"""
        event_type = event.get('type')

        if event_type == 'inject_text':
            self.focus_window(event.get('window', ''))
            self.type_string(event.get('text', ''))

        elif event_type == 'capture_response':
            content = self.capture_from_platform(event.get('platform', ''))
            self.save_capture(content, event.get('filename', 'capture.txt'))

        elif event_type == 'execute_sequence':
            self.execute_sequence(
                event.get('platform', ''),
                event.get('sequence', '')
            )

    def save_capture(self, content, filename):
        """Guarda captura en directorio de fragmentos"""
        fragments_dir = Path("~/neurobit/data/fragments").expanduser()
        fragments_dir.mkdir(parents=True, exist_ok=True)

        filepath = fragments_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"[CAPTURED]: {datetime.now().isoformat()}\n[CONTENT]:\n{content}")

        print(f"✅ Captura guardada: {filepath}")

    def shutdown(self):
        """Apagado limpio"""
        self.running = False
        if self.ui:
            self.ui.close()
        print("🛑 NEUROBIT_HID_DAEMON detenido")

# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='NEUROBIT HID Daemon')
    parser.add_argument('--daemon', action='store_true', help='Ejecutar como daemon')
    parser.add_argument('--test', action='store_true', help='Test de dispositivo virtual')
    parser.add_argument('--capture', type=str, help='Capturar de plataforma (gemini/chatgpt)')
    parser.add_argument('--inject', type=str, help='Inyectar texto en ventana')
    parser.add_argument('--window', type=str, default='', help='Nombre de ventana destino')

    args = parser.parse_args()

    daemon = NeurobitHIDDaemon()

    if args.daemon:
        if not daemon.create_virtual_device():
            exit(1)
        daemon.run_daemon()

    elif args.test:
        if daemon.create_virtual_device():
            print("✅ Test: Escribiendo 'hola'")
            daemon.type_string("hola")
            daemon.shutdown()

    elif args.capture:
        if daemon.create_virtual_device():
            content = daemon.capture_from_platform(args.capture)
            print(f"✅ Capturado ({len(content)} chars):")
            print(content[:200] + "..." if len(content) > 200 else content)
            daemon.shutdown()

    elif args.inject:
        if daemon.create_virtual_device():
            daemon.focus_window(args.window)
            daemon.type_string(args.inject)
            daemon.shutdown()

    else:
        parser.print_help()
