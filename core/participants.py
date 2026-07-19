"""Loader for participants configuration.

Provides a simple API to list and lookup participants defined in
`config/participants.json`.
"""
from pathlib import Path
import json

def _load_config():
    base = Path(__file__).resolve().parents[1]
    cfg = base / 'config' / 'participants.json'
    if not cfg.exists():
        return []
    try:
        with cfg.open('r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('participants', [])
    except Exception:
        return []

def list_participants():
    return _load_config()

def get_participant(entity_id: str):
    for p in _load_config():
        if p.get('entity_id') == entity_id:
            return p
    return None
