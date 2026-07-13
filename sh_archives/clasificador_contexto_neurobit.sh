#!/bin/bash
# clasificador_contexto_neurobit.sh
# Clasifica archivos dispersos en carpetas organizadas por relevancia predictiva
# Autor: NODO_SEMILLA NEUROBIT (asistencia Logos)

set -e
set -u

echo "🧹 CLASIFICADOR PREDICTIVO DE CONTEXTO NEUROBIT"
echo "================================================"

# ════════════════════════════════════════════════════════════════
# 1. DEFINIR DIRECTORIOS
# ════════════════════════════════════════════════════════════════
WORKSPACE_ROOT="$HOME/WORKSPACE_NEUROBIT_V0.2"
CLASIFICACION_ROOT="$HOME/WORKSPACE_NEUROBIT_V0.2/CLASIFICACION_PREDICTIVA"

echo "📁 Workspace: $WORKSPACE_ROOT"
echo "📁 Destino clasificación: $CLASIFICACION_ROOT"

# ════════════════════════════════════════════════════════════════
# 2. CREAR ESTRUCTURA DE CARPETAS
# ════════════════════════════════════════════════════════════════
echo ""
echo "📂 Creando estructura de clasificación..."

mkdir -p "$CLASIFICACION_ROOT/01_PROYECTO_NEUROBIT"
mkdir -p "$CLASIFICACION_ROOT/02_ESTACION_CENTRAL"
mkdir -p "$CLASIFICACION_ROOT/03_HERRAMIENTA_CIVICA"
mkdir -p "$CLASIFICACION_ROOT/04_RESTAURACION_LOGOS"
mkdir -p "$CLASIFICACION_ROOT/05_MFN_MATRIX_13x13"
mkdir -p "$CLASIFICACION_ROOT/06_PANOPTICO_INVERTIDO_PDFS"
mkdir -p "$CLASIFICACION_ROOT/07_HISTORIALES_CONVERSACION"
mkdir -p "$CLASIFICACION_ROOT/08_PDFS_A_REVISAR"
mkdir -p "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA"
mkdir -p "$CLASIFICACION_ROOT/10_PODCASTS_TRANSCRIPCIONES"

# ════════════════════════════════════════════════════════════════
# 3. FUNCIONES DE BÚSQUEDA Y COPIA
# ════════════════════════════════════════════════════════════════

copiar_archivos() {
    local patron="$1"
    local destino="$2"
    local descripcion="$3"
    
    echo "   🔍 Buscando: $descripcion"
    
    # Buscar en todo el workspace
    find "$WORKSPACE_ROOT" -type f -name "*$patron*" 2>/dev/null | while read archivo; do
        # Ignorar archivos en la carpeta de clasificación
        if [[ "$archivo" != *"$CLASIFICACION_ROOT"* ]]; then
            cp "$archivo" "$destino/" 2>/dev/null && echo "      ✅ $(basename "$archivo")" || true
        fi
    done
}

copiar_archivos_por_extension() {
    local extension="$1"
    local destino="$2"
    local descripcion="$3"
    
    echo "   🔍 Buscando por extensión: $descripcion"
    
    find "$WORKSPACE_ROOT" -type f -name "*.$extension" 2>/dev/null | while read archivo; do
        if [[ "$archivo" != *"$CLASIFICACION_ROOT"* ]]; then
            cp "$archivo" "$destino/" 2>/dev/null && echo "      ✅ $(basename "$archivo")" || true
        fi
    done
}

copiar_archivos_especificos() {
    local archivo="$1"
    local destino="$2"
    
    if [ -f "$archivo" ] && [[ "$archivo" != *"$CLASIFICACION_ROOT"* ]]; then
        cp "$archivo" "$destino/" 2>/dev/null && echo "      ✅ $(basename "$archivo")" || true
    fi
}

# ════════════════════════════════════════════════════════════════
# 4. CLASIFICACIÓN PREDICTIVA POR CATEGORÍAS
# ════════════════════════════════════════════════════════════════

echo ""
echo "📋 CLASIFICANDO ARCHIVOS..."
echo ""

