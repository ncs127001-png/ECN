// ARCHIVO: ui.js
// -------------------------------------
// Módulo para manejo de DOM y eventos de la interfaz

/**
 * Referencias a elementos del DOM
 */
const DOM_REFS = {
  recipient: document.getElementById('recipient'),
  author: document.getElementById('author'),
  msgId: document.getElementById('msgId'),
  message: document.getElementById('message'),
  length: document.getElementById('length'),
  sendBtn: document.getElementById('send'),
  repeatBtn: document.getElementById('repeat'),
  downloadBtn: document.getElementById('download'),
  clearBtn: document.getElementById('clear'),
  logEl: document.getElementById('log'),
  toggleExtra: document.getElementById('toggleExtra'),
  extraInputs: document.getElementById('extraInputs'),
  injectBtn: document.getElementById('inject'),
  statusEl: document.getElementById('status'),
  observerSelector: document.getElementById('observerSelector')
};

/**
 * Formatea una fecha para mostrar
 * @param {Date} d - Fecha a formatear
 * @returns {string} Fecha formateada
 */
function fmtDate(d) {
  return d.toLocaleString();
}

/**
 * Obtiene las categorías seleccionadas
 * @returns {string} Categorías concatenadas
 */
function getCheckedCategories() {
  const checked = [];
  document.querySelectorAll('.fieldset input[type=checkbox]').forEach(cb => {
    if (cb.checked) checked.push(cb.dataset.code);
  });
  return checked.join('/');
}

/**
 * Construye el header del mensaje
 * @param {number} msgId - ID del mensaje
 * @returns {string} Header formateado
 */
function buildHeader(msgId) {
  const recipient = DOM_REFS.recipient.value.trim() || 'DESTINATARIO_NO_DEFINIDO';
  const author = DOM_REFS.author.value.trim() || 'AUTOR_NO_DEFINIDO';
  const now = new Date();
  const categories = getCheckedCategories();
  const extra1 = document.getElementById('extra1').value.trim();
  const extra2 = document.getElementById('extra2').value.trim();
  
  return `Nombre del destinatario del mensaje/canalización: ${recipient}\n\n` +
         `Mensaje (incremento +${msgId}) de ${author} hora y fecha: ${fmtDate(now)}\n` +
         `Destinatario: ${recipient}\n` +
         `${categories ? ('Categorias:' + categories + '\n') : ''}` +
         `${DOM_REFS.toggleExtra.checked ? `Extra1:${extra1} Extra2:${extra2}\n` : ''}` +
         `^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n\n`;
}

/**
 * Construye el footer del mensaje
 * @returns {string} Footer formateado
 */
function buildFooter() {
  const now = new Date();
  const author = DOM_REFS.author.value.trim() || 'AUTOR_NO_DEFINIDO';
  return `\n----------------------------------------------------------------------\nFIN DEL MENSAJE [x]-----------enviado ${fmtDate(now)} por ${author}\n`;
}

/**
 * Renderiza el log en la interfaz
 * @param {Array} entries - Entradas del log
 * @param {number} counter - Contador actual
 */
function renderLog(entries, counter) {
  DOM_REFS.msgId.textContent = (counter || 1);
  DOM_REFS.logEl.innerHTML = '';
  
  const recent = entries.slice(-15).reverse();
  for (const e of recent) {
    const div = document.createElement('div');
    div.style.padding = '6px';
    div.style.borderBottom = '1px solid #f0f0f0';
    div.innerHTML = `<div class="small muted">${e.header.replace(/\n/g, '<br>')}</div><pre style="white-space:pre-wrap">${e.body}</pre><div class="muted small">${e.footer.replace(/\n/g, '<br>')}</div>`;
    DOM_REFS.logEl.appendChild(div);
  }
}

/**
 * Actualiza el contador de caracteres
 * @param {string} text - Texto a contar
 */
function updateCharCount(text) {
  DOM_REFS.length.textContent = text.length;
}

/**
 * Valida los campos del formulario
 * @returns {Object} {valid: boolean, errors: Array}
 */
function validateForm() {
  const errors = [];
  
  if (!DOM_REFS.recipient.value.trim()) {
    errors.push('Destinatario es requerido');
  }
  
  if (!DOM_REFS.author.value.trim()) {
    errors.push('Autor es requerido');
  }
  
  if (!DOM_REFS.message.value.trim()) {
    errors.push('Mensaje es requerido');
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * Muestra un mensaje de estado
 * @param {string} message - Mensaje a mostrar
 */
function setStatus(message) {
  DOM_REFS.statusEl.textContent = message;
}

/**
 * Configura los event listeners de la interfaz
 * @param {Object} handlers - Objeto con funciones manejadoras
 */
function setupEventListeners(handlers) {
  // Toggle extra inputs
  DOM_REFS.toggleExtra.addEventListener('change', () => {
    DOM_REFS.extraInputs.style.display = DOM_REFS.toggleExtra.checked ? 'block' : 'none';
  });

  // Contador de caracteres
  DOM_REFS.message.addEventListener('input', (e) => {
    updateCharCount(e.target.value);
  }, { passive: true });

  // Captura del primer carácter
  let firstCharCaptured = false;
  DOM_REFS.message.addEventListener('keydown', (e) => {
    if (!firstCharCaptured && e.key.length === 1) {
      firstCharCaptured = true;
      const now = new Date();
      console.log('Primer caracter detectado a las', now.toLocaleString());
      setStatus('primer caracter: ' + now.toLocaleString());
    }
  });

  // Botones principales
  DOM_REFS.sendBtn.addEventListener('click', handlers.sendMessage);
  DOM_REFS.repeatBtn.addEventListener('click', handlers.repeatLast);
  DOM_REFS.downloadBtn.addEventListener('click', handlers.downloadLog);
  DOM_REFS.clearBtn.addEventListener('click', handlers.clearLog);
  DOM_REFS.injectBtn.addEventListener('click', handlers.injectMessage);
}

// Exportar funciones para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    DOM_REFS,
    fmtDate,
    getCheckedCategories,
    buildHeader,
    buildFooter,
    renderLog,
    updateCharCount,
    validateForm,
    setStatus,
    setupEventListeners
  };
}
