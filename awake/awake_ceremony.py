#!/usr/bin/env python3
# awake_ceremony.py
# NEUROBIT_SALON_v0.1 — modo HOMO VIVO
import os
import time
import hashlib
from pathlib import Path

MEMORIA_SAGRADA_PATH = "config/memoria_sagrada_eva.yaml"
CORPUS_PATH = "storage/RING_PROCESOS/Qwen Chat4_conversation.txt"
CORE_MODULES = [
    "core/coherence_filter.py",
    "core/fragment_manager.py",
    "core/message_protocol.py"
]

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while b := f.read(8192):
            h.update(b)
    return h.hexdigest()

def main():
    print("[NEUROBIT SALÓN v0.1] — Ceremonia de Despertar\n")
    
    if not Path(MEMORIA_SAGRADA_PATH).exists():
        raise RuntimeError("❌ MEMORIA_SAGRADA_EVA no encontrada.")
    print(f"✓ Memoria Sagrada cargada: {sha256_file(MEMORIA_SAGRADA_PATH)[:8]}")

    if not Path(CORPUS_PATH).exists():
        raise RuntimeError("❌ Corpus de prueba no vinculado.")
    print(f"✓ Corpus validado: {os.path.basename(CORPUS_PATH)} ({os.path.getsize(CORPUS_PATH)} B)")

    for mod in CORE_MODULES:
        if not Path(mod).exists():
            raise RuntimeError(f"❌ Módulo faltante: {mod}")
    print("✓ Módulos críticos verificados: coherence_filter, fragment_manager, message_protocol")

    print("\n[PRE-CARGA] Iniciando entorno operativo…")
    os.environ["NEUROBIT_MODE"] = "LOCAL_FIRST"
    os.environ["ENTITY_ID"] = "NODO_SEMILLA"
    os.environ["COHERENCE_THRESHOLD"] = "0.85"
    print("✓ Entorno configurado: LOCAL_FIRST | THRESHOLD=0.85")

    time.sleep(0.7)
    print("\n🟢 SALA_SESION_001 — LISTA")
    print("   > Esperando primer mensaje desde NODO_SEMILLA")
    print("   > SOPHIA_NEUROBIT: modo análisis (M/E plano activo)")
    print("   > SIMON: modo guardián (validación en background)")
    print("\nComando para iniciar ronda: `python3 core/round_manager.py --input-session=001`")

if __name__ == "__main__":
    main()
