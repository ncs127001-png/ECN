"""Adapter para simon_validator - validador local (LLM / heurística).

El script espera un archivo YAML. Si no hay función importable, generamos
un mensaje YAML mínimo a partir del envelope y llamamos al script con la ruta
al archivo.
"""
from typing import Dict, Any
from ._loader import load_module_from_relpath, find_callable
import tempfile
import yaml
from pathlib import Path
import uuid
from datetime import datetime

REL = "storage/modules/simon_validator_from_neurobit_central/simon_validator.py"


def _dump_message_yaml_from_envelope(envelope: Dict[str, Any], target_path: Path) -> None:
    # Minimal mapping to the simon expected schema
    content = envelope.get('content') or envelope.get('CONTENT') or str(envelope)
    created = envelope.get('CREATED_AT') or (datetime.utcnow().isoformat() + 'Z')
    origen = envelope.get('entity_id') or envelope.get('ORIGEN') or envelope.get('origin') or 'TRON'
    # compute short sha1 like msg_builder
    def sha1_short(text):
        import hashlib
        return hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]
    message_hash = sha1_short(str(content) + str(origen) + str(created))
    doc = {
        "PROTOCOL_ID": envelope.get('PROTOCOL_ID', 'NEUROBIT_MSG_v0'),
        "VERSION": envelope.get('VERSION', '0.1'),
        "MESSAGE_ID": envelope.get('MESSAGE_ID', str(uuid.uuid4())),
        "SESSION_ID": envelope.get('SESSION_ID', envelope.get('session', 'SALA_01')),
        "CREATED_AT": created,
        "ORIGEN": origen,
        "FRAGMENT": envelope.get('FRAGMENT', {"INDEX": 1, "TOTAL": 1}),
        "CONTENT": content,
        "MESSAGE_HASH": message_hash,
    }
    with open(target_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True)


def send_message(envelope: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        # Simpler, robust path: create YAML and call the script via subprocess.
        tmp = tempfile.mkdtemp(prefix="neurobit_simon_")
        msg_path = Path(tmp) / "msg.yaml"
        _dump_message_yaml_from_envelope(envelope, msg_path)
        from ._subproc import run_script_with_args
        # Primary attempt: pass path as positional
        subres = run_script_with_args(REL, [str(msg_path)], timeout=10.0)
        # If Usage/returncode indicates it didn't accept path, try --stdin with YAML bytes
        if subres.get('returncode') != 0 and ("Usage" in str(subres.get('stdout') or '') or "Usage" in str(subres.get('stderr') or '')):
            try:
                yaml_bytes = open(msg_path, 'rb').read()
                subres2 = run_script_with_args(REL, ["--stdin"], input_bytes=yaml_bytes, timeout=10.0)
                if subres2.get('returncode') == 0:
                    subres = subres2
            except Exception:
                # try explicit flags as fallback
                alt_args = [["--message", str(msg_path)], ["--input", str(msg_path)], ["--file", str(msg_path)]]
                for alt in alt_args:
                    try:
                        subres3 = run_script_with_args(REL, alt, timeout=10.0)
                        if subres3.get('returncode') == 0:
                            subres = subres3
                            break
                    except Exception:
                        continue
        return {"status": "ok" if subres.get("returncode") == 0 else "error", "note": "simon_validator executed", "result": subres}
    except Exception as e:
        return {"status": "error", "note": f"simon subprocess failed: {e}"}
