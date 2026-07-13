/**
 * station_progresivo.js
 * ═══════════════════════════════════════════════════════════════
 * Lógica para Estación Central - Versión Progresiva
 * 
 * Arquitectura modular para permitir expansión a fases posteriores
 * (Dashboard, Neuronal Visual, etc.)
 * ═══════════════════════════════════════════════════════════════
 */

// ═══════════════════════════════════════════════════════════════
// CONFIGURACIÓN GLOBAL
// ═══════════════════════════════════════════════════════════════
const CONFIG = {
  mcp_server: 'http://127.0.0.1:8090',
  protocol_id: 'NEUROBIT_MSG_v0',
  version: '0.1',
  storage_key: 'neurobit_session_historial',
  message_limit: 25000,
};

// ═══════════════════════════════════════════════════════════════
// MÓDULO: CRIPTOGRAFÍA Y HASH
// ═══════════════════════════════════════════════════════════════
const Crypto = {
  /**
   * Calcula SHA1 simple (8 primeros caracteres como en SIMON validator)
   * Nota: Usar crypto.subtle en navegadores modernos
   */
  sha1Short: async (text) => {
    try {
      const buffer = new TextEncoder().encode(text);
      const hashBuffer = await crypto.subtle.digest('SHA-1', buffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      return hashHex.substring(0, 12);
    } catch (e) {
      console.warn('SHA-1 no disponible, usando fallback', e);
      return Crypto.simpleHash(text);
    }
  },

  /**
   * Fallback: hash simple sin crypto.subtle
   */
  simpleHash: (text) => {
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
      const char = text.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convertir a 32-bit integer
    }
    return Math.abs(hash).toString(16).padStart(12, '0');
  },

  /**
   * Genera UUID v4
   */
  uuid: () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  },

  /**
   * ISO8601 con zona UTC
   */
  isoTimestamp: () => {
    return new Date().toISOString();
  }
};

