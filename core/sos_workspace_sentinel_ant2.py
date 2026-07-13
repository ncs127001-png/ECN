#!/bin/bash
# sos_workspace_sentinel.sh
# Centinela del Workspace - Basado en inotifywait
# Versión: 1.2 - Fix completo de bucles

WORKSPACE="/home/gus/ECN"
INBOX="$WORKSPACE/inbox"
QUARANTINE="$INBOX/quarantine"
LOG_FILE="$WORKSPACE/data/logs/sentinel_audit.log"
MFN_MAP="$WORKSPACE/data/mfn_location_map.json"

# Crear directorios
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

    if [ -z "$mfn_location" ]; then
        log "⚠️  SIN MFN_LOCATION: Moviendo a cuarentena: $(basename "$file")"
        if [[ "$file" == *"/quarantine/"* ]]; then
            return 1
        fi
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

    # FILTRO 1: Ignorar si está en quarantine o no existe
    if [[ "$file" == *"/quarantine/"* ]] || [ ! -f "$file" ]; then
        return 0
    fi

    # FILTRO 2: Solo procesar CREATE
    if [[ "$event" != *"CREATE"* ]]; then
        return 0
    fi

    # FILTRO 3: Solo archivos Python y YAML
    if [[ ! "$file" =~ \.(py|yaml|yml)$ ]]; then
        return 0
    fi

    log "📄 DETECTADO: $event → $(basename "$file")"

    # Esperar a que el archivo esté completamente escrito
    sleep 0.5

    if [ ! -f "$file" ]; then
        log "⏭️  FANTASMA: $(basename "$file") ya no existe"
        return 0
    fi

    local mfn_location=$(extract_mfn_location "$file")
    route_file "$file" "$mfn_location"
}

log "👁️  WORKSPACE SENTINEL INICIADO (v1.2)"
log "📂 Vigilando: $INBOX"
log "🔔 Solo procesando: CREATE"
log "🚫 Ignorando: quarantine/, MODIFY, MOVED_TO"

if ! command -v inotifywait &> /dev/null; then
    log "❌ ERROR: inotifywait no está instalado"
    log "💡 Instalar con: sudo apt install inotify-tools"
    exit 1
fi

# Monitoreo SOLO de eventos CREATE, excluyendo quarantine
inotifywait -m -e create --format '%w%f %e' "$INBOX" 2>/dev/null | \
while read file event; do
    if [ -d "$file" ]; then
        continue
    fi

    if [[ "$file" =~ \.(swp|tmp|bak|log)$ ]]; then
        continue
    fi

    process_file "$file" "$event"
done
