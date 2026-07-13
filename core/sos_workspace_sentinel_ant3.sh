#!/bin/bash
# sos_workspace_sentinel.sh - Versión 1.3 (Final)

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INBOX="$WORKSPACE/inbox"
QUARANTINE="$INBOX/quarantine"
LOG_FILE="$WORKSPACE/data/logs/sentinel_audit.log"
MFN_MAP="$WORKSPACE/data/mfn_location_map.json"

mkdir -p "$INBOX" "$QUARANTINE" "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

extract_mfn_location() {
    local file="$1"
    grep -m1 "^MFN_LOCATION:" "$file" 2>/dev/null | cut -d' ' -f2 | tr -d '\r\n'
}

route_file() {
    local file="$1"
    local mfn_location="$2"

    # Protección: si ya está en quarantine, no hacer nada
    if [[ "$file" == *"/quarantine/"* ]]; then
        return 0
    fi

    # Verificar que el archivo existe
    if [ ! -f "$file" ]; then
        return 0
    fi

    if [ -z "$mfn_location" ]; then
        log "⚠️  SIN MFN_LOCATION: $(basename "$file") → cuarentena"
        mv "$file" "$QUARANTINE/" 2>/dev/null
        return 1
    fi

    local dest_dir="$WORKSPACE/$mfn_location"
    mkdir -p "$dest_dir"

    local filename=$(basename "$file")
    local dest_path="$dest_dir/$filename"

    if [ -f "$dest_path" ]; then
        local timestamp=$(date +%s)
        local name="${filename%.*}"
        local ext="${filename##*.}"
        dest_path="$dest_dir/${name}_${timestamp}.${ext}"
    fi

    mv "$file" "$dest_path" 2>/dev/null
    log "✅ ENRUTADO: $filename → $mfn_location/"

    echo "{\"file\": \"$dest_path\", \"location\": \"$mfn_location\", \"timestamp\": \"$(date -Iseconds)\"}" >> "$MFN_MAP"

    if [ -f "$WORKSPACE/tools/generate_path_map.py" ]; then
        python3 "$WORKSPACE/tools/generate_path_map.py" 2>/dev/null &
    fi

    return 0
}

process_file() {
    local file="$1"
    local event="$2"

    # FILTRO CRÍTICO: Solo procesar CREATE
    if [[ "$event" != *"CREATE"* ]]; then
        return 0
    fi

    # Ignorar directorios
    if [ -d "$file" ]; then
        return 0
    fi

    # Ignorar archivos en quarantine
    if [[ "$file" == *"/quarantine/"* ]]; then
        return 0
    fi

    # Solo Python y YAML
    if [[ ! "$file" =~ \.(py|yaml|yml)$ ]]; then
        return 0
    fi

    log "📄 DETECTADO: CREATE → $(basename "$file")"

    # Esperar a que el archivo esté completo
    sleep 0.5

    if [ ! -f "$file" ]; then
        return 0
    fi

    local mfn_location=$(extract_mfn_location "$file")
    route_file "$file" "$mfn_location"
}

log "👁️  WORKSPACE SENTINEL v1.3 INICIADO"
log "📂 Vigilando: $INBOX"
log " Solo CREATE | Ignorando: MODIFY, MOVED_TO, quarantine/"

if ! command -v inotifywait &> /dev/null; then
    log " inotifywait no instalado. sudo apt install inotify-tools"
    exit 1
fi

# Monitoreo SOLO CREATE, excluyendo quarantine recursivamente
inotifywait -m -e create --format '%w%f %e' "$INBOX" 2>/dev/null | \
while read file event; do
    process_file "$file" "$event"
done
