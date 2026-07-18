let controller = null;
let logEntries = [];
let isRunning = false;
let fragmentList = []; // Lista de fragmentos desde el servidor

// Ocultar elementos de selección de carpeta
document.getElementById('folderSelection').style.display = 'none';

function log(msg) {
  logEntries.push({ ts: new Date().toISOString(), msg });
}

function updateStatus(text) {
  document.getElementById('status').textContent = text;
}

function playSound() {
  const soundFile = document.getElementById('soundFile').files[0];
  if (!soundFile) return;
  const url = URL.createObjectURL(soundFile);
  const audio = new Audio(url);
  audio.play().catch(e => console.warn('Audio blocked:', e));
}

async function sendFragmentToTab(platform, text) {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) throw new Error('No hay pestaña activa');

  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: (platform, msg) => {
      let box = null;
      let btn = null;

      if (platform === 'chatgpt') {
        box = document.querySelector('[contenteditable="true"]');
        btn = document.querySelector('button[data-testid="send-button"]');
      } else if (platform === 'gemini') {
        box = document.querySelector('div[role="textbox"]');
        btn = document.querySelector('button[aria-label*="Enviar"], button[aria-label*="Send"]');
      }

      if (!box) throw new Error('Campo no encontrado');
      box.textContent = msg;
      box.dispatchEvent(new Event('input', { bubbles: true }));
      box.dispatchEvent(new Event('change', { bubbles: true }));

      if (btn) {
        setTimeout(() => btn.click(), 100);
      }
    },
    args: [platform, text]
  });
}

// NUEVO: verificar que el LLM haya terminado de generar
async function isLLMStable(platform) {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const result = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: (platform) => {
      if (platform === 'chatgpt') {
        // Si existe stop-button, aún está generando
        return document.querySelector('button[data-testid="stop-button"]') === null;
      } else if (platform === 'gemini') {
        // Buscar cualquier indicador de "generando", "typing", etc.
        const typingIndicators = document.querySelectorAll(
          'div[aria-label*="generando"], div[aria-label*="typing"], div[aria-label*="escribiendo"], .loading-spinner'
        );
        return typingIndicators.length === 0;
      }
      return true;
    },
    args: [platform]
  });
  return result[0].result;
}

// NUEVO: esperar a que el LLM esté estable
async function waitForLLMStable(platform, timeoutMs = 30000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (await isLLMStable(platform)) return true;
    await new Promise(r => setTimeout(r, 500));
  }
  return false;
}

async function getLastLLMResponse(platform) {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const result = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: (platform) => {
      let messages = [];
      if (platform === 'chatgpt') {
        messages = Array.from(document.querySelectorAll('div[data-message-author-role="assistant"]'));
      } else if (platform === 'gemini') {
        messages = Array.from(document.querySelectorAll('div[aria-label*="Respuesta de Gemini"], div[aria-label*="Gemini response"]'));
      }
      const last = messages[messages.length - 1];
      return last ? last.innerText.trim() : null;
    },
    args: [platform]
  });
  return result[0].result;
}

