"""Adapter para llama_dispatcher_connector (conector LLM local - ollama/llama).
"""
from typing import Dict, Any
from ._loader import load_module_from_relpath, find_callable
import tempfile
from pathlib import Path
import yaml
import uuid
from datetime import datetime

REL = "storage/modules/llama_dispatcher_connector_from_neurobit_central/llama_dispatcher_connector.py"


def send_message(envelope: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        mod = load_module_from_relpath(REL)
        fn = find_callable(mod, ["send_message", "dispatch", "call_llm", "main", "run"])
        if fn is None:
            # try CLI path: write message YAML and call script with path
            try:
                tmp = tempfile.mkdtemp(prefix="neurobit_llama_")
                msg_path = Path(tmp) / "msg.yaml"
                doc = {
                    "PROTOCOL_ID": envelope.get('PROTOCOL_ID', 'NEUROBIT_MSG_v0'),
                    "VERSION": envelope.get('VERSION', '0.1'),
                    "MESSAGE_ID": envelope.get('MESSAGE_ID', str(uuid.uuid4())),
                    "SESSION_ID": envelope.get('SESSION_ID', 'SALA_01'),
                    "CREATED_AT": envelope.get('CREATED_AT', datetime.utcnow().isoformat() + 'Z'),
                    "ORIGEN": envelope.get('entity_id') or envelope.get('ORIGEN') or 'TRON',
                    "FRAGMENT": envelope.get('FRAGMENT', {"INDEX": 1, "TOTAL": 1}),
                    "CONTENT": envelope.get('content') or envelope.get('CONTENT') or str(envelope)
                }
                with open(msg_path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True)
                from ._subproc import run_script_with_args
                subres = run_script_with_args(REL, [str(msg_path)], timeout=20.0)
                return {"status": "ok" if subres.get("returncode") == 0 else "error", "note": "llama CLI executed", "result": subres}
            except Exception as e:
                return {"status": "error", "note": f"llama CLI failed: {e}"}
        # respect dry_run
        if options and options.get("dry_run"):
            return {"status": "ok", "note": "dry_run", "preview": str(envelope.get("content", ""))}
        # call with envelope or content (robust sequence)
        res = None
        try:
            res = fn(envelope)
        except Exception:
            # try passing the raw content
            try:
                res = fn(envelope.get("content"))
            except Exception:
                # try passing a temporary YAML path
                try:
                    tmp2 = tempfile.mkdtemp(prefix="neurobit_llama_call_")
                    p = Path(tmp2) / "call.yaml"
                    content_obj = envelope.get("content") or envelope
                    with open(p, 'w', encoding='utf-8') as f:
                        yaml.safe_dump(content_obj, f, sort_keys=False, allow_unicode=True)
                    res = fn(str(p))
                except Exception:
                    # fallback to CLI invocation
                    try:
                        tmp = tempfile.mkdtemp(prefix="neurobit_llama_")
                        msg_path = Path(tmp) / "msg.yaml"
                        doc = {
                            "PROTOCOL_ID": envelope.get('PROTOCOL_ID', 'NEUROBIT_MSG_v0'),
                            "VERSION": envelope.get('VERSION', '0.1'),
                            "MESSAGE_ID": envelope.get('MESSAGE_ID', str(uuid.uuid4())),
                            "SESSION_ID": envelope.get('SESSION_ID', 'SALA_01'),
                            "CREATED_AT": envelope.get('CREATED_AT', datetime.utcnow().isoformat() + 'Z'),
                            "ORIGEN": envelope.get('entity_id') or envelope.get('ORIGEN') or 'TRON',
                            "FRAGMENT": envelope.get('FRAGMENT', {"INDEX": 1, "TOTAL": 1}),
                            "CONTENT": envelope.get('content') or envelope.get('CONTENT') or str(envelope)
                        }
                        with open(msg_path, 'w', encoding='utf-8') as f:
                            yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True)
                        from ._subproc import run_script_with_args
                        subres = run_script_with_args(REL, [str(msg_path)], timeout=20.0)
                        return {"status": "ok" if subres.get("returncode") == 0 else "error", "note": "llama CLI executed fallback", "result": subres}
                    except Exception as e2:
                        return {"status": "error", "note": f"llama call failed both importable and CLI: {e2}"}
        # If the callable returned a dict with a path-type error, try CLI as a last resort
        if isinstance(res, dict) and any("expected str" in str(v) or "os.PathLike" in str(v) for v in res.values()):
            try:
                tmp = tempfile.mkdtemp(prefix="neurobit_llama_")
                msg_path = Path(tmp) / "msg.yaml"
                doc = {
                    "PROTOCOL_ID": envelope.get('PROTOCOL_ID', 'NEUROBIT_MSG_v0'),
                    "VERSION": envelope.get('VERSION', '0.1'),
                    "MESSAGE_ID": envelope.get('MESSAGE_ID', str(uuid.uuid4())),
                    "SESSION_ID": envelope.get('SESSION_ID', 'SALA_01'),
                    "CREATED_AT": envelope.get('CREATED_AT', datetime.utcnow().isoformat() + 'Z'),
                    "ORIGEN": envelope.get('entity_id') or envelope.get('ORIGEN') or 'TRON',
                    "FRAGMENT": envelope.get('FRAGMENT', {"INDEX": 1, "TOTAL": 1}),
                    "CONTENT": envelope.get('content') or envelope.get('CONTENT') or str(envelope)
                }
                with open(msg_path, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True)
                from ._subproc import run_script_with_args
                subres = run_script_with_args(REL, [str(msg_path)], timeout=20.0)
                return {"status": "ok" if subres.get("returncode") == 0 else "error", "note": "llama CLI executed after importable error", "result": subres}
            except Exception:
                pass
        return {"status": "ok", "note": "llama connector called", "result": res}
    except Exception as e:
        return {"status": "error", "note": str(e)}
    except BaseException as e:
        return {"status": "error", "note": f"fatal: {e}"}
