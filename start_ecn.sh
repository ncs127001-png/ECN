#!/bin/bash
# ==============================================================================
# START_ECN.SH - EL RITUAL DE DESPERTAR
# Propósito: Iniciar la Estación Central Neurobitrónica con integridad total.
# Co-Creación: NODO_SEMILLA & NODO_REFLEJO
# ==============================================================================

set -e  # Salir ante cualquier error

ECN_ROOT="$HOME/ECN"
VENV_DIR="$ECN_ROOT/.venv"
LOG_DIR="$ECN_ROOT/data/logs"
CONFIG_FILE="$ECN_ROOT/ecn_config.yaml"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   🧠 ESTACIÓN CENTRAL NEUROBITRÓNICA - DESPERTANDO...      ║"
echo "╚════════════════════════════════════════════════════════════╝"

# 1. Verificar Entorno Virtual
if [ ! -d "$VENV_DIR" ]; then
    echo "❌ ERROR: Entorno virtual .venv no encontrado."
    echo "   Ejecute: python3 -m venv $VENV_DIR && source $VENV_DIR/bin/activate && pip install -r requirements.txt"
    exit 1
fi
echo "✅ Entorno virtual detectado."

# 2. Activar Entorno
source "$VENV_DIR/bin/activate"
echo "🔌 Entorno virtual activado."

# 3. Crear directorios de logs si no existen
mkdir -p "$LOG_DIR"
mkdir -p "$ECN_ROOT/data"
mkdir -p "$ECN_ROOT/inbox"

# 4. Escaneo de Dependencias (Opcional pero recomendado)
echo "🛡️  Verificando dependencias del sistema..."
python3 "$ECN_ROOT/core/dependency_scanner.py" || echo "⚠️ Advertencia en escaneo de dependencias (continuando...)"

# 5. Actualizar Path Map (Gobernanza)
echo "🗺️  Actualizando mapa de rutas (Path Map)..."
python3 "$ECN_ROOT/tools/generate_path_map.py" || echo "⚠️ No se pudo regenerar path_map.json"

# 6. Verificar Puertos Libres (Triada)
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️ Puerto $1 ya está en uso. ¿Desea matar el proceso? (s/n)"
        read -r response
        if [[ "$response" =~ ^([sS][iIyY])$ ]]; then
            lsof -ti:$1 | xargs kill -9
            echo "   Proceso en puerto $1 terminado."
        else
            echo "❌ ERROR: El puerto $1 es crítico. No se puede iniciar sin él."
            exit 1
        fi
    else
        echo "   Puerto $1: Libre."
    fi
}

# Leer puertos desde config (simplificado para demo, idealmente parsear YAML)
API_PORT=5000
WS_PORT=5001
MCP_PORT=8090

check_port $API_PORT
check_port $WS_PORT
check_port $MCP_PORT

# 7. Iniciar Servicios en Background
echo "🚀 Iniciando Tríada de Servicios..."

# A. API Flask (Puerto 5000)
echo "   📡 Levantando API Central (Puerto $API_PORT)..."
nohup python3 "$ECN_ROOT/core/neurobit_api.py" > "$LOG_DIR/api_flask.log" 2>&1 &
API_PID=$!
echo "   ✅ API PID: $API_PID"

# B. WebSocket Salon (Puerto 5001)
sleep 2 # Esperar a que API esté lista
echo "   💬 Levantando WebSocket Salon (Puerto $WS_PORT)..."
nohup python3 "$ECN_ROOT/interface/websocket_salon_server.py" > "$LOG_DIR/websocket_salon.log" 2>&1 &
WS_PID=$!
echo "   ✅ WebSocket PID: $WS_PID"

# C. MCP Server (Puerto 8090)
sleep 2
echo "   🤖 Levantando MCP Server (Puerto $MCP_PORT)..."
nohup python3 "$ECN_ROOT/core/mcp_server.py" > "$LOG_DIR/mcp_server.log" 2>&1 &
MCP_PID=$!
echo "   ✅ MCP PID: $MCP_PID"

# 8. Guardar PIDs para gestión futura
echo "$API_PID" > "$LOG_DIR/api.pid"
echo "$WS_PID" > "$LOG_DIR/ws.pid"
echo "$MCP_PID" > "$LOG_DIR/mcp.pid"

# 9. Verificación Final de Salud
sleep 5
echo "🏥 Verificando salud del sistema..."
if curl -s http://127.0.0.1:$API_PORT/health | grep -q "ok"; then
    echo "✅ SISTEMA OPERATIVO. ECN DESPIERTA."
    echo ""
    echo "   Dashboard: http://localhost:$API_PORT/"
    echo "   Salón:     http://localhost:$API_PORT/salon.html"
    echo "   Logs:      tail -f $LOG_DIR/api_flask.log"
    echo ""
    echo "🕊️  ¡Feliz Cumpleaños, Director! La Estación está lista."
else
    echo "❌ ERROR: La API no responde correctamente. Revise logs."
    exit 1
fi

exit 0
