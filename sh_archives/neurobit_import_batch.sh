#!/bin/bash
# neurobit_import_batch.sh - VERSIÓN CORREGIDA

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  NEUROBIT_BATCH_IMPORT - 65 CONVERSACIONES               ║"
echo "╚══════════════════════════════════════════════════════════╝"

# Verificar que el directorio de entrada existe
if [ ! -d "conversaciones_separadas/" ]; then
    echo "❌ ERROR: El directorio 'conversaciones_separadas/' no existe"
    exit 1
fi

# 1. Transformar todo el corpus
python3 neurobit_import_transformer_v3.py batch \
    conversaciones_separadas/ \
    import_ready/

# 2. Verificar archivos generados
echo -e "\n📊 Archivos listos para importar:"
if [ -d "import_ready/" ]; then
    ls -1 import_ready/IMPORT_*.json 2>/dev/null | wc -l
    echo " archivos transformados"
    
    # 3. Crear índice para importación manual
    echo -e "\n📋 Índice de archivos:"
    ls -1 import_ready/IMPORT_*.json 2>/dev/null | nl > import_ready/INDICE_CONVERSACIONES.txt
    echo "Índice creado: import_ready/INDICE_CONVERSACIONES.txt"
else
    echo "❌ ERROR: El directorio 'import_ready/' no fue creado"
    exit 1
fi

echo -e "\n⚠️  IMPORTACIÓN MANUAL:"
echo "   1. Ir a: Configuración → Chats → Importar chats"
echo "   2. Seleccionar archivos de import_ready/"
echo "   3. Importar en lotes de 5-10 para evitar timeouts"
echo "   4. Verificar mensaje verde: 'Importación exitosa'"