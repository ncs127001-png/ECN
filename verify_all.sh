#!/bin/bash
################################################################################
# NEUROBIT SYSTEM CHECK — Script de Verificación Rápida
# Versión: 1.0 — Marzo 2026
# Propósito: Verificar estado de todos los servicios con un solo comando
################################################################################

# Configuración
WORKSPACE="$HOME/WORKSPACE_NEUROBIT_V0.2"
API_PORT=5000
MCP_PORT=8090

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Contadores
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

################################################################################
# FUNCIONES
################################################################################

print_header() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  NEUROBIT SYSTEM CHECK — Verificación Rápida"
    echo -e "${BLUE}║${NC}  $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_item() {
    local name="$1"
    local check_cmd="$2"
    
    if eval "$check_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}[✓]${NC} $name"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}[✗]${NC} $name"
        ((CHECKS_FAILED++))
    fi
}

check_warning() {
    local name="$1"
    local check_cmd="$2"
    
    if eval "$check_cmd" > /dev/null 2>&1; then
        echo -e "${YELLOW}[!]${NC} $name"
        ((CHECKS_WARNING++))
    fi
}

print_section() {
    local title="$1"
    echo ""
    echo -e "${BLUE}━━━ $title ━━━${NC}"
}

print_footer() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  RESULTADOS"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    
    echo -e "${GREEN}✓ Verificaciones exitosas:${NC} $CHECKS_PASSED"
    
    if [ $CHECKS_FAILED -gt 0 ]; then
        echo -e "${RED}✗ Verificaciones fallidas:${NC} $CHECKS_FAILED"
    fi
    
    if [ $CHECKS_WARNING -gt 0 ]; then
        echo -e "${YELLOW}! Advertencias:${NC} $CHECKS_WARNING"
    fi
    
    echo ""
    
    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🟢 SISTEMA EN ESTADO VERDE${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}🔴 PROBLEMAS DETECTADOS${NC}"
        echo ""
        return 1
    fi
}

get_endpoint_status() {
    local url="$1"
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$http_code" = "200" ]; then
        return 0
    else
        return 1
    fi
}

################################################################################
# MAIN
################################################################################

print_header

# ============================================================================
# 1. DIRECTORIO Y PERMISOS
# ============================================================================

print_section "1. DIRECTORIO Y PERMISOS"

check_item "Workspace existe" "[ -d '$WORKSPACE' ]"
check_item "data/logs/ existe" "[ -d '$WORKSPACE/data/logs' ]"
check_item "data/logs/ es escribible" "[ -w '$WORKSPACE/data/logs' ]"
check_item "data/memoria_eva.jsonl existe" "[ -f '$WORKSPACE/data/memoria_eva.jsonl' ]"
check_item "iniciar.sh es ejecutable" "[ -x '$WORKSPACE/iniciar.sh' ]"

# ============================================================================
# 2. SERVICIOS CORRIENDO
# ============================================================================

print_section "2. SERVICIOS CORRIENDO"

check_item "API Flask (port $API_PORT) responde" "get_endpoint_status 'http://127.0.0.1:$API_PORT/health'"
check_item "MCP Server (port $MCP_PORT) disponible" "get_endpoint_status 'http://127.0.0.1:$MCP_PORT/health'"

# ============================================================================
# 3. ENDPOINTS PRINCIPALES
# ============================================================================

print_section "3. ENDPOINTS PRINCIPALES"

check_item "/analyze endpoint" "get_endpoint_status 'http://127.0.0.1:$API_PORT/analyze'"
check_item "/memoria endpoint" "get_endpoint_status 'http://127.0.0.1:$API_PORT/memoria'"
check_item "/centinela_status endpoint" "get_endpoint_status 'http://127.0.0.1:$API_PORT/centinela_status'"
check_item "/interface endpoint" "get_endpoint_status 'http://127.0.0.1:$API_PORT/interface/index.html'"

# ============================================================================
# 4. ARCHIVOS CRÍTICOS
# ============================================================================

print_section "4. ARCHIVOS CRÍTICOS"

check_item "neurobit_api.py existe" "[ -f '$WORKSPACE/neurobit_api.py' ]"
check_item "centinela_monitor.py existe" "[ -f '$WORKSPACE/core/centinela_monitor.py' ]"
check_item "core/__init__.py existe" "[ -f '$WORKSPACE/core/__init__.py' ]"
check_item "config/memoria_sagrada_eva.yaml existe" "[ -f '$WORKSPACE/config/memoria_sagrada_eva.yaml' ]"