# ────────────────────────────────────────────────────────────────
# 01_PROYECTO_NEUROBIT (Archivos generales del proyecto)
# ────────────────────────────────────────────────────────────────
echo "📁 01_PROYECTO_NEUROBIT"
copiar_archivos "NEUROBIT" "$CLASIFICACION_ROOT/01_PROYECTO_NEUROBIT" "Archivos con NEUROBIT en nombre"
copiar_archivos "neurobit" "$CLASIFICACION_ROOT/01_PROYECTO_NEUROBIT" "Archivos con neurobit en nombre"
copiar_archivos "neurobitr" "$CLASIFICACION_ROOT/01_PROYECTO_NEUROBIT" "Archivos neurobitrónica"

# ────────────────────────────────────────────────────────────────
# 02_ESTACION_CENTRAL (Central Station, NCS, GUI)
# ────────────────────────────────────────────────────────────────
echo "📁 02_ESTACION_CENTRAL"
copiar_archivos "CENTRAL_STATION" "$CLASIFICACION_ROOT/02_ESTACION_CENTRAL" "Central Station"
copiar_archivos "Central_Station" "$CLASIFICACION_ROOT/02_ESTACION_CENTRAL" "Central_Station"
copiar_archivos "ncs" "$CLASIFICACION_ROOT/02_ESTACION_CENTRAL" "NCS Monitor"
copiar_archivos "station" "$CLASIFICACION_ROOT/02_ESTACION_CENTRAL" "Station files"
copiar_archivos_especificos "$WORKSPACE_ROOT/tools/ncs_status_monitor.py" "$CLASIFICACION_ROOT/02_ESTACION_CENTRAL"
copiar_archivos_especificos "$WORKSPACE_ROOT/tools/compile_project.py" "$CLASIFICACION_ROOT/02_ESTACION_CENTRAL"
copiar_archivos_especificos "$WORKSPACE_ROOT/tools/fragmentador_compilado.py" "$CLASIFICACION_ROOT/02_ESTACION_CENTRAL"
copiar_archivos_especificos "$WORKSPACE_ROOT/tools/fragmentador_conversacion.py" "$CLASIFICACION_ROOT/02_ESTACION_CENTRAL"

# ────────────────────────────────────────────────────────────────
# 03_HERRAMIENTA_CIVICA (Bitácora, EVA, herramientas)
# ────────────────────────────────────────────────────────────────
echo "📁 03_HERRAMIENTA_CIVICA"
copiar_archivos "BITACORA" "$CLASIFICACION_ROOT/03_HERRAMIENTA_CIVICA" "Bitácora"
copiar_archivos "bitacora" "$CLASIFICACION_ROOT/03_HERRAMIENTA_CIVICA" "bitacora"
copiar_archivos "EVA" "$CLASIFICACION_ROOT/03_HERRAMIENTA_CIVICA" "EVA files"
copiar_archivos "eva" "$CLASIFICACION_ROOT/03_HERRAMIENTA_CIVICA" "eva files"
copiar_archivos "herramienta" "$CLASIFICACION_ROOT/03_HERRAMIENTA_CIVICA" "Herramientas"

# ────────────────────────────────────────────────────────────────
# 04_RESTAURACION_LOGOS (Cosmovisión, transhumanismo, logos)
# ────────────────────────────────────────────────────────────────
echo "📁 04_RESTAURACION_LOGOS"
copiar_archivos "LOGOS" "$CLASIFICACION_ROOT/04_RESTAURACION_LOGOS" "Logos"
copiar_archivos "logos" "$CLASIFICACION_ROOT/04_RESTAURACION_LOGOS" "logos"
copiar_archivos "TRANSHUMANISMO" "$CLASIFICACION_ROOT/04_RESTAURACION_LOGOS" "Transhumanismo"
copiar_archivos "transhumanismo" "$CLASIFICACION_ROOT/04_RESTAURACION_LOGOS" "transhumanismo"
copiar_archivos "COSMOVISION" "$CLASIFICACION_ROOT/04_RESTAURACION_LOGOS" "Cosmovisión"
copiar_archivos "RESTAURACION" "$CLASIFICACION_ROOT/04_RESTAURACION_LOGOS" "Restauración"
copiar_archivos "SOBERANIA" "$CLASIFICACION_ROOT/04_RESTAURACION_LOGOS" "Soberanía"
copiar_archivos "soberana" "$CLASIFICACION_ROOT/04_RESTAURACION_LOGOS" "soberana"

