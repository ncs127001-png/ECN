"""
Adapter MCP: cliente ligero para el servidor MCP local.
Provee send_message(envelope, options) y funciones auxiliares para read_arca.
"""
from __future__ import annotations
import json
import os
import sys
from typing import Optional, Dict, Any

try:
    import requests
except Exception:
    requests = None
    from urllib import request as _urllib_request
    from urllib import parse as _urllib_parse

MCP_URL = os.environ.get("NEUROBIT_MCP_URL", "http://127.0.0.1:8090")


def _post(path: str, payload: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
    url = MCP_URL.rstrip('/') + path
    headers = {"Content-Type": "application/json"}
    body = json.dumps(payload).encode('utf-8')
    if requests:
        r = requests.post(url, json=payload, headers=headers, timeout=timeout)
        try:
            return r.json()
        except Exception:
            return {"status": "error", "http_code": r.status_code, "text": r.text}
    else:
        req = _urllib_request.Request(url, data=body, headers=headers, method='POST')
        with _urllib_request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode('utf-8')
            try:
                return json.loads(text)
            except Exception:
                return {"status": "ok", "text": text}


def _get(path: str, params: Optional[Dict[str, Any]] = None, timeout: int = 10) -> Dict[str, Any]:
    base = MCP_URL.rstrip('/') + path
    if params:
        qs = '&'.join(f"{k}={v}" for k, v in params.items())
        url = f"{base}?{qs}"
    else:
        url = base

    if requests:
        r = requests.get(url, timeout=timeout)
        try:
            return r.json()
        except Exception:
            return {"status": "error", "http_code": r.status_code, "text": r.text}
    else:
        with _urllib_request.urlopen(url, timeout=timeout) as resp:
            text = resp.read().decode('utf-8')
            try:
                return json.loads(text)
            except Exception:
                return {"status": "ok", "text": text}


def send_message(envelope: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Enviar un envelope al servidor MCP (escribe en la arca).

    Envelope esperado: contiene al menos 'MESSAGE_ID' y 'content'
    """
    payload = {
        "MESSAGE_ID": envelope.get("MESSAGE_ID") or envelope.get("message_id") or envelope.get("id"),
        "content": envelope.get("content"),
        "SESSION_TAG": envelope.get("SESSION_TAG"),
        "ORIGEN": envelope.get("ORIGEN"),
        "DESTINO": envelope.get("DESTINO"),
    }

    return _post('/write_arca', payload)


def read_arca(limit: int = 5) -> Dict[str, Any]:
    """Leer los últimos registros de la arca vía MCP"""
    return _get('/read_arca', params={"limit": limit})


if __name__ == '__main__':
    # Prueba rápida de import
    print('MCP adapter - test ping to', MCP_URL)
    print(read_arca(3))
