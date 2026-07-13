#!/bin/bash
# run_explorer.sh

set -e

echo "[NEUROBIT_FILE_EXPLORER] Iniciando secuencia..."

# Parámetros por defecto (ajustables)
PATRON="${1:-*.md}"
NIVEL="${2:-3}"
RAIZ="${3:-$(pwd)}"

echo "Patrón: $PATRON | Nivel: $NIVEL | Raíz: $RAIZ"

# Ejecutar módulos en secuencia
python3 explorer.py "$PATRON" "$NIVEL" "$RAIZ"

# Entrar en la última carpeta RESULTADOS_*
LAST_DIR=$(ls -d RESULTADOS_* 2>/dev/null | sort -V | tail -n1)
if [ -z "$LAST_DIR" ]; then
    echo "[ERROR] No se creó ninguna carpeta RESULTADOS_*"
    exit 1
fi

cd "$LAST_DIR"

python3 ../sorter.py
python3 ../concatenator.py

echo "[OK] Proceso completado en: $(pwd)"
