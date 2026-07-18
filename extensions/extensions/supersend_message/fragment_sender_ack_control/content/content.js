// content/content.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "FRAGMENT_SEND") {
    const { platform, message } = request;
    let box = null;
    let btn = null;

    if (platform === 'chatgpt') {
      // Selectores ACTUALIZADOS para nueva UI de ChatGPT
      box = document.querySelector('[contenteditable="true"][data-id="root"]');
      
      // Múltiples opciones para el botón de envío (según versión actual)
      btn = document.querySelector('button[data-testid="send-button"]') || 
            document.querySelector('button.rounded-full') || 
            document.querySelector('button[aria-label="Send message"]');
    
    } else if (platform === 'gemini') {
      box = document.querySelector('div[role="textbox"]');
      btn = document.querySelector('button[aria-label*="Enviar"], button[aria-label*="Send"]');
    }

    if (box) {
      // Método probado de la bitácora que siempre funciona
      box.textContent = message;
      box.dispatchEvent(new Event("input", { bubbles: true, cancelable: true }));
      box.dispatchEvent(new Event("change", { bubbles: true, cancelable: true }));
      
      // Forzar actualización de React
      const inputEvent = new Event('input', { bubbles: true, cancelable: true });
      Object.defineProperty(inputEvent, 'target', { value: box });
      box.dispatchEvent(inputEvent);
      
      console.log("[Fragment Sender] ✅ Texto inyectado con éxito");

      // Esperar un poco más para asegurar que React procese
      setTimeout(() => {
        if (btn) {
          console.log("[Fragment Sender] ✅ Botón de envío encontrado. Enviando...");
          btn.click();
          
          // Fallback: si no funciona el primer clic
          setTimeout(() => {
            if (box.textContent) {
              const enterEvent = new KeyboardEvent('keydown', {
                key: 'Enter',
                bubbles: true,
                cancelable: true
              });
              box.dispatchEvent(enterEvent);
            }
          }, 300);
        } else {
          console.warn("[Fragment Sender] ⚠️ Botón de envío no encontrado. Intentando enviar con tecla Enter...");
          
          // Fallback 2: enviar con tecla Enter
          const enterEvent = new KeyboardEvent('keydown', {
            key: 'Enter',
            bubbles: true,
            cancelable: true
          });
          box.dispatchEvent(enterEvent);
        }
      }, 200);
    } else {
      console.error("[Fragment Sender] ❌ Campo editable NO ENCONTRADO. Selectores desactualizados.");
    }

    sendResponse({ success: true });
  }
  return true;
});

console.log("[Fragment Sender] Content script activo y listo para recibir fragmentos.");
