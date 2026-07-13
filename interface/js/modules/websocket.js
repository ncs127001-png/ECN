/**
 * NEUROBIT WebSocket Module
 * Módulo independiente para conexión WebSocket
 */

let salonSocket = null;
let wsConnected = false;

export function initWebSocket() {
  if (typeof io === 'undefined') {
    console.error('❌ [WebSocket] Socket.IO no cargado');
    return false;
  }
  
  try {
    salonSocket = io('http://127.0.0.1:5001', {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
      transports: ['websocket', 'polling']
    });
    
    salonSocket.on('connect', () => {
      wsConnected = true;
      console.log('✅ [WebSocket] Conectado');
      updateWebSocketStatus(true);
    });
    
    salonSocket.on('disconnect', () => {
      wsConnected = false;
      console.log('⚠️ [WebSocket] Desconectado');
      updateWebSocketStatus(false);
    });
    
    return true;
  } catch (err) {
    console.error('❌ [WebSocket] Error:', err);
    return false;
  }
}

export function updateWebSocketStatus(connected) {
  const status = document.getElementById('wsStatus');
  if (status) {
    status.textContent = connected ? 'WebSocket: EN LÍNEA' : 'WebSocket: DESCONECTADO';
    status.className = connected ? 'ws-connected' : 'ws-disconnected';
  }
}

export function emitMessage(data) {
  if (salonSocket && wsConnected) {
    salonSocket.emit('nuevo_mensaje', data);
  }
}