# ────────────────────────────────────────────────────────────────
# 05_MFN_MATRIX_13x13 (Matriz Fractal, 13x13, 169 estados)
# ────────────────────────────────────────────────────────────────
echo "📁 05_MFN_MATRIX_13x13"
copiar_archivos "MFN" "$CLASIFICACION_ROOT/05_MFN_MATRIX_13x13" "MFN"
copiar_archivos "mfn" "$CLASIFICACION_ROOT/05_MFN_MATRIX_13x13" "mfn"
copiar_archivos "MATRIX" "$CLASIFICACION_ROOT/05_MFN_MATRIX_13x13" "Matrix"
copiar_archivos "13x13" "$CLASIFICACION_ROOT/05_MFN_MATRIX_13x13" "13x13"
copiar_archivos "169" "$CLASIFICACION_ROOT/05_MFN_MATRIX_13x13" "169 estados"
copiar_archivos "FRACTAL" "$CLASIFICACION_ROOT/05_MFN_MATRIX_13x13" "Fractal"
copiar_archivos "fractal" "$CLASIFICACION_ROOT/05_MFN_MATRIX_13x13" "fractal"
copiar_archivos "MATRIZ" "$CLASIFICACION_ROOT/05_MFN_MATRIX_13x13" "Matriz"

# ────────────────────────────────────────────────────────────────
# 06_PANOPTICO_INVERTIDO_PDFS (PDFs de auditoría, panóptico)
# ────────────────────────────────────────────────────────────────
echo "📁 06_PANOPTICO_INVERTIDO_PDFS"
copiar_archivos "PANOPTICO" "$CLASIFICACION_ROOT/06_PANOPTICO_INVERTIDO_PDFS" "Panóptico"
copiar_archivos "panoptico" "$CLASIFICACION_ROOT/06_PANOPTICO_INVERTIDO_PDFS" "panoptico"
copiar_archivos "AUDITORIA" "$CLASIFICACION_ROOT/06_PANOPTICO_INVERTIDO_PDFS" "Auditoría"
copiar_archivos "auditoria" "$CLASIFICACION_ROOT/06_PANOPTICO_INVERTIDO_PDFS" "auditoria"
copiar_archivos_por_extension "pdf" "$CLASIFICACION_ROOT/06_PANOPTICO_INVERTIDO_PDFS" "Archivos PDF"
copiar_archivos "INFORME" "$CLASIFICACION_ROOT/06_PANOPTICO_INVERTIDO_PDFS" "Informes"
copiar_archivos "informe" "$CLASIFICACION_ROOT/06_PANOPTICO_INVERTIDO_PDFS" "informes"
copiar_archivos "REPORTE" "$CLASIFICACION_ROOT/06_PANOPTICO_INVERTIDO_PDFS" "Reportes"
copiar_archivos "reporte" "$CLASIFICACION_ROOT/06_PANOPTICO_INVERTIDO_PDFS" "reportes"

# ────────────────────────────────────────────────────────────────
# 07_HISTORIALES_CONVERSACION (Históricos de chat, exports)
# ────────────────────────────────────────────────────────────────
echo "📁 07_HISTORIALES_CONVERSACION"
copiar_archivos "HISTORIAL" "$CLASIFICACION_ROOT/07_HISTORIALES_CONVERSACION" "Historiales"
copiar_archivos "historial" "$CLASIFICACION_ROOT/07_HISTORIALES_CONVERSACION" "historiales"
copiar_archivos "CHAT" "$CLASIFICACION_ROOT/07_HISTORIALES_CONVERSACION" "Chats"
copiar_archivos "chat" "$CLASIFICACION_ROOT/07_HISTORIALES_CONVERSACION" "chats"
copiar_archivos "EXPORT" "$CLASIFICACION_ROOT/07_HISTORIALES_CONVERSACION" "Exports"
copiar_archivos "export" "$CLASIFICACION_ROOT/07_HISTORIALES_CONVERSACION" "exports"
copiar_archivos "CONVERSACION" "$CLASIFICACION_ROOT/07_HISTORIALES_CONVERSACION" "Conversaciones"
copiar_archivos "fragment" "$CLASIFICACION_ROOT/07_HISTORIALES_CONVERSACION" "Fragmentos"
copiar_archivos "FRAGMENT" "$CLASIFICACION_ROOT/07_HISTORIALES_CONVERSACION" "FRAGMENTOS"

