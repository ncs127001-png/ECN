# 📖 bitacora-eva — NEUROBIT

**Versión:** v3.0  
**Manifest:** v3.0 (MV3)  
**Estado:** 🟢 Production  
**Última actualización:** 2026-03-23

> 🛡️ **ARQUITECTURA SOBERANA:** Esta extensión opera en el contexto local del NODO_SEMILLA. No envía datos a servidores corporativos. La bitácora se almacena localmente y se sincroniza SOLO con la API local de Neurobit (127.0.0.1:5000).

---

## 📋 DESCRIPCIÓN

**Bitácora EVA** es una extensión de Chrome que captura y registra eventos de navegación en tiempo real:

- ✅ Clics en elementos
- ✅ Inputs de texto
- ✅ Cambios de página
- ✅ Eventos del DOM
- ✅ Historial de interacciones

Todo se sincroniza con la API de **Neurobit Central Station** para análisis centralizado.

---

## 🚀 INSTALACIÓN

### Requisitos

- Chrome 88 o superior
- API Neurobit corriendo en `http://127.0.0.1:5000`

### Pasos

```bash
# 1. Abrir Chrome
google-chrome

# 2. Ir a extensiones
chrome://extensions/

# 3. Activar "Modo desarrollador" (esquina superior derecha)

# 4. Click en "Cargar extensión sin empaquetar"

# 5. Seleccionar carpeta
~/WORKSPACE_NEUROBIT_V0.2/extensions/bitacora-eva/

# 6. ✅ Extensión instalada
```

---

## 💡 CÓMO USAR

### Activar Bitácora

```bash
1. Click en ícono de Bitácora (barra de herramientas)
2. Popup aparece con opciones:
   - ✅ Enabled (activada)
   - 📊 Stats (estadísticas)
   - 🔧 Settings (configuración)
3. Navegar por sitios normalmente
4. Bitácora registra todo automáticamente
```

### Ver Registros

```bash
# En Chrome DevTools (F12)
# Pestaña "Storage" → "Local Storage" → bitacora-eva
# Ver todos los eventos registrados

# O a través de API
curl http://127.0.0.1:5000/memoria | jq '.bitacora'
```

### Exportar Datos

```bash
# Click en ícono de Bitácora → Settings
# → "Export data" → guardar JSON
```

---

## 📂 ARCHIVOS PRINCIPALES

| Archivo | Función |
| --- | --- |
| `manifest.json` | Configuración de la extensión (MV3) |
| `background.js` | Service worker (event listener principal) |
| `content/content.js` | Script inyectado en páginas |
| `popup/popup.html` | UI del popup |
| `popup/popup.js` | Lógica del popup |
| `popup/storage.js` | Gestión de almacenamiento local |
| `popup/injector.js` | Inyector de scripts |
| `feedback.css` | Estilos de feedback |
| `feedback.js` | Lógica de feedback visual |

---

## 🔌 ENDPOINTS API REQUERIDOS

Bitácora EVA usa estos endpoints:

| Endpoint | Método | Propósito |
| --- | --- | --- |
| `/health` | GET | Verificar que API está activa |
| `/memoria` | GET | Enviar registros |
| `/analyze` | POST | Analizar eventos |
| `/register_agent` | POST | Registrar como agente |

---

## ⚙️ CONFIGURACIÓN

### Settings Disponibles

```javascript
// En popup/popup.js
{
  "enabled": true,          // Habilitar/deshabilitar
  "capture_clicks": true,   // Capturar clics
  "capture_inputs": true,   // Capturar inputs de texto
  "capture_navigation": true, // Capturar cambios de página
  "storage_limit": 1000,    // Máximo de eventos en memoria
  "sync_interval": 5000     // Intervalo de sincronización (ms)
}
```

### Modificar Configuración

```bash
1. Click en ícono → Settings
2. Cambiar valores
3. Click "Save"
4. Recargar extensión en chrome://extensions/
```

---

## 🐛 TROUBLESHOOTING

### Extensión no aparece en Chrome

