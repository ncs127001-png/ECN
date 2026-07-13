"""Adapter para modulo_integrador copiado en storage/modules.
"""
from pathlib import Path
from ._loader import load_module_from_relpath, find_callable
from typing import Dict, Any
import tempfile
from pathlib import Path as P
import os


REL = "storage/modules/modulo_integrador_from_neurobit_central/modulo_integrador.py"


def send_message(envelope: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        mod = load_module_from_relpath(REL)
        fn = find_callable(mod, ["integrate", "send_message", "dispatch", "main", "run"])
        if fn is None:
            # create temp lista file and call CLI with sensible defaults
            try:
                tmp = tempfile.mkdtemp(prefix="neurobit_integrador_")
                lista = P(tmp) / "lista.txt"
                # envelope content may be a list or text; try to create lines
                content = envelope.get('content') or envelope.get('CONTENT') or envelope
                if isinstance(content, (list, tuple)):
                    lines = [str(x) for x in content]
                else:
                    lines = str(content).splitlines() or [str(content)]
                with open(lista, 'w', encoding='utf-8') as f:
                    for l in lines:
                        f.write(l.strip() + "\n")

                dir_busqueda = str(P('.').resolve())
                dir_destino = str(P(tmp) / 'dest')
                os.makedirs(dir_destino, exist_ok=True)
                from ._subproc import run_script_with_args
                args = ["--lista_archivos", str(lista), "--dir_busqueda", dir_busqueda, "--dir_destino", dir_destino]
                subres = run_script_with_args(REL, args, timeout=30.0)
                # if usage error (returncode != 0) try alternative flag names
                if subres.get("returncode") != 0:
                    alt_args_sets = [
                        ["--lista", str(lista), "--dir_busqueda", dir_busqueda, "--out", dir_destino],
                        ["--input", str(lista), "--root", dir_busqueda, "--dest", dir_destino],
                    ]
                    for alt in alt_args_sets:
                        try:
                            subres2 = run_script_with_args(REL, alt, timeout=30.0)
                            if subres2.get("returncode") == 0:
                                subres = subres2
                                break
                        except Exception:
                            continue
                subres['dest_dir'] = dir_destino
                if subres.get("returncode") != 0:
                    # try running script with JSON on stdin as last resort
                    try:
                        from ._subproc import run_script_with_json
                        subres2 = run_script_with_json(REL, envelope, timeout=30.0)
                        subres2['dest_dir'] = dir_destino
                        return {"status": "ok" if subres2.get("returncode") == 0 else "error", "note": "modulo_integrador executed (json stdin fallback)", "result": subres2}
                    except Exception:
                        pass
                return {"status": "ok" if subres.get("returncode") == 0 else "error", "note": "modulo_integrador executed (CLI)", "result": subres}
            except Exception as e:
                return {"status": "error", "note": f"modulo_integrador subprocess failed: {e}"}
        # intentar pasar envelope completo
        try:
            try:
                # preferir llamar directamente si la función acepta el envelope
                if hasattr(fn, "__code__") and fn.__code__.co_argcount > 0:
                    res = fn(envelope)
                else:
                    res = fn()
                return {"status": "ok", "note": "called modulo_integrador", "result": res}
            except Exception as e:
                # si falla la llamada importable, intentar la ruta CLI/JSON
                try:
                    # create temp lista file and call CLI (reuse logic above)
                    tmp = tempfile.mkdtemp(prefix="neurobit_integrador_")
                    lista = P(tmp) / "lista.txt"
                    content = envelope.get('content') or envelope.get('CONTENT') or envelope
                    if isinstance(content, (list, tuple)):
                        lines = [str(x) for x in content]
                    else:
                        lines = str(content).splitlines() or [str(content)]
                    with open(lista, 'w', encoding='utf-8') as f:
                        for l in lines:
                            f.write(l.strip() + "\n")
                    dir_busqueda = str(P('.').resolve())
                    dir_destino = str(P(tmp) / 'dest')
                    os.makedirs(dir_destino, exist_ok=True)
                    from ._subproc import run_script_with_args, run_script_with_json
                    args = ["--lista_archivos", str(lista), "--dir_busqueda", dir_busqueda, "--dir_destino", dir_destino]
                    subres = run_script_with_args(REL, args, timeout=30.0)
                    if subres.get("returncode") != 0:
                        # try alternatives
                        alt_args_sets = [
                            ["--lista", str(lista), "--dir_busqueda", dir_busqueda, "--out", dir_destino],
                            ["--input", str(lista), "--root", dir_busqueda, "--dest", dir_destino],
                        ]
                        for alt in alt_args_sets:
                            try:
                                subres2 = run_script_with_args(REL, alt, timeout=30.0)
                                if subres2.get("returncode") == 0:
                                    subres = subres2
                                    break
                            except Exception:
                                continue
                    # last resort: run with JSON stdin
                    if subres.get("returncode") != 0:
                        try:
                            subres_json = run_script_with_json(REL, envelope, timeout=30.0)
                            subres_json['dest_dir'] = dir_destino
                            return {"status": "ok" if subres_json.get("returncode") == 0 else "error", "note": "modulo_integrador executed (json stdin fallback)", "result": subres_json}
                        except Exception:
                            pass
                    subres['dest_dir'] = dir_destino
                    return {"status": "ok" if subres.get("returncode") == 0 else "error", "note": "modulo_integrador executed (CLI)", "result": subres}
                except Exception:
                    return {"status": "error", "note": f"modulo_integrador import call failed: {e}"}
        except BaseException as e:
            return {"status": "error", "note": f"fatal: {e}"}
    except BaseException as e:
        return {"status": "error", "note": f"fatal: {e}"}
