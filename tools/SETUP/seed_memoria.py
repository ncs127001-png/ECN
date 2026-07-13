#!/usr/bin/env python3
"""Append a small set of seed messages to data/memoria_eva.jsonl

Usage: python3 tools/seed_memoria.py
"""
import json
import time
from pathlib import Path

base = Path(__file__).resolve().parents[1]
out = base / 'data' / 'memoria_eva.jsonl'
out.parent.mkdir(parents=True, exist_ok=True)

seeds = [
    {
        'message_id': 'msg_seed_welcome',
        'entity_id': 'NODO_SEMILLA',
        'perspective': 'organizativa',
        'content': 'Bienvenidos al Salón NEUROBIT. Objetivo: comenzar la primera ronda de integración.',
        'analysis': {},
        'provenance': {'created': time.strftime('%Y-%m-%dT%H:%M:%SZ')},
        'action': 'store',
        'human_approval': {'approved': False}
    },
    {
        'message_id': 'msg_seed_rules',
        'entity_id': 'DIRECTOR',
        'perspective': 'organizativa',
        'content': 'Reglas: 1) Respetar turnos. 2) Mantener claridad. 3) Registrar decisiones en Memoria.' ,
        'analysis': {},
        'provenance': {'created': time.strftime('%Y-%m-%dT%H:%M:%SZ')},
        'action': 'store',
        'human_approval': {'approved': False}
    }
]

with out.open('a', encoding='utf-8') as f:
    for s in seeds:
        f.write(json.dumps(s, ensure_ascii=False) + '\n')

print('Appended', len(seeds), 'seed messages to', str(out))