```bash
# 1. Verificar Modo Desarrollador está activado
# chrome://extensions/ → esquina superior derecha

# 2. Recargar extensión
# chrome://extensions/ → botón de recarga

# 3. Ver errores
# chrome://extensions/ → Detalles → "Ver errores"
```

### Registros no se sincronizaban

```bash
# 1. Verificar que API está corriendo
curl http://127.0.0.1:5000/health | jq

# 2. Abrir DevTools (F12)
# → Console → ver si hay errores
# → Network → ver si hay solicitudes a /memoria

# 3. Limpiar storage local
# chrome://extensions/ → Detalles → Borrar datos
```

### Popup no se abre

```bash
# 1. Verificar que manifest.json es válido
python3 -m json.tool ~/WORKSPACE_NEUROBIT_V0.2/extensions/bitacora-eva/manifest.json

# 2. Recargar extensión en chrome://extensions/

# 3. Ver error en DevTools
# chrome://extensions/ → Detalles → "Ver errores"
```

---

## 📊 ESTADÍSTICAS

Bitácora recolecta:

- **Clics:** Número total de clics capturados
- **Inputs:** Número de inputs de texto
- **Navegaciones:** Número de cambios de página
- **Últimos 10 eventos:** Preview de eventos recientes

Acceder a stats:

```bash
# Popup → Stats (pestaña)
# Ver gráfico de actividad
```

---

## 🔐 PRIVACIDAD Y SEGURIDAD

### ¿Qué datos se capturan?

- ✅ Clics, inputs, navegación (SOLO en navegador local)
- ✅ No se capturan contraseñas directamente
- ✅ No se envía a internet (solo a localhost:5000)

### ¿Dónde se almacenan?

- 🔒 Almacenamiento local del navegador (Chrome)
- 🔒 Sincronización local a `http://127.0.0.1:5000`
- 🔒 No se envía a servidor externo

### Cómo limpieza de datos

```bash
# 1. Popup → Settings
# 2. Click "Clear all data"
# 3. Confirmar

# O manual:
# chrome://extensions/ → Detalles → "Borrar datos"
```

---

## 📝 NOTAS DE DESARROLLO

### Agregar nuevo tipo de evento

```javascript
// En content/content.js

// 1. Agregar listener
document.addEventListener('nombre_evento', (event) => {
  console.log('Evento capturado:', event);
  // 2. Enviar a storage
  chrome.storage.local.set({ event_data: {...} });
});

// 3. Sincronizar con API
fetch('http://127.0.0.1:5000/memoria', {
  method: 'POST',
  body: JSON.stringify(event_data)
});
```

### Debuggear Bitácora

```bash
# En DevTools (F12)
# → Pestaña Application
# → Local Storage
# → https://[sitio]
# Ver datos almacenados

# Ver console.log
# → Pestaña Console
# Ver todos los logs de la extensión
```

---

## 🔄 ESTADO OPERACIONAL

| Componente | Estado | Última Verificación |
| --- | --- | --- |
| Captura de eventos | 🟢 Ok | 2026-03-23 |
| Sincronización API | 🟢 Ok | 2026-03-23 |
| Almacenamiento local | 🟢 Ok | 2026-03-23 |
| UI Popup | 🟢 Ok | 2026-03-23 |
| Background Service Worker | 🟢 Ok | 2026-03-23 |

---

## 📞 SOPORTE

Si tienes problemas:

1. Revisar sección "Troubleshooting" arriba
2. Revisar logs: `~/WORKSPACE_NEUROBIT_V0.2/data/logs/api_flask.log`
3. Contactar al equipo: [equipo de desarrollo]

---

## 🔗 REFERENCIAS

- [Documentación de Manifest v3](https://developer.chrome.com/docs/extensions/mv3/)
- [API Local Storage](https://developer.chrome.com/docs/extensions/reference/storage/)
- [Content Scripts](https://developer.chrome.com/docs/extensions/mv3/content_scripts/)

---

**Versión:** 3.0  
**Última revisión:** 2026-03-23  
**Responsable:** Equipo Neurobit
