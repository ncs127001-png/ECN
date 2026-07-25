#!/bin/bash
# ==============================================================================
# START_ECN.SH - RITUAL DE DESPERTAR SOBERANO (v0.2 - Corregido)
# Principio: Soberanía de Ruta Relativa (Igual que StatePersistence)
# ==============================================================================

set -e

# 1. DEFINICIÓN SOBERANA DE LA RAÍZ
# No importa dónde estés parado en la terminal, esto siempre apunta a ~/ECN
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$SCRIPT_DIR"

# 2. INYECCIÓN CRÍTICA EN PYTHONPATH
# Añadimos la raíz al PATH de Python ANTES de hacer cualquier cosa.
# Esto permite que 'import core' funcione siempre.
export PYTHONPATH="$WORKSPACE:$PYTHONPATH"

cd "$WORKSPACE"

# Colores
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🧠 ECN v0.2 - INICIANDO RITUAL DE DESPERTAR...           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"

# ─────────────────────────────────────────────────────────────────────────────
# PASO 0: ACTIVACIÓN DEL ENTORNO VIRTUAL
# ─────────────────────────────────────────────────────────────────────────────
echo -e "\n${YELLOW}[0/6] Activando entorno virtual...${NC}"
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo -e "${GREEN}✅ Entorno activado.${NC}"
else
    echo -e "${RED}❌ ERROR: No se encuentra .venv${NC}"
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# PASO 1: CARGA DE CONFIGURACIÓN (Lectura No Destructiva)
# ─────────────────────────────────────────────────────────────────────────────
echo -e "\n${YELLOW}[1/6] Leyendo ADN del sistema (Config)...${NC}"

# Usamos python para leer el YAML y exportar las variables de entorno al Bash
eval "$(python3 - << 'PY_CONFIG'
import yaml
import os

config_file = os.path.join(os.environ.get('PWD', '.'), "ecn_config.yaml")
try:
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    ports = config.get('network', {}).get('ports', {})
    api_port = ports.get('api_flask', 5000)
    ws_port = ports.get('websocket_salon', 5001)
    mcp_port = ports.get('mcp_server', 8090)
    
    # Imprimir comandos export para que bash los evalúe
    print(f"export API_PORT={api_port}")
    print(f"export WS_PORT={ws_port}")
    print(f"export MCP_PORT={mcp_port}")
    print(f"echo \"✅ Configuración cargada (API:{api_port}, WS:{ws_port}, MCP:{mcp_port})\"")
except Exception as e:
    # Defaults si falla
    print("export API_PORT=5000")
    print("export WS_PORT=5001")
    print("export MCP_PORT=8090")
    print("echo \"⚠️  Config no encontrada. Usando defaults.\"")
PY_CONFIG
)"

# Verificar/Generar Path Map (Solo como índice visual, no para rutas críticas)
MAP_FILE="$WORKSPACE/data/path_map.json"
if [ ! -f "$MAP_FILE" ]; then
    echo "⚠️  Path Map no encontrado. Regenerando..."
    if [ -f "$WORKSPACE/tools/generate_path_map.py" ]; then
        python3 "$WORKSPACE/tools/generate_path_map.py"
        echo "✅ Mapa generado."
    fi
else
    echo "✅ Mapa existente detectado."
fi

# ─────────────────────────────────────────────────────────────────────────────
# PASO 2: LIMPIEZA DE PROCESOS ANTERIORES
# ─────────────────────────────────────────────────────────────────────────────
echo -e "\n${YELLOW}[2/6] Limpiando procesos residuales...${NC}"
pkill -f "neurobit_api.py" 2>/dev/null || true
pkill -f "websocket_salon_server.py" 2>/dev/null || true
pkill -f "mcp_server.py" 2>/dev/null || true
sleep 1
echo -e "${GREEN}✅ Limpieza completada.${NC}"

