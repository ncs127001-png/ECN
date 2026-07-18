// injector_multiplatform.js
// Módulo independiente de inyección y envío para múltiples plataformas
// Extraído de la Bitácora EVA - Versión estable y probada

export class PlatformInjector {
  constructor() {
    this.platforms = {
      chatgpt: this.injectChatGPT,
      gemini: this.injectGemini,
      // Agregar más plataformas aquí
    };
  }

  // Dispatcher principal - determina qué plataforma está activa
  async dispatch(platform, message) {
    if (!this.platforms[platform]) {
      throw new Error(`Plataforma no soportada: ${platform}`);
    }
    
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) throw new Error('No hay pestaña activa');
    
    console.log(`[Injector] Enviando a ${platform}: ${message.substring(0, 50)}...`);
    
    // Envía mensaje al content script específico de la plataforma
    await chrome.tabs.sendMessage(tab.id, {
      type: "NEUROBIT_INJECT",
      platform: platform,
      message: message
    });
    
    return true;
  }

  // Métodos específicos por plataforma (solo para documentación)
  // La lógica real está en el content script

  async injectChatGPT(message) {
    return this.dispatch('chatgpt', message);
  }

  async injectGemini(message) {
    return this.dispatch('gemini', message);
  }
}

// Content script que debe inyectarse en las páginas destino
export const CONTENT_SCRIPT = `
// content_injector.js - Content script para inyección multiplataforma
// Este script debe inyectarse en las páginas de las plataformas destino

// Escucha mensajes desde el popup/inyector
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "NEUROBIT_INJECT") {
    const { platform, message } = request;
    console.log("[Injector] Recibido mensaje para:", platform);
    
    try {
      if (platform === 'chatgpt') {
        injectChatGPT(message);
      } else if (platform === 'gemini') {
        injectGemini(message);
      } else {
        throw new Error('Plataforma no reconocida');
      }
      
      sendResponse({ success: true });
    } catch (err) {
      console.error("[Injector] Error:", err);
      sendResponse({ success: false, error: err.message });
    }
    
    return true; // Mantiene el canal abierto para respuesta asíncrona
  }
});

// Implementación para ChatGPT
function injectChatGPT(message) {
  console.log("[Injector] Inyectando en ChatGPT...");
  
  // 1. Buscar el campo de texto editable
  const box = document.querySelector("div[contenteditable='true']") || 
              document.querySelector('[contenteditable="true"]');
  
  if (!box) throw new Error("Campo editable no encontrado en ChatGPT");
  
  // 2. Inyectar el mensaje (textContent es crítico para React)
  box.textContent = message;
  
  // 3. Disparar eventos para que React detecte el cambio
  ['input', 'change'].forEach(eventName => {
    const event = new Event(eventName, { bubbles: true, cancelable: true });
    box.dispatchEvent(event);
  });
  
  console.log("[Injector] ✅ Texto inyectado en ChatGPT");
  
  // 4. Esperar y hacer clic en el botón de envío
  setTimeout(() => {
    const sendBtn = document.querySelector("button[data-testid='send-button']") || 
                    document.querySelector('button.rounded-full') || 
                    document.querySelector('button[aria-label*="Send"]');
    
    if (sendBtn) {
      sendBtn.click();
      console.log("[Injector] ✅ Botón de envío presionado en ChatGPT");
    } else {
      console.warn("[Injector] ⚠️ Botón de envío no encontrado en ChatGPT");
      // Fallback: intentar con tecla Enter
      const enterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        bubbles: true,
        cancelable: true
      });
      box.dispatchEvent(enterEvent);
      console.log("[Injector] ✅ Usando fallback: tecla Enter");
    }
  }, 150);
}

// Implementación para Gemini
function injectGemini(message) {
  console.log("[Injector] Inyectando en Gemini...");
  
  // 1. Buscar el campo de texto editable
  const box = document.querySelector("div[role='textbox']") || 
              document.querySelector('.textbox');
  
  if (!box) throw new Error("Campo editable no encontrado en Gemini");
  
  // 2. Inyectar el mensaje
  box.textContent = message;
  
  // 3. Disparar eventos
  ['input', 'change'].forEach(eventName => {
    const event = new Event(eventName, { bubbles: true });
    box.dispatchEvent(event);
  });
  
  console.log("[Injector] ✅ Texto inyectado en Gemini");
  
  // 4. Esperar y hacer clic en el botón de envío
  setTimeout(() => {
    const sendBtn = document.querySelector("button[aria-label*='Enviar'], button[aria-label*='Send']");
    
    if (sendBtn) {
      sendBtn.click();
      console.log("[Injector] ✅ Botón de envío presionado en Gemini");
    } else {
      console.warn("[Injector] ⚠️ Botón de envío no encontrado en Gemini");
      // Fallback: intentar con tecla Enter
      const enterEvent = new KeyboardEvent('keydown', {
        key: 'Enter',
        bubbles: true,
        cancelable: true
      });
      box.dispatchEvent(enterEvent);
      console.log("[Injector] ✅ Usando fallback: tecla Enter");
    }
  }, 150);
}

console.log("[Injector] Content script activo y listo para recibir mensajes");
`;

// Configuración para el manifest.json
export const MANIFEST_CONFIG = {
  "content_scripts": [
    {
      "matches": [
        "https://chat.openai.com/*",
        "https://chatgpt.com/*",
        "https://gemini.google.com/*"
      ],
      "js": ["content_injector.js"],
      "run_at": "document_start"
    }
  ],
  "permissions": [
    "activeTab",
    "scripting",
    "tabs"
  ],
  "host_permissions": [
    "https://chat.openai.com/*",
    "https://chatgpt.com/*",
    "https://gemini.google.com/*"
  ]
};

// Uso desde popup.js u otro script
export function usageExample() {
  const injector = new PlatformInjector();
  
  // Ejemplo de uso
  document.getElementById('sendButton').addEventListener('click', async () => {
    try {
      const platform = document.getElementById('platformSelect').value;
      const message = document.getElementById('messageInput').value;
      
      await injector.dispatch(platform, message);
      console.log("✅ Mensaje enviado correctamente");
    } catch (err) {
      console.error("❌ Error al enviar:", err);
    }
  });
}