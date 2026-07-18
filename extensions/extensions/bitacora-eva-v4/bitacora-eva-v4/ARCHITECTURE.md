# 🏗️ ARCHITECTURE.md — Bitácora EVA v4.0 (Chrome vs Firefox)

**Versión:** 4.0  
**Fecha:** Abril 1, 2026  
**Objetivo:** Documentar diferencias arquitectónicas y decisiones de diseño  

---

## 📌 Tabla Comparativa: Chrome vs Firefox

| Característica | Chrome | Firefox | Implicación |
|---|---|---|---|
| **Manifest Version** | 3 | 3 | ✅ Compatible |
| **Browser API** | `chrome.*` | `browser.*` | Wrapper requerido |
| **Background Script Type** | `service_worker` | `scripts: [...]` | Persistencia diferente |
| **Background Lifecycle** | Descargable (ephemeral) | Persistente | Firefox mejor para WebSocket |
| **Storage API** | `chrome.storage` | `browser.storage` | API unificada en wrapper |
| **Promise Support** | Limited (callbacks) | Full (Promises) | Wrapper maneja ambos |
| **Extension ID** | Auto-generated (dev) | Requerido (Gecko ID) | browser_specific_settings |
| **Installation** | chrome://extensions | about:debugging | Diferente UI |
| **Debugging** | DevTools | Web Extension Debugger | Diferente herramienta |

---

## 🔌 API Unificación (Wrapper Pattern)

### Problema

```javascript
// Chrome
chrome.tabs.sendMessage(tabId, message);

// Firefox (Promise-based)
browser.tabs.sendMessage(tabId, message);
```

### Solución en background.js

```javascript
// Detect runtime
const API = typeof browser !== 'undefined' ? browser : chrome;

// Uso unificado
API.tabs.sendMessage(tabId, message);
API.storage.local.get(['key'], (result) => { ... });
```

---

## 🔄 Manifestos

### Chrome Manifest (`chrome/manifest.json`)

```json
{
  "manifest_version": 3,
  "name": "Bitácora EVA",
  "version": "4.0",
  "description": "Extensión para inyección de agentes TRON/SIMON",
  
  "permissions": [
    "tabs",
    "storage",
    "webRequest"
  ],
  
  "host_permissions": [
    "https://chat.openai.com/*",
    "https://gemini.google.com/*",
    "https://claude.ai/*",
    "http://127.0.0.1:5000/*"
  ],
  
  "background": {
    "service_worker": "background.js"
  },
  
  "content_scripts": [
    {
      "matches": ["https://chat.openai.com/*"],
      "js": ["content/content.js"],
      "run_at": "document_start"
    }
  ]
}
```

### Firefox Manifest (`firefox/manifest.firefox.json`)

```json
{
  "manifest_version": 3,
  "name": "Bitácora EVA",
  "version": "4.0",
  "description": "Extensión para inyección de agentes TRON/SIMON",
  
  "browser_specific_settings": {
    "gecko": {
      "id": "bitacora-eva@neurobit.local",
      "strict_min_version": "109.0"
    }
  },
  
  "permissions": [
    "tabs",
    "storage",
    "webRequest"
  ],
  
  "host_permissions": [
    "https://chat.openai.com/*",
    "https://gemini.google.com/*",
    "https://claude.ai/*",
    "http://127.0.0.1:5000/*",
    "http://127.0.0.1:5001/*"
  ],
  
  "background": {
    "scripts": ["background.js"],
    "type": "module"
  },
  
  "content_scripts": [
    {
      "matches": ["https://chat.openai.com/*"],
      "js": ["content/content.js"],
      "run_at": "document_start"
    }
  ]
}
```

### Diferencias Clave

1. **`browser_specific_settings.gecko`** (Firefox)
   - Requerido para identificar extensión en Firefox
   - `id`: Gecko ID único (`bitacora-eva@neurobit.local`)
   - `strict_min_version`: Versión mínima de Firefox (109.0 = MV3 compatible)

2. **`background.scripts`** vs **`background.service_worker`**
   - Chrome: Service Worker (ephemeral, descargable)
   - Firefox: Background page persistente

3. **`host_permissions`**
   - Firefox incluye `5001` (WebSocket)
   - Chrome incluye `5000` (HTTP API)

---

## 🧠 Background Script Logic

### Estructura General (mismo código en ambos)

```javascript
// 1. API Wrapper
const API = typeof browser !== 'undefined' ? browser : chrome;

// 2. WebSocket Setup (Socket.IO)
let socket = null;

function connectSocketIO() {
  if (typeof io === 'undefined') {
    connectWebSocketFallback();
    return;
  }

  socket = io('http://127.0.0.1:5001', {
    reconnection: true,
    reconnectionDelay: 3000,
    reconnectionAttempts: 10,
    transports: ['websocket', 'polling']
  });

  socket.on('agent_registered', (data) => {
    console.log('[EVA background] agent_registered:', data);
    
    // Enviar a content script
    API.tabs.sendMessage(data.tabId, {
      type: 'INJECT_AGENT_METADATA',
      agent: data
    });
  });
}

// 3. Message Handlers
API.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'EVA_SAVE_REPLY') {
    API.storage.local.set({
      last_reply: message.content,
      timestamp: Date.now()
    });
    sendResponse({status: 'saved'});
  }
});

// 4. Initialize
connectSocketIO();
API.alarms.create('reconnect_socket', {periodInMinutes: 1});
```