# ─────────────────────────────────────────────────────────────────────────────
# PASO 3: VERIFICACIÓN DE PUERTOS
# ─────────────────────────────────────────────────────────────────────────────
echo -e "\n${YELLOW}[3/6] Verificando puertos ($API_PORT, $WS_PORT, $MCP_PORT)...${NC}"
for port in $API_PORT $WS_PORT $MCP_PORT; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}⚠️  Puerto $port ocupado. Liberando...${NC}"
        kill $(lsof -t -i:$port) 2>/dev/null || true
        sleep 1
    else
        echo -e "${GREEN}✅ Puerto $port libre.${NC}"
    fi
done

# ─────────────────────────────────────────────────────────────────────────────
# PASO 4: INICIO DE LA TRIADA (BACKGROUND)
# ─────────────────────────────────────────────────────────────────────────────
echo -e "\n${YELLOW}[4/6] Iniciando servicios en background...${NC}"

# 4.1 API Central
echo -e "   📡 Levantando API Flask (Puerto $API_PORT)..."
# NOTA: Al tener PYTHONPATH seteado arriba, 'core.neurobit_api' funciona

# Reemplazar la línea:
# python3 -m core.neurobit_api > data/logs/api.log 2>&1 &

# Por esta:
mkdir -p "$WORKSPACE/data/logs"
python3 "$WORKSPACE/core/bootstrap.py" > data/logs/api.log 2>&1 &
API_PID=$!
echo -e "      ${BLUE}PID: $API_PID${NC}"

# 4.2 WebSocket Salon
if [ -f "$WORKSPACE/core/websocket_salon_server.py" ]; then
    echo -e "   💬 Levantando WebSocket Salon (Puerto $WS_PORT)..."
    python3 -m core.websocket_salon_server > data/logs/ws.log 2>&1 &
    WS_PID=$!
    echo -e "      ${BLUE}PID: $WS_PID${NC}"
fi

# 4.3 MCP Server
if [ -f "$WORKSPACE/core/mcp_server.py" ]; then
    echo -e "   🤖 Levantando MCP Server (Puerto $MCP_PORT)..."
    python3 -m core.mcp_server > data/logs/mcp.log 2>&1 &
    MCP_PID=$!
    echo -e "      ${BLUE}PID: $MCP_PID${NC}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# PASO 5: ESPERA ACTIVA INTELIGENTE (HEALTH CHECK)
# ─────────────────────────────────────────────────────────────────────────────
echo -e "\n${YELLOW}[5/6] Esperando inicio de servicios (Health Check)...${NC}"
MAX_ATTEMPTS=15
ATTEMPT=0
API_OK=false

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    ATTEMPT=$((ATTEMPT + 1))
    
    if curl -s "http://127.0.0.1:$API_PORT/health" | grep -q '"status"'; then
        echo -e "${GREEN}✅ API Central RESPONDE (Intento $ATTEMPT/$MAX_ATTEMPTS)${NC}"
        API_OK=true
        break
    fi
    
    echo -ne "${YELLOW}\r   Esperando API... ($ATTEMPT/$MAX_ATTEMPTS)${NC}"
    sleep 1
done

if [ "$API_OK" != "true" ]; then
    echo -e "\n${RED}❌ ERROR: La API no levantó en ${MAX_ATTEMPTS}s.${NC}"
    echo -e "${YELLOW}Últimas líneas del log:${NC}"
    tail -n 10 data/logs/api.log
    kill $API_PID 2>/dev/null
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# PASO 6: REPORTE FINAL
# ─────────────────────────────────────────────────────────────────────────────
echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✅ ECN DESPIERTA - SISTEMA OPERATIVO                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"

echo -e "\n${BLUE}SERVICIOS ACTIVOS:${NC}"
echo -e "   🌐 API Interface : ${YELLOW}http://127.0.0.1:$API_PORT${NC}"
echo -e "   🔌 WebSocket     : ${YELLOW}ws://127.0.0.1:$WS_PORT${NC}"
echo -e "   🤖 MCP Context   : ${YELLOW}http://127.0.0.1:$MCP_PORT${NC}"

echo -e "\n${BLUE}NAVEGACIÓN NO DESTRUCTIVA:${NC}"
echo -e "   El sistema opera sobre índices en memoria."
echo -e "   Los archivos físicos están protegidos."

echo -e "\n${YELLOW}PARA DETENER:${NC}"
echo -e "   pkill -f neurobit_api"

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════${NC}\n"
