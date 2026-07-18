#!/bin/bash
################################################################################
# NEUROBIT_CENTRAL_STATION — Script de Inicio Unificado v2.0
# Fecha: Marzo 2026
# Propósito: Iniciar TODOS los servicios con UN solo comando
################################################################################

set -e  # Exit on error

# CONFIGURACIÓN
WORKSPACE="$HOME/WORKSPACE_NEUROBIT_V0.2"
MCP_HOME="$HOME/NEUROBIT_MCP_SERVER"
API_PORT=5000
MCP_PORT=8090

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

################################################################################
# FUNCIONES
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

cleanup_services() {
    log_warning "Deteniendo servicios anteriores..."
    pkill -f "python3.*neurobit_api.py" 2>/dev/null || true
    pkill -f "mcp_server.py" 2>/dev/null || true
    sleep 2
}

check_venv() {
    if [ -d "$WORKSPACE/.venv" ]; then
        log_success "Entorno virtual encontrado en $WORKSPACE/.venv"
        source "$WORKSPACE/.venv/bin/activate"
        return 0
    elif [ -d "$HOME/venv" ]; then
        log_success "Entorno virtual encontrado en $HOME/venv"
        source "$HOME/venv/bin/activate"
        return 0
    else
        log_warning "No se encontró entorno virtual. Continuando sin activar..."
        return 0
    fi
}

check_critical_dirs() {
    log_info "Verificando directorios críticos..."
    
    mkdir -p "$WORKSPACE/data/logs"
    mkdir -p "$WORKSPACE/data/fragments"
    mkdir -p "$WORKSPACE/data/mcp_conversations"
    
    # Verificar permisos
    if [ ! -w "$WORKSPACE/data/logs" ]; then
        log_error "Directorio $WORKSPACE/data/logs NO tiene permisos de escritura"
        return 1
    fi
    
    log_success "Directorios críticos verificados"
    return 0
}

start_api_flask() {
    log_info "Iniciando neurobit_api.py (puerto $API_PORT)..."
    
    cd "$WORKSPACE"
    python3 neurobit_api.py > "$WORKSPACE/data/logs/api_flask.log" 2>&1 &
    API_PID=$!
    
    echo $API_PID > /tmp/neurobit_api.pid
    sleep 3
    
    # Verificar que está corriendo
    if ! ps -p $API_PID > /dev/null; then
        log_error "neurobit_api.py NO se inició correctamente"
        cat "$WORKSPACE/data/logs/api_flask.log"
        return 1
    fi
    
    # Verificar endpoint
    if curl -s http://127.0.0.1:$API_PORT/health > /dev/null 2>&1; then
        log_success "neurobit_api.py iniciado (PID: $API_PID, Puerto: $API_PORT)"
        return 0
    else
        log_warning "neurobit_api.py está corriendo pero /health no responde aún (PID: $API_PID)"
        sleep 2
        return 0
    fi
}

start_mcp_server() {
    if [ ! -f "$MCP_HOME/start_mcp.sh" ]; then
        log_warning "MCP Server script NO encontrado en $MCP_HOME/start_mcp.sh (OMITIENDO)"
        return 0
    fi
    
    log_info "Iniciando MCP Server (puerto $MCP_PORT)..."
    
    # Ejecutar script MCP
    bash "$MCP_HOME/start_mcp.sh" > "$WORKSPACE/data/logs/mcp_server.log" 2>&1 &
    MCP_PID=$!
    
    echo $MCP_PID > /tmp/neurobit_mcp.pid
    sleep 3
    
    if ! ps -p $MCP_PID > /dev/null; then
        log_warning "MCP Server NO se inició correctamente (verificar $WORKSPACE/data/logs/mcp_server.log)"
        return 0
    fi
    
    # Intentar verificar endpoint MCP
    if curl -s http://127.0.0.1:$MCP_PORT/health > /dev/null 2>&1; then
        log_success "MCP Server iniciado (PID: $MCP_PID, Puerto: $MCP_PORT)"
    else
        log_warning "MCP Server está corriendo pero /health no responde aún (PID: $MCP_PID)"
    fi
    
    return 0
}

start_centinela() {
    log_info "Iniciando Centinela (clipboard monitor)..."
    
    # Esperar a que API esté lista
    local max_attempts=10
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://127.0.0.1:$API_PORT/health > /dev/null 2>&1; then
            if curl -s -X POST http://127.0.0.1:$API_PORT/start_centinela > /dev/null 2>&1; then
                log_success "Centinela iniciado correctamente"
                return 0
            fi
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    log_warning "No se pudo iniciar Centinela (API puede no estar lista)"
    return 0
}