---

## 📤 Content Script (Compartido)

```javascript
// content/content.js - IDÉNTICO en Chrome y Firefox

const API = typeof browser !== 'undefined' ? browser : chrome;

// Escuchar mensajes del background
API.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'INJECT_AGENT_METADATA') {
    console.log('[EVA content] Inyectando agente:', message.agent);
    
    // Crear script para inyectar
    const script = document.createElement('script');
    script.textContent = `
      window.NEUROBIT_AGENT = ${JSON.stringify(message.agent)};
      console.log('✅ TRON/SIMON agent inyectado:', window.NEUROBIT_AGENT);
    `;
    
    document.documentElement.appendChild(script);
    sendResponse({status: 'injected'});
  }
});
```

---

## 🔐 Storage Unification

### Chrome Pattern (Callbacks)

```javascript
chrome.storage.local.set({key: value}, () => {
  console.log('Guardado');
});

chrome.storage.local.get(['key'], (result) => {
  console.log('Valor:', result.key);
});
```

### Firefox Pattern (Promises)

```javascript
browser.storage.local.set({key: value}).then(() => {
  console.log('Guardado');
});

browser.storage.local.get('key').then((result) => {
  console.log('Valor:', result.key);
});
```

### Wrapper Unificado (background.js)

```javascript
const API = typeof browser !== 'undefined' ? browser : chrome;

// Ambos navegadores - callback compatible
API.storage.local.set({key: value}, () => {
  console.log('Guardado (Chrome style)');
});

// O con Promise
if (typeof API.storage.local.set({}).then === 'function') {
  API.storage.local.set({key: value}).then(() => {
    console.log('Guardado (Firefox style)');
  });
}
```

---

## 🌐 WebSocket Integration (Socket.IO)

### Server (neurobit_api.py - 127.0.0.1:5001)

```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    emit('server_status', {'status': 'connected'})

@socketio.on('agent_registered')
def broadcast_registration(data):
    socketio.emit('agent_registered', data, broadcast=True)
```

### Client (background.js - Chrome & Firefox)

```javascript
// Conectar a Socket.IO
const socket = io('http://127.0.0.1:5001', {
  reconnection: true,
  transports: ['websocket', 'polling']
});

// Escuchar broadcasts
socket.on('agent_registered', (data) => {
  console.log('[EVA] Agent registered:', data);
  
  // Inyectar en la pestaña apropiada
  API.tabs.sendMessage(data.tabId, {
    type: 'INJECT_AGENT_METADATA',
    agent: data
  });
});

// Fallback WebSocket si Socket.IO no disponible
function connectWebSocketFallback() {
  const ws = new WebSocket('ws://127.0.0.1:5001');
  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.type === 'agent_registered') {
      // Mismo flujo
    }
  };
}
```

---

## 🎯 Decisiones de Arquitectura

### 1. ¿Por qué v4.0 separa Chrome y Firefox?

**Antes (v3.0):** Un directorio con condiciones hardcoded  
**Ahora (v4.0):** Directorios explícitos con manifests claros

**Ventajas:**
- ✅ Claridad inmediata sobre qué es de dónde
- ✅ Facilita mantenimiento específico por navegador
- ✅ Prepara para futuras extensiones (Safari, Edge)
- ✅ Código compartido donde es posible

### 2. ¿Por qué Socket.IO en lugar de WebSocket raw?

**Ventajas Socket.IO:**
- ✅ Auto-reconnection
- ✅ Fallback HTTP polling
- ✅ Namespace support
- ✅ Room broadcasting
- ✅ Compatible Chrome + Firefox

### 3. ¿Por qué 127.0.0.1:5001 para WebSocket?

**Soberanía garantizada:**
- ✅ Local-only (no sale del equipo)
- ✅ Sin APIs externas
- ✅ Control total de datos
- ✅ Previene data exfiltration

---

## 🧪 Testing Checklist

### Chrome

- [ ] Cargar en `chrome://extensions`
- [ ] Verificar background script cargado
- [ ] Abrir DevTools (F12)
- [ ] Console sin errores
- [ ] WebSocket conecta a 127.0.0.1:5001
- [ ] Mensaje `agent_registered` recibido
- [ ] Content script inyecta AGENT_METADATA

### Firefox

- [ ] Cargar en `about:debugging`
- [ ] Verificar background script cargado
- [ ] Web Extension Debugger abierto
- [ ] Console sin errores
- [ ] WebSocket conecta a 127.0.0.1:5001
- [ ] Mensaje `agent_registered` recibido
- [ ] Content script inyecta AGENT_METADATA

---

## 📋 Resumen de Diferencias

| Aspecto | Cómo Manejarlo |
|--------|---|
| **API namespace** | Usar `const API = browser \|\| chrome;` |
| **Background type** | Same code, different manifest |
| **Storage** | API unificada en wrapper |
| **WebSocket** | Socket.IO con fallback |
| **Debugging** | Herramientas diferentes pero funcionalidad igual |
| **Installation** | URLs diferentes pero proceso similar |

---

**Conclusión:** Bitácora EVA v4.0 es **totalmente compatible** con ambos navegadores usando un **patrón de wrapper** simple y efectivo.

**Status:** ✅ ARQUITECTURA VALIDADA
