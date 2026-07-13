#!/bin/bash
# compilador_recursivo_v4.sh
# Compila cada carpeta con: conversión PDF→TXT + fragmentación si >19MB
# CORRECCIÓN: Variables en ASCII puro (sin ñ, tildes)

set -e
set -u

echo "📦 COMPILADOR RECURSIVO V4 — VARIABLES ASCII"
echo "============================================="

# ════════════════════════════════════════════════════════════════
# 1. DEFINIR DIRECTORIOS
# ════════════════════════════════════════════════════════════════
CLASIFICACION_ROOT="$HOME/WORKSPACE_NEUROBIT_V0.2/CLASIFICACION_PREDICTIVA"
COMPILE_SCRIPT="$CLASIFICACION_ROOT/compile_project.py"
FRAGMENTADOR_SCRIPT="$HOME/WORKSPACE_NEUROBIT_V0.2/tools/fragmentador_compilado_2partes.py"
OUTPUT_ROOT="$CLASIFICACION_ROOT/COMPILADOS_POR_CARPETA"
PDF_TEMP="$CLASIFICACION_ROOT/TEMP_PDF_CONVERTIDOS"

echo "📁 Clasificación: $CLASIFICACION_ROOT"
echo "📄 Script compile: $COMPILE_SCRIPT"
echo "🔧 Script fragmentador: $FRAGMENTADOR_SCRIPT"
echo "📂 Salida compilados: $OUTPUT_ROOT"
echo "📄 Temp PDF→TXT: $PDF_TEMP"

# ════════════════════════════════════════════════════════════════
# 2. VALIDAR SCRIPTS EXISTENTES
# ════════════════════════════════════════════════════════════════
if [ ! -f "$COMPILE_SCRIPT" ]; then
    echo "❌ ERROR: compile_project.py no encontrado"
    exit 1
fi
echo "✅ compile_project.py encontrado"

# ════════════════════════════════════════════════════════════════
# 3. CREAR DIRECTORIOS DE SALIDA
# ════════════════════════════════════════════════════════════════
if [ -d "$OUTPUT_ROOT" ]; then
    echo "🗑️  Eliminando compilados anteriores..."
    rm -rf "$OUTPUT_ROOT"
fi
mkdir -p "$OUTPUT_ROOT"

if [ -d "$PDF_TEMP" ]; then
    rm -rf "$PDF_TEMP"
fi
mkdir -p "$PDF_TEMP"

echo "✅ Directorios creados"

# ════════════════════════════════════════════════════════════════
# 4. FUNCIÓN: CONVERTIR PDF A TXT
# ════════════════════════════════════════════════════════════════
convertir_pdf_a_txt() {
    local carpeta="$1"
    local pdf_count=0
    local txt_count=0
    
    echo "   📄 Buscando PDFs para convertir..."
    
    while IFS= read -r -d '' pdf; do
        if [ -f "$pdf" ]; then
            pdf_count=$((pdf_count + 1))
            nombre_base=$(basename "$pdf" .pdf)
            txt_destino="$PDF_TEMP/${nombre_base}.txt"
            
            if command -v pdftotext &> /dev/null; then
                if pdftotext "$pdf" "$txt_destino" 2>/dev/null; then
                    echo "      ✅ $(basename "$pdf") → $(basename "$txt_destino")"
                    txt_count=$((txt_count + 1))
                else
                    echo "      ⚠️  $(basename "$pdf") (falló conversión)"
                fi
            else
                echo "      ⚠️  pdftotext no instalado. Saltando: $(basename "$pdf")"
            fi
        fi
    done < <(find "$carpeta" -name "*.pdf" -print0 2>/dev/null)
    
    echo "   📊 PDFs encontrados: $pdf_count | Convertidos: $txt_count"
}

