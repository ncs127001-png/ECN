// background.js - Motor persistente de envío secuencial
let isRunning = false;
let currentSequence = null;

// Manejar mensajes desde el popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'START_SEND') {
    if (isRunning) {
      console.warn('[BACKGROUND] Ya hay una secuencia en ejecución');
      return;
    }
    
    isRunning = true;
    currentSequence = request;
    runSequence(request);
    sendResponse({ status: 'started' });
    return true; // Mantener canal abierto para async
  }
  
  if (request.type === 'STOP_SEND') {
    isRunning = false;
    currentSequence = null;
    console.log('[BACKGROUND] Secuencia detenida');
    sendResponse({ status: 'stopped' });
  }
});

// Función principal de envío secuencial
async function runSequence(config) {
  abortController = new AbortController();
  isRunning = true;
  
  const { fragments, platform, delay } = config;
  const delayMs = (delay || 3) * 1000;
  let currentFragment = 0;
  
  try {
    // Notificar inicio al popup
    updatePopupStatus(`▶️ Empezando secuencia (${fragments.length} fragmentos)`);
    
    for (let i = 0; i < fragments.length && isRunning; i++) {
      currentFragment = i;
      const fragName = fragments[i];
      
      // Notificar fragmento actual
      updatePopupStatus(`📤 Enviando: ${fragName} (${i+1}/${fragments.length})`);
      
      // Obtener contenido del fragmento
      const response = await fetch(`http://localhost:5000/get_fragment_content?name=${encodeURIComponent(fragName)}`, {
        mode: 'cors'
      });
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const content = await response.text();
      
      const finalMessage = `[FRAGMENT: ${fragName}]\n${content}`;
      
      // Enviar a la pestaña activa
      await sendToActiveTab(platform, finalMessage);
      
      // Esperar entre fragmentos (solo si no es el último)
      if (i < fragments.length - 1) {
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }
    
    if (isRunning) {
      updatePopupStatus('🎉 ¡SECUENCIA COMPLETADA!');
      playSuccessSound();
    } else {
      updatePopupStatus('⏹️ Secuencia detenida manualmente');
    }
    
  } catch (err) {
    console.error('[BACKGROUND] Error en secuencia:', err);
    updatePopupStatus(`❌ Error: ${err.message}`);
  } finally {
    isRunning = false;
    currentSequence = null;
  }
}

// Enviar mensaje a la pestaña activa
async function sendToActiveTab(platform, message) {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) throw new Error('Ninguna pestaña activa');
  
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: (platform, msg) => {
      let box = null;
      let btn = null;
      
      if (platform === 'chatgpt') {
        box = document.querySelector('[contenteditable="true"]');
      } else if (platform === 'gemini') {
        box = document.querySelector('div[role="textbox"]');
      }
      
      if (box) {
        box.textContent = msg;
        
        // Disparar eventos para React
        ['input', 'change'].forEach(eventName => {
          box.dispatchEvent(new Event(eventName, { bubbles: true }));
        });
        
        // Enviar con Enter (más estable que botón)
        setTimeout(() => {
          const enterEvent = new KeyboardEvent('keydown', {
            key: 'Enter',
            bubbles: true,
            cancelable: true
          });
          box.dispatchEvent(enterEvent);
        }, 200);
      } else {
        throw new Error('Campo editable no encontrado');
      }
    },
    args: [platform, message]
  });
}

// Actualizar estado en el popup
function updatePopupStatus(text) {
  chrome.runtime.sendMessage({
    type: 'UPDATE_STATUS',
    text: text
  });
}

// Reproducir sonido de éxito
function playSuccessSound() {
  // Crear beep simple sin archivos externos
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    
    osc.connect(gain);
    gain.connect(ctx.destination);
    
    osc.type = 'sine';
    osc.frequency.value = 880;
    gain.gain.value = 0.1;
    
    osc.start();
    setTimeout(() => {
      osc.stop();
      ctx.close().catch(e => console.log('AudioContext closed'));
    }, 300);
  } catch (e) {
    console.log('Beep no disponible en este entorno');
  }
}
