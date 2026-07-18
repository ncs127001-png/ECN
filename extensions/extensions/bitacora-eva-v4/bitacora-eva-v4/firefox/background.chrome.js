chrome.runtime.onInstalled.addListener(() => {
  console.log("Bitácora EVA instalada.");
});
// background.js - gestor simple de bitácora
chrome.runtime.onInstalled.addListener(() => {
  console.log('[EVA background] installed');
});

// escucha mensajes de content.js
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if(msg && msg.type === 'EVA_SAVE_REPLY' && msg.entry){
    chrome.storage.local.get({ bitacora: [] }, (res) => {
      const arr = res.bitacora || [];
      arr.push(msg.entry);
      chrome.storage.local.set({ bitacora: arr }, () => {
        console.log('[EVA background] entry saved. total=', arr.length);
        sendResponse({ ok: true, total: arr.length });
      });
    });
    // keep message channel open for async response
    return true;
  }
});

// =====================================
// CAMBIO 5: Socket.IO Listener (ACTUALIZADO para FASE 2.2)
// =====================================
// Nota: Socket.IO debe estar disponible globalmente o via importScripts

let socket = null;
let socketRetryCount = 0;
const SOCKET_MAX_RETRIES = 10;
const SOCKET_RETRY_DELAY = 3000;

function connectSocketIO() {
  if (socket && socket.connected) {
    return;
  }

  console.log('[EVA background] Intentando conectar Socket.IO a 127.0.0.1:5001 (intento ' + (socketRetryCount + 1) + ')');
  
  // Socket.IO via protocolo http (upgradable a ws)
  // Nota: Si socket.io.js no está disponible, fallback a WebSocket
  if (typeof io === 'undefined') {
    console.log('[EVA background] Socket.IO no disponible, usando WebSocket fallback');
    connectWebSocketFallback();
    return;
  }

  try {
    socket = io('http://127.0.0.1:5001', {
      reconnection: true,
      reconnectionDelay: SOCKET_RETRY_DELAY,
      reconnectionAttempts: SOCKET_MAX_RETRIES,
      transports: ['websocket', 'polling']
    });

    socket.on('connect', () => {
      console.log('[EVA background] ✅ Socket.IO conectado a http://127.0.0.1:5001');
      socketRetryCount = 0;
    });

    socket.on('agent_registered', (data) => {
      console.log('[EVA background] 🎯 agent_registered recibido:', data);
      
      const { tabId, platform, name, url, agent_id } = data;
      
      if (tabId && platform === 'teamviewer_extension') {
        // Forward a content.js para inyección
        chrome.tabs.sendMessage(tabId, {
          type: 'INJECT_AGENT_METADATA',
          agent: {
            id: agent_id,
            name: name,
            platform: platform,
            url: url,
            tabId: tabId,
            injected_at: new Date().toISOString()
          }
        }, (response) => {
          if (chrome.runtime.lastError) {
            console.log('[EVA background] ⚠️ Tab no disponible:', tabId);
          } else {
            console.log('[EVA background] ✅ Inyección enviada a tab', tabId);
          }
        });
      }
    });

    socket.on('disconnect', () => {
      console.log('[EVA background] ⏸️ Socket.IO desconectado. Auto-reconectando...');
    });

    socket.on('connect_error', (error) => {
      console.log('[EVA background] ❌ Socket.IO connection error:', error.message);
    });

  } catch (err) {
    console.log('[EVA background] ❌ Error al crear Socket.IO:', err.message);
    if (socketRetryCount < SOCKET_MAX_RETRIES) {
      socketRetryCount++;
      setTimeout(connectSocketIO, SOCKET_RETRY_DELAY);
    }
  }
}

// Fallback: usar WebSocket raw si Socket.IO no está disponible
let ws = null;

function connectWebSocketFallback() {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return;
  }

  console.log('[EVA background] Usando WebSocket fallback (127.0.0.1:5001)');
  
  ws = new WebSocket('ws://127.0.0.1:5001');

  ws.onopen = () => {
    console.log('[EVA background] ✅ WebSocket fallback conectado');
  };

  ws.onmessage = (event) => {
    try {
      const message = JSON.parse(event.data);
      
      if (message.type === 'agent_registered') {
        console.log('[EVA background] 🎯 agent_registered (fallback):', message);
        
        const { tabId, platform, name, url, agent_id } = message;
        
        if (tabId && platform === 'teamviewer_extension') {
          chrome.tabs.sendMessage(tabId, {
            type: 'INJECT_AGENT_METADATA',
            agent: {
              id: agent_id,
              name: name,
              platform: platform,
              url: url,
              tabId: tabId
            }
          }, (response) => {
            if (chrome.runtime.lastError) {
              console.log('[EVA background] ⚠️ Tab no disponible (fallback):', tabId);
            } else {
              console.log('[EVA background] ✅ Inyección enviada (fallback):', tabId);
            }
          });
        }
      }
    } catch (e) {
      console.error('[EVA background] Error parsing WebSocket message:', e);
    }
  };

  ws.onerror = (error) => {
    console.log('[EVA background] ❌ WebSocket fallback error:', error);
  };

  ws.onclose = () => {
    console.log('[EVA background] ⏸️ WebSocket fallback desconectado. Reintentando...');
    setTimeout(connectWebSocketFallback, 3000);
  };
}

// Conectar al iniciar extensión (Socket.IO con fallback a WebSocket)
connectSocketIO();

// Reconectar periódicamente
chrome.alarms.create('reconnect_socketio', { periodInMinutes: 1 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'reconnect_socketio') {
    if (!socket || !socket.connected) {
      console.log('[EVA background] Alarm: Reconectando Socket.IO');
      connectSocketIO();
    }
  }
});

console.log('[EVA background] ✅ background.js cargado');
