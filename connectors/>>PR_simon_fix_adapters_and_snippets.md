# PR: Fix adapters, make modules import-safe, and clean snippets

Branch: `simon/fix-adapters-and-snippets-20251229`

Resumen
-------
Este PR agrupa las correcciones que hice localmente para estabilizar la batería de adaptadores y eliminar snippets no ejecutables que rompían la comprobación global de sintaxis.

Cambios principales
------------------
- Core adapters: mejoras en fallbacks y en la ejecución importable → CLI → stdin (no interactivo). Archivos en `core/adapters/` actualizados.
- Módulos legacy: pequeños parches para exponer entrypoints programáticos y aceptar `--stdin` o argumentos opcionales. Localizados en `storage/modules/*`.
- Snippets: moví varios `storage/RING_PROCESOS/code_snippets/snippet_*.py` que contienen shell/texto a `*.txt` para evitar que `py_compile` los parsee. También reemplacé espacios NBSP por espacios normales en varios `.py` donde causaban SyntaxError.
- Tests y docs: añadí un test mínimo de humo y este documento PR con instrucciones para revisar los cambios.

Archivos destacados cambiados
---------------------------
- core/adapters/adapter_msg_builder.py
- core/adapters/adapter_modulo_integrador.py
- core/adapters/adapter_msg_sequencer.py
- core/adapters/adapter_dispatcher_lite.py
- core/adapters/adapter_llama_dispatcher_connector.py
- core/adapters/adapter_simon_validator.py
- storage/modules/* (varios parchados para API programática)
- storage/RING_PROCESOS/code_snippets/snippet_*.py -> renombrados a `.txt`

Cómo probar (smoke test)
------------------------
1. Ejecutar la batería de adaptadores (ya incluida en `scripts/`):

```bash
chmod +x scripts/run_adapters_test.sh
./scripts/run_adapters_test.sh
```

2. Verificar que `data/modules_import_report_detailed.json` se haya generado y que los adaptadores clave aparezcan con `status: ok`.

```bash
jq '.adapters | to_entries[] | {name: .key, status: .value.status}' data/modules_import_report_detailed.json
```

3. Ejecutar el test mínimo incluido:

```bash
python3 -m pytest -q
```

Notas y riesgos
--------------
- He movido varios archivos `.py` que eran en realidad snippets a `.txt`. Revisa `storage/RING_PROCESOS/code_snippets/` y restaura cualquier archivo que realmente deba ser ejecutable.
- Reemplacé NBSP invisibles en algunos ficheros; esto es seguro y necesario para la sintaxis. Si prefieres, puedo limitar los cambios a un commit separado.

Siguiente paso propuesto
-----------------------
- Revisar los diffs en `docs/changes.diff` y `docs/changes.patch` (se generan al crear el branch/commit local).
- Si todo está OK, puedo abrir un PR en el repositorio remoto (si existe) o preparar los parches para aplicar en el repo principal.

----
Preparado por SIMON (accionador automático). Fecha: 2025-12-29
