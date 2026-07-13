"""Adapter para msg_builder - construye/prefila mensajes.

Si el módulo es importable, intenta llamar a su función. Si no, crea un archivo
temporal con el contenido y llama al script CLI con --source/--node/--out.
"""
from typing import Dict, Any
from ._loader import load_module_from_relpath, find_callable
import tempfile
from pathlib import Path

REL = "storage/modules/msg_builder_from_neurobit_central/msg_builder.py"


def send_message(envelope: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        mod = load_module_from_relpath(REL)
        fn = find_callable(mod, ["build", "make", "construct", "main"])
        if fn is None:
            # No direct callable -> run script non-interactively using temp files
            try:
                content = str(envelope.get('content') or envelope.get('CONTENT') or envelope)
                tmp_dir = tempfile.mkdtemp(prefix="neurobit_msg_builder_")
                src_path = Path(tmp_dir) / "source.txt"
                out_path = Path(tmp_dir) / "out_message.yaml"
                with open(src_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                node = envelope.get('entity_id') or envelope.get('ORIGEN') or envelope.get('origin') or 'TRON'
                from ._subproc import run_script_with_args
                args = ["--source", str(src_path), "--node", str(node), "--out", str(out_path)]
                subres = run_script_with_args(REL, args, timeout=15.0)
                # if usage error, try alternative flags and finally JSON stdin
                if subres.get('returncode') != 0:
                    alt_sets = [
                        ["--source", str(src_path), "--out", str(out_path), "--node", str(node)],
                        ["--input", str(src_path), "--out", str(out_path)],
                    ]
                    for alt in alt_sets:
                        try:
                            subres2 = run_script_with_args(REL, alt, timeout=15.0)
                            if subres2.get('returncode') == 0:
                                subres = subres2
                                break
                        except Exception:
                            continue
                    # last resort: pass envelope as JSON stdin
                    if subres.get('returncode') != 0:
                        try:
                            from ._subproc import run_script_with_json
                            subres3 = run_script_with_json(REL, envelope, timeout=20.0)
                            subres = subres3
                        except Exception:
                            pass
                if out_path.exists():
                    with open(out_path, 'r', encoding='utf-8') as f:
                        subres['generated_message'] = f.read()
                    subres['generated_path'] = str(out_path)
                return {"status": "ok" if subres.get("returncode") == 0 else "error", "note": "executed script subprocess (msg_builder)", "result": subres}
            except Exception as e:
                return {"status": "error", "note": f"msg_builder subprocess failed: {e}"}
        # if fn exists, call it
        try:
            res = fn(envelope)
            return {"status": "ok", "note": "msg_builder called", "result": res}
        except TypeError:
            from ._subproc import run_script_with_json
            subres = run_script_with_json(REL, envelope)
            return {"status": "ok" if subres.get("returncode")==0 else "error", "note": "executed script subprocess", "result": subres}
    except BaseException as e:
        return {"status": "error", "note": f"fatal: {e}"}
