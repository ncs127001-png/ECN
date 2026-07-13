#!/bin/bash
################################################################################
# NEUROBIT TAREA 5 — Start WebSocket + API Servers
# 
# Inicia:
#   1. API Server en puerto 5000 (neurobit_api.py)
#   2. WebSocket Server en puerto 5001 (websocket_salon_server.py)
#   3. Abre navegador en http://127.0.0.1:5000/interface/salon.html
#
# Principios:
#   - SOBERANÍA: Solo localhost (127.0.0.1)
#   - APPEND-ONLY: Todos los eventos se registran en memoria_eva.jsonl
#   - FALLBACK: Si WebSocket falla, API polling continúa
################################################################################

set -e

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORKSPACE"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🧠 NEUROBIT TAREA 5 — WebSocket Real-Time Setup${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: Verificar entorno Python
# ─────────────────────────────────────────────────────────────────────────────

echo -e "\n${YELLOW}[STEP 1]${NC} Verificando entorno Python..."

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 no encontrado${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python ${PYTHON_VERSION}${NC}"

# Verificar que estamos en workspace
if [ ! -f "neurobit_api.py" ]; then
    echo -e "${RED}❌ neurobit_api.py no encontrado en ${WORKSPACE}${NC}"
    exit 1
fi

if [ ! -f "core/websocket_salon_server.py" ]; then
    echo -e "${RED}❌ core/websocket_salon_server.py no encontrado${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Archivos necesarios encontrados${NC}"

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: Matar procesos antiguos
# ─────────────────────────────────────────────────────────────────────────────

echo -e "\n${YELLOW}[STEP 2]${NC} Limpiando procesos anteriores..."

pkill -f "python3 neurobit_api.py" 2>/dev/null || true
pkill -f "websocket_salon_server.py" 2>/dev/null || true

sleep 1
echo -e "${GREEN}✅ Procesos limpios${NC}"

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: Verificar puertos
# ─────────────────────────────────────────────────────────────────────────────

echo -e "\n${YELLOW}[STEP 3]${NC} Verificando puertos..."

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}⚠️  Puerto $1 está en uso${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ Puerto $1 disponible${NC}"
    return 0
}

check_port 5000 || true
check_port 5001 || true

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: Crear directorios necesarios
# ─────────────────────────────────────────────────────────────────────────────

echo -e "\n${YELLOW}[STEP 4]${NC} Verificando directorios..."

mkdir -p data/logs
echo -e "${GREEN}✅ Directorios listos${NC}"

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: Iniciar servidor API (puerto 5000)
# ─────────────────────────────────────────────────────────────────────────────

echo -e "\n${YELLOW}[STEP 5]${NC} Iniciando servidor API (puerto 5000)..."

python3 neurobit_api.py > data/logs/api_server.log 2>&1 &
API_PID=$!

sleep 2

if ps -p $API_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API Server iniciado (PID: $API_PID)${NC}"
else
    echo -e "${RED}❌ Error iniciando API Server${NC}"
    cat data/logs/api_server.log
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: Iniciar servidor WebSocket (puerto 5001)
# ─────────────────────────────────────────────────────────────────────────────

echo -e "\n${YELLOW}[STEP 6]${NC} Iniciando servidor WebSocket (puerto 5001)..."

cd core
python3 websocket_salon_server.py > ../data/logs/websocket_server.log 2>&1 &
WS_PID=$!
cd ..

sleep 2

if ps -p $WS_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ WebSocket Server iniciado (PID: $WS_PID)${NC}"
else
    echo -e "${RED}❌ Error iniciando WebSocket Server${NC}"
    cat data/logs/websocket_server.log
    kill $API_PID 2>/dev/null || true
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: Verificar salud de los servidores
# ─────────────────────────────────────────────────────────────────────────────

echo -e "\n${YELLOW}[STEP 7]${NC} Verificando salud de los servidores..."

sleep 2

# Probar API
if curl -s http://127.0.0.1:5000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API Server respondiendo${NC}"
else
    echo -e "${RED}⚠️  API Server no respondiendo en /health${NC}"
fi

# Probar WebSocket (solo verificar que puerto está abierto)
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${GREEN}✅ WebSocket Server escuchando en puerto 5001${NC}"
else
    echo -e "${RED}⚠️  WebSocket Server no escuchando${NC}"
fi

# ─────────────────────────────────────────────────────────────────────────────
# STEP 8: Mostrar información
# ─────────────────────────────────────────────────────────────────────────────

echo -e "\n${GREEN}════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ TAREA 5 — Servidores iniciados correctamente${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}INFORMACIÓN DE CONEXIÓN:${NC}"
echo -e "  🌐 Interface (Salón)        : ${YELLOW}http://127.0.0.1:5000/interface/salon.html${NC}"
echo -e "  📡 API Server              : ${YELLOW}http://127.0.0.1:5000${NC}"
echo -e "  🔌 WebSocket Server        : ${YELLOW}ws://127.0.0.1:5001${NC}"
echo -e "  📊 Health Check            : ${YELLOW}http://127.0.0.1:5000/health${NC}"
echo -e "  📈 WebSocket Stats         : ${YELLOW}http://127.0.0.1:5001/stats${NC}"
echo -e "  📝 API Logs                : ${YELLOW}${WORKSPACE}/data/logs/api_server.log${NC}"
echo -e "  📝 WebSocket Logs          : ${YELLOW}${WORKSPACE}/data/logs/websocket_server.log${NC}"

echo -e "\n${BLUE}CARACTERÍSTICAS (TAREA 5):${NC}"
echo -e "  ✨ Mensajes en tiempo real via WebSocket"
echo -e "  ✨ Fallback a API polling si WebSocket falla"
echo -e "  ✨ Append-only logging en memoria_eva.jsonl"
echo -e "  ✨ Soberanía: Solo localhost (127.0.0.1)"
echo -e "  ✨ Estado visual del WebSocket en la interfaz"

echo -e "\n${BLUE}PARA DETENER LOS SERVIDORES:${NC}"
echo -e "  ${YELLOW}kill $API_PID $WS_PID${NC}"
echo -e "  o use: ${YELLOW}pkill -f 'neurobit_api\\|websocket_salon'${NC}"

echo -e "\n${BLUE}MONITOREO:${NC}"
echo -e "  ${YELLOW}tail -f ${WORKSPACE}/data/logs/api_server.log${NC}"
echo -e "  ${YELLOW}tail -f ${WORKSPACE}/data/logs/websocket_server.log${NC}"

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}\n"

# ─────────────────────────────────────────────────────────────────────────────
# Esperar a que se termine
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${YELLOW}Presiona Ctrl+C para detener los servidores...${NC}\n"

# Mantener en foreground
trap "echo -e '\n${YELLOW}Deteniendo servidores...${NC}'; kill $API_PID $WS_PID 2>/dev/null; exit 0" INT TERM

wait

