// ARCHIVO: popup.js (Refactorizado)
// -------------------------------------
// Módulo principal que coordina todos los componentes

// Importar módulos (en un entorno real usaríamos import/export)
// Por ahora, asumimos que los módulos están disponibles globalmente

// Estado global
let state = null;
let lastSent = null;
let domObserver = null;
let chatGPTObserver = null;

/**
 * Inicializa la aplicación
 */
function init() {
  console.log('[EVA Popup] Inicializando aplicación');
  
  // Cargar estado inicial
  state = loadState();
  if (!state.arr) state.arr = [];
  if (!state.counter) state.counter = 1;
  
  // Inicializar observadores
  domObserver = new DOMObserver();
  chatGPTObserver = new ChatGPTResponseObserver();
  
  // Configurar callbacks
  domObserver.setStatusCallback(setStatus);
  chatGPTObserver.startResponseObserver(handleChatGPTResponse);
  
  // Configurar event listeners
  setupEventListeners({
    sendMessage: handleSendMessage,
    repeatLast: handleRepeatLast,
    downloadLog: handleDownloadLog,
    clearLog: handleClearLog,
    injectMessage: handleInjectMessage
  });
  
  // Renderizar interfaz inicial
  renderLog(state.arr, state.counter);
  
  console.log('[EVA Popup] Aplicación inicializada correctamente');
}

/**
 * Maneja el envío de mensajes
 */
async function handleSendMessage() {
  console.log('[EVA Popup] Procesando envío de mensaje');
  
  // Validar formulario
  const validation = validateForm();
  if (!validation.valid) {
    alert('Errores en el formulario:\n' + validation.errors.join('\n'));
    return;
  }
  
  const text = DOM_REFS.message.value;
  const id = state.counter || 1;
  const header = buildHeader(id);
  const footer = buildFooter();
  const entry = { id, header, body: text, footer, ts: Date.now() };
  
  // Añadir al log
  state = appendLog(entry, state);
  lastSent = entry;
  
  setStatus('enviando...');
  
  // Intentar inyectar en la página
  try {
    const success = await tryInjectToPage(text, setStatus);
    if (success) {
      setStatus('mensaje enviado exitosamente');
    } else {
      setStatus('error al enviar mensaje');
    }
  } catch (error) {
    console.error('[EVA Popup] Error al inyectar mensaje:', error);
    setStatus('error al inyectar mensaje');
  }
  
  // Limpiar textarea para el siguiente fragmento
  DOM_REFS.message.value = '';
  updateCharCount('');
  
  // Actualizar interfaz
  renderLog(state.arr, state.counter);
}

/**
 * Repite el último mensaje enviado
 */
async function handleRepeatLast() {
  if (!lastSent) {
    alert('No hay mensaje previo para repetir');
    return;
  }
  
  console.log('[EVA Popup] Repitiendo último mensaje');
  setStatus('reinyectando último mensaje...');
  
  try {
    const success = await tryInjectToPage(lastSent.body, setStatus);
    if (success) {
      setStatus('último mensaje reinyectado');
    } else {
      setStatus('error al reinyectar mensaje');
    }
  } catch (error) {
    console.error('[EVA Popup] Error al reinyectar mensaje:', error);
    setStatus('error al reinyectar mensaje');
  }
}

/**
 * Descarga la bitácora completa
 */
function handleDownloadLog() {
  console.log('[EVA Popup] Descargando bitácora');
  
  try {
    const content = generateDownloadContent(state.arr);
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    
    a.href = url;
    a.download = `bitacora_${(new Date()).toISOString().replace(/[:.]/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    
    setStatus('bitácora descargada');
  } catch (error) {
    console.error('[EVA Popup] Error al descargar bitácora:', error);
    setStatus('error al descargar bitácora');
  }
}

/**
 * Limpia la bitácora actual
 */
function handleClearLog() {
  if (!confirm('Crear nueva bitácora y borrar la actual?')) {
    return;
  }
  
  console.log('[EVA Popup] Limpiando bitácora');
  state = clearLog();
  lastSent = null;
  renderLog(state.arr, state.counter);
  setStatus('nueva bitácora creada');
}

/**
 * Inyecta mensaje manualmente
 */
async function handleInjectMessage() {
  const text = DOM_REFS.message.value || (lastSent && lastSent.body) || '';
  if (!text) {
    alert('Nada para inyectar');
    return;
  }
  
  console.log('[EVA Popup] Inyección manual de mensaje');
  setStatus('inyectando mensaje...');
  
  try {
    const success = await tryInjectToPage(text, setStatus);
    if (success) {
      setStatus('mensaje inyectado manualmente');
    } else {
      setStatus('error en inyección manual');
    }
  } catch (error) {
    console.error('[EVA Popup] Error en inyección manual:', error);
    setStatus('error en inyección manual');
  }
}

/**
 * Maneja respuestas de ChatGPT
 * @param {Object} entry - Entrada de respuesta
 */
function handleChatGPTResponse(entry) {
  console.log('[EVA Popup] Respuesta de ChatGPT recibida:', entry);
  
  // Enviar al background para guardar
  chrome.runtime.sendMessage({ type: 'EVA_SAVE_REPLY', entry }, (response) => {
    if (chrome.runtime.lastError) {
      console.error('[EVA Popup] Error al guardar respuesta:', chrome.runtime.lastError);
    } else {
      console.log('[EVA Popup] Respuesta guardada en background:', response);
      setStatus('respuesta de ChatGPT capturada');
    }
  });
}

/**
 * Maneja cambios en el selector de observador
 */
function handleObserverSelectorChange() {
  const selector = DOM_REFS.observerSelector.value.trim();
  
  if (selector) {
    const success = domObserver.startObserver(selector);
    if (!success) {
      // El error ya se mostró en el callback de estado
    }
  } else {
    domObserver.stopObserver();
  }
}

// Configurar event listener para el selector de observador
DOM_REFS.observerSelector.addEventListener('change', handleObserverSelectorChange);

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

// Exportar funciones principales para uso externo
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    init,
    handleSendMessage,
    handleRepeatLast,
    handleDownloadLog,
    handleClearLog,
    handleInjectMessage
  };
}
