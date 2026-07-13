#!/usr/bin/env python3
"""
test_postman_integration.py — Test de integración Postman → Dispatcher
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

API_URL = "http://127.0.0.1:5000"
DISPATCHER_QUEUE = f"{API_URL}/dispatch/queue"
DISPATCHER_STATUS = f"{API_URL}/dispatch/status"

def test_postman_integration():
    """Test: Simular ciclo de Postman y verificar que llega al dispatcher"""
    
    print("=" * 70)
    print("TEST: Postman → Dispatcher Integration")
    print("=" * 70)
    print()
    
    # 1. Verificar API disponible
    print("1️⃣  Verificando API disponible...")
    try:
        resp = requests.get(DISPATCHER_STATUS, timeout=5)
        if resp.status_code == 200:
            print("   ✅ API responde en", API_URL)
        else:
            print("   ❌ API no responde correctamente")
            return False
    except requests.RequestException as e:
        print(f"   ❌ Error conectando a API: {e}")
        return False
    
    # 2. Obtener estado inicial
    print("\n2️⃣  Estado inicial del dispatcher:")
    status = resp.json()
    events_before = status.get('events_written', 0)
    print(f"   Eventos escritos antes: {events_before}")
    
    # 3. Simular ciclo de Postman (recolección → clasificación → entrega)
    print("\n3️⃣  Simulando ciclo de Postman (Cartero Consciente)...")
    
    # Mensaje de ejemplo para clasificar
    test_messages = [
        {
            'type': 'postman_delivery',
            'content': 'Informe de arquitectura del sistema',
            'destino': 'arquitectura',
            'timestamp': datetime.now().isoformat(),
            'source': 'neurobit_postman_daemon'
        },
        {
            'type': 'postman_delivery',
            'content': 'Estado general del equipo NODO_SEMILLA',
            'destino': 'estado',
            'timestamp': datetime.now().isoformat(),
            'source': 'neurobit_postman_daemon'
        },
        {
            'type': 'postman_checkpoint',
            'content': 'Cartero paso completado - ciclo 8 horas',
            'timestamp': datetime.now().isoformat(),
            'source': 'neurobit_postman_daemon'
        }
    ]
    
    try:
        resp = requests.post(
            DISPATCHER_QUEUE,
            json={"events": test_messages},
            timeout=5
        )
        if resp.status_code == 200:
            result = resp.json()
            print(f"   ✅ {result.get('count', 0)} eventos de Postman encolados")
            print(f"   Buffer size: {result.get('buffer_size', 0)}")
        else:
            print(f"   ❌ Error: {resp.status_code}")
            return False
    except requests.RequestException as e:
        print(f"   ❌ Error encolando: {e}")
        return False
    
    # 4. Esperar flush
    print("\n4️⃣  Esperando auto-flush (max 35 segundos)...")
    time.sleep(2)
    
    # 5. Verificar que los eventos fueron escritos
    print("\n5️⃣  Verificando eventos en dispatcher...")
    try:
        resp = requests.get(DISPATCHER_STATUS, timeout=5)
        status = resp.json()
        events_after = status.get('events_written', 0)
        
        if events_after > events_before:
            print(f"   ✅ Eventos persisten: {events_before} → {events_after}")
            print(f"   Batches flushed: {status.get('batches_flushed', 0)}")
            print(f"   Buffer actual: {status.get('buffer_size', 0)}")
        else:
            print(f"   ⚠️  No se incrementaron eventos: {events_before} → {events_after}")
    except requests.RequestException as e:
        print(f"   ❌ Error verificando: {e}")
        return False
    
    # 6. Verificar memoria_eva.jsonl
    print("\n6️⃣  Verificando memoria_eva.jsonl...")
    try:
        with open("/home/oxo-nuxun-80-08-unxnu-oxo/WORKSPACE_NEUROBIT_V0.2/data/memoria_eva.jsonl", "r") as f:
            lines = f.readlines()
            
        # Buscar eventos de Postman
        postman_events = [
            json.loads(line) for line in lines
            if "postman" in line.lower()
        ]
        
        if postman_events:
            print(f"   ✅ {len(postman_events)} eventos de Postman en memoria_eva.jsonl")
            for evt in postman_events[-3:]:
                print(f"      - {evt.get('type', '?')}: {evt.get('content', '?')[:40]}...")
        else:
            print(f"   ℹ️  No se encontraron eventos postman (primera ejecución)")
    except FileNotFoundError:
        print("   ⚠️  memoria_eva.jsonl no encontrado")
    except Exception as e:
        print(f"   ❌ Error verificando archivo: {e}")
    
    # 7. Verificar directorios de Postman creados
    print("\n7️⃣  Verificando estructura de directorios Postman...")
    workspace = Path.home() / 'WORKSPACE_NEUROBIT_V0.2'
    dirs_to_check = [
        workspace / 'data' / 'bbs' / 'informes',
        workspace / 'data' / 'bbs' / 'arquitectura',
        workspace / 'data' / 'sala' / 'estado'
    ]
    
    for d in dirs_to_check:
        if d.exists():
            print(f"   ✅ {d.name}/ existe")
        else:
            print(f"   ❌ {d.name}/ NO existe")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETADO")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        success = test_postman_integration()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrumpido")
        exit(1)
