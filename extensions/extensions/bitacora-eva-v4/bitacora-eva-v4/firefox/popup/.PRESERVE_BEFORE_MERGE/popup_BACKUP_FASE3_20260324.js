// ============================================================================
// BITACORA 3.0 - POPUP.JS - VERSIÓN LIMPIA Y FUNCIONAL
// ============================================================================

document.addEventListener("DOMContentLoaded", () => {
  const btnEnviar = document.getElementById("enviarBtn");
  const btnGuardar = document.getElementById("guardarBtn");
  const btnDescargar = document.getElementById("descargarBtn");
  const estado = document.getElementById("estado");
  const messageInput = document.getElementById("mensaje");

  // ========== RECOVERY: Restaurar mensaje anterior si se perdió ==========
  // Cuando el popup se abre, intenta recuperar el último mensaje guardado
  (async () => {
    const lastMessage = await NeurobitTracker.recoverLastMessage();
    if (lastMessage && messageInput.value === "") {
      messageInput.value = lastMessage;
      estado.innerText = "🔄 Mensaje recuperado del checkpoint";
      setTimeout(() => {
        estado.innerText = "✅ Listo";
      }, 2000);
    }
  })();

  // ========== BUTTON: ENVIAR ==========
  // Inyecta mensaje en ChatGPT y lo envía automáticamente
  btnEnviar.addEventListener("click", () => {
    const destinatario = document.getElementById("destinatario").value || "ChatGPT";
    const mensaje = document.getElementById("mensaje").value;

    if (!mensaje.trim()) {
      estado.innerText = "⚠️ Escribe un mensaje";
      return;
    }

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const url = tabs[0].url;
      if (url.includes("chat.openai.com") || url.includes("chatgpt.com")) {
        chrome.scripting.executeScript({
          target: { tabId: tabs[0].id },
          func: (dest, msg) => {
            window.postMessage({ type: "EVA_SEND", dest, msg }, "*");
          },
          args: [destinatario, mensaje]
        });
        estado.innerText = "📤 Inyectando en ChatGPT...";
      } else {
        estado.innerText = "⚠️ Abre ChatGPT primero";
      }
    });
  });

  // ========== BUTTON: GUARDAR ==========
  // Guarda entrada ACTUAL en chrome.storage (NO descarga) CON VALIDACIÓN
  btnGuardar.addEventListener("click", () => {
    const destinatario = document.getElementById("destinatario").value || "ChatGPT";
    const mensaje = document.getElementById("mensaje").value;

    if (!mensaje.trim()) {
      console.warn("⚠️ [GUARDAR] Intento de guardar mensaje vacío");
      estado.innerText = "⚠️ Nada que guardar";
      return;
    }

    console.log(`💾 [GUARDAR] Guardando mensaje...`);
    console.log(`  - Destinatario: ${destinatario}`);
    console.log(`  - Longitud: ${mensaje.length} caracteres`);

    const entrada = {
      source: "popup-manual",
      destinatario: destinatario,
      text: mensaje,
      ts: Date.now()
    };

    // Validar que entrada tiene todos los campos requeridos
    if (!entrada.text || !entrada.destinatario) {
      console.error("❌ [GUARDAR] Entrada incompleta:", entrada);
      estado.innerText = "⚠️ Error: datos incompletos";
      return;
    }

    chrome.storage.local.get({ bitacora: [] }, (res) => {
      try {
        const bitacora = res.bitacora || [];
        console.log(`📊 [GUARDAR] Bitácora actual: ${bitacora.length} entradas`);
        
        bitacora.push(entrada);
        console.log(`✅ [GUARDAR] Nueva entrada agregada. Total: ${bitacora.length}`);
        
        chrome.storage.local.set({ bitacora }, () => {
          if (chrome.runtime.lastError) {
            console.error("❌ [GUARDAR] Error al guardar en storage:", chrome.runtime.lastError);
            estado.innerText = "⚠️ Error al guardar (ver consola)";
            return;
          }
          
          console.log(`✅ [GUARDAR] Guardado exitosamente en chrome.storage.local`);
          estado.innerText = "✅ Guardado en memoria";
          
          // Log en audit trail
          NeurobitTracker.logEvent("MESSAGE_SAVED", {
            destinatario: destinatario,
            length: mensaje.length,
            timestamp: new Date().toISOString()
          });
          
          document.getElementById("mensaje").value = ""; // limpiar textarea
          setTimeout(() => {
            estado.innerText = "✅ Listo";
          }, 2000);
        });
      } catch (error) {
        console.error("❌ [GUARDAR] Error procesando storage:", error);
        estado.innerText = "⚠️ Error al guardar";
      }
    });
  });

  // ========== BUTTON: DESCARGAR BITÁCORA ==========
  // Descarga TODAS las entradas guardadas como .txt CON LOGGING COMPLETO
  btnDescargar.addEventListener("click", async () => {
    console.log("🔵 [DESCARGA] Iniciando proceso de descarga...");
    estado.innerText = "⏳ Preparando descarga...";
    
    try {
      chrome.storage.local.get({ bitacora: [] }, (res) => {
        try {
          const bitacora = res.bitacora || [];
          console.log(`📊 [DESCARGA] Bitácora obtenida. Entradas: ${bitacora.length}`);

          if (bitacora.length === 0) {
            console.warn("⚠️ [DESCARGA] No hay entradas guardadas");
            estado.innerText = "⚠️ No hay entradas guardadas";
            return;
          }

          console.log(`📝 [DESCARGA] Formateando ${bitacora.length} entradas...`);
          // Formatear entradas CON VALIDACIÓN
          const lineas = bitacora.map((e, i) => {
            if (!e.text) {
              console.warn(`⚠️ [DESCARGA] Entrada ${i + 1} tiene text vacío`);
              return "";
            }
            const ts = new Date(e.ts || Date.now()).toLocaleString();
            return `--- Entrada ${i + 1} — ${ts} ---\nDe: ${e.destinatario || "Desconocido"}\n${"-".repeat(40)}\n${e.text}\n${"-".repeat(40)}\nFIN DEL MENSAJE\n`;
          }).filter(line => line.length > 0).join("\n\n");

          console.log(`✅ [DESCARGA] Formato completado. Bytes: ${lineas.length}`);

          // Generar URL data:// CON VALIDACIÓN
          try {
            const dataUrl = "data:text/plain;charset=utf-8," + encodeURIComponent(lineas);
            const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
            
            console.log(`📥 [DESCARGA] Iniciando chrome.downloads.download...`);
            console.log(`  - Filename: bitacora_eva_${timestamp}.txt`);
            console.log(`  - Tamaño: ${lineas.length} caracteres`);
            
            // Usar chrome.downloads.download
            chrome.downloads.download(
              {
                url: dataUrl,
                filename: `bitacora_eva_${timestamp}.txt`,
                saveAs: false
              },
              (downloadId) => {
                if (chrome.runtime.lastError) {
                  console.error("❌ [DESCARGA] Error en chrome.downloads:", chrome.runtime.lastError);
                  estado.innerText = "❌ Error al descargar (ver consola)";
                  NeurobitTracker.logEvent("DOWNLOAD_ERROR", {
                    error: chrome.runtime.lastError?.message || "Unknown",
                    timestamp: new Date().toISOString()
                  });
                  return;
                }
                
                console.log(`✅ [DESCARGA] Descarga iniciada exitosamente`);
                console.log(`  - Download ID: ${downloadId}`);
                estado.innerText = "✅ Bitácora descargada (revisar carpeta Descargas)";
                
                // Log en audit trail
                NeurobitTracker.logEvent("BITACORA_DOWNLOADED", {
                  entries: bitacora.length,
                  bytes: lineas.length,
                  timestamp: new Date().toISOString(),
                  download_id: downloadId
                });
                
                setTimeout(() => {
                  estado.innerText = "✅ Listo";
                }, 3000);
              }
            );
          } catch (urlError) {
            console.error("❌ [DESCARGA] Error al crear data URL:", urlError);
            estado.innerText = "❌ Error al procesar datos";
            NeurobitTracker.logEvent("DOWNLOAD_URL_ERROR", {
              error: urlError.message,
              timestamp: new Date().toISOString()
            });
          }
        } catch (processError) {
          console.error("❌ [DESCARGA] Error procesando respuesta de storage:", processError);
          estado.innerText = "❌ Error al acceder a storage";
          NeurobitTracker.logEvent("DOWNLOAD_PROCESS_ERROR", {
            error: processError.message,
            timestamp: new Date().toISOString()
          });
        }
      });
    } catch (outerError) {
      console.error("❌ [DESCARGA] Error exterior:", outerError);
      estado.innerText = "❌ Error general en descarga";
      NeurobitTracker.logEvent("DOWNLOAD_OUTER_ERROR", {
        error: outerError.message,
        timestamp: new Date().toISOString()
      });
    }
  });

  // ========== EXTRA: Keyboard shortcut para descargar LOGS de tracking ==========
  // Presiona Ctrl+Shift+L para descargar el log de eventos
  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === "L") {
      e.preventDefault();
      estado.innerText = "📊 Descargando logs de tracking...";
      
      NeurobitTracker.exportLogs().then((result) => {
        estado.innerText = `📊 Logs descargados (${result.entries} eventos)`;
        setTimeout(() => {
          estado.innerText = "✅ Listo";
        }, 2000);
      });
    }
  });

  // ========== DEBUG: Log de estadísticas en consola ==========
  // Para debugging, muestra estadísticas del tracker
  window.logStats = async () => {
    const stats = await NeurobitTracker.getStats();
    console.table(stats);
    return stats;
  };

  // ========================================
  // PASO 3: FEEDBACK VISUAL COPY
  // ========================================
  // Listener global para cualquier acción COPY (manual o programática)
  document.addEventListener("copy", async (e) => {
    const copiedText = e.clipboardData.getData("text");
    
    if (copiedText.trim()) {
      // Generar ID único para este COPY
      const copyId = Math.floor(Math.random() * 10000);
      
      // Mostrar feedback visual (cambiar estado)
      const originalText = estado.innerText;
      estado.innerText = `✓ COPIADO #${copyId} AL ARCA`;
      estado.style.backgroundColor = "#4CAF50";
      estado.style.color = "white";
      estado.style.borderLeftColor = "#4CAF50";
      
      // Log en audit trail
      NeurobitTracker.logEvent("COPY_TO_CLIPBOARD", {
        copy_id: copyId,
        length: copiedText.length,
        timestamp: new Date().toISOString()
      });
      
      // Volver a estado original después de 2s
      setTimeout(() => {
        estado.innerText = originalText;
        estado.style.backgroundColor = "";
        estado.style.color = "";
        estado.style.borderLeftColor = "";
      }, 2000);
    }
  });

  // ========================================
  // PASO 3: LISTENER ALTERNATIVO (para historial/items específicos)
  // ========================================
  // Si existen botones COPY en el futuro historial, capturarlos también
  document.addEventListener("click", async (e) => {
    if (e.target.classList && e.target.classList.contains("copy-btn")) {
      e.preventDefault();
      
      const messageId = e.target.dataset.messageId || "UNKNOWN";
      const messageItem = e.target.closest(".history-item");
      
      if (messageItem) {
        const contenido = messageItem.textContent.trim();
        
        // Copiar al clipboard
        try {
          await navigator.clipboard.writeText(contenido);
          
          // Feedback visual
          const originalText = e.target.textContent;
          e.target.textContent = `✓ COPIADO #${messageId}`;
          e.target.style.backgroundColor = "#4CAF50";
          e.target.style.color = "white";
          
          // Log
          NeurobitTracker.logEvent("COPY_HISTORY_ITEM", {
            message_id: messageId,
            length: contenido.length,
            timestamp: new Date().toISOString()
          });
          
          // Volver a original después de 2s
          setTimeout(() => {
            e.target.textContent = originalText;
            e.target.style.backgroundColor = "";
            e.target.style.color = "";
          }, 2000);
          
        } catch (err) {
          console.error("Error copying to clipboard:", err);
          estado.innerText = "⚠️ Error al copiar";
        }
      }
    }
  });
});
