from pathlib import Path
import importlib.util
import inspect
from types import ModuleType
from typing import Optional, Callable


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_module_from_relpath(relpath: str) -> ModuleType:
    """Carga un módulo Python desde una ruta relativa al root del proyecto.

    relpath: ejemplo 'storage/modules/modulo_integrador_from_neurobit_central/modulo_integrador.py'
    """
    p = PROJECT_ROOT.joinpath(relpath)
    if not p.exists():
        raise FileNotFoundError(f"Module file not found: {p}")
    name = "ext_" + p.stem
    import sys as _sys
    spec = importlib.util.spec_from_file_location(name, str(p))
    mod = importlib.util.module_from_spec(spec)
    loader = spec.loader
    assert loader is not None
    # Ejecutar el módulo con argv temporal para evitar que parsers globales consuman sys.argv
    saved_argv = list(_sys.argv)
    try:
        _sys.argv = [str(p.name)]
        loader.exec_module(mod)
    finally:
        _sys.argv = saved_argv
    return mod


def find_callable(mod: ModuleType, candidates=None) -> Optional[Callable]:
    if candidates is None:
        candidates = [
            "send_message",
            "dispatch",
            "dispatch_message",
            "integrate",
            "process",
            "run",
            "main",
            "handle",
            "validate",
            "build",
        ]
    for name in candidates:
        fn = getattr(mod, name, None)
        if callable(fn):
            return fn
    # fallback: find any top-level callable
    for _, obj in inspect.getmembers(mod, inspect.isfunction):
        return obj
    return None
