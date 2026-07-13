#!/bin/bash
# compilador_recursivo_clasificacion.sh
# Compila cada carpeta de CLASIFICACION_PREDICTIVA en un .txt independiente
# Autor: NODO_SEMILLA NEUROBIT

set -e
set -u

echo "📦 COMPILADOR RECURSIVO DE CLASIFICACIÓN NEUROBIT"
echo "=================================================="

# ════════════════════════════════════════════════════════════════
# 1. DEFINIR DIRECTORIOS
# ════════════════════════════════════════════════════════════════
CLASIFICACION_ROOT="$HOME/WORKSPACE_NEUROBIT_V0.2/CLASIFICACION_PREDICTIVA"
COMPILE_SCRIPT="$CLASIFICACION_ROOT/compile_project.py"
OUTPUT_ROOT="$CLASIFICACION_ROOT/COMPILADOS_POR_CARPETA"

echo "📁 Clasificación: $CLASIFICACION_ROOT"
echo "📄 Script compile: $COMPILE_SCRIPT"
echo "📂 Salida compilados: $OUTPUT_ROOT"

# ════════════════════════════════════════════════════════════════
# 2. VALIDAR QUE EXISTE EL SCRIPT DE COMPILACIÓN
# ════════════════════════════════════════════════════════════════
if [ ! -f "$COMPILE_SCRIPT" ]; then
    echo "❌ ERROR: compile_project.py no encontrado en $COMPILE_SCRIPT"
    exit 1
fi
echo "✅ compile_project.py encontrado"

# ════════════════════════════════════════════════════════════════
# 3. CREAR DIRECTORIO DE SALIDA PARA COMPILADOS
# ════════════════════════════════════════════════════════════════
if [ -d "$OUTPUT_ROOT" ]; then
    echo "🗑️  Eliminando compilados anteriores..."
    rm -rf "$OUTPUT_ROOT"
fi
mkdir -p "$OUTPUT_ROOT"
echo "✅ Directorio de salida creado: $OUTPUT_ROOT"

# ════════════════════════════════════════════════════════════════
# 4. FUNCIÓN DE COMPILACIÓN POR CARPETA
# ════════════════════════════════════════════════════════════════
compilar_carpeta() {
    local carpeta="$1"
    local nombre_carpeta=$(basename "$carpeta")
    local output_file="$OUTPUT_ROOT/${nombre_carpeta}-compilacion.txt"
    
    echo ""
    echo "📦 Compilando: $nombre_carpeta"
    echo "   📄 Salida: ${nombre_carpeta}-compilacion.txt"
    
    # Verificar si la carpeta tiene archivos
    cantidad_archivos=$(find "$carpeta" -type f 2>/dev/null | wc -l)
    
    if [ "$cantidad_archivos" -eq 0 ]; then
        echo "   ⚠️  Carpeta vacía, saltando..."
        return 0
    fi
    
    echo "   📊 Archivos a compilar: $cantidad_archivos"
    
    # Ejecutar compile_project.py
    python3 "$COMPILE_SCRIPT" \
        --project "$carpeta" \
        --output "$output_file" \
        --ignore .git __pycache__ *.pyc *.log *.tmp *.bak *.sqlite *.db .venv venv
    
    # Verificar resultado
    if [ -f "$output_file" ]; then
        tamaño=$(du -h "$output_file" | cut -f1)
        lineas=$(wc -l < "$output_file")
        echo "   ✅ Compilado: $tamaño ($lineas líneas)"
    else
        echo "   ❌ Error: No se generó el archivo de salida"
    fi
}

# ════════════════════════════════════════════════════════════════
# 5. ITERAR RECURSIVAMENTE POR TODAS LAS CARPETAS
# ════════════════════════════════════════════════════════════════
echo ""
echo "🔄 INICIANDO COMPILACIÓN RECURSIVA..."
echo "====================================="

# Contador de carpetas procesadas
contador=0
total_carpetas=$(find "$CLASIFICACION_ROOT" -maxdepth 1 -type d | wc -l)
total_carpetas=$((total_carpetas - 1))  # Restar el directorio raíz

for carpeta in "$CLASIFICACION_ROOT"/*/; do
    if [ -d "$carpeta" ]; then
        contador=$((contador + 1))
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📂 PROCESANDO CARPETA $contador/$total_carpetas"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        compilar_carpeta "$carpeta"
    fi
done

# ════════════════════════════════════════════════════════════════
# 6. GENERAR RESUMEN FINAL
# ════════════════════════════════════════════════════════════════
echo ""
echo "✅ COMPILACIÓN RECURSIVA COMPLETADA"
echo "==================================="
echo ""
echo "📊 RESUMEN DE COMPILADOS:"
echo "-------------------------"

total_archivos=0
total_tamano="0"

for compilado in "$OUTPUT_ROOT"/*-compilacion.txt; do
    if [ -f "$compilado" ]; then
        nombre=$(basename "$compilado")
        tamaño=$(du -h "$compilado" | cut -f1)
        lineas=$(wc -l < "$compilado")
        echo "   📄 $nombre: $tamaño ($lineas líneas)"
        total_archivos=$((total_archivos + 1))
    fi
done

echo ""
echo "📈 TOTAL:"
echo "   📁 Carpetas procesadas: $total_carpetas"
echo "   📄 Archivos compilados: $total_archivos"
echo "   📂 Ubicación: $OUTPUT_ROOT"
echo ""
echo "🔍 Para ver el contenido de un compilado:"
echo "   head -100 \"$OUTPUT_ROOT/01_PROYECTO_NEUROBIT-compilacion.txt\""
echo ""
echo "📋 Para listar todos los compilados:"
echo "   ls -lh \"$OUTPUT_ROOT/\""