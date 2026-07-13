#!/usr/bin/env python3
"""
neurobit_keylogger.py — Daemon de captura HID con WAL y integración Dispatcher
Autor: NODO_SEMILLA
Fecha: 23 de mayo de 2026 - v1
Estado: ✅ Operacional con Append-Only Storage
v0.6 — FIX: Agregado método run() faltante + indentación corregida
"""

import os
import json
import time
import signal
from datetime import datetime
from pathlib import Path
from threading import Thread, Event

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests no disponible - fallback a archivo local")


# ============================================================================
# CLASE PRINCIPAL: KeyloggerWithWAL
# ============================================================================
class KeyloggerWithWAL:
    def __init__(self, logs_dir="data/logs", dispatcher_url="http://127.0.0.1:5000/dispatch/queue",
                 capture_keyboard=True, capture_mouse=False):
        # 1. PRIMERO: Definir rutas y directorios
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. Definir archivos de log
        self.main_log = self.logs_dir / "keylog_main.jsonl"
        self.temp_log = self.logs_dir / "keylog_temp.jsonl"

        # 3. Dispatcher integration
        self.dispatcher_url = dispatcher_url if REQUESTS_AVAILABLE else None
        
        # 4. Configuración de commit
        self.batch_size = 50
        self.batch_interval = 30
        self.event_count = 0
        self.last_commit = datetime.now()
        
        # 5. Filtros de dispositivos (UNA SOLA VEZ)
        self.capture_keyboard = capture_keyboard
        self.capture_mouse = capture_mouse

        # 6. Recuperar datos no comprometidos
        self._recover_uncommitted_data()

        # 7. Shutdown control
        self.shutdown_event = Event()
        self._shutdown_called = False
  
    def shutdown(self):
        """Shutdown limpio — idempotente (evita doble ejecución)"""
        if self._shutdown_called:
            return
        self._shutdown_called = True
        
        print("\n⏹️  Keylogger shutting down...")
        self.shutdown_event.set()
        self.force_commit()
        print("✅ Keylogger cerrado")
    
    def _recover_uncommitted_data(self):
        """Recupera datos del archivo temporal si existen (post-corte de luz)"""
        if self.temp_log.exists() and self.temp_log.stat().st_size > 0:
            print(f"⚠️ Recuperando {self.temp_log.stat().st_size} bytes no comprometidos...")
            try:
                with open(self.temp_log, 'r', encoding='utf-8') as f:
                    uncommitted = f.readlines()
                
                with open(self.main_log, 'a', encoding='utf-8') as f:
                    f.writelines(uncommitted)
                
                self.temp_log.write_text('')
                print(f"✅ {len(uncommitted)} eventos recuperados exitosamente")
            except Exception as e:
                print(f"❌ Error en recuperación: {e}")
    
    def log_keystroke(self, data):
        """Registra pulsación con WAL"""
        event = {
            **data,
            'timestamp': datetime.now().isoformat(),
            'entity_id': 'NODO_SEMILLA'
        }
        
        with open(self.temp_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False) + '\n')
        
        self.event_count += 1
        
        if self._should_commit():
            self._commit_to_main()
    
    def _should_commit(self):
        """Determina si debe comprometer al archivo principal"""
        if self.event_count >= self.batch_size:
            return True
        if (datetime.now() - self.last_commit).seconds >= self.batch_interval:
            return True
        return False
    
    def _commit_to_main(self):
        """Compromete datos del temporal al principal"""
        try:
            # ✅ VERIFICAR que el archivo temporal existe antes de leerlo
            if not self.temp_log.exists() or self.temp_log.stat().st_size == 0:
                return

            with open(self.temp_log, 'r', encoding='utf-8') as f:
                data = f.readlines()
            
            if not data:
                return
            
            # Intentar enviar al dispatcher primero
            if self.dispatcher_url and REQUESTS_AVAILABLE:
                try:
                    events = []
                    for line in data:
                        try:
                            event_data = json.loads(line)
                            events.append(event_data)
                        except json.JSONDecodeError:
                            pass
                    
                    if events:
                        response = requests.post(
                            self.dispatcher_url,
                            json={"events": events},
                            timeout=5
                        )
                        if response.status_code == 200:
                            print(f"✅ Keylogger → Dispatcher: {len(events)} eventos encolados")
                            self.temp_log.write_text('')
                            self.event_count = 0
                            self.last_commit = datetime.now()
                            return
                except requests.RequestException as e:
                    print(f"⚠️ Dispatcher unavailable ({e}), fallback a archivo local")
            
            # FALLBACK: Escribir al principal (append-only)
            with open(self.main_log, 'a', encoding='utf-8') as f:
                f.writelines(data)
            
            self.temp_log.write_text('')
            self.event_count = 0
            self.last_commit = datetime.now()
            print(f"✅ Commit local: {len(data)} eventos asentados (fallback)")
            
        except Exception as e:
            print(f"❌ Error en commit: {e}")
    
    def force_commit(self):
        """Forzar commit (para shutdown limpio)"""
        print("🔄 Forzando commit final...")
        self._commit_to_main()
        print("✅ Commit final completado")