// ═══════════════════════════════════════════════════════════════
// MÓDULO: VALIDACIÓN SIMON
// ═══════════════════════════════════════════════════════════════
const SimonValidator = {
  /**
   * Valida campos requeridos para mensaje protocolar
   */
  validateRequired: (envelope) => {
    const required = ['PROTOCOL_ID', 'VERSION', 'MESSAGE_ID', 'SESSION_ID', 
                     'CREATED_AT', 'ORIGEN', 'FRAGMENT', 'CONTENT', 'MESSAGE_HASH'];
    const missing = required.filter(key => !(key in envelope));
    return {
      valid: missing.length === 0,
      missing,
    };
  },

  /**
   * Valida estructura FRAGMENT
   */
  validateFragment: (fragment) => {
    return fragment && typeof fragment === 'object' && 
           'INDEX' in fragment && 'TOTAL' in fragment;
  },

  /**
   * Valida ISO8601
   */
  validateTimestamp: (timestamp) => {
    try {
      new Date(timestamp.replace('Z', '+00:00'));
      return true;
    } catch {
      return false;
    }
  },

  /**
   * Validación completa (llamado después de enviar)
   */
  validateFull: (envelope) => {
    const errors = [];

    // Check required
    const requiredCheck = SimonValidator.validateRequired(envelope);
    if (!requiredCheck.valid) {
      errors.push(`Campos faltantes: ${requiredCheck.missing.join(', ')}`);
    }

    // Check timestamp
    if (envelope.CREATED_AT && !SimonValidator.validateTimestamp(envelope.CREATED_AT)) {
      errors.push('CREATED_AT no es válido ISO8601');
    }

    // Check fragment
    if (envelope.FRAGMENT && !SimonValidator.validateFragment(envelope.FRAGMENT)) {
      errors.push('FRAGMENT debe ser {INDEX, TOTAL}');
    }

    // Check content no vacío
    if (!envelope.CONTENT || envelope.CONTENT.trim() === '') {
      errors.push('CONTENT no puede estar vacío');
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }
};

// ═══════════════════════════════════════════════════════════════
// MÓDULO: ALMACENAMIENTO LOCAL
// ═══════════════════════════════════════════════════════════════
const Storage = {
  /**
   * Guarda mensaje en historial local
   */
  saveMessage: (envelope) => {
    try {
      const historial = Storage.getHistorial();
      historial.push({
        ...envelope,
        saved_at: new Date().toISOString(),
      });
      localStorage.setItem(CONFIG.storage_key, JSON.stringify(historial));
      return true;
    } catch (e) {
      console.error('Error guardando mensaje:', e);
      return false;
    }
  },

  /**
   * Carga historial desde localStorage
   */
  getHistorial: () => {
    try {
      const data = localStorage.getItem(CONFIG.storage_key);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error('Error cargando historial:', e);
      return [];
    }
  },

  /**
   * Limpia historial
   */
  clearHistorial: () => {
    try {
      localStorage.removeItem(CONFIG.storage_key);
      return true;
    } catch (e) {
      console.error('Error limpiando historial:', e);
      return false;
    }
  },

  /**
   * Exporta historial a JSON
   */
  exportJson: () => {
    const historial = Storage.getHistorial();
    return JSON.stringify(historial, null, 2);
  },

  /**
   * Exporta historial a CSV
   */
  exportCsv: () => {
    const historial = Storage.getHistorial();
    if (!historial.length) return '';

    const headers = ['MESSAGE_ID', 'ORIGEN', 'CREATED_AT', 'CONTENT', 'saved_at'];
    const rows = historial.map(msg => 
      headers.map(h => `"${(msg[h] || '').toString().replace(/"/g, '""')}"`).join(',')
    );

    return [headers.join(','), ...rows].join('\n');
  }
};

// ═══════════════════════════════════════════════════════════════
// MÓDULO: API MCP (Comunicación con servidor)
// ═══════════════════════════════════════════════════════════════
const MCP = {
  /**
   * Escribe mensaje en Arca (mediante POST /write_arca)
   */
  writeArca: async (envelope) => {
    try {
      const response = await fetch(`${CONFIG.mcp_server}/write_arca`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(envelope),
      });

      if (response.ok) {
        return { ok: true, data: await response.json() };
      } else {
        return { ok: false, error: `HTTP ${response.status}` };
      }
    } catch (e) {
      // Si no hay servidor MCP, es OK (fase 1 es local)
      console.warn('MCP server no disponible:', e.message);
      return { ok: false, error: e.message };
    }
  },

  /**
   * Lee últimos mensajes desde Arca
   */
  readArca: async (limit = 5) => {
    try {
      const response = await fetch(`${CONFIG.mcp_server}/read_arca?limit=${limit}`);
      if (response.ok) {
        return { ok: true, data: await response.json() };
      } else {
        return { ok: false, error: `HTTP ${response.status}` };
      }
    } catch (e) {
      console.warn('MCP server no disponible:', e.message);
      return { ok: false, error: e.message };
    }
  },

  /**
   * Valida mensaje con SIMON (opcional, para fases posteriores)
   */
  validateWithSimon: async (envelope) => {
    try {
      const response = await fetch(`${CONFIG.mcp_server}/validate_with_simon`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(envelope),
      });

      if (response.ok) {
        return { ok: true, data: await response.json() };
      } else {
        return { ok: false, error: `HTTP ${response.status}` };
      }
    } catch (e) {
      console.warn('MCP server no disponible:', e.message);
      return { ok: false, error: e.message };
    }
  }
};

// ═══════════════════════════════════════════════════════════════
// MÓDULO: CONSTRUCTOR DE ENVELOPES
// ═══════════════════════════════════════════════════════════════
const EnvelopeBuilder = {
  /**
   * Construye envelope NEUROBIT_MSG_v0.1 completo
   */
  build: async (senderName, sessionId, content) => {
    const messageId = Crypto.uuid();
    const createdAt = Crypto.isoTimestamp();
    
    // Calcular hash SIMON (contenido + origen + timestamp)
    const hashInput = content + senderName + createdAt;
    const messageHash = await Crypto.sha1Short(hashInput);

    return {
      PROTOCOL_ID: CONFIG.protocol_id,
      VERSION: CONFIG.version,
      MESSAGE_ID: messageId,
      SESSION_ID: sessionId,
      CREATED_AT: createdAt,
      ORIGEN: senderName || 'ANONYMOUS',
      MESSAGE_HASH: messageHash,
      FRAGMENT: {
        INDEX: 1,
        TOTAL: 1,
      },
      CONTENT: content,
      TAGS: ['generated_by_station_progresivo'],
    };
  }
};

