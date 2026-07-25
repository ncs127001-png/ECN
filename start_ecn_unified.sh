#!/bin/bash
################################################################################
# ECN UNIFIED STARTER — Script de Inicio Unificado v0.2
# Fecha: Julio 2026
# Propósito: Iniciar TODOS los servicios con UN solo comando
################################################################################

set -e  # Exit on error

# CONFIGURACIÓN
WORKSPACE="$HOME/ECN"
API_PORT=5000
WS_PORT=5001
MCP_PORT=8090

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }

cleanup_services() {
    log_warning "Deteniendo servicios anteriores..."
    pkill -f "python3.*neurobit_api.py" 2>/dev/null || true
    pkill -f "python3.*websocket_salon_server.py" 2>/dev/null || true
    sleep 2
}

check_venv() {
    if [ -d "$WORKSPACE/.venv" ]; then
        log_success "Entorno virtual encontrado"
        source "$WORKSPACE/.venv/bin/activate"
        return 0
    else
        log_warning "No se encontró entorno virtual"
        return 0
    fi
}

check_critical_dirs() {
    log_info "Verificando directorios críticos..."
    mkdir -p "$WORKSPACE/data/logs"
    mkdir -p "$WORKSPACE/data/fragments"
    mkdir -p "$WORKSPACE/data/mcp_conversations"
    mkdir -p "$WORKSPACE/config"
    log_success "Directorios críticos verificados"
}

start_api_flask() {
    log_info "Iniciando neurobit_api.py (puerto $API_PORT)..."
    cd "$WORKSPACE"
    
    # Generar path_map si no existe
    if [ ! -f "$WORKSPACE/data/path_map.json" ]; then
        log_info "Generando path_map.json..."
        python3 tools/generate_path_map.py
    fi
    
    # Iniciar API
    python3 core/bootstrap.py > "$WORKSPACE/data/logs/api_flask.log" 2>&1 &
    API_PID=$!
    echo $API_PID > /tmp/neurobit_api.pid
    
    sleep 3
    
    # Verificar que está corriendo
    if ! ps -p $API_PID > /dev/null; then
        log_error "neurobit_api.py NO se inició correctamente"
        tail -20 "$WORKSPACE/data/logs/api_flask.log"
        return 1
    fi
    
    # Health check
    local attempts=0
    while [ $attempts -lt 15 ]; do
        if curl -s http://127.0.0.1:$API_PORT/health > /dev/null 2>&1; then
            log_success "✅ API Flask iniciada (PID: $API_PID, Puerto: $API_PORT)"
            return 0
        fi
        attempts=$((attempts + 1))
        sleep 1
        echo -ne "\r   Esperando API... ($attempts/15)"
    done
    
    log_error "La API no respondió en 15s"
    tail -20 "$WORKSPACE/data/logs/api_flask.log"
    return 1
}

show_status() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo -e "║   ${GREEN}✅ ECN DESPIERTA - SISTEMA OPERATIVO${NC}                     ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo -e "${GREEN}SERVICIOS ACTIVOS:${NC}"
    echo -e "    API Interface : ${YELLOW}http://127.0.0.1:$API_PORT${NC}"
    echo -e "   🔌 WebSocket     : ${YELLOW}ws://127.0.0.1:$WS_PORT${NC}"
    echo -e "   🤖 MCP Context   : ${YELLOW}http://127.0.0.1:$MCP_PORT${NC}"
    echo ""
    echo -e "${BLUE}ACCESO A INTERFACES:${NC}"
    echo -e "   Estación Central: ${YELLOW}file:///home/gus/ECN/interface/index.html${NC}"
    echo -e "   Salón de Reuniones: ${YELLOW}file:///home/gus/ECN/interface/salon.html${NC}"
    echo ""
    echo -e "${YELLOW}PARA DETENER:${NC}"
    echo "   pkill -f neurobit_api"
    echo ""
}

################################################################################
# MAIN
################################################################################

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo -e "║   ${BLUE}🧠 ECN v0.2 - INICIANDO RITUAL DE DESPERTAR...${NC}           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Paso 1: Limpiar servicios
cleanup_services

# Paso 2: Verificar workspace
if [ ! -d "$WORKSPACE" ]; then
    log_error "Workspace no encontrado: $WORKSPACE"
    exit 1
fi
log_success "Workspace encontrado: $WORKSPACE"

# Paso 3: Activar entorno virtual
check_venv

# Paso 4: Verificar directorios
check_critical_dirs

# Paso 5: Iniciar API
if ! start_api_flask; then
    log_error "Error al iniciar API Flask"
    exit 1
fi

# Paso 6: Mostrar estado
show_status

log_success " ECN está operativa"
exit 0
