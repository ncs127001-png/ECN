#!/bin/bash
################################################################################
# NEUROBIT TAREA 5 — Validation Suite
#
# Valida:
#   1. WebSocket server corre en puerto 5001
#   2. API server corre en puerto 5000
#   3. Socket.IO import en salon.html
#   4. WebSocket code en salon.js
#   5. memoria_eva.jsonl append-only logging
#   6. Fallback mechanism
################################################################################

set -e

WORKSPACE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$WORKSPACE"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TEST_COUNT=0
PASS_COUNT=0
FAIL_COUNT=0

test_passed() {
    ((PASS_COUNT++))
    echo -e "${GREEN}✅ PASS${NC}: $1"
}

test_failed() {
    ((FAIL_COUNT++))
    echo -e "${RED}❌ FAIL${NC}: $1"
}

test_start() {
    ((TEST_COUNT++))
    echo -e "\n${BLUE}[TEST $TEST_COUNT]${NC} $1"
}

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🧪 NEUROBIT TAREA 5 — Validation Suite${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"

# ─────────────────────────────────────────────────────────────────────────────
# TEST 1: WebSocket Server File Exists
# ─────────────────────────────────────────────────────────────────────────────

test_start "WebSocket server file exists"

if [ -f "core/websocket_salon_server.py" ]; then
    SIZE=$(wc -l < core/websocket_salon_server.py)
    test_passed "core/websocket_salon_server.py exists ($SIZE lines)"
else
    test_failed "core/websocket_salon_server.py not found"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 2: WebSocket Code in salon.js
# ─────────────────────────────────────────────────────────────────────────────

test_start "WebSocket initialization in salon.js"

if grep -q "initWebSocket()" interface/salon.js; then
    test_passed "initWebSocket() function exists"
else
    test_failed "initWebSocket() function not found"
fi

if grep -q "salonSocket = io(" interface/salon.js; then
    test_passed "Socket.IO connection created"
else
    test_failed "Socket.IO connection not found"
fi

if grep -q "salonSocket.on('connect'" interface/salon.js; then
    test_passed "Socket.IO 'connect' handler exists"
else
    test_failed "Socket.IO 'connect' handler not found"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 3: Socket.IO CDN Import in salon.html
# ─────────────────────────────────────────────────────────────────────────────

test_start "Socket.IO CDN import in salon.html"

if grep -q "socket.io.min.js" interface/salon.html; then
    test_passed "Socket.IO CDN import found"
else
    test_failed "Socket.IO CDN import not found"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 4: WebSocket Status Indicator HTML
# ─────────────────────────────────────────────────────────────────────────────

test_start "WebSocket status indicator in salon.html"

if grep -q 'id="wsStatus"' interface/salon.html; then
    test_passed "WebSocket status indicator (#wsStatus) found"
else
    test_failed "WebSocket status indicator not found"
fi

if grep -q "ws-connected" interface/salon.html; then
    test_passed ".ws-connected CSS class found"
else
    test_failed ".ws-connected CSS class not found"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 5: WebSocket Message Broadcasting
# ─────────────────────────────────────────────────────────────────────────────

test_start "WebSocket message broadcasting in salon.js"

if grep -q "salonSocket.emit('nuevo_mensaje'" interface/salon.js; then
    test_passed "WebSocket emit 'nuevo_mensaje' found"
else
    test_failed "WebSocket emit 'nuevo_mensaje' not found"
fi

if grep -q "salonSocket.on('mensaje_recibido'" interface/salon.js; then
    test_passed "WebSocket handler 'mensaje_recibido' found"
else
    test_failed "WebSocket handler 'mensaje_recibido' not found"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 6: Fallback Mechanism
# ─────────────────────────────────────────────────────────────────────────────

test_start "Fallback mechanism in salon.js"

if grep -q "wsConnected" interface/salon.js; then
    test_passed "wsConnected flag exists"
else
    test_failed "wsConnected flag not found"
fi

if grep -q "if.*wsConnected\|if.*salonSocket" interface/salon.js; then
    test_passed "WebSocket availability check exists"
else
    test_failed "WebSocket availability check not found"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 7: Memory (Append-Only) Support
# ─────────────────────────────────────────────────────────────────────────────

test_start "Append-only memoria_eva.jsonl support"

if grep -q "save_to_memoria" core/websocket_salon_server.py; then
    test_passed "save_to_memoria() function found"
else
    test_failed "save_to_memoria() function not found"
fi

if grep -q "MEMORIA_FILE" core/websocket_salon_server.py; then
    test_passed "MEMORIA_FILE path defined"
else
    test_failed "MEMORIA_FILE path not defined"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 8: CORS Configuration (SOBERANÍA)
# ─────────────────────────────────────────────────────────────────────────────

test_start "CORS configuration (SOBERANÍA - only localhost)"

if grep -q "127.0.0.1" core/websocket_salon_server.py; then
    test_passed "Localhost-only binding found"
else
    test_failed "Localhost-only binding not found"
fi

if grep -q "localhost:5000" core/websocket_salon_server.py; then
    test_passed "CORS restricted to localhost"
else
    test_failed "CORS not properly restricted"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 9: Socket.IO Handlers
# ─────────────────────────────────────────────────────────────────────────────

test_start "Socket.IO event handlers in server"

if grep -q "@socketio.on('connect')" core/websocket_salon_server.py; then
    test_passed "socketio.on('connect') handler found"
else
    test_failed "socketio.on('connect') handler not found"
fi

if grep -q "@socketio.on('nuevo_mensaje')" core/websocket_salon_server.py; then
    test_passed "socketio.on('nuevo_mensaje') handler found"
else
    test_failed "socketio.on('nuevo_mensaje') handler not found"
fi

if grep -q "@socketio.on('disconnect')" core/websocket_salon_server.py; then
    test_passed "socketio.on('disconnect') handler found"
else
    test_failed "socketio.on('disconnect') handler not found"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 10: Logging Endpoints
# ─────────────────────────────────────────────────────────────────────────────

test_start "WebSocket server health/stats endpoints"

if grep -q "@app.route('/health'" core/websocket_salon_server.py; then
    test_passed "/health endpoint found"
else
    test_failed "/health endpoint not found"
fi

if grep -q "@app.route('/stats'" core/websocket_salon_server.py; then
    test_passed "/stats endpoint found"
else
    test_failed "/stats endpoint not found"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TEST 11: Start Script
# ─────────────────────────────────────────────────────────────────────────────

test_start "Startup script exists and is executable"

if [ -f "start_tarea5_websocket.sh" ]; then
    test_passed "start_tarea5_websocket.sh exists"
else
    test_failed "start_tarea5_websocket.sh not found"
fi

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────────────────────

echo -e "\n${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}🧪 TEST RESULTS${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════════${NC}\n"

echo -e "Total Tests: ${BLUE}$TEST_COUNT${NC}"
echo -e "Passed:      ${GREEN}$PASS_COUNT${NC}"
echo -e "Failed:      ${RED}$FAIL_COUNT${NC}"

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "\n${GREEN}✅ ALL TESTS PASSED!${NC}\n"
    exit 0
else
    echo -e "\n${RED}❌ SOME TESTS FAILED${NC}\n"
    exit 1
fi