// ═══════════════════════════════════════════════════════════════
// MÓDULO: UI (Actualización de Interfaz)
// ═══════════════════════════════════════════════════════════════
const UI = {
  /**
   * Actualiza validación en vivo
   */
  updateValidation: async (content, senderName) => {
    const validationInfo = document.getElementById('validationInfo');
    const hashIcon = document.getElementById('hashIcon');
    const hashValue = document.getElementById('hashValue');
    const lengthIcon = document.getElementById('lengthIcon');
    const lengthValue = document.getElementById('lengthValue');

    if (content.length > 0) {
      validationInfo.classList.add('active');

      // Calcular hash
      const hashInput = content + (senderName || 'ANONYMOUS') + Crypto.isoTimestamp();
      const hash = await Crypto.sha1Short(hashInput);
      hashValue.textContent = hash;

      // Longitud
      const len = content.length;
      lengthValue.textContent = len;
      
      if (len > CONFIG.message_limit) {
        lengthIcon.className = 'validation-icon error';
        lengthIcon.textContent = '✕';
      } else if (len > CONFIG.message_limit * 0.9) {
        lengthIcon.className = 'validation-icon warn';
        lengthIcon.textContent = '⚠';
      } else {
        lengthIcon.className = 'validation-icon ok';
        lengthIcon.textContent = '✓';
      }
    } else {
      validationInfo.classList.remove('active');
    }
  },

  /**
   * Muestra mensaje de estado
   */
  showStatus: (message, type = 'success', duration = 3000) => {
    const statusMsg = document.getElementById('statusMessage');
    statusMsg.textContent = message;
    statusMsg.className = `status-message active ${type}`;

    if (duration) {
      setTimeout(() => {
        statusMsg.classList.remove('active');
      }, duration);
    }
  },

  /**
   * Actualiza encabezado de estado de conexión
   */
  updateConnectionStatus: (connected) => {
    const statusText = document.getElementById('statusText');
    const statusDot = document.querySelector('.status-dot');
    
    if (connected) {
      statusText.textContent = '🟢 Conectado';
      statusDot.style.background = '#22c55e';
    } else {
      statusText.textContent = '🔴 Desconectado (modo local)';
      statusDot.style.background = '#ef4444';
    }
  },

  /**
   * Actualiza historial visual
   */
  updateHistorial: () => {
    const historial = Storage.getHistorial();
    const container = document.getElementById('historialContainer');
    const count = document.getElementById('historialCount');

    count.textContent = `${historial.length} registros`;

    if (historial.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; color: var(--color-text-muted); padding: 30px;">
          Sin mensajes aún. ¡Envía el primero!
        </div>
      `;
      return;
    }

    container.innerHTML = historial
      .slice()
      .reverse()
      .map((msg, idx) => `
        <div class="historial-entry" onclick="UI.showMessageDetail('${msg.MESSAGE_ID}')">
          <div class="historial-entry-header">
            <span class="historial-entry-number">#${historial.length - idx}</span>
            <span class="historial-entry-time">${new Date(msg.CREATED_AT).toLocaleTimeString()}</span>
          </div>
          <div style="margin-bottom: 6px; font-size: 12px; color: var(--color-accent-primary); font-weight: 500;">
            ${msg.ORIGEN}
          </div>
          <div class="historial-entry-preview">
            <div class="historial-entry-content">${msg.CONTENT.substring(0, 100)}</div>
          </div>
        </div>
      `).join('');
  },

  /**
   * Muestra detalle de mensaje (para futuras fases)
   */
  showMessageDetail: (messageId) => {
    const historial = Storage.getHistorial();
    const msg = historial.find(m => m.MESSAGE_ID === messageId);
    if (msg) {
      alert(`Mensaje: ${msg.MESSAGE_ID}\n\nOrigen: ${msg.ORIGEN}\nContenido:\n\n${msg.CONTENT}`);
    }
  },

  /**
   * Limpia formulario
   */
  clearForm: () => {
    document.getElementById('messageForm').reset();
    document.getElementById('messageContent').focus();
  }
};

// ═══════════════════════════════════════════════════════════════
// MÓDULO: EVENT LISTENERS
// ═══════════════════════════════════════════════════════════════
const Events = {
  init: () => {
    // Form submit
    document.getElementById('messageForm').addEventListener('submit', Events.handleSubmit);

    // Validación en vivo
    document.getElementById('messageContent').addEventListener('input', async (e) => {
      const senderName = document.getElementById('senderName').value;
      await UI.updateValidation(e.target.value, senderName);
    });

    // Botones secundarios
    document.getElementById('btnClear').addEventListener('click', (e) => {
      e.preventDefault();
      UI.clearForm();
    });

    document.getElementById('btnExport').addEventListener('click', Events.handleExport);
    document.getElementById('btnClearHistory').addEventListener('click', Events.handleClearHistory);

    // Verificar conexión con MCP
    Events.checkMcpConnection();
  },

  /**
   * Envío de formulario
   */
  handleSubmit: async (e) => {
    e.preventDefault();

    const senderName = document.getElementById('senderName').value.trim();
    const sessionId = document.getElementById('sessionId').value.trim();
    const content = document.getElementById('messageContent').value.trim();

    // Validaciones básicas
    if (!senderName) {
      UI.showStatus('⚠️ Por favor, ingresa tu nombre/identidad', 'warning');
      return;
    }

    if (!content) {
      UI.showStatus('⚠️ Por favor, escribe un mensaje', 'warning');
      return;
    }

    if (content.length > CONFIG.message_limit) {
      UI.showStatus('❌ El mensaje es demasiado largo', 'error');
      return;
    }

    try {
      // Construir envelope
      const envelope = await EnvelopeBuilder.build(senderName, sessionId, content);

      // Validar completitud
      const validation = SimonValidator.validateFull(envelope);
      if (!validation.valid) {
        UI.showStatus(`❌ Validación SIMON falló: ${validation.errors[0]}`, 'error');
        return;
      }

      // Guardar localmente
      Storage.saveMessage(envelope);
      UI.updateHistorial();
      UI.showStatus('✅ Mensaje guardado localmente', 'success');

      // Intentar enviar a MCP (opcional en fase 1)
      const mcpResult = await MCP.writeArca(envelope);
      if (mcpResult.ok) {
        UI.showStatus('✅ Mensaje también guardado en Arca Central', 'success', 2000);
      } else {
        console.warn('MCP offline, pero guardado localmente OK');
      }

      // Limpiar formulario
      UI.clearForm();

    } catch (e) {
      UI.showStatus(`❌ Error: ${e.message}`, 'error');
      console.error(e);
    }
  },

  /**
   * Exportar historial
   */
  handleExport: () => {
    const historial = Storage.getHistorial();
    if (historial.length === 0) {
      UI.showStatus('⚠️ No hay mensajes para exportar', 'warning');
      return;
    }

    const json = Storage.exportJson();
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `neurobit_historial_${new Date().getTime()}.json`;
    a.click();
    URL.revokeObjectURL(url);

    UI.showStatus('💾 Historial exportado', 'success');
  },

  /**
   * Limpiar historial
   */
  handleClearHistory: () => {
    if (confirm('⚠️ ¿Estás seguro de que quieres borrar TODO el historial? No se puede deshacer.')) {
      Storage.clearHistorial();
      UI.updateHistorial();
      UI.showStatus('🧹 Historial eliminado', 'success');
    }
  },

  /**
   * Verifica conexión con MCP server
   */
  checkMcpConnection: async () => {
    try {
      const response = await fetch(`${CONFIG.mcp_server}/status`, {
        method: 'GET',
        timeout: 2000,
      });
      if (response.ok) {
        UI.updateConnectionStatus(true);
      } else {
        UI.updateConnectionStatus(false);
      }
    } catch {
      UI.updateConnectionStatus(false);
    }
  }
};

// ═══════════════════════════════════════════════════════════════
// INICIALIZACIÓN
// ═══════════════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  Events.init();
  UI.updateHistorial();
  
  // Inicializar Matriz 13x13 (si arquetipos.js está cargado)
  if (typeof MatrizArquetipos !== 'undefined') {
    console.log('🧬 Inicializando Matriz de Arquetipos...');
    
    // Crear contenedor para la matriz si no existe
    const mainContent = document.querySelector('.main-content');
    const matrizContainer = document.createElement('div');
    matrizContainer.id = 'matriz-container';
    
    // Insertar DESPUÉS del área de input pero ANTES del historial
    const inputArea = document.querySelector('.input-area');
    const historialSection = document.querySelector('.section');
    if (inputArea && historialSection) {
      inputArea.parentNode.insertBefore(matrizContainer, historialSection);
    } else {
      mainContent.appendChild(matrizContainer);
    }
    
    // Inicializar MatrizUI
    window.matrizUI = new MatrizUI('#matriz-container', 13);
    console.log('✓ Matriz 13x13 lista');
  }
  
  // Focus en el primer campo
  document.getElementById('senderName').focus();

  console.log('✅ Estación Central - Versión Progresiva inicializada');
  console.log('📡 MCP Server:', CONFIG.mcp_server);
  console.log('📦 Protocol:', CONFIG.protocol_id);
});
