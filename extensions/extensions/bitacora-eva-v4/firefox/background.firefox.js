/**
 * background.firefox.js — Wrapper para compatibilidad Chrome/Firefox
 * Usa namespace 'browser' en Firefox, 'chrome' en Chrome
 * 
 * CAMBIO 5 (Firefox Edition): WebSocket listener + auto-reconnect + content.js bridge
 */

// Seleccionar namespace correcto (Firefox = browser, Chrome = chrome)
const API = typeof browser !== 'undefined' ? browser : chrome;

// =====================================
// UTILIDADES
// =====================================

function log(message, data = null) {
  const timestamp = new Date().toISOString();
  if (data) {
    console.log(`[EVA background ${timestamp}] ${message}`, data);
  } else {
    console.log(`[EVA background ${timestamp}] ${message}`);
  }
}

// =====================================
// EVENTOS DE INSTALACIÓN
// =====================================

API.runtime.onInstalled.addListener(() => {
  log('Firefox complemento instalado');
  
  // Guardar metadatos de instalación
  API.storage.local.set({
    installed_at: new Date().toISOString(),
    platform: 'firefox',
    version: '3.0'
  });
});

// =====================================
// MESSAGE LISTENER (Storage + Bitácora)
// =====================================

API.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (!msg || !msg.type) {
    return;
  }
  
  // EVA_SAVE_REPLY: Guardar entrada en bitácora
  if (msg.type === 'EVA_SAVE_REPLY' && msg.entry) {
    API.storage.local.get({ bitacora: [] }, (res) => {
      const arr = res.bitacora || [];
      arr.push({
        ...msg.entry,
        saved_at: new Date().toISOString(),
        browser: 'firefox'
      });
      
      API.storage.local.set({ bitacora: arr }, () => {
        log('Entrada guardada en bitácora', { total: arr.length });
        sendResponse({ ok: true, total: arr.length });
      });
    });
    return true; // Indica que sendResponse será llamado asincronamente
  }
  
  // EVA_GET_BITACORA: Recuperar bitácora
  if (msg.type === 'EVA_GET_BITACORA') {
    API.storage.local.get({ bitacora: [] }, (res) => {
      sendResponse({ bitacora: res.bitacora || [] });
    });
    return true;
  }
  
  // INJECT_AGENT_METADATA: Mensaje desde WebSocket listener (ver abajo)
  if (msg.type === 'INJECT_AGENT_METADATA' && msg.agent) {
    log('Recibido INJECT_AGENT_METADATA', msg.agent);
    
    // Forward a content.js de la tab correspondiente
    if (sender.tab && sender.tab.id) {
      API.tabs.sendMessage(sender.tab.id, {
        type: 'AGENT_METADATA_INJECTED',
        agent: msg.agent
      }).catch((err) => {
        log('Error al enviar a content.js', err.message);
      });
    }
    
    sendResponse({ ok: true, agent_id: msg.agent.id });
    return true;
  }
});

// =====================================
// WEBSOCKET LISTENER (CAMBIO 5 - Firefox Edition)
// =====================================

let ws = null;
let wsRetryCount = 0;
const WS_MAX_RETRIES = 10;
const WS_RETRY_DELAY = 3000; // 3 segundos

function connectWebSocket() {
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    log('WebSocket ya conectado o conectando');
    return;
  }

  log('Intentando conectar a ws://127.0.0.1:5001 (intento ' + (wsRetryCount + 1) + ')');
  
  try {
    ws = new WebSocket('ws://127.0.0.1:5001');

    ws.onopen = () => {
      log('✅ WebSocket conectado a ws://127.0.0.1:5001');
      wsRetryCount = 0;
      
      // Enviar ping periódico para mantener viva la conexión
      setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000); // Cada 30 segundos
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        log('Mensaje WebSocket recibido', message);
        
        if (message.type === 'agent_registered') {
          log('🎯 agent_registered detectado', message);
          
          const { tabId, platform, name, url, agent_id } = message;
          
          if (tabId && platform === 'teamviewer_extension') {
            // Forward a content.js para inyección
            API.tabs.sendMessage(tabId, {
              type: 'INJECT_AGENT_METADATA',
              agent: {
                id: agent_id,
                name: name,
                platform: platform,
                url: url,
                tabId: tabId,
                injected_at: new Date().toISOString()
              }
            }).then(() => {
              log('✅ Inyección enviada a tab', { tabId: tabId });
            }).catch((err) => {
              log('⚠️ Tab no disponible o no listo', { tabId: tabId, error: err.message });
            });
          }
        }
      } catch (e) {
        log('❌ Error al parsear mensaje WebSocket', e.message);
      }
    };

    ws.onerror = (error) => {
      log('❌ WebSocket error', error.message || error);
    };

    ws.onclose = () => {
      log('⏸️ WebSocket desconectado. Reintentando en ' + WS_RETRY_DELAY + 'ms...');
      
      if (wsRetryCount < WS_MAX_RETRIES) {
        wsRetryCount++;
        setTimeout(connectWebSocket, WS_RETRY_DELAY);
      } else {
        log('❌ WebSocket: máximo número de reintentos alcanzado (' + WS_MAX_RETRIES + ')');
      }
    };

  } catch (err) {
    log('❌ Error al crear WebSocket', err.message);
    if (wsRetryCount < WS_MAX_RETRIES) {
      wsRetryCount++;
      setTimeout(connectWebSocket, WS_RETRY_DELAY);
    }
  }
}

// Conectar WebSocket al iniciar la extensión
connectWebSocket();

// Reconectar si la extensión detecta cambios en el estado de la conexión
API.alarms.create('reconnect_ws', { periodInMinutes: 1 });

API.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'reconnect_ws') {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      log('Alarm: Reconectando WebSocket');
      connectWebSocket();
    }
  }
});

log('✅ background.firefox.js cargado y listo');
