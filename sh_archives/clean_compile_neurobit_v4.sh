#!/bin/bash
# clean_compile_neurobit_v4.sh
# VERSIÓN FINAL: Usa la lista EXACTA de NODO_SEMILLA (sin patrones genéricos)

set -e
set -u

WORKSPACE_ROOT="$HOME/WORKSPACE_NEUROBIT_V0.2"
WORKSPACE_CLEAN="$HOME/WORKSPACE_NEUROBIT_V0.2_CLEAN_V4"

echo "🧹 LIMPIEZA NEUROBIT — V4 (Lista Exacta de NODO_SEMILLA)"
echo "========================================================="

# Validar workspace
if [ ! -d "$WORKSPACE_ROOT" ]; then
    echo "❌ ERROR: Workspace no existe en $WORKSPACE_ROOT"
    exit 1
fi

# Eliminar copia limpia anterior
if [ -d "$WORKSPACE_CLEAN" ]; then
    echo "🗑️  Eliminando copia limpia anterior..."
    rm -rf "$WORKSPACE_CLEAN"
fi

# Crear copia limpia
echo "📋 Creando copia limpia..."
cp -r "$WORKSPACE_ROOT" "$WORKSPACE_CLEAN"

if [ ! -d "$WORKSPACE_CLEAN" ]; then
    echo "❌ ERROR: No se pudo crear la copia limpia"
    exit 1
fi

cd "$WORKSPACE_CLEAN"

echo "🗑️  ELIMINANDO ARCHIVOS ESPECÍFICOS (lista de NODO_SEMILLA)..."

# ════════════════════════════════════════════════════════════════
# 1. ARCHIVOS DE TEXTO PESADOS (tools/)
# ════════════════════════════════════════════════════════════════
echo "   📁 tools/modules_revisar.txt (67M)"
rm -f tools/modules_revisar.txt

echo "   📁 modulos_sueltos_extra.txt (30M)"
rm -f modulos_sueltos_extra.txt

echo "   📁 tools/historial_para_continuidad.txt (4.5M)"
rm -f tools/historial_para_continuidad.txt

# ════════════════════════════════════════════════════════════════
# 2. DATA (compendio_index.jsonl)
# ════════════════════════════════════════════════════════════════
echo "   📁 data/compendio_index.jsonl (12M)"
rm -f data/compendio_index.jsonl

echo "   📁 .PRESERVE_BEFORE_MERGE/data/compendio_index.jsonl (12M)"
rm -f .PRESERVE_BEFORE_MERGE/data/compendio_index.jsonl

# ════════════════════════════════════════════════════════════════
# 3. DOCS/HISTORICAL (JSONs pesados)
# ════════════════════════════════════════════════════════════════
echo "   📁 docs/guias/CHAT_SPLITTER/historical/exportacion_total.json (32M)"
rm -f docs/guias/CHAT_SPLITTER/historical/exportacion_total.json

echo "   📁 docs/guias/CHAT_SPLITTER/historical/chat-export-Qwen-Nodo_Semilla-13-3-2026.json (32M)"
rm -f docs/guias/CHAT_SPLITTER/historical/chat-export-Qwen-Nodo_Semilla-13-3-2026.json

echo "   📁 docs/Ultimas interacciones.json (4.4M)"
rm -f docs/Ultimas\ interacciones.json

# ════════════════════════════════════════════════════════════════
# 4. GIT OBJECTS (pesados)
# ════════════════════════════════════════════════════════════════
echo "   📁 .git/objects/ (múltiples archivos: 56M+54M+31M+10M+9.3M+7M+6.4M+6.1M+6M+2.8M+1.9M+1.7M+1.3M+1.1M)"
rm -rf .git/

# ════════════════════════════════════════════════════════════════
# 5. INCOMPLETOS (PDFs + imágenes + txt)
# ════════════════════════════════════════════════════════════════
echo "   📁 Incompletos/referencias_teoricas/*.pdf (20M+19M+16M+2.8M+2.8M+2.7M+1.8M+1.8M+1.6M+3.4M+2.0M)"
rm -rf Incompletos/referencias_teoricas/

echo "   📁 Incompletos/concept.png (6.0M)"
rm -f Incompletos/concept.png

echo "   📁 Incompletos/unnamed.png (5.8M)"
rm -f Incompletos/unnamed.png

echo "   📁 Incompletos/8 HISTORIALES*.txt (2.2M)"
rm -f "Incompletos/8 HISTORIALES  GPT52 - Z3R9K - EDU5R - X5_LOG - GPT5A - TRGLN - S0PHI - QW3N4.txt"

# ════════════════════════════════════════════════════════════════
# 6. JSON CONFIG
# ════════════════════════════════════════════════════════════════
echo "   📁 INICIO_PARA_CLAUDE.json (2.0M)"
rm -f INICIO_PARA_CLAUDE.json

# ════════════════════════════════════════════════════════════════
# 7. MODULOS SUELTOS EXTRA (web_files + JSON + MP3)
# ════════════════════════════════════════════════════════════════
echo "   📁 modulos sueltos extra/BITACORA EVA RELEASE/src2/neurobit/chat-export-*.json (17M)"
rm -f "modulos sueltos extra/BITACORA EVA RELEASE/src2/neurobit/chat-export-1771752589171-Nodo_Neurobit.json"

