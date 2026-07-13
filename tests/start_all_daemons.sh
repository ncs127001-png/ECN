#!/bin/bash

###############################################################################
# start_all_daemons.sh — Inicia TODOS los daemons de NEUROBIT V0.2
###############################################################################

set -e

WORKSPACE="$HOME/WORKSPACE_NEUROBIT_V0.2"
SCRIPTS_DIR="$WORKSPACE/scripts"
LOG_DIR="$WORKSPACE/data/logs"

# Crear directorio de logs
mkdir -p "$LOG_DIR"

echo "========================================================================="
echo "🚀 NEUROBIT V0.2 — Iniciando TODOS los daemons"
echo "========================================================================="
echo ""

# Banner de requerimientos
echo "📋 Requerimientos:"
echo "   • Grupo 'input' para Keylogger (para /dev/input/event*)"
echo "   • Python 3.10+ con requests"
echo "   • API corriendo en 127.0.0.1:5000 (ver neurobit_api.py)"
echo ""

# Verificar API corriendo
echo "1️⃣  Verificando API dispatcher..."
if curl -s http://127.0.0.1:5000/dispatch/status > /dev/null 2>&1; then
    echo "   ✅ API respondiendo en 127.0.0.1:5000"
else
    echo "   ⚠️  WARNING: API no responde (iniciar con: python3 neurobit_api.py)"
    echo "      Los daemons usarán fallback a archivo local"
fi
echo ""

# 1. Keylogger
echo "2️⃣  Iniciando Keylogger (captura de teclado HID)..."
if [ -f "$WORKSPACE/modules/neurobit_hid_daemon/neurobit_keylogger.py" ]; then
    cd "$WORKSPACE"
    nohup python3 modules/neurobit_hid_daemon/neurobit_keylogger.py > "$LOG_DIR/keylogger_daemon.log" 2>&1 &
    KEYLOGGER_PID=$!
    echo "   ✅ Keylogger iniciado (PID: $KEYLOGGER_PID)"
else
    echo "   ❌ Keylogger script no encontrado"
fi
echo ""

# 2. Postman
echo "3️⃣  Iniciando Postman (Cartero Consciente, ciclo 8 horas)..."
if [ -f "$WORKSPACE/modules/neurobit_postman_daemon.py" ]; then
    cd "$WORKSPACE"
    nohup python3 modules/neurobit_postman_daemon.py > "$LOG_DIR/postman_daemon.log" 2>&1 &
    POSTMAN_PID=$!
    echo "   ✅ Postman iniciado (PID: $POSTMAN_PID)"
else
    echo "   ❌ Postman script no encontrado"
fi
echo ""

# 3. Centinela (si existe)
echo "4️⃣  Verificando Centinela (monitor de clipboard)..."
if [ -f "$WORKSPACE/modules/centinela_monitor.py" ]; then
    cd "$WORKSPACE"
    nohup python3 modules/centinela_monitor.py > "$LOG_DIR/centinela_daemon.log" 2>&1 &
    CENTINELA_PID=$!
    echo "   ✅ Centinela iniciado (PID: $CENTINELA_PID)"
elif [ -f "$WORKSPACE/modules/centinela.py" ]; then
    cd "$WORKSPACE"
    nohup python3 modules/centinela.py > "$LOG_DIR/centinela_daemon.log" 2>&1 &
    CENTINELA_PID=$!
    echo "   ✅ Centinela (v1) iniciado (PID: $CENTINELA_PID)"
else
    echo "   ℹ️  Centinela no encontrado (opcional)"
fi
echo ""

# Status final
echo "========================================================================="
echo "✅ TODOS LOS DAEMONS INICIADOS"
echo "========================================================================="
echo ""

echo "📊 Estado actual:"
echo "   Keylogger:  $(ps aux | grep -c 'python3.*keylogger' || echo '0') procesos"
echo "   Postman:    $(ps aux | grep -c 'python3.*postman' || echo '0') procesos"
echo "   Centinela:  $(ps aux | grep -c 'python3.*centinela' || echo '0') procesos"
echo ""

echo "📝 Ubicación de logs:"
echo "   Keylogger:   $LOG_DIR/keylogger_daemon.log"
echo "   Postman:     $LOG_DIR/postman_daemon.log"
echo "   Centinela:   $LOG_DIR/centinela_daemon.log"
echo ""

echo "🔍 Comandos de monitoreo:"
echo "   Estado dispatcher:  curl http://127.0.0.1:5000/dispatch/status | jq"
echo "   Ver todos los logs: tail -f $LOG_DIR/*.log"
echo "   Procesos activos:   ps aux | grep -E 'keylogger|postman|centinela' | grep -v grep"
echo ""

echo "🛑 Detener todos los daemons:"
echo "   pkill -f 'python3.*(keylogger|postman|centinela)'"
echo ""

echo "⚡ Modo de prueba rápido (10 segundos):"
echo "   1. Espera 10 segundos"
echo "   2. Verifica: curl http://127.0.0.1:5000/dispatch/status | jq"
echo "   3. Detén:    pkill -f 'python3.*keylogger'"
echo ""

# Esperar un poco para que los daemons arranquen
sleep 2

# Mostrar PID finales
echo "🎯 PIDs iniciales (pueden cambiar si usan systemd/cron después):"
ps aux | grep -E 'python3.*(keylogger|postman|centinela)' | grep -v grep || echo "   (Procesos en background)"

echo ""
echo "✨ Daemons de NEUROBIT V0.2 operativos en 127.0.0.1 (SOBERANÍA TOTAL)"
