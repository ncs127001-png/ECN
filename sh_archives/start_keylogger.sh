#!/bin/bash

###############################################################################
# start_keylogger.sh — Inicia el daemon Keylogger con integración dispatcher
# Autor: NODO_SEMILLA
# Fecha: 23 de mayo de 2026
# Propósito: Script de inicio para el Keylogger de la Estación Central
###############################################################################

set -e

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

WORKSPACE="${HOME}/WORKSPACE_NEUROBIT_V0.2"
KEYLOGGER_SCRIPT="${WORKSPACE}/modules/neurobit_hid_daemon/neurobit_keylogger.py"
LOG_DIR="${WORKSPACE}/data/logs"
DISPATCHER_URL="http://127.0.0.1:5000/dispatch/queue"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCIONES
# ============================================================================

log_info() {
    echo -e "${BLUE}[ℹ️  INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✅ OK]${NC} $1"
}

log_error() {
    echo -e "${RED}[❌ ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠️  WARN]${NC} $1"
}

# ============================================================================
# VALIDACIONES PREVIAS
# ============================================================================

echo ""
echo "========================================================================"
echo "🔑 NEUROBIT KEYLOGGER — Inicializando daemon"
echo "========================================================================"
echo ""

# 1. Verificar que el workspace existe
if [ ! -d "$WORKSPACE" ]; then
    log_error "Workspace no encontrado: $WORKSPACE"
    exit 1
fi

log_info "Workspace: $WORKSPACE"

# 2. Verificar que el script keylogger existe
if [ ! -f "$KEYLOGGER_SCRIPT" ]; then
    log_error "Script keylogger no encontrado en: $KEYLOGGER_SCRIPT"
    exit 1
fi

log_success "Script encontrado: $KEYLOGGER_SCRIPT"

# 3. Verificar y crear directorio de logs
mkdir -p "$LOG_DIR"
if [ ! -w "$LOG_DIR" ]; then
    log_error "Directorio de logs NO tiene permisos de escritura: $LOG_DIR"
    exit 1
fi

log_success "Directorio de logs: $LOG_DIR"

# 4. Verificar que el API dispatcher está corriendo
log_info "Verificando API dispatcher..."
if ! curl -s "$DISPATCHER_URL" -X OPTIONS > /dev/null 2>&1; then
    log_warning "API dispatcher no responde en $DISPATCHER_URL"
    log_warning "El keylogger usará fallback a archivo local (memoria_eva.jsonl)"
    echo ""
else
    log_success "API dispatcher accesible en $DISPATCHER_URL"
fi

# 5. Verificar permisos de /dev/input
log_info "Verificando permisos de /dev/input..."

if [ ! -e /dev/input/event0 ] 2>/dev/null; then
    log_warning "No se encontraron dispositivos /dev/input/event* en el sistema"
    log_warning "El keylogger operará en modo simulación (testing)"
    echo ""
else
    # Verificar si puede leer al menos un dispositivo
    if ! [ -r /dev/input/event0 ] 2>/dev/null; then
        log_warning "No hay acceso a /dev/input/event0 (permisos insuficientes)"
        log_warning "Opciones:"
        echo "   1. Agregar usuario a grupo 'input':"
        echo "      $ sudo usermod -a -G input \$USER"
        echo "      $ newgrp input"
        echo ""
        echo "   2. O ejecutar con permisos elevados (no recomendado):"
        echo "      $ sudo bash start_keylogger.sh"
        echo ""
    else
        log_success "Acceso a dispositivos HID disponible"
    fi
fi

# ============================================================================
# INICIAR DAEMON
# ============================================================================

log_info "Iniciando keylogger daemon..."
echo ""
# Después de las validaciones, antes de ejecutar:
cd "$WORKSPACE" || exit 1

# Ejecutar con ruta absoluta
nohup python3 "$KEYLOGGER_SCRIPT" > "$LOG_DIR/keylogger_daemon.log" 2>&1 &
# Cambiar a workspace

# CODIGO ANTERIOR
'''cd "$WORKSPACE"

# Opción A: Correr en foreground (para debugging interactivo)
# python3 "$KEYLOGGER_SCRIPT"

# Opción B: Correr en background con nohup (recomendado)
log_info "Ejecutando: python3 $KEYLOGGER_SCRIPT"
log_info "Logs se guardarán en: $LOG_DIR/keylogger_daemon.log"
echo ""

nohup python3 "$KEYLOGGER_SCRIPT" > "$LOG_DIR/keylogger_daemon.log" 2>&1 &
'''

KEYLOGGER_PID=$!

# Guardar PID para posterior control
echo $KEYLOGGER_PID > /tmp/neurobit_keylogger.pid

# Esperar un momento para verificar que no crasheó inmediatamente
sleep 2

if ! ps -p $KEYLOGGER_PID > /dev/null 2>&1; then
    log_error "Keylogger NO se inició correctamente (PID: $KEYLOGGER_PID)"
    echo ""
    log_info "Últimas líneas del log:"
    tail -10 "$LOG_DIR/keylogger_daemon.log"
    exit 1
fi

# ============================================================================
# CONFIRMACIÓN
# ============================================================================

log_success "Keylogger iniciado correctamente"
echo ""
echo "========================================================================"
echo "📊 INFORMACIÓN DEL DAEMON"
echo "========================================================================"
echo ""
echo "  PID:                $KEYLOGGER_PID"
echo "  Log daemon:         $LOG_DIR/keylogger_daemon.log"
echo "  Log principal:      $LOG_DIR/keylog_main.jsonl"
echo "  Dispatcher:         $DISPATCHER_URL"
echo ""
echo "========================================================================"
echo "🎮 COMANDOS ÚTILES"
echo "========================================================================"
echo ""
echo "  Ver logs en vivo:"
echo "    $ tail -f $LOG_DIR/keylogger_daemon.log"
echo ""
echo "  Ver evento capturados:"
echo "    $ tail -20 $LOG_DIR/keylog_main.jsonl"
echo ""
echo "  Ver status del dispatcher:"
echo "    $ curl -s http://127.0.0.1:5000/dispatch/status | jq"
echo ""
echo "  Detener keylogger:"
echo "    $ pkill -f 'python3.*neurobit_keylogger'"
echo "    O: $ kill $KEYLOGGER_PID"
echo ""
echo "  Ver proceso corriendo:"
echo "    $ ps aux | grep keylogger | grep -v grep"
echo ""
echo "========================================================================"
echo ""

exit 0