# ============================================================================
# 5. EXTENSIONES
# ============================================================================

print_section "5. EXTENSIONES CHROME"

check_item "bitacora-eva/manifest.json" "[ -f '$WORKSPACE/extensions/bitacora-eva/manifest.json' ]"
check_item "fragment-sender-ack/manifest.json" "[ -f '$WORKSPACE/extensions/fragment-sender-ack/manifest.json' ]"
check_item "fragment-sender-simple/manifest.json" "[ -f '$WORKSPACE/extensions/fragment-sender-simple/manifest.json' ]"

# ============================================================================
# 6. INTERFACE WEB
# ============================================================================

print_section "6. INTERFACE WEB"

check_item "interface/index.html" "[ -f '$WORKSPACE/interface/index.html' ]"
check_item "interface/station.js" "[ -f '$WORKSPACE/interface/station.js' ]"
check_item "interface/matriz_ui.js" "[ -f '$WORKSPACE/interface/matriz_ui.js' ]"
check_item "interface/arquetipos.js" "[ -f '$WORKSPACE/interface/arquetipos.js' ]"

# ============================================================================
# 7. SINTAXIS PYTHON
# ============================================================================

print_section "7. SINTAXIS PYTHON"

check_item "neurobit_api.py sintaxis OK" "python3 -m py_compile '$WORKSPACE/neurobit_api.py' 2>/dev/null"
check_item "centinela_monitor.py sintaxis OK" "python3 -m py_compile '$WORKSPACE/core/centinela_monitor.py' 2>/dev/null"

# ============================================================================
# 8. MEMORIA Y DATOS
# ============================================================================

print_section "8. MEMORIA Y DATOS"

check_item "memoria_eva.jsonl es legible" "[ -r '$WORKSPACE/data/memoria_eva.jsonl' ]"

# Contar líneas de memoria
MEMORIA_LINES=$(wc -l < "$WORKSPACE/data/memoria_eva.jsonl" 2>/dev/null)
if [ -n "$MEMORIA_LINES" ] && [ "$MEMORIA_LINES" -gt 0 ]; then
    echo -e "${GREEN}[✓]${NC} memoria_eva.jsonl contiene registros ($MEMORIA_LINES líneas)"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}[!]${NC} memoria_eva.jsonl vacío o no accesible"
    ((CHECKS_WARNING++))
fi

# ============================================================================
# 9. LOGS
# ============================================================================

print_section "9. LOGS"

check_item "data/logs/ es escribible" "[ -w '$WORKSPACE/data/logs' ]"
check_item "conversation_history.jsonl legible" "[ -r '$WORKSPACE/data/logs/conversation_history.jsonl' ]"

# ============================================================================
# 10. HERRAMIENTAS
# ============================================================================

print_section "10. HERRAMIENTAS DISPONIBLES"

check_item "curl instalado" "command -v curl >/dev/null 2>&1"
check_item "python3 instalado" "command -v python3 >/dev/null 2>&1"
check_item "jq instalado (opcional)" "command -v jq >/dev/null 2>&1"

# ============================================================================
# RESULTADOS
# ============================================================================

print_footer
exit_code=$?

# ============================================================================
# RECOMENDACIONES
# ============================================================================

if [ $CHECKS_FAILED -gt 0 ]; then
    echo -e "${YELLOW}RECOMENDACIONES:${NC}"
    echo ""
    echo "1. Si falta API Flask:"
    echo "   cd ~/WORKSPACE_NEUROBIT_V0.2"
    echo "   ./iniciar.sh"
    echo ""
    echo "2. Si falla sintaxis Python:"
    echo "   python3 -m py_compile ~/WORKSPACE_NEUROBIT_V0.2/neurobit_api.py"
    echo ""
    echo "3. Si hay problemas de permisos:"
    echo "   chmod 755 ~/WORKSPACE_NEUROBIT_V0.2/data/logs"
    echo ""
fi

echo -e "${GRAY}Para verificación detallada, ver: docs/ESTADO_ACTUAL_MARZO2026.md${NC}"
echo ""

exit $exit_code