# ============================================================================
# CLASE DAEMON: KeyloggerDaemon
# ============================================================================
class KeyloggerDaemon:
    """Daemon que captura eventos HID y los registra"""
    
    def __init__(self, capture_keyboard=True, capture_mouse=False):
        self.keylogger = KeyloggerWithWAL(
            capture_keyboard=capture_keyboard,
            capture_mouse=capture_mouse
        )
        self.running = True
    
    def simulate_keypresses(self):
        """Simula captura de pulsaciones (para testing sin acceso a /dev/input)"""
        import time
        
        # ✅ CORREGIDO: Usar caracteres individuales, no strings
        test_keys = ['a', 'b', 'c', 'd', 'e', ' ', 'Return']
        
        print("\n🔄 Modo simulación - capturando pulsaciones de prueba...")
        print("   (En producción leerá de /dev/input/event*)")
        print()
        
        for i in range(20):
            if self.keylogger.shutdown_event.is_set():
                break
            
            key = test_keys[i % len(test_keys)]
            self.keylogger.log_keystroke({
                'key': key,
                'device': '/dev/input/event0',
                'raw_code': ord(key) if len(key) == 1 else 0
            })
            
            print(f"   📝 Tecla capturada: {key}")
            time.sleep(0.5)
        
        self.keylogger.force_commit()
    
    def capture_real_events(self):
        """Captura eventos HID reales filtrando la duplicación en caliente."""
        try:
            import evdev
            from evdev import ecodes
            import select
            print("\n  Capturando eventos HID reales optimizados...")
        except ImportError:
            print("\n  evdev no instalado - usando simulación")
            return self.simulate_keypresses()

        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        except Exception as e:
            print(f" Error accediendo a /dev/input: {e}")
            return self.simulate_keypresses()

        active_devices = []
        for dev in devices:
            caps = dev.capabilities()
            if self.keylogger.capture_keyboard and ecodes.EV_KEY in caps:
                if any(k in dev.name.lower() for k in ['power button', 'sleep button', 'video bus', 'lid switch']):
                    continue
                active_devices.append(dev)

        try:
            while not self.keylogger.shutdown_event.is_set():
                readable, _, _ = select.select(active_devices, [], [], 1.0)
                for device in readable:
                    try:
                        for event in device.read():
                            if self.keylogger.shutdown_event.is_set():
                                break
                            
                            # CRÍTICO: Filtrar estrictamente para evitar duplicados en el archivo .jsonl
                            # event.value == 1 asegura registrar SOLO cuando la tecla se hunde (Press)
                            # Se ignoran event.value == 0 (Release) y 2 (Long-press repetitivo)
                            if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                                key_name = evdev.ecodes.KEY.get(event.code, f"KEY_{event.code}")
                                
                                # Evitamos contaminar el log si son movimientos nativos de puntero/mouse de rango 272+
                                if event.code < 250:
                                    self.keylogger.log_keystroke({
                                        'key': str(key_name),
                                        'device': device.path,
                                        'raw_code': event.code
                                    })
                    except OSError:
                        continue
        except KeyboardInterrupt:
            pass
        finally:
            self.keylogger.force_commit()

    
    def run(self):
        """Inicia el daemon: captura real o simulación"""
        print("\n" + "=" * 70)
        print("🔑 NEUROBIT KEYLOGGER DAEMON")
        print("=" * 70)
        
        try:
            self.capture_real_events()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"❌ Error en daemon: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.keylogger.shutdown()


# ============================================================================
# ENTRY POINT
# ============================================================================
def signal_handler(signum, frame):
    """Manejo limpio de señales"""
    global daemon
    print(f"\n⚠️  Señal {signum} recibida")
    daemon.keylogger.shutdown()
    exit(0)


if __name__ == "__main__":
    # Configurar handlers de señal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Crear y ejecutar daemon (SOLO teclado por defecto)
    daemon = KeyloggerDaemon(capture_keyboard=True, capture_mouse=False)
    daemon.run()