// NUEVO: Cargar fragmentos desde el servidor NEUROBIT
async function cargarFragmentos() {
  try {
    updateStatus('📡 Conectando con NEUROBIT Central Station...');
    
    const response = await fetch('http://localhost:5000/get_fragments_state', {
      mode: 'cors',
      headers: {
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.fragments || data.fragments.length === 0) {
      updateStatus('⚠️ No hay fragmentos disponibles en NEUROBIT');
      document.getElementById('fragmentList').innerHTML = `
        <div style="text-align: center; color: #e74c3c; padding: 20px;">
          ❌ No hay fragmentos disponibles<br>
          Usa la GUI NEUROBIT para fragmentar primero
        </div>
      `;
      return;
    }
    
    fragmentList = data.fragments;
    mostrarFragmentos();
    updateStatus(`✅ ${fragmentList.length} fragmentos listos para enviar`);
    
  } catch (err) {
    console.error('Error al cargar fragmentos:', err);
    updateStatus('❌ Error al conectar con NEUROBIT');
    document.getElementById('fragmentList').innerHTML = `
      <div style="text-align: center; color: #e74c3c; padding: 20px;">
        ❌ Error de conexión<br>
        Asegúrate de que el servidor NEUROBIT está ejecutándose:<br>
        python3 ~/neurobit_salon_v0.1/tools/fragment_state_server.py
      </div>
    `;
  }
}

// NUEVO: Mostrar fragmentos en la interfaz
function mostrarFragmentos() {
  const container = document.getElementById('fragmentList');
  container.innerHTML = '';
  
  fragmentList.forEach(fragmento => {
    const item = document.createElement('div');
    item.className = 'fragment-item';
    item.dataset.name = fragmento;
    
    item.innerHTML = `
      <input type="checkbox" disabled>
      <span>${fragmento}</span>
    `;
    
    container.appendChild(item);
  });
}

// NUEVO: Marcar fragmento como enviado
function marcarEnviado(fragmentoNombre) {
  const items = document.querySelectorAll('.fragment-item');
  items.forEach(item => {
    if (item.dataset.name === fragmentoNombre) {
      item.querySelector('input').checked = true;
      item.querySelector('input').disabled = false;
      item.classList.add('sent');
    }
  });
}

// NUEVO: Obtener contenido de un fragmento específico
async function getFragmentContent(fragmentName) {
  try {
    const response = await fetch(`http://localhost:5000/get_fragment_content?name=${encodeURIComponent(fragmentName)}`, {
      mode: 'cors'
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.text();
  } catch (err) {
    console.error(`Error al obtener contenido de ${fragmentName}:`, err);
    throw err;
  }
}

async function runSequence() {
  if (fragmentList.length === 0) {
    updateStatus('⚠️ No hay fragmentos para enviar');
    return;
  }

  const platform = document.getElementById('platform').value;
  const delaySec = parseInt(document.getElementById('delay').value, 10);
  const delayMs = delaySec * 1000;
  const useHook = document.getElementById('hook').checked;

  isRunning = true;
  document.getElementById('startBtn').disabled = true;
  document.getElementById('stopBtn').disabled = false;

  log(`Inicio: plataforma=${platform}, fragmentos=${fragmentList.length}, delay=${delaySec}s`);

  try {
    for (let i = 0; i < fragmentList.length; i++) {
      if (!isRunning) {
        log('DETENIDO_MANUAL');
        break;
      }

      const fragName = fragmentList[i];
      updateStatus(`Cargando contenido de ${fragName}...`);
      log(`Cargando ${fragName}`);
      
      let content = await getFragmentContent(fragName);
      const prefixedContent = `[FRAGMENT: ${fragName}]\n${content}`;
      let finalMessage = useHook ? `${prefixedContent}\n\nhook` : prefixedContent;

      updateStatus(`Enviando ${fragName}...`);
      log(`Enviando ${fragName}`);
      await sendFragmentToTab(platform, finalMessage);

      // Esperar a que el LLM termine de generar
      updateStatus(`Esperando que LLM termine de generar...`);
      const stable = await waitForLLMStable(platform);
      if (!stable) {
        log(`ADVERTENCIA: LLM no se estabilizó tras enviar ${fragName}`);
      }

      // Esperar delay configurado antes de leer ACK
      await new Promise(r => setTimeout(r, delayMs));

      updateStatus(`Esperando ACK para ${fragName}...`);
      let ackReceived = false;
      let attempts = 0;
      const maxAttempts = 3;

      while (attempts < maxAttempts && isRunning) {
        const response = await getLastLLMResponse(platform);
        if (response) {
          // Validación estricta: debe contener "ACK parte_N" (case-insensitive)
          const ackPattern = new RegExp(`ACK\\s+${fragName}|ack\\s+${fragName}`, 'i');
          if (ackPattern.test(response)) {
            ackReceived = true;
            log(`ACK recibido para ${fragName}`);
            updateStatus(`ACK recibido → ${fragName}`);
            marcarEnviado(fragName); // Marcar visualmente
            break;
          }
        }
        attempts++;
        await new Promise(r => setTimeout(r, delayMs)); // usa el mismo delay
      }

      if (!ackReceived) {
        updateStatus(`❌ Sin ACK válido para ${fragName}. Detenido.`);
        log(`FALLO_ACK_${fragName}`);
        isRunning = false;
        break;
      }
    }

    if (isRunning) {
      log('✅ Secuencia completada');
      updateStatus('✅ FINALIZADO');
      playSound();
    }

  } catch (err) {
    log(`ERROR_TECNICO: ${err.message}`);
    updateStatus(`⚠️ Error: ${err.message}`);
  } finally {
    isRunning = false;
    document.getElementById('startBtn').disabled = false;
    document.getElementById('stopBtn').disabled = true;

    // Descargar log
    const logText = logEntries.map(e => `[${e.ts}] ${e.msg}`).join('\n');
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    chrome.downloads.download({
      url: url,
      filename: `fragment_sender_log_${Date.now()}.log`
    });
  }
}

document.getElementById('startBtn').addEventListener('click', () => {
  logEntries = [];
  runSequence();
});

document.getElementById('stopBtn').addEventListener('click', () => {
  isRunning = false;
  updateStatus('⏹ Detenido manualmente');
});

// Cargar fragmentos al iniciar
document.addEventListener('DOMContentLoaded', () => {
  // Verificar si estamos en un entorno de extensión de Chrome
  if (typeof chrome !== 'undefined' && chrome.runtime) {
    cargarFragmentos();
  } else {
    // Modo de desarrollo/dummy para pruebas fuera de Chrome
    updateStatus('⚠️ Modo de desarrollo: sin conexión a Chrome');
    setTimeout(() => {
      fragmentList = ['parte_01.txt', 'parte_02.txt', 'parte_03.txt'];
      mostrarFragmentos();
      updateStatus('✅ 3 fragmentos de prueba cargados');
    }, 1000);
  }
});