echo "   📁 modulos sueltos extra/BITACORA EVA RELEASE/src2/neurobit/web_files/ (2.3M+1.7M+2.2M+1.3M)"
rm -rf "modulos sueltos extra/BITACORA EVA RELEASE/src2/neurobit/web_files/"

# ════════════════════════════════════════════════════════════════
# 8. PRESERVE_BEFORE_MERGE (ARCHIVOS PESADOS ESPECÍFICOS)
# ════════════════════════════════════════════════════════════════
echo "   📁 .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/bitacora/compilado_neurobit_otro_desarrollo.txt (11M)"
rm -f .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/bitacora/compilado_neurobit_otro_desarrollo.txt

echo "   📁 .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/bitacora/logs/bitacora_full.txt (4.0M)"
rm -f .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/bitacora/logs/bitacora_full.txt

echo "   📁 .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/bitacora/texto_completo/Hacer que imagen hable - Viernes.html (2.9M)"
rm -f .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/bitacora/texto_completo/Hacer\ que\ imagen\ hable\ -\ Viernes.html

echo "   📁 .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/bitacora/texto_completo/Hacer que imagen hable.mhtml (1.6M)"
rm -f .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/bitacora/texto_completo/Hacer\ que\ imagen\ hable.mhtml

echo "   📁 .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/bitacora EVA 3.0/ (1.8M)"
rm -rf .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/bitacora\ EVA\ 3.0/

echo "   📁 .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/EVA LÚMENA MANNAGEMENT/EVA_LUMENA_LAB/audio/ (7.7M+7.5M+6.5M)"
rm -rf .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/EVA\ LÚMENA\ MANNAGEMENT/EVA_LUMENA_LAB/audio/

echo "   📁 .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/EVA LÚMENA MANNAGEMENT/EVA_LUMENA_LAB/fotos/ (2.8M+2.8M+1.9M)"
rm -rf .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/EVA\ LÚMENA\ MANNAGEMENT/EVA_LUMENA_LAB/fotos/

echo "   📁 .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/EVA LÚMENA MANNAGEMENT/EVA_LUMENA_LAB/video/ (56M+54M+31M)"
rm -rf .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/EVA\ LÚMENA\ MANNAGEMENT/EVA_LUMENA_LAB/video/

echo "   📁 .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/Investigación EVA pistas HACIENDO JUNTOS LA BITACORA.mhtml (11M)"
rm -f .PRESERVE_BEFORE_MERGE/extensions/message-builder/RECUPERADOS/Investigación\ EVA\ pistas\ \ HACIENDO\ JUNTOS\ LA\ BITACORA.mhtml

# ════════════════════════════════════════════════════════════════
# 9. PYTHON CACHE
# ════════════════════════════════════════════════════════════════
echo "   📁 __pycache__/ (variable)"
rm -rf __pycache__/

# ════════════════════════════════════════════════════════════════
# 10. VENV
# ════════════════════════════════════════════════════════════════
echo "   📁 .venv/ (1.1M+2.6M+...)"
rm -rf .venv/

# ════════════════════════════════════════════════════════════════
# 11. BACKUPS
# ════════════════════════════════════════════════════════════════
echo "   📁 backups/*.tar.gz (7.6M+7.6M)"
rm -f backups/*.tar.gz
rm -f backups/*.gz.sha256

echo ""
echo "📦 Ejecutando compilación..."

python3 tools/compile_project.py \
  --project . \
  --output neurobit_compendio_v0.4_EXACTO.txt \
  --ignore \
    .git .gitignore __pycache__ *.pyc *.egg-info \
    .venv venv build dist *.log *.tmp *.bak \
    *.sqlite *.db .env .env.* \
    .idea .vscode .DS_Store \
    *.png *.jpg *.jpeg *.gif *.ico \
    *.pdf *.zip *.tar.gz *.tar.bz2 \
    node_modules \
    fragments_conversacion fragments \
    data/memoria_eva.jsonl data/neurobit.db \
    code_snippets \
    vm_logs \
    vms

echo ""
echo "✅ COMPILACIÓN COMPLETADA"
echo "========================="
ls -lh neurobit_compendio_v0.4_EXACTO.txt
wc -l neurobit_compendio_v0.4_EXACTO.txt

echo ""
echo "📊 COMPARACIÓN:"
echo "==============="
echo "Original: $(du -sh "$WORKSPACE_ROOT/neurobit_compendio_v0.2.txt" 2>/dev/null | cut -f1)"
echo "Clean (fallido): $(du -sh "$WORKSPACE_ROOT/neurobit_compendio_v0.2_CLEAN.txt" 2>/dev/null | cut -f1)"
echo "FIXED (fallido): $(du -sh "$WORKSPACE_ROOT/neurobit_compendio_v0.2_FIXED.txt" 2>/dev/null | cut -f1)"
echo "EXACTO V4 (lista NODO_SEMILLA): $(du -sh neurobit_compendio_v0.4_EXACTO.txt | cut -f1)"