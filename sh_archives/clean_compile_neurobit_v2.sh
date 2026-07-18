#!/bin/bash
set -e
set -u

WORKSPACE_ROOT="$HOME/WORKSPACE_NEUROBIT_V0.2"
WORKSPACE_CLEAN="$HOME/WORKSPACE_NEUROBIT_V0.2_CLEAN"

echo "🧹 LIMPIEZA PRE-COMPILACIÓN NEUROBIT"
echo "====================================="

if [ ! -d "$WORKSPACE_ROOT" ]; then
    echo "❌ ERROR: Workspace no existe"
    exit 1
fi

if [ -d "$WORKSPACE_CLEAN" ]; then
    rm -rf "$WORKSPACE_CLEAN"
fi

cp -r "$WORKSPACE_ROOT" "$WORKSPACE_CLEAN"
cd "$WORKSPACE_CLEAN"

rm -f tools/modules_revisar.txt 2>/dev/null || true
rm -f tools/historial_para_continuidad.txt 2>/dev/null || true
rm -f data/compendio_index.jsonl 2>/dev/null || true

rm -rf .venv/ 2>/dev/null || true
rm -rf __pycache__/ 2>/dev/null || true
rm -rf backups/ 2>/dev/null || true
rm -rf "modulos sueltos extra"/ 2>/dev/null || true
rm -rf Incompletos/ 2>/dev/null || true
rm -rf .PRESERVE_BEFORE_MERGE/ 2>/dev/null || true
rm -rf code_snippets/ 2>/dev/null || true

echo "📦 Compilando..."
python3 tools/compile_project.py \
  --project . \
  --output neurobit_compendio_v0.2_FIXED.txt \
  --ignore .git .venv __pycache__ *.log *.tmp *.bak *.sqlite *.db *.png *.jpg *.pdf backups "modulos sueltos extra" Incompletos .PRESERVE_BEFORE_MERGE code_snippets data/memoria_eva.jsonl

echo "✅ RESULTADO:"
ls -lh neurobit_compendio_v0.2_FIXED.txt
