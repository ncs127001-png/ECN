"""Adapter para dispatcher_lite (wrapper ligero).
"""
from typing import Dict, Any
from ._loader import load_module_from_relpath, find_callable

REL = "storage/modules/dispatcher_lite_from_neurobit_central/dispatcher_lite.py"


def send_message(envelope: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        mod = load_module_from_relpath(REL)
        fn = find_callable(mod, ["send_message", "dispatch", "send", "main"])
        if fn is None:
            return {"status": "error", "note": "No callable found in dispatcher_lite"}
        if options and options.get("dry_run"):
            return {"status": "ok", "note": "dry_run", "preview": envelope.get("content")}
        # If callable expects (agent, task) or similar, map envelope accordingly.
        # Try several calling conventions robustly. Some modules expect (agent, task),
        # others expect envelope or content only. Try in order and fall back to subprocess.
        tried = []
        def try_call(*args):
            try:
                return True, fn(*args)
            except TypeError as te:
                tried.append(str(te))
                return False, te
            except Exception as e:
                tried.append(str(e))
                return False, e

        agent = envelope.get('DESTINO') or envelope.get('agent') or envelope.get('to') or envelope.get('entity_id') or 'TRON'
        task = envelope.get('task') or envelope.get('content') or envelope

        # 1) try (agent, task)
        ok, res = try_call(agent, task)
        if not ok:
            # 2) try (agent, envelope)
            ok, res = try_call(agent, envelope)
        if not ok:
            # 3) try envelope only
            ok, res = try_call(envelope)
        if not ok:
            # 4) try content only
            ok, res = try_call(envelope.get('content'))

        if not ok:
            # on any failure calling the importable, prefer running the script as a subprocess
            try:
                from ._subproc import run_script_with_json
                subres = run_script_with_json(REL, envelope)
                return {"status": "ok" if subres.get("returncode") == 0 else "error", "note": "dispatcher_lite executed via subprocess fallback", "result": subres}
            except Exception as e:
                return {"status": "error", "note": f"dispatcher_lite call failed and subprocess fallback failed: {e}", "tried": tried}
        return {"status": "ok", "note": "dispatcher_lite called", "result": res}
    except Exception as e:
        return {"status": "error", "note": str(e)}
    except BaseException as e:
        return {"status": "error", "note": f"fatal: {e}"}
