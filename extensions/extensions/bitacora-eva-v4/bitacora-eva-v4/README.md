# 📚 Bitácora EVA v4.0 — Arquitectura Unificada (Chrome + Firefox)

**Versión:** 4.0  
**Fecha:** Abril 1, 2026  
**Estado:** ✅ ESTRUCTURA UNIFICADA (Base: v3.0)  
**Plataformas:** Chrome + Firefox (Manifest v3 compatible)  

---

## 🎯 ¿Qué es Bitácora EVA v4.0?

**Bitácora EVA v4.0** es la **unificación arquitectónica** de la extensión Bitácora EVA que:

1. **Preserva** la base funcional probada (v3.0)
2. **Unifica** Chrome y Firefox en una sola estructura
3. **Separa** archivos específicos por navegador (manifest, background)
4. **Mantiene** máxima compatibilidad y reutilización de código

---

## 📁 Estructura de Directorios

```
bitacora-eva-v4/
├── README.md ........................... (Este archivo)
├── ARCHITECTURE.md .................... (Diferencias Chrome vs Firefox)
│
├── chrome/
│   ├── manifest.json .................. (Chrome Manifest v3)
│   ├── background.js .................. (Chrome background script)
│   ├── background.firefox.js .......... (NO USAR EN CHROME)
│   ├── manifest.firefox.json .......... (NO USAR EN CHROME)
│   ├── content/
│   │   ├── content.js
│   │   └── ...
│   ├── popup/
│   │   ├── popup.html
│   │   ├── popup.js
│   │   └── ...
│   ├── feedback.js
│   ├── popup.js
│   └── ...
│
└── firefox/
    ├── manifest.json .................. (NO USAR EN FIREFOX - usar manifest.firefox.json)
    ├── manifest.firefox.json .......... (Firefox Manifest v3 + Gecko settings)
    ├── background.js .................. (Firefox background script)
    ├── background.firefox.js .......... (Compatibilidad - mismo que background.js)
    ├── content/
    │   ├── content.js ................. (Compartido con Chrome)
    │   └── ...
    ├── popup/
    │   ├── popup.html
    │   ├── popup.js
    │   └── ...
    ├── feedback.js .................... (Compartido con Chrome)
    ├── popup.js ....................... (Compartido con Chrome)
    └── ...
```

---

## 🔧 Diferencias Chrome vs Firefox

### 1. Manifest

**Chrome (`chrome/manifest.json`):**
```json
{
  "manifest_version": 3,
  "name": "Bitácora EVA",
  "version": "4.0",
  "background": {
    "service_worker": "background.js"
  }
}
```

**Firefox (`firefox/manifest.firefox.json`):**
```json
{
  "manifest_version": 3,
  "name": "Bitácora EVA",
  "version": "4.0",
  "browser_specific_settings": {
    "gecko": {
      "id": "bitacora-eva@neurobit.local",
      "strict_min_version": "109.0"
    }
  },
  "background": {
    "scripts": ["background.js"],
    "type": "module"
  }
}
```

### 2. API Namespace

**Chrome:** `chrome.*`  
**Firefox:** `browser.*` (con Promises)

**Solución:** API wrapper en `background.js`:
```javascript
const API = typeof browser !== 'undefined' ? browser : chrome;
```

### 3. Background Script

**Chrome:** `service_worker` (ephemeral, sin persistencia)  
**Firefox:** `scripts: [background.js]` (persistent background page)

**Implicación:** Firefox mantiene el background script activo; Chrome lo descarga cuando no está en uso.

---

## 🚀 Instalación

### Chrome

```bash
1. Abrir chrome://extensions/
2. Activar "Developer mode"
3. Click "Load unpacked"
4. Seleccionar: ~/WORKSPACE_NEUROBIT_V0.2/extensions/bitacora-eva-v4/chrome/
```

### Firefox

```bash
1. Abrir about:debugging#/runtime/this-firefox
2. Click "Load Temporary Add-on..."
3. Seleccionar: ~/WORKSPACE_NEUROBIT_V0.2/extensions/bitacora-eva-v4/firefox/manifest.firefox.json
```

---

## 📋 Archivos Específicos por Navegador

