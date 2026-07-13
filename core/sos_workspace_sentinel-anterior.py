#!/bin/bash
# sos_workspace_sentinel.sh
# Centinela del Workspace - Basado en inotifywait
# Detecta, audita y organiza archivos automáticamente
# Versión: 1.1 - Fix de bucles y eventos fantasma

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

# Función para extraer MFN_LOCATION de un archivo Python
extract_mfn_location() {
    local file="$1"
    grep -m1 "^MFN_LOCATION:" "$file" 2>/dev/null | cut -d' ' -f2 | tr -d '\r\n'
}

# Función para mover archivo a su ubicación MFN
route_file() {
    local file="$1"
    local mfn_location="$2"

    if [ -z "$mfn_location" ]; then
        log "⚠️  SIN MFN_LOCATION: Moviendo a cuarentena: $(basename "$file")"
        # Verificar que no esté ya en quarantine
        if [[ "$file" == *"/quarantine/"* ]]; then
            return 1
        fi
        mv "$file" "$QUARANTINE/" 2>/dev/null
        return 1
    fi

    # Construir ruta destino
    local dest_dir="$WORKSPACE/$mfn_location"
    mkdir -p "$dest_dir"

    local filename=$(basename "$file")
    local dest_path="$dest_dir/$filename"

    # Evitar sobrescritura
    if [ -f "$dest_path" ]; then
        local timestamp=$(date +%s)
        local name="${filename%.*}"
        local ext="${filename##*.}"
        dest_path="$dest_dir/${name}_${timestamp}.${ext}"
    fi

    mv "$file" "$dest_path" 2>/dev/null
    log "✅ ENRUTADO: $filename → $mfn_location/"

    # Actualizar mapa MFN
    echo "{\"file\": \"$dest_path\", \"location\": \"$mfn_location\", \"timestamp\": \"$(date -Iseconds)\"}" >> "$MFN_MAP"

    # Regenerar path_map.json
    if [ -f "$WORKSPACE/tools/generate_path_map.py" ]; then
        python3 "$WORKSPACE/tools/generate_path_map.py" 2>/dev/null &
    fi

    return 0
}

# Procesar un archivo nuevo
process_file() {
process_file() {
    local file="$1"
    local event="$2"
    # ═══════════════════════════════════════════
    # FILTRO 1: Ignorar archivos en quarantine/
    # ═══════════════════════════════════════════
    
    # 🔒 SEGURIDAD: Ignorar si el archivo ya no existe o si está en cuarentena
    if [ ! -f "$file" ] || [[ "$file" == *"quarantine"* ]]; then
        return 0
    fi
    
    log "📄 DETECTADO: $event → $(basename "$file")"
    # ... (resto de la función igual)


    # ═══════════════════════════════════════════
    # FILTRO 2: Solo procesar CREATE (ignorar MODIFY y MOVED_TO)
    # ═══════════════════════════════════════════
    if [[ "$event" != *"CREATE"* ]]; then
        return 0
    fi

    log "📄 DETECTADO: $event → $(basename "$file")"

    # Solo procesar archivos Python y YAML
    if [[ ! "$file" =~ \.(py|yaml|yml)$ ]]; then
        return 0
    fi

    # ═══════════════════════════════════════════
    # FILTRO 3: Verificar que el archivo existe
    # (evita eventos fantasma MODIFY tras CREATE)
    # ═══════════════════════════════════════════
    sleep 0.5
    if [ ! -f "$file" ]; then
        log "⏭️  FANTASMA: $(basename "$file") ya no existe, ignorando"
        return 0
    fi

    # Extraer MFN_LOCATION
    local mfn_location=$(extract_mfn_location "$file")

    # Enrutar archivo
    route_file "$file" "$mfn_location"
}

# ═══════════════════════════════════════════════════════════════
# MONITOREO PRINCIPAL CON INOTIFYWAIT
# ═══════════════════════════════════════════════════════════════

log "👁️  WORKSPACE SENTINEL INICIADO (v1.1)"
log "📂 Vigilando: $INBOX"
log "🔔 Solo procesando: CREATE"
log "🚫 Ignorando: quarantine/, MODIFY, MOVED_TO"

# Verificar si inotifywait está instalado
if ! command -v inotifywait &> /dev/null; then
    log "❌ ERROR: inotifywait no está instalado"
    log "💡 Instalar con: sudo apt install inotify-tools"
    exit 1
fi

# Monitoreo continuo - solo eventos # Monitoreo continuo, recursivo, EXCLUYENDO la carpeta quarantine
inotifywait -m -r -e create -e modify -e moved_to \
    --exclude 'quarantine' \
    --format '%w%f %e' "$INBOX" 2>/dev/null | \
while read file event; do
    # ... (resto del bucle igual)
    # Ignorar directorios
    if [ -d "$file" ]; then
        continue
    fi

    # Ignorar archivos temporales
    if [[ "$file" =~ \.(swp|tmp|bak|log)$ ]]; then
        continue
    fi

    process_file "$file" "$event"
done