start_keylogger() {
    log_info "Iniciando Keylogger (HID daemon)..."
    
    local keylogger_script="$WORKSPACE/modules/neurobit_hid_daemon/neurobit_keylogger.py"
    local keylogger_log="$WORKSPACE/data/logs/keylogger_daemon.log"
    
    # Verificar que el script existe
    if [ ! -f "$keylogger_script" ]; then
        log_warning "Script keylogger no encontrado: $keylogger_script (OMITIENDO)"
        return 0
    fi
    
    # Iniciar keylogger en background
    cd "$WORKSPACE"
    nohup python3 "$keylogger_script" > "$keylogger_log" 2>&1 &
    KEYLOGGER_PID=$!
    
    echo $KEYLOGGER_PID > /tmp/neurobit_keylogger.pid
    sleep 2
    
    # Verificar que está corriendo
    if ! ps -p $KEYLOGGER_PID > /dev/null; then
        log_warning "Keylogger NO se inició correctamente (verificar $keylogger_log)"
        return 0
    fi
    
    log_success "Keylogger iniciado (PID: $KEYLOGGER_PID)"
    return 0
}

show_status() {
    echo ""
    echo "======================================"
    echo -e "${GREEN}✅ SERVICIOS INICIADOS${NC}"
    echo "======================================"
    echo ""
    
    # API Flask
    if [ -f /tmp/neurobit_api.pid ]; then
        API_PID=$(cat /tmp/neurobit_api.pid)
        if ps -p $API_PID > /dev/null; then
            echo -e "${GREEN}API Flask${NC}"
            echo "  PID:      $API_PID"
            echo "  Puerto:   $API_PORT"
            echo "  URL:      http://127.0.0.1:$API_PORT"
            echo "  Health:   http://127.0.0.1:$API_PORT/health"
            echo ""
        fi
    fi
    
    # MCP Server
    if [ -f /tmp/neurobit_mcp.pid ]; then
        MCP_PID=$(cat /tmp/neurobit_mcp.pid)
        if ps -p $MCP_PID > /dev/null; then
            echo -e "${GREEN}MCP Server${NC}"
            echo "  PID:      $MCP_PID"
            echo "  Puerto:   $MCP_PORT"
            echo "  URL:      http://127.0.0.1:$MCP_PORT"
            echo ""
        fi
    fi
    
    # Keylogger
    if [ -f /tmp/neurobit_keylogger.pid ]; then
        KEYLOGGER_PID=$(cat /tmp/neurobit_keylogger.pid)
        if ps -p $KEYLOGGER_PID > /dev/null; then
            echo -e "${GREEN}🔑 Keylogger${NC}"
            echo "  PID:      $KEYLOGGER_PID"
            echo "  Logs:     $WORKSPACE/data/logs/keylog_main.jsonl"
            echo ""
        fi
    fi
    
    echo -e "${GREEN}ACCESO A SERVICIOS${NC}"
    echo "  Estación web:   http://127.0.0.1:$API_PORT/interface/index.html"
    echo "  API:            http://127.0.0.1:$API_PORT"
    echo "  Memoria:        http://127.0.0.1:$API_PORT/memoria"
    echo "  Centinela:      http://127.0.0.1:$API_PORT/centinela_status"
    echo ""
    
    echo -e "${GREEN}LOGS${NC}"
    echo "  API:            $WORKSPACE/data/logs/api_flask.log"
    echo "  MCP:            $WORKSPACE/data/logs/mcp_server.log"
    echo "  Keylogger:      $WORKSPACE/data/logs/keylogger_daemon.log"
    echo ""
    
    echo "======================================"
    echo -e "${YELLOW}Para detener servicios:${NC}"
    echo "  pkill -f neurobit_api.py"
    echo "  pkill -f mcp_server.py"
    echo "  pkill -f neurobit_keylogger.py"
    echo ""
    echo -e "${YELLOW}Para verificar estado:${NC}"
    echo "  curl http://127.0.0.1:$API_PORT/health | jq"
    echo "======================================"
}

################################################################################
# MAIN
################################################################################

echo ""
echo "======================================"
echo -e "${BLUE}🧠 NEUROBIT CENTRAL STATION v2.0${NC}"
echo "======================================"
echo ""

# Paso 1: Limpiar servicios anteriores
cleanup_services

# Paso 2: Verificar workspace
if [ ! -d "$WORKSPACE" ]; then
    log_error "Workspace no encontrado: $WORKSPACE"
    exit 1
fi
log_success "Workspace encontrado: $WORKSPACE"

# Paso 3: Activar entorno virtual
check_venv

# Paso 4: Verificar directorios críticos
if ! check_critical_dirs; then
    log_error "Error al verificar directorios críticos"
    exit 1
fi

# Paso 5: Iniciar servicios
if ! start_api_flask; then
    log_error "Error al iniciar API Flask"
    exit 1
fi

if ! start_mcp_server; then
    log_warning "MCP Server no se inició, pero continuando..."
fi

# Paso 6: Iniciar Centinela
if ! start_centinela; then
    log_warning "Centinela no se inició, pero los servicios están disponibles"
fi

# Paso 7: Iniciar Keylogger
if ! start_keylogger; then
    log_warning "Keylogger no se inició, pero los servicios están disponibles"
fi

# Paso 8: Mostrar estado final
show_status

log_success "🎉 NEUROBIT CENTRAL STATION está operativo"
exit 0