| Archivo | Chrome | Firefox | Uso |
|---------|--------|---------|-----|
| `manifest.json` | ✅ USAR | ❌ NO | Manifest Chrome |
| `manifest.firefox.json` | ❌ NO | ✅ USAR | Manifest Firefox |
| `background.js` | ✅ USAR | ✅ USAR | Background script (mismo código) |
| `background.firefox.js` | ❌ NO | ✅ COMPATIBLE | API wrapper (opcional) |
| `content/content.js` | ✅ COMPARTIR | ✅ COMPARTIR | Content script (igual en ambos) |
| `popup/popup.js` | ✅ COMPARTIR | ✅ COMPARTIR | Popup logic (igual en ambos) |
| `feedback.js` | ✅ COMPARTIR | ✅ COMPARTIR | Feedback logic (igual en ambos) |

---

## 🔄 Flujo de Mensajes (WebSocket + Extension)

```
[Usuario en Salón Web]
        ↓
POST /register_agent {name, platform, url, tabId, pid}
        ↓
[neurobit_api.py]
├─ register_agent()
├─ broadcast_agent_registered()
└─ socketio.emit('agent_registered', {...}, broadcast=True)
        ↓
[WebSocket 127.0.0.1:5001]
        ↓
[background.js - Chrome & Firefox]
├─ socket.on('agent_registered', (data) => {...})
├─ chrome/browser.tabs.sendMessage(tabId, INJECT_AGENT_METADATA)
└─ Storage.local.set({agent: data})
        ↓
[content/content.js - Chrome & Firefox]
├─ chrome/browser.runtime.onMessage.addListener()
├─ Inyectar TRON/SIMON script en página
└─ Inicializar overlay EVA
```

---

## ✅ Validación

### Sintaxis

```bash
# Chrome
python3 -m json.tool chrome/manifest.json
node -c chrome/background.js

# Firefox
python3 -m json.tool firefox/manifest.firefox.json
node -c firefox/background.js
```

### Storage

```javascript
// Ambos navegadores
chrome.storage.local.get(['agent'], (result) => {
  console.log('✅ Agent data:', result.agent);
});

// Firefox (Promise-based)
browser.storage.local.get('agent').then((result) => {
  console.log('✅ Agent data:', result.agent);
});
```

---

## 🐛 Debugging

### Chrome DevTools

```
1. chrome://extensions/
2. Seleccionar Bitácora EVA
3. Click "Inspect views" → "background page"
4. Console, Network, Storage tabs
```

### Firefox Web Extension Debugger

```
1. about:debugging#/runtime/this-firefox
2. Click "Inspect" bajo Bitácora EVA
3. Console, Network tabs
```

---

## 📊 Cambios desde v3.0 → v4.0

| Aspecto | v3.0 | v4.0 | Nota |
|---------|------|------|------|
| **Estructura** | Monolítica | Chrome + Firefox separados | Mejor mantenimiento |
| **Manifests** | 1 + variante | 2 explícitos | Claridad |
| **Base** | Chrome-first | Agnostic | Compatible ambos |
| **API wrapper** | background.js | background.js (same) | Automatizado |
| **Content.js** | 1 | 2 (idénticos) | Reutilización máxima |

---

## 🚨 Notas Importantes

1. **NO MODIFICAR** `background.firefox.js` si estás usando v4.0
   - Es un wrapper de compatibilidad heredado
   - `background.js` ya contiene la lógica unificada

2. **NO USAR** `manifest.json` en Firefox
   - Siempre usar `manifest.firefox.json`
   - Contiene `browser_specific_settings.gecko`

3. **Persistencia en Firefox**
   - Background script persiste (a diferencia de Chrome service_worker)
   - WebSocket puede permanecer activo más tiempo

4. **Local Storage**
   - Ambos navegadores usan `chrome.storage.local` (API unificada)
   - Firefox también soporta `browser.storage.local` (Promise-based)

---

## 📝 Próximos Pasos

1. ✅ **Estructura v4.0** creada (Chrome + Firefox)
2. ⏳ **Testing** (cargar en ambos navegadores)
3. ⏳ **Integración WebSocket** (Socket.IO 127.0.0.1:5001)
4. ⏳ **Documentación** de diferencias (ARCHITECTURE.md)

---

## 🎊 Resumen

**Bitácora EVA v4.0** es la **evolución arquitectónica** que:

✅ Preserva la base funcional v3.0  
✅ Separa Chrome y Firefox en directorios explícitos  
✅ Mantiene máxima reutilización de código  
✅ Facilita futuro mantenimiento y evolución  
✅ Soporta WebSocket en ambos navegadores  
✅ Garantiza soberanía (127.0.0.1 only)  

**Status:** ✅ LISTA PARA TESTING

---

**Versión:** 4.0  
**Fecha:** Abril 1, 2026  
**Mantener:** Soberanía + Compatibilidad + Claridad arquitectónica
