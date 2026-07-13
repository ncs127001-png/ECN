#!/bin/bash
################################################################################
# NEUROBIT QUICK STATUS — Health Check Ultrarrápido
# Versión: 1.0 — Marzo 2026
# Propósito: Ver estado en una línea con colores
################################################################################

API_PORT=5000
MCP_PORT=8090

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$API_PORT/health 2>/dev/null)
MCP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:$MCP_PORT/health 2>/dev/null)
LOGS_OK=$([ -w ~/WORKSPACE_NEUROBIT_V0.2/data/logs ] && echo "OK" || echo "FAIL")
MEMORIA_LINES=$(wc -l < ~/WORKSPACE_NEUROBIT_V0.2/data/memoria_eva.jsonl 2>/dev/null)

# API Status
if [ "$API_STATUS" = "200" ]; then
    API_ICON="${GREEN}✓${NC}"
else
    API_ICON="${RED}✗${NC}"
fi

# MCP Status
if [ "$MCP_STATUS" = "200" ]; then
    MCP_ICON="${GREEN}✓${NC}"
else
    MCP_ICON="${RED}✗${NC}"
fi

# Logs
if [ "$LOGS_OK" = "OK" ]; then
    LOGS_ICON="${GREEN}✓${NC}"
else
    LOGS_ICON="${RED}✗${NC}"
fi

echo -e "NEUROBIT STATUS: API[$API_ICON] MCP[$MCP_ICON] LOGS[$LOGS_ICON] MEMORIA[$MEMORIA_LINES registros]"
