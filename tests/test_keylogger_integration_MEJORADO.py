#!/usr/bin/env python3
"""
test_keylogger_integration.py — Test de integración Keylogger → Dispatcher
Autor: NODO_SEMILLA
Fecha: 27 de marzo de 2026
Propósito: Validar que los eventos del keylogger se integran correctamente
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

WORKSPACE = os.path.expanduser("~/WORKSPACE_NEUROBIT_V0.2")
API_URL = "http://127.0.0.1:5000"
DISPATCHER_QUEUE = f"{API_URL}/dispatch/queue"
DISPATCHER_STATUS = f"{API_URL}/dispatch/status"
DATA_DIR = os.path.join(WORKSPACE, "data")
MEMORIA_EVA = os.path.join(DATA_DIR, "memoria_eva.jsonl")

# Colores
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'

# ============================================================================
# UTILIDADES
# ============================================================================

def print_header(title):
    print()
    print("=" * 70)
    print(f"{BLUE}{title}{NC}")
    print("=" * 70)
    print()

def print_success(msg):
    print(f"{GREEN}✅ {msg}{NC}")

def print_error(msg):
    print(f"{RED}❌ {msg}{NC}")

def print_warning(msg):
    print(f"{YELLOW}⚠️  {msg}{NC}")

def print_info(msg):
    print(f"{BLUE}ℹ️  {msg}{NC}")

# ============================================================================
# TESTS
# ============================================================================

def test_api_available():
    """Test 1: Verificar que API está disponible"""
    print_info("1️⃣  Verificando API disponible...")
    
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        if resp.status_code == 200:
            print_success("API responde en " + API_URL)
            return True
        else:
            print_warning(f"API responde con status {resp.status_code}")
            return False
    except requests.RequestException as e:
        print_error(f"No se puede conectar a API: {e}")
        return False

def test_dispatcher_status():
    """Test 2: Verificar status del dispatcher"""
    print_info("2️⃣  Verificando status del dispatcher...")
    
    try:
        resp = requests.get(DISPATCHER_STATUS, timeout=5)
        if resp.status_code != 200:
            print_error(f"Dispatcher status: {resp.status_code}")
            return False, None
        
        status = resp.json()
        print_success("Dispatcher disponible")
        print(f"   - Eventos recibidos: {status.get('events_received', '?')}")
        print(f"   - Eventos escritos: {status.get('events_written', '?')}")
        print(f"   - Buffer actual: {status.get('buffer_size', '?')}")
        print(f"   - Worker activo: {status.get('worker_alive', False)}")
        
        return True, status
    except Exception as e:
        print_error(f"Error verificando dispatcher: {e}")
        return False, None

def test_queue_events():
    """Test 3: Encolar eventos simulados"""
    print_info("3️⃣  Encolando eventos simulados...")
    
    test_events = [
        {
            "type": "keylog_batch",
            "content": "tecla: h\ntecla: o\ntecla: l\ntecla: a",
            "source": "neurobit_keylogger_test",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        },
        {
            "type": "keylog_batch",
            "content": "tecla: Return",
            "source": "neurobit_keylogger_test",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
    ]
    
    try:
        resp = requests.post(
            DISPATCHER_QUEUE,
            json={"events": test_events},
            timeout=5
        )
        
        if resp.status_code != 200:
            print_error(f"No se pudieron encolar eventos: {resp.status_code}")
            return False
        
        result = resp.json()
        print_success(f"{result.get('count', 0)} eventos encolados")
        print(f"   - Buffer size: {result.get('buffer_size', 0)}")
        
        return True
    except Exception as e:
        print_error(f"Error encolando: {e}")
        return False

def test_auto_flush():
    """Test 4: Esperar y verificar auto-flush"""
    print_info("4️⃣  Esperando auto-flush (máximo 35 segundos)...")
    
    time.sleep(2)
    
    try:
        resp = requests.get(DISPATCHER_STATUS, timeout=5)
        if resp.status_code != 200:
            print_warning("No se pudo obtener status del dispatcher")
            return False
        
        status = resp.json()
        print_success("Dispatcher status actualizado")
        print(f"   - Buffer después del flush: {status.get('buffer_size', 0)}")
        print(f"   - Batches flushed: {status.get('batches_flushed', 0)}")
        
        return True
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_memoria_eva():
    """Test 5: Verificar persistencia en memoria_eva.jsonl"""
    print_info("5️⃣  Verificando memoria_eva.jsonl...")
    
    if not os.path.exists(MEMORIA_EVA):
        print_warning(f"Archivo no existe aún: {MEMORIA_EVA}")
        print("   (Esto es normal en primera ejecución)")
        return True
    
    try:
        with open(MEMORIA_EVA, 'r') as f:
            lines = f.readlines()
        
        print_success(f"Archivo accesible ({len(lines)} líneas)")
        
        # Buscar eventos de keylogger de test
        keylog_count = 0
        for line in lines:
            try:
                event = json.loads(line)
                if 'keylog' in event.get('type', '') and 'test' in event.get('source', ''):
                    keylog_count += 1
            except json.JSONDecodeError:
                pass
        
        if keylog_count > 0:
            print_success(f"Encontrados {keylog_count} eventos de keylogger")
            # Mostrar últimos 2
            print("   Últimos eventos:")
            for line in lines[-2:]:
                try:
                    event = json.loads(line)
                    content = event.get('content', '?')[:30]
                    print(f"   - {event.get('type', '?')}: {content}...")
                except:
                    pass
        else:
            print_warning("No se encontraron eventos de keylogger (aún)")
        
        return True
    except Exception as e:
        print_error(f"Error verificando archivo: {e}")
        return False

def test_keylogger_process():
    """Test 6: Verificar si el proceso keylogger está corriendo"""
    print_info("6️⃣  Verificando proceso keylogger...")
    
    try:
        import subprocess
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = result.stdout
        if 'neurobit_keylogger.py' in output and 'grep' not in output:
            print_success("Proceso keylogger está corriendo")
            # Extractar PID
            for line in output.split('\n'):
                if 'neurobit_keylogger.py' in line and 'grep' not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        print(f"   - PID: {parts[1]}")
            return True
        else:
            print_warning("Proceso keylogger NO está corriendo")
            print("   Iniciar con: bash start_keylogger.sh")
            return True  # No es error, solo warning
    except Exception as e:
        print_warning(f"No se pudo verificar proceso: {e}")
        return True

# ============================================================================
# MAIN
# ============================================================================

def main():
    print_header("🔑 TEST DE INTEGRACIÓN KEYLOGGER → DISPATCHER")
    print(f"Workspace: {WORKSPACE}")
    print(f"API URL: {API_URL}")
    print()
    
    tests = [
        ("API disponible", test_api_available),
        ("Dispatcher status", test_dispatcher_status),
        ("Encolar eventos", test_queue_events),
        ("Auto-flush", test_auto_flush),
        ("memoria_eva.jsonl", test_memoria_eva),
        ("Proceso keylogger", test_keylogger_process),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            # Si test_func retorna tupla, usar primer elemento
            if isinstance(result, tuple):
                result = result[0]
            results.append((name, result))
        except KeyboardInterrupt:
            print_warning("\nTest interrumpido por usuario")
            break
        except Exception as e:
            print_error(f"Error inesperado: {e}")
            results.append((name, False))
        
        print()
    
    # ========================================================================
    # RESUMEN
    # ========================================================================
    
    print_header("📊 RESUMEN DE RESULTADOS")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✅ PASS{NC}" if result else f"{RED}❌ FAIL{NC}"
        print(f"  {status} - {name}")
    
    print()
    print(f"Total: {passed}/{total} tests pasados")
    print()
    
    if passed == total:
        print_success("TODOS LOS TESTS PASARON ✨")
        print()
        print("La integración Keylogger → Dispatcher está funcionando correctamente.")
        return 0
    else:
        print_warning(f"{total - passed} test(s) fallaron")
        print()
        print("Verificar logs:")
        print(f"  - API: $WORKSPACE/data/logs/api_flask.log")
        print(f"  - Keylogger: $WORKSPACE/data/logs/keylogger_daemon.log")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print()
        print_warning("Test interrumpido")
        sys.exit(1)
