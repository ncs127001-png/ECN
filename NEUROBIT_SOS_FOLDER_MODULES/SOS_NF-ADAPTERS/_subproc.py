"""Helpers para ejecutar módulos CLI (scripts) como subprocess y comunicarlos con adaptadores.

Proporciona run_script_with_json that ejecuta el script con Python, pasa el `envelope` por stdin
como JSON y devuelve un dict con stdout/returncode/stderr.
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_script_with_json(relpath: str, envelope: Dict[str, Any], timeout: float = 10.0) -> Dict[str, Any]:
    """Ejecuta un script Python relativo al root del proyecto.

    - relpath: ruta relativa desde el root del proyecto hacia el script (ej: storage/modules/.../script.py)
    - envelope: dict que se serializa a JSON y se pasa por stdin
    - timeout: segundos para timeout

    Retorna dict: { returncode, stdout, stderr, parsed_output? }
    Si stdout contiene JSON válido se incluye parsed_output.
    """
    p = PROJECT_ROOT.joinpath(relpath)
    if not p.exists():
        return {"status": "error", "note": f"script not found: {p}"}

    cmd = ["/usr/bin/env", "python3", str(p)]
    try:
        proc = subprocess.run(
            cmd,
            input=json.dumps(envelope).encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        return {"status": "error", "note": "timeout", "timeout": True}

    out = proc.stdout.decode("utf-8", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace").strip()
    result = {"status": "ok" if proc.returncode == 0 else "error", "returncode": proc.returncode, "stdout": out, "stderr": err}
    # intentar parsear stdout como JSON útil
    try:
        if out:
            result["parsed_output"] = json.loads(out)
    except Exception:
        # no JSON, dejar stdout textual
        pass
    return result


def run_script_with_args(relpath: str, args: list, input_bytes: Optional[bytes] = None, timeout: float = 10.0) -> Dict[str, Any]:
    """Ejecuta un script Python relativo al root con una lista de argumentos CLI.

    - relpath: ruta relativa desde el root del proyecto hacia el script
    - args: lista de argumentos (ej: ["--file", "path/to/file.txt"])
    - input_bytes: si se quiere pasar stdin como bytes
    - timeout: segundos

    Retorna dict similar a run_script_with_json.
    """
    p = PROJECT_ROOT.joinpath(relpath)
    if not p.exists():
        return {"status": "error", "note": f"script not found: {p}"}

    cmd = ["/usr/bin/env", "python3", str(p)] + args
    try:
        proc = subprocess.run(
            cmd,
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"status": "error", "note": "timeout", "timeout": True}

    out = proc.stdout.decode("utf-8", errors="replace").strip()
    err = proc.stderr.decode("utf-8", errors="replace").strip()
    result = {"status": "ok" if proc.returncode == 0 else "error", "returncode": proc.returncode, "stdout": out, "stderr": err}
    try:
        if out:
            result["parsed_output"] = json.loads(out)
    except Exception:
        pass
    return result