# ════════════════════════════════════════════════════════════════
# 5. FUNCIÓN: FRAGMENTAR SI EXCEDE 19MB (VARIABLES EN ASCII)
# ════════════════════════════════════════════════════════════════
fragmentar_si_grande() {
    local archivo="$1"
    # ✅ CORREGIDO: tamano_bytes (sin ñ)
    local tamano_bytes=$(stat -c%s "$archivo" 2>/dev/null || echo "0")
    local limite_bytes=$((19 * 1024 * 1024))
    
    if [ "$tamano_bytes" -gt "$limite_bytes" ]; then
        local tamano_mb=$((tamano_bytes / 1024 / 1024))
        echo "   ⚠️  Archivo grande: ${tamano_mb}MB (>19MB)"
        echo "   ✂️  Fragmentando..."
        
        local nombre_base=$(basename "$archivo" .txt)
        
        if [ -f "$FRAGMENTADOR_SCRIPT" ]; then
            if python3 "$FRAGMENTADOR_SCRIPT" "$archivo" "$nombre_base" 2>/dev/null; then
                rm "$archivo"
                echo "   ✅ Fragmentado con script"
            else
                echo "   🔄 Usando método alternativo (2 partes)..."
                fragmentar_manual "$archivo"
            fi
        else
            echo "   ⚠️  Fragmentador no encontrado. Método manual..."
            fragmentar_manual "$archivo"
        fi
    else
        local tamano_mb=$((tamano_bytes / 1024 / 1024))
        echo "   ✅ Tamaño OK: ${tamano_mb}MB"
    fi
}

fragmentar_manual() {
    local archivo="$1"
    local lineas_totales=$(wc -l < "$archivo")
    local lineas_mitad=$((lineas_totales / 2))
    
    head -n "$lineas_mitad" "$archivo" > "${archivo%.txt}_parte_1_de_2.txt"
    tail -n +"$((lineas_mitad + 1))" "$archivo" > "${archivo%.txt}_parte_2_de_2.txt"
    
    rm "$archivo"
    echo "   ✅ Dividido en 2 partes (manual)"
}

# ════════════════════════════════════════════════════════════════
# 6. FUNCIÓN: COMPILAR CARPETA
# ════════════════════════════════════════════════════════════════
compilar_carpeta() {
    local carpeta="$1"
    local nombre_carpeta=$(basename "$carpeta")
    local output_file="$OUTPUT_ROOT/${nombre_carpeta}-compilacion.txt"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📂 PROCESANDO: $nombre_carpeta"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local cantidad_archivos=$(find "$carpeta" -type f 2>/dev/null | wc -l)
    
    if [ "$cantidad_archivos" -eq 0 ]; then
        echo "   ⚠️  Carpeta vacía, saltando..."
        return 0
    fi
    
    echo "   📊 Archivos totales: $cantidad_archivos"
    
    convertir_pdf_a_txt "$carpeta"
    
    echo "   📦 Ejecutando compile_project.py..."
    
    if python3 "$COMPILE_SCRIPT" \
        --project "$carpeta" \
        --output "$output_file" \
        --ignore .git __pycache__ *.pyc *.log *.tmp *.bak *.sqlite *.db .venv venv *.pdf 2>/dev/null; then
        
        if [ -f "$output_file" ]; then
            fragmentar_si_grande "$output_file"
        else
            echo "   ❌ Error: No se generó el archivo de salida"
        fi
    else
        echo "   ❌ Error en compile_project.py"
    fi
}

# ════════════════════════════════════════════════════════════════
# 7. ITERAR POR TODAS LAS CARPETAS
# ════════════════════════════════════════════════════════════════
echo ""
echo "🔄 INICIANDO COMPILACIÓN RECURSIVA V4..."
echo "========================================"

local contador=0
local total_carpetas=$(find "$CLASIFICACION_ROOT" -maxdepth 1 -type d | wc -l)
total_carpetas=$((total_carpetas - 1))

for carpeta in "$CLASIFICACION_ROOT"/*/; do
    if [ -d "$carpeta" ]; then
        contador=$((contador + 1))
        compilar_carpeta "$carpeta"
    fi
done

# ════════════════════════════════════════════════════════════════
# 8. RESUMEN FINAL
# ════════════════════════════════════════════════════════════════
echo ""
echo "✅ COMPILACIÓN RECURSIVA V4 COMPLETADA"
echo "======================================"
echo ""
echo "📊 RESULTADOS:"
echo "--------------"

for archivo in "$OUTPUT_ROOT"/*.txt; do
    if [ -f "$archivo" ]; then
        local nombre=$(basename "$archivo")
        local tamano=$(du -h "$archivo" 2>/dev/null | cut -f1)
        local lineas=$(wc -l < "$archivo")
        echo "   📄 $nombre: $tamano ($lineas líneas)"
    fi
done

echo ""
echo "📂 Ubicación: $OUTPUT_ROOT"
echo "📄 Temp PDF→TXT: $PDF_TEMP"
