// ARCHIVO: storage.js
// -------------------------------------
// Módulo para manejo de localStorage y persistencia

const LS_KEY = 'pec_log_v1';
const LS_COUNTER = 'pec_log_counter';

/**
 * Carga el estado desde localStorage
 * @returns {Object} {arr: Array, counter: number}
 */
function loadState() {
  const raw = localStorage.getItem(LS_KEY);
  const arr = raw ? JSON.parse(raw) : [];
  const counter = parseInt(localStorage.getItem(LS_COUNTER) || '1', 10);
  return { arr, counter };
}

/**
 * Guarda el estado en localStorage
 * @param {Array} arr - Array de entradas
 * @param {number} counter - Contador actual
 */
function saveState(arr, counter) {
  localStorage.setItem(LS_KEY, JSON.stringify(arr));
  localStorage.setItem(LS_COUNTER, '' + counter);
}

/**
 * Añade una nueva entrada al log
 * @param {Object} entry - Entrada a añadir
 * @param {Object} state - Estado actual
 * @returns {Object} Estado actualizado
 */
function appendLog(entry, state) {
  state.arr.push(entry);
  state.counter = state.counter + 1;
  saveState(state.arr, state.counter);
  return state;
}

/**
 * Limpia el log y resetea el contador
 * @returns {Object} Estado limpio
 */
function clearLog() {
  const cleanState = { arr: [], counter: 1 };
  saveState(cleanState.arr, cleanState.counter);
  return cleanState;
}

/**
 * Genera el contenido para descarga
 * @param {Array} entries - Entradas del log
 * @returns {string} Contenido formateado
 */
function generateDownloadContent(entries) {
  return entries.map(e => e.header + e.body + e.footer).join('\n\n-----\n\n');
}

// Exportar funciones para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    loadState,
    saveState,
    appendLog,
    clearLog,
    generateDownloadContent
  };
}