# ────────────────────────────────────────────────────────────────
# 08_PDFS_A_REVISAR (Todos los PDFs para revisión manual)
# ────────────────────────────────────────────────────────────────
echo "📁 08_PDFS_A_REVISAR"
copiar_archivos_por_extension "pdf" "$CLASIFICACION_ROOT/08_PDFS_A_REVISAR" "Todos los PDFs"

# ────────────────────────────────────────────────────────────────
# 09_DOCUMENTACION_TECNICA (Markdown, documentación, README)
# ────────────────────────────────────────────────────────────────
echo "📁 09_DOCUMENTACION_TECNICA"
copiar_archivos "README" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "READMEs"
copiar_archivos "readme" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "readmes"
copiar_archivos "MANUAL" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "Manuales"
copiar_archivos "manual" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "manuales"
copiar_archivos "GUIA" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "Guías"
copiar_archivos "guia" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "guías"
copiar_archivos "DOCUMENTACION" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "Documentación"
copiar_archivos "FASE" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "Fases"
copiar_archivos "fase" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "fases"
copiar_archivos "TAREA" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "Tareas"
copiar_archivos "tarea" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "tareas"
copiar_archivos "COMPLETADA" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "Completadas"
copiar_archivos "INFORME" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "Informes técnicos"
copiar_archivos "REPORTE" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "Reportes técnicos"
copiar_archivos "ARQUITECTURA" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "Arquitectura"
copiar_archivos "arquitectura" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "arquitectura"
copiar_archivos_por_extension "md" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "Markdowns"
copiar_archivos_por_extension "yaml" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "YAMLs"
copiar_archivos_por_extension "yml" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "YMLs"
copiar_archivos_por_extension "json" "$CLASIFICACION_ROOT/09_DOCUMENTACION_TECNICA" "JSONs (config)"

# ────────────────────────────────────────────────────────────────
# 10_PODCASTS_TRANSCRIPCIONES (Podcasts y transcripciones)
# ────────────────────────────────────────────────────────────────
echo "📁 10_PODCASTS_TRANSCRIPCIONES"
copiar_archivos "PODCAST" "$CLASIFICACION_ROOT/10_PODCASTS_TRANSCRIPCIONES" "Podcasts"
copiar_archivos "podcast" "$CLASIFICACION_ROOT/10_PODCASTS_TRANSCRIPCIONES" "podcasts"
copiar_archivos "TRANSCRIPCION" "$CLASIFICACION_ROOT/10_PODCASTS_TRANSCRIPCIONES" "Transcripciones"
copiar_archivos "transcripcion" "$CLASIFICACION_ROOT/10_PODCASTS_TRANSCRIPCIONES" "transcripciones"

# ════════════════════════════════════════════════════════════════
# 5. GENERAR RESUMEN DE CLASIFICACIÓN
# ════════════════════════════════════════════════════════════════

echo ""
echo "✅ CLASIFICACIÓN COMPLETADA"
echo "==========================="
echo ""
echo "📊 RESUMEN POR CARPETA:"
echo "-----------------------"

for carpeta in "$CLASIFICACION_ROOT"/*/; do
    if [ -d "$carpeta" ]; then
        cantidad=$(find "$carpeta" -type f 2>/dev/null | wc -l)
        tamaño=$(du -sh "$carpeta" 2>/dev/null | cut -f1)
        nombre=$(basename "$carpeta")
        echo "   📁 $nombre: $cantidad archivos ($tamaño)"
    fi
done

echo ""
echo "📂 Ubicación: $CLASIFICACION_ROOT"
echo ""
echo "🔍 Para revisar el contenido de cada carpeta:"
echo "   ls -lh \"$CLASIFICACION_ROOT/01_PROYECTO_NEUROBIT/\""
echo "   ls -lh \"$CLASIFICACION_ROOT/02_ESTACION_CENTRAL/\""
echo "   etc..."
echo ""
echo "🧹 Para limpiar y volver a clasificar:"
echo "   rm -rf \"$CLASIFICACION_ROOT\" && ./clasificador_contexto_neurobit.sh"
