// ARCHIVO: injector.js
// -------------------------------------
// Módulo para lógica de inyección de texto en páginas web

/**
 * Sanitiza texto para inyección segura
 * @param {string} text - Texto a sanitizar
 * @returns {string} Texto sanitizado
 */
function sanitizeText(text) {
  if (typeof text !== 'string') return '';
  
  // Remover caracteres de control peligrosos
  return text
    .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '') // Caracteres de control
    .replace(/javascript:/gi, '') // URLs javascript
    .replace(/on\w+\s*=/gi, '') // Event handlers
    .trim();
}

/**
 * Encuentra el elemento editable en la página
 * @returns {Element|null} Elemento editable encontrado
 */
function findEditable() {
  // Heurísticos: contentEditable div, or visible textarea
  const ta = document.querySelector('textarea:not([style*="display: none"]), textarea:not([hidden])');
  if (ta && ta.offsetParent !== null) return ta;
  
  const editable = document.querySelector('[contenteditable="true"]');
  if (editable) return editable;
  
  // try more generic
  const ed2 = Array.from(document.querySelectorAll('[contenteditable]'))
    .find(e => e.getAttribute('contenteditable') !== 'false');
  if (ed2) return ed2;
  
  return null;
}

/**
 * Encuentra el botón de envío en la página
 * @returns {Element|null} Botón de envío encontrado
 */
function findSendButton() {
  // try common selectors; best-effort
  return document.querySelector('#composer-submit-button') || 
         document.querySelector('button[data-testid="send-button"]') || 
         document.querySelector('button[aria-label*="Enviar"], button[aria-label*="Send"]');
}

/**
 * Inyecta texto en un textarea
 * @param {HTMLTextAreaElement} ta - Elemento textarea
 * @param {string} text - Texto a inyectar
 */
function injectToTextarea(ta, text) {
  const { selectionStart, selectionEnd } = ta;
  ta.value = text;
  ta.selectionStart = ta.selectionEnd = ta.value.length;
  ta.dispatchEvent(new Event('input', { bubbles: true }));
}

/**
 * Inyecta texto en un elemento contentEditable
 * @param {Element} editable - Elemento contentEditable
 * @param {string} text - Texto a inyectar
 */
function injectToContentEditable(editable, text) {
  editable.focus();
  
  // Para seguridad, insertar texto plano preservando saltos de línea
  const lines = text.split('\n');
  editable.innerHTML = '';
  
  for (let i = 0; i < lines.length; i++) {
    const span = document.createElement('div');
    span.textContent = lines[i];
    editable.appendChild(span);
  }
  
  // dispatch input
  editable.dispatchEvent(new InputEvent('input', { bubbles: true }));
}

/**
 * Intenta inyectar texto en la página actual
 * @param {string} text - Texto a inyectar
 * @param {Function} statusCallback - Callback para actualizar estado
 * @returns {Promise<boolean>} true si la inyección fue exitosa
 */
async function tryInjectToPage(text, statusCallback) {
  const sanitizedText = sanitizeText(text);
  
  if (!sanitizedText) {
    statusCallback('Texto vacío o inválido');
    return false;
  }

  // Prefer contentEditable if present
  const editable = findEditable();
  if (editable) {
    try {
      // Si es un textarea
      if (editable.tagName === 'TEXTAREA') {
        injectToTextarea(editable, sanitizedText);
      } else if (editable.isContentEditable) {
        injectToContentEditable(editable, sanitizedText);
      }

      // Buscar botón de envío dinámicamente
      const sendBtn = findSendButton();
      if (sendBtn) {
        // Pequeño delay para que React se reconcilie
        setTimeout(() => {
          try {
            sendBtn.click();
            statusCallback('mensaje enviado (click)');
            return true;
          } catch (e) {
            console.warn(e);
            statusCallback('error click');
            return false;
          }
        }, 120);
      } else {
        // fallback: copiar al portapapeles e informar usuario
        try {
          await navigator.clipboard.writeText(sanitizedText);
          alert('Texto copiado al portapapeles. Pega manualmente en el editor y envía.');
          statusCallback('copiado al portapapeles (fallback)');
          return true;
        } catch (clipboardError) {
          console.error('Error al copiar al portapapeles:', clipboardError);
          alert('No se pudo inyectar ni copiar. No hay editor detectable.');
          statusCallback('error: no se pudo inyectar ni copiar');
          return false;
        }
      }
    } catch (error) {
      console.error('Error durante la inyección:', error);
      statusCallback('error durante inyección');
      return false;
    }
  } else {
    alert('No se detectó editor en la página. Puedes pegar manualmente.');
    statusCallback('no se detectó editor');
    return false;
  }
}

/**
 * Obtiene el último texto de respuesta de ChatGPT
 * @returns {Promise<string|null>} Texto de la última respuesta
 */
async function getLastResponseText() {
  // Selecciona todos los botones de copiar (en español)
  const copyBtns = document.querySelectorAll('button[aria-label="Copiar"]');
  if (!copyBtns.length) return null;

  // Último botón = último mensaje de la conversación
  const lastBtn = copyBtns[copyBtns.length - 1];

  // Simula un click para copiar al portapapeles
  lastBtn.click();

  // Ahora intentamos leer desde el portapapeles
  try {
    return await navigator.clipboard.readText();
  } catch (error) {
    console.error('Error al leer del portapapeles:', error);
    return null;
  }
}

// Exportar funciones para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    sanitizeText,
    findEditable,
    findSendButton,
    tryInjectToPage,
    getLastResponseText
  };
}
