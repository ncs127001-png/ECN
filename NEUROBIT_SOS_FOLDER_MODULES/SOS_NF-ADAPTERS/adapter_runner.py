#!/usr/bin/env python3
"""Ejecutor por adaptador: carga el adaptador solicitado y ejecuta send_message.
Salida: JSON en stdout.
"""
import sys
import json
import os

# Asegurar que el root del proyecto esté en sys.path para permitir imports relativos
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from typing import Dict

from core.adapters import (
    adapter_modulo_integrador,
    adapter_llama_dispatcher_connector,
    adapter_dispatcher_lite,
    adapter_msg_sequencer,
    adapter_msg_builder,
    adapter_simon_validator,
    adapter_sala_app,
)

ADAPTERS: Dict[str, object] = {
    'modulo_integrador': adapter_modulo_integrador,
    'llama_dispatcher_connector': adapter_llama_dispatcher_connector,
    'dispatcher_lite': adapter_dispatcher_lite,
    'msg_sequencer': adapter_msg_sequencer,
    'msg_builder': adapter_msg_builder,
    'simon_validator': adapter_simon_validator,
    'sala_app': adapter_sala_app,
}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'adapter name required'}))
        sys.exit(2)
    name = sys.argv[1]
    mod = ADAPTERS.get(name)
    if mod is None:
        print(json.dumps({'error': f'unknown adapter {name}'}))
        sys.exit(3)

    env = {'content': 'prueba adaptador desde runner', 'entity_id': 'SIMON_RUNNER', 'PROTOCOL_ID': 'NEUROBIT_MSG_v0'}
    try:
        res = mod.send_message(env, options={'dry_run': False})
    except BaseException as e:
        res = {'status': 'error', 'exception': str(e)}
    # Ensure JSON-serializable
    try:
        json.dumps(res)
    except Exception:
        res = {k: (v if isinstance(v, (str, int, float, bool, list, dict, type(None))) else str(v)) for k, v in res.items()}
    print(json.dumps(res, ensure_ascii=False))


if __name__ == '__main__':
    main()
