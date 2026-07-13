"""Adapter para sala_app - integra la app de sala como destino o endpoint local.
"""
from typing import Dict, Any
from ._loader import load_module_from_relpath, find_callable

REL = "storage/modules/sala_app_from_neurobit_central/sala_app.py"


def send_message(envelope: Dict[str, Any], options: Dict[str, Any] = None) -> Dict[str, Any]:
    try:
        # Intentar cargar como módulo si existe
        try:
            mod = load_module_from_relpath(REL)
        except FileNotFoundError:
            mod = None

        if mod:
            fn = find_callable(mod, ["push_message", "post_message", "handle", "main"])
            if fn:
                try:
                    res = fn(envelope)
                    return {"status": "ok", "note": "sala_app module called", "result": res}
                except TypeError:
                    # try calling without args or with content only
                    try:
                        res = fn()
                        return {"status": "ok", "note": "sala_app module called without args", "result": res}
                    except Exception:
                        try:
                            res = fn(envelope.get('content'))
                            return {"status": "ok", "note": "sala_app module called with content", "result": res}
                        except Exception:
                            # fallback to HTTP below
                            pass
                except Exception as e:
                    return {"status": "error", "note": f"sala_app module call failed: {e}"}

        # Si no hay módulo ejecutable, intentar pedir a un endpoint por opciones
        endpoint = None
        if options and options.get("endpoint"):
            endpoint = options.get("endpoint")
        else:
            # fallback al valor del proyecto (puede no existir)
            endpoint = "http://127.0.0.1:5000/send_message"  # convención mínima (sala_app usa /send_message)

        if options and options.get("dry_run"):
            return {"status": "ok", "note": "dry_run", "endpoint": endpoint}

        # enviar como JSON (importar requests sólo cuando se necesite)
        try:
            import requests
        except Exception:
            return {"status": "error", "note": "requests library not installed for HTTP fallback"}
        r = requests.post(endpoint, json=envelope, timeout=5)
        return {"status": "ok" if r.ok else "error", "code": r.status_code, "text": r.text}
    except Exception as e:
        return {"status": "error", "note": str(e)}
    except BaseException as e:
        return {"status": "error", "note": f"fatal: {e}"}
