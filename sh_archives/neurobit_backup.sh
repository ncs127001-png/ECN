#!/bin/bash
# neurobit_backup.sh
# Crea una copia de seguridad secuencial de un archivo antes de modificarlo.
# Uso: ./neurobit_backup.sh <ruta_al_archivo> [directorio_destino]

FILE_TO_BACKUP="$1"
BACKUP_DIR="${2:-$HOME/WORKSPACE_NEUROBIT_V0.2/backups/manual}"

if [ -z "$FILE_TO_BACKUP" ]; then
    echo "Uso: $0 <archivo_a_guardar> [dir_destino]"
    exit 1
fi

if [ ! -f "$FILE_TO_BACKUP" ]; then
    echo "Error: El archivo '$FILE_TO_BACKUP' no existe."
    exit 1
fi

mkdir -p "$BACKUP_DIR"

FILENAME=$(basename "$FILE_TO_BACKUP")
EXTENSION="${FILENAME##*.}"
BASENAME="${FILENAME%.*}"

# Buscar la última versión existente
LAST_VERSION=$(ls "$BACKUP_DIR" | grep "^${BASENAME}_v" | sort -V | tail -1 | sed 's/.*_v\([0-9]*\)\..*/\1/')

if [ -z "$LAST_VERSION" ]; then
    NEW_VERSION="1"
else
    NEW_VERSION=$((LAST_VERSION + 1))
fi

BACKUP_FILE="${BACKUP_DIR}/${BASENAME}_v${NEW_VERSION}.${EXTENSION}"

cp "$FILE_TO_BACKUP" "$BACKUP_FILE"

echo "✅ Backup creado: $BACKUP_FILE"
echo "   Original: $FILE_TO_BACKUP"