"""Adapter para msg_sequencer - orquestador de secuencias de mensajes.

Este script tiene modo interactivo por defecto; para uso programático
escribimos un archivo .txt temporal y llamamos la opción --file del script
o pasamos --input/--output según sea necesario.
"""
from typing import Dict, Any
from ._loader import load_module_from_relpath, find_callable
import tempfile
from pathlib import Path

REL = "storage/modules/msg_sequencer_from_neurobit_central/msg_sequencer.py"


def send_message(envelope: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        # Always prepare a non-interactive temp input/output pair up-front so fallbacks can reuse them.
        content = str(envelope.get('content') or envelope.get('CONTENT') or envelope)
        tmp_dir = Path(tempfile.mkdtemp(prefix="neurobit_msg_seq_"))
        input_dir = (tmp_dir / "input_texts").resolve()
        output_dir = (tmp_dir / "messages").resolve()
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = input_dir / "input_1.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        node = envelope.get('entity_id') or envelope.get('ORIGEN') or 'TRON'

        mod = load_module_from_relpath(REL)
        fn = find_callable(mod, ["sequence", "send", "process", "main"])
        if fn is None:
            # No importable callable: call script non-interactively with --file
            try:
                from ._subproc import run_script_with_args
                args = ["--file", str(file_path.resolve()), "--output", str(output_dir), "--node", str(node), "--non-interactive"]
                subres = run_script_with_args(REL, args, timeout=20.0)
                # if still failing, try alternative flags
                stdout = str(subres.get('stdout') or '')
                if subres.get('returncode') != 0 or any(k in stdout for k in ['Selecciona', 'interactive', 'Modo interactivo', 'Please enter']):
                    alt_flags = [
                        ["--file", str(file_path.resolve()), "--output", str(output_dir), "--node", str(node), "--select", "1"],
                        ["--input", str(input_dir), "--output", str(output_dir), "--node", str(node), "--non-interactive"],
                    ]
                    for alt in alt_flags:
                        try:
                            subres2 = run_script_with_args(REL, alt, timeout=20.0)
                            if subres2.get('returncode') == 0:
                                subres = subres2
                                break
                        except Exception:
                            continue
                subres['output_dir'] = str(output_dir)
                return {"status": "ok" if subres.get("returncode") == 0 else "error", "note": "msg_sequencer executed (non-interactive)", "result": subres}
            except Exception as e:
                return {"status": "error", "note": f"msg_sequencer subprocess failed: {e}"}

        # If fn exists, try calling it in safe sequences
        try:
            # prefer file-based API if available
            try:
                res = fn(str(file_path), str(output_dir), node)
            except TypeError:
                try:
                    res = fn(file_path, output_dir, node)
                except TypeError:
                    # fall back to passing envelope
                    res = fn(envelope)
            return {"status": "ok", "note": "msg_sequencer called", "result": res}
        except Exception:
            # try run_script_with_json as a fallback
            try:
                from ._subproc import run_script_with_json
                subres = run_script_with_json(REL, envelope)
                if subres.get('returncode') == 0:
                    return {"status": "ok", "note": "msg_sequencer executed via json stdin fallback", "result": subres}
            except Exception:
                pass
            # last attempt: if module exposes process_text_file, call it directly with the file we created above
            try:
                proc_fn = getattr(mod, 'process_text_file', None)
                if callable(proc_fn):
                    # attempt to call module's specific helper
                    ok = proc_fn(file_path, output_dir, node)
                    if ok:
                        return {"status": "ok", "note": "msg_sequencer.process_text_file invoked", "result": {"processed": True}}
            except Exception:
                # ignore and try msg_builder fallback below
                pass

            # Last-resort: invoke the known msg_builder script directly to build message from the text
            try:
                from ._subproc import run_script_with_args
                # prefer the centralized msg_builder module path
                MB_REL = "storage/modules/msg_builder_from_neurobit_central/msg_builder.py"
                out_name = f"mensaje_1.yaml"
                out_path = Path(output_dir) / out_name
                args = ["--source", str(file_path.resolve()), "--node", str(node), "--out", str(out_path), "--fragment-index", "1"]
                subres_mb = run_script_with_args(MB_REL, args, timeout=20.0)
                if subres_mb.get('returncode') == 0 and out_path.exists():
                    return {"status": "ok", "note": "msg_sequencer used msg_builder fallback", "result": {"generated": str(out_path)}}
            except Exception:
                pass

            return {"status": "error", "note": "msg_sequencer failed all fallbacks"}
    except BaseException as e:
        return {"status": "error", "note": f"fatal: {e}"}
