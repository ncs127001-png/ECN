#!/bin/bash

###############################################################################
# start_postman.sh — Inicia el daemon Postman con integración dispatcher
###############################################################################

set -e

WORKSPACE="$HOME/WORKSPACE_NEUROBIT_V0.2"
POSTMAN_SCRIPT="$WORKSPACE/modules/neurobit_postman_daemon.py"
LOG_DIR="$WORKSPACE/data/logs"
DISPATCHER_URL="http://127.0.0.1:5000/dispatch/queue"

echo "🚀 NEUROBIT POSTMAN — Iniciando daemon del Cartero..."
echo ""

# 1. Verificar que el API está corriendo
echo "📡 Verificando API dispatcher..."
if ! curl -s "$DISPATCHER_URL" -X OPTIONS > /dev/null 2>&1; then
    echo "⚠️  WARNING: API dispatcher no responde en $DISPATCHER_URL"
    echo "   El Postman usará fallback a archivo local"
    echo ""
fi

# 2. Verificar que el archivo existe
if [ ! -f "$POSTMAN_SCRIPT" ]; then
    echo "❌ ERROR: Postman script no encontrado en $POSTMAN_SCRIPT"
    exit 1
fi

# 3. Crear directorio de logs
mkdir -p "$LOG_DIR"
mkdir -p "$WORKSPACE/data/bbs/informes"
mkdir -p "$WORKSPACE/data/bbs/arquitectura"
mkdir -p "$WORKSPACE/data/sala/estado"

# 4. Iniciar el daemon
cd "$WORKSPACE"
echo "▶️  Iniciando: python3 $POSTMAN_SCRIPT"
echo "   Dispatcher: $DISPATCHER_URL"
echo "   Ciclo: Cada 8 horas (Recolectar → Clasificar → Entregar)"
echo "   Logs: $LOG_DIR/postman_daemon.log"
echo ""

# Opción A: Correr en foreground (para debugging)
# python3 "$POSTMAN_SCRIPT"

# Opción B: Correr en background con nohup
nohup python3 "$POSTMAN_SCRIPT" > "$LOG_DIR/postman_daemon.log" 2>&1 &
POSTMAN_PID=$!

echo "✅ Postman iniciado (PID: $POSTMAN_PID)"
echo ""
echo "📊 Comandos útiles:"
echo "   - Ver logs:        tail -f $LOG_DIR/postman_daemon.log"
echo "   - Ver checkpoint:  grep 'checkpoint' $LOG_DIR/postman_daemon.log"
echo "   - Ver estado dispatcher:"
echo "     curl http://127.0.0.1:5000/dispatch/status | jq"
echo "   - Detener:         pkill -f 'python3.*neurobit_postman'"
echo ""
echo "🛑 Para detener: pkill -f neurobit_postman"
echo ""
echo "📝 Nota: El Cartero pasa cada 8 horas."
echo "   Para ciclo inmediato en modo debug, ejecutar:"
echo "   python3 $POSTMAN_SCRIPT"
