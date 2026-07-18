// ============================================================================
// NEUROBIT_TRACKER.JS - DOM KEYLOGGER + PERSISTENT APPEND-ONLY LOGGING
// ============================================================================
// 
// Propósito: Capturar TODAS las acciones del usuario sin pérdida de datos
// - DOM events (input, click, change)
// - Temporal backup (antes de que se pierda)
// - Persistent append-only log (permanente)
// - Recovery mechanism (recupera si se borra)
//
// Integración: popup.js debe incluir este script
// ============================================================================

const NeurobitTracker = (() => {
  // Estado local (memoria de esta sesión)
  let sessionLog = [];
  let messageBuffer = ""; // Buffer temporal de lo que escribió el usuario
  let lastCheckpoint = null;

  // ========================================================================
  // PARTE 1: CAPTURA DE EVENTOS (DOM Keylogger)
  // ========================================================================

  function initDOMTracking() {
    console.log("[TRACKER] 🔴 Iniciando captura de eventos DOM...");

    // CAPTURA 1: Textarea "mensaje"
    const messageInput = document.getElementById("mensaje");
    if (messageInput) {
      messageInput.addEventListener("input", (e) => {
        messageBuffer = e.target.value;
        logEvent("TEXT_INPUT", {
          length: messageBuffer.length,
          preview: messageBuffer.substring(0, 50)
        });
      });

      messageInput.addEventListener("focus", (e) => {
        logEvent("TEXTAREA_FOCUS", {
          currentContent: e.target.value.substring(0, 50)
        });
      });

      messageInput.addEventListener("blur", (e) => {
        // CHECKPOINT: Guardar estado antes de que se pierda
        saveCheckpoint("TEXTAREA_BLUR", e.target.value);
      });
    }

    // CAPTURA 2: Input "destinatario"
    const recipientInput = document.getElementById("destinatario");
    if (recipientInput) {
      recipientInput.addEventListener("change", (e) => {
        logEvent("RECIPIENT_CHANGED", {
          value: e.target.value
        });
      });
    }

    // CAPTURA 3: Botón "Enviar"
    const btnEnviar = document.getElementById("enviarBtn");
    if (btnEnviar) {
      btnEnviar.addEventListener("click", (e) => {
        const msg = document.getElementById("mensaje").value;
        logEvent("BUTTON_ENVIAR_CLICKED", {
          messageLength: msg.length,
          message: msg
        });
        // Guardar snapshot ANTES de enviar
        saveCheckpoint("BEFORE_SEND", msg);
      });
    }

    // CAPTURA 4: Botón "Guardar"
    const btnGuardar = document.getElementById("guardarBtn");
    if (btnGuardar) {
      btnGuardar.addEventListener("click", (e) => {
        const msg = document.getElementById("mensaje").value;
        logEvent("BUTTON_GUARDAR_CLICKED", {
          messageLength: msg.length,
          message: msg
        });
        // Guardar snapshot DESPUÉS de hacer click
        setTimeout(() => {
          const msgAfter = document.getElementById("mensaje").value;
          logEvent("AFTER_GUARDAR_SNAPSHOT", {
            messageWasCleared: msgAfter === "",
            originalContent: msg
          });
          if (msg !== "") {
            saveCheckpoint("POST_GUARDAR", msg);
          }
        }, 500);
      });
    }

    // CAPTURA 5: Botón "Descargar"
    const btnDescargar = document.getElementById("descargarBtn");
    if (btnDescargar) {
      btnDescargar.addEventListener("click", (e) => {
        logEvent("BUTTON_DESCARGAR_CLICKED", {
          sessionLogLength: sessionLog.length
        });
      });
    }

    // CAPTURA 6: Status indicator changes (via MutationObserver)
    const statusDiv = document.getElementById("estado");
    if (statusDiv) {
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.type === "childList" || mutation.type === "characterData") {
            logEvent("STATUS_CHANGED", {
              newStatus: statusDiv.innerText
            });
          }
        });
      });
      observer.observe(statusDiv, {
        characterData: true,
        childList: true,
        subtree: true
      });
    }

    console.log("[TRACKER] ✅ Tracking de eventos inicializado");
  }

  // ========================================================================
  // PARTE 2: LOGGING LOCAL (en memoria)
  // ========================================================================

  function logEvent(eventType, data) {
    const entry = {
      timestamp: new Date().toISOString(),
      type: eventType,
      data: data
    };

    sessionLog.push(entry);
    console.log(`[TRACKER] 📝 ${eventType}:`, data);

    // CRÍTICO: Guardar en chrome.storage para persistencia
    persistLog(entry);
  }

  // ========================================================================
  // PARTE 3: PERSISTENCIA APPEND-ONLY (chrome.storage)
  // ========================================================================

  function persistLog(entry) {
    chrome.storage.local.get({ neurobit_log: [] }, (res) => {
      const log = res.neurobit_log || [];
      log.push(entry);

      // Mantener máximo 1000 entradas (límite de storage)
      if (log.length > 1000) {
        log.shift(); // Remover la más antigua
      }

      chrome.storage.local.set({ neurobit_log: log }, () => {
        // Log persistido exitosamente
      });
    });
  }

  // ========================================================================
  // PARTE 4: CHECKPOINTS (Recuperación ante pérdida de datos)
  // ========================================================================

  function saveCheckpoint(reason, content) {
    lastCheckpoint = {
      timestamp: new Date().toISOString(),
      reason: reason,
      content: content,
      length: content.length
    };

    chrome.storage.local.get({ neurobit_checkpoints: [] }, (res) => {
      const checkpoints = res.neurobit_checkpoints || [];
      checkpoints.push(lastCheckpoint);

      // Mantener solo últimos 20 checkpoints
      if (checkpoints.length > 20) {
        checkpoints.shift();
      }

      chrome.storage.local.set({ neurobit_checkpoints: checkpoints }, () => {
        logEvent("CHECKPOINT_SAVED", {
          reason: reason,
          contentLength: content.length
        });
      });
    });
  }

  // ========================================================================
  // PARTE 5: RECOVERY (Recuperar texto perdido)
  // ========================================================================

  function recoverLastMessage() {
    return new Promise((resolve) => {
      chrome.storage.local.get({ neurobit_checkpoints: [] }, (res) => {
        const checkpoints = res.neurobit_checkpoints || [];
        if (checkpoints.length === 0) {
          resolve(null);
          return;
        }

        // Obtener el último checkpoint que NO fue causado por BEFORE_SEND
        const lastValid = checkpoints
          .reverse()
          .find((cp) => cp.reason !== "BEFORE_SEND" && cp.content.length > 0);

        resolve(lastValid ? lastValid.content : null);
      });
    });
  }

  // ========================================================================
  // PARTE 6: EXPORT (Descargar logs como archivo JSONL)
  // ========================================================================

  function exportLogs() {
    return new Promise((resolve) => {
      chrome.storage.local.get({ neurobit_log: [] }, (res) => {
        const log = res.neurobit_log || [];

        // Convertir a JSONL (una línea JSON por entrada)
        const jsonl = log.map((entry) => JSON.stringify(entry)).join("\n");

        const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
        const filename = `neurobit_log_${timestamp}.jsonl`;

        // Descargar usando data URL
        const dataUrl =
          "data:text/plain;charset=utf-8," + encodeURIComponent(jsonl);

        chrome.downloads.download({
          url: dataUrl,
          filename: filename,
          saveAs: false
        });

        resolve({
          success: true,
          entries: log.length,
          filename: filename
        });
      });
    });
  }

  // ========================================================================
  // PARTE 7: ESTADÍSTICAS (Para debugging)
  // ========================================================================

  function getStats() {
    return new Promise((resolve) => {
      chrome.storage.local.get(
        { neurobit_log: [], neurobit_checkpoints: [] },
        (res) => {
          resolve({
            logEntries: (res.neurobit_log || []).length,
            checkpoints: (res.neurobit_checkpoints || []).length,
            sessionLogSize: sessionLog.length,
            lastCheckpoint: lastCheckpoint
          });
        }
      );
    });
  }

  // ========================================================================
  // PARTE 8: INICIALIZACIÓN
  // ========================================================================

  function init() {
    console.log("[TRACKER] 🚀 NeurobitTracker inicializando...");

    // Esperar a que el DOM esté cargado
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => {
        initDOMTracking();
      });
    } else {
      initDOMTracking();
    }

    console.log("[TRACKER] ✅ NeurobitTracker listo");
  }

  // ========================================================================
  // API PÚBLICA
  // ========================================================================

  return {
    init: init,
    recoverLastMessage: recoverLastMessage,
    exportLogs: exportLogs,
    getStats: getStats,
    logEvent: logEvent,
    saveCheckpoint: saveCheckpoint,
    getMessageBuffer: () => messageBuffer,
    getSessionLog: () => sessionLog
  };
})();

// ============================================================================
// AUTO-INICIALIZAR
// ============================================================================

if (typeof module !== "undefined" && module.exports) {
  module.exports = NeurobitTracker;
} else {
  // Auto-inicializar en popup
  NeurobitTracker.init();
}
