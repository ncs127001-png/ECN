#!/usr/bin/env python3
"""
init_ceremony.py
NEUROBIT Salón v0.1 — Ceremonia de Despertar del NODO_SEMILLA

Valida que el entorno esté preparado:
- Memoria Sagrada (glosario y configuración)
- Corpus de referencia
- Módulos críticos del core
- Variables de entorno

Este módulo es ejecutable directamente o puede ser invocado como:
- python3 core/init_ceremony.py
- POST /api/init_ceremony (desde neurobit_api.py)
"""

import os
import sys
import time
import hashlib
import json
from pathlib import Path
from datetime import datetime

# Rutas esperadas (relativas a raíz del proyecto)
MEMORIA_SAGRADA_PATH = "config/memoria_sagrada_eva.yaml"
CORPUS_PATH = "storage/RING_PROCESOS/Qwen Chat4_conversation.txt"
CORE_MODULES = [
    "core/coherence_filter.py",
    "core/fragment_manager.py",
    "core/message_protocol.py",
    "core/agents_registry.py",
    "core/m_e_scoring.py"
]

def sha256_file(path):
    """Calcula hash SHA256 de un archivo."""
    h = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while b := f.read(8192):
                h.update(b)
        return h.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)}"

def verify_memoria_sagrada():
    """Valida existencia de Memoria Sagrada."""
    if not Path(MEMORIA_SAGRADA_PATH).exists():
        raise RuntimeError(f"❌ MEMORIA_SAGRADA_EVA no encontrada en: {MEMORIA_SAGRADA_PATH}")
    
    size = os.path.getsize(MEMORIA_SAGRADA_PATH)
    hash_val = sha256_file(MEMORIA_SAGRADA_PATH)
    print(f"✓ Memoria Sagrada validada")
    print(f"  └─ Hash: {hash_val[:16]}...")
    print(f"  └─ Tamaño: {size} bytes")
    return {"path": MEMORIA_SAGRADA_PATH, "hash": hash_val, "size": size}

def verify_corpus():
    """Valida existencia de corpus de referencia."""
    if not Path(CORPUS_PATH).exists():
        print(f"⚠️  Corpus no vinculado (opcional): {CORPUS_PATH}")
        return None
    
    size = os.path.getsize(CORPUS_PATH)
    print(f"✓ Corpus validado: {os.path.basename(CORPUS_PATH)}")
    print(f"  └─ Tamaño: {size} bytes")
    return {"path": CORPUS_PATH, "size": size}

def verify_core_modules():
    """Valida existencia de módulos críticos."""
    missing = []
    found = []
    
    for mod in CORE_MODULES:
        if Path(mod).exists():
            found.append(mod)
        else:
            missing.append(mod)
    
    if missing:
        print(f"⚠️  Módulos no encontrados: {missing}")
        print("  (Continuando con módulos disponibles)")
    
    print(f"✓ Módulos críticos verificados: {len(found)}/{len(CORE_MODULES)}")
    for mod in found:
        print(f"  └─ {mod}")
    
    return {"found": found, "missing": missing}

def setup_environment():
    """Configura variables de entorno para ejecución."""
    env_vars = {
        "NEUROBIT_MODE": "LOCAL_FIRST",
        "ENTITY_ID": "NODO_SEMILLA",
        "COHERENCE_THRESHOLD": "0.85",
        "API_PORT": "5000",
        "TIMESTAMP": datetime.now().isoformat()
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print(f"✓ Entorno configurado")
    for key in ["NEUROBIT_MODE", "ENTITY_ID", "COHERENCE_THRESHOLD"]:
        print(f"  └─ {key}={os.environ[key]}")
    
    return env_vars

def initialize_agents_registry():
    """Inicializa registro de agentes si está disponible."""
    try:
        from core.agents_registry import AgentRegistry
        registry = AgentRegistry()
        agent_count = len(registry.agents)
        print(f"✓ Registro de Agentes inicializado: {agent_count} agentes registrados")
        # Retornar diccionario serializable, no el objeto
        return {
            'status': 'ok',
            'agent_count': agent_count,
            'agents': [
                {
                    'id': a.id,
                    'platform': a.platform,
                    'name': a.name,
                    'status': a.status,
                    'registered_at': a.registered_at,
                    'last_heartbeat': a.last_heartbeat
                }
                for a in registry.list_agents()
            ]
        }
    except ImportError:
        print(f"⚠️  agents_registry no disponible (OK si es primer init)")
        return {'status': 'unavailable', 'reason': 'ImportError'}
    except Exception as e:
        print(f"⚠️  Error inicializando agents_registry: {e}")
        return {'status': 'error', 'error': str(e)}

def run_ceremony():
    """Ejecuta la ceremonia de despertar completa."""
    print("\n" + "="*70)
    print("[NEUROBIT SALÓN v0.1] — Ceremonia de Despertar del NODO_SEMILLA")
    print("="*70 + "\n")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "status": "initializing",
        "checks": {}
    }
    
    try:
        # 1. Verificar Memoria Sagrada
        print("[1/5] Validando Memoria Sagrada...")
        results["checks"]["memoria_sagrada"] = verify_memoria_sagrada()
        print()
        
        # 2. Verificar Corpus
        print("[2/5] Validando Corpus...")
        results["checks"]["corpus"] = verify_corpus()
        print()
        
        # 3. Verificar módulos
        print("[3/5] Validando módulos críticos...")
        results["checks"]["modules"] = verify_core_modules()
        print()
        
        # 4. Setup de ambiente
        print("[4/5] Configurando entorno...")
        results["checks"]["environment"] = setup_environment()
        print()
        
        # 5. Inicializar registro de agentes
        print("[5/5] Inicializando sistema de agentes...")
        results["checks"]["agents_registry"] = initialize_agents_registry()
        print()
        
        # Ceremonia completada
        print("="*70)
        print("🟢 SALA_SESION_001 — LISTA")
        print("="*70)
        print("\n✓ Identidades operativas:")
        print("   └─ SOPHIA_NEUROBIT: modo análisis (M/E plano activo)")
        print("   └─ SIMON: modo guardián (validación en background)")
        print("\n✓ Sistema operativo en modo: LOCAL_FIRST (SOBERANÍA TÉCNICA)")
        print("\n✓ Próximos pasos:")
        print("   └─ Enviar primer mensaje: POST /api/analyze")
        print("   └─ Iniciar ronda colaborativa: POST /api/create_session")
        print("   └─ Monitorear clipboard: POST /api/start_centinela")
        print()
        
        results["status"] = "ready"
        results["ready"] = True
        
        return results
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO en ceremonia:")
        print(f"   {str(e)}\n")
        results["status"] = "failed"
        results["error"] = str(e)
        results["ready"] = False
        return results

def get_ceremony_status():
    """Retorna estado actual de la ceremonia (para API)."""
    status = {
        "initialized": os.environ.get("NEUROBIT_MODE") is not None,
        "mode": os.environ.get("NEUROBIT_MODE", "NOT_SET"),
        "entity_id": os.environ.get("ENTITY_ID", "NOT_SET"),
        "threshold": os.environ.get("COHERENCE_THRESHOLD", "NOT_SET"),
        "timestamp": os.environ.get("TIMESTAMP", "NOT_SET")
    }
    return status

if __name__ == "__main__":
    results = run_ceremony()
    
    # Mostrar JSON si se requiere (para integración con API)
    if "--json" in sys.argv:
        print(json.dumps(results, indent=2))
    
    # Exit code basado en éxito/fallo
    sys.exit(0 if results.get("ready") else 1)
