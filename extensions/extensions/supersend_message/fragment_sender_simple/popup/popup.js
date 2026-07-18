document.addEventListener('DOMContentLoaded', () => {
  console.log('Intialized Fragment Sender - Versión Background');
  cargarFragmentos();
  
  // Escuchar actualizaciones de estado desde background
  chrome.runtime.onMessage.addListener((request) => {
    if (request.type === 'UPDATE_STATUS') {
      document.getElementById('status').textContent = request.text;
    }
  });
});
let isRunning = false;
let abortController = null; // Controlador para abortar operaciones
let fragmentList = [];

async function cargarFragmentos() {
  try {
    document.getElementById('status').textContent = '📡 Conectando con NEUROBIT...';
    
    const response = await fetch(`http://localhost:5000/get_fragment_content?name=${encodeURIComponent(fragName)}`, {
  signal: abortController.signal
});

// Ejemplo para los timeouts:
await new Promise((resolve, reject) => {
  const timeout = setTimeout(resolve, delayMs * 1000);
  abortController.signal.addEventListener('abort', () => {
    clearTimeout(timeout);
    reject(new Error('Operación abortada por HALT'));
  });
});
   
    
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const data = await response.json();
    fragmentList = data.fragments || [];
    
    document.getElementById('fragmentList').innerHTML = fragmentList.map(frag => `
      <div class="fragment-item">${frag}</div>
    `).join('');
    
    document.getElementById('status').textContent = `✅ ${fragmentList.length} fragmentos listos`;
    
  } catch (err) {
    console.error('Error al cargar fragmentos:', err);
    document.getElementById('status').textContent = '❌ NEUROBIT no responde';
    document.getElementById('fragmentList').innerHTML = `
      <div style="text-align:center;padding:20px;color:#e74c3c">
        ❌ Servidor NEUROBIT no disponible<br>
        Ejecuta: python3 fragment_state_server.py
      </div>
    `;
  }
}

// Evento para el botón HALT
document.getElementById('haltBtn').addEventListener('click', () => {
  if (isRunning) {
    isRunning = false;
    if (abortController) {
      abortController.abort();
      abortController = null;
    }
    document.getElementById('status').textContent = '⏹️ PROCESO DETENIDO (HALT)';
    console.log('[HALT] Proceso de envío detenido por el usuario');
  }
});

document.getElementById('startBtn').addEventListener('click', () => {
  if (fragmentList.length === 0) {
    document.getElementById('status').textContent = '⚠️ No hay fragmentos para enviar';
    return;
  }
  
  const platform = document.getElementById('platform').value;
  const delay = parseInt(document.getElementById('delay').value, 10) || 3;
  
  // Enviar comando al background (no hacer el loop aquí)
  chrome.runtime.sendMessage({
    type: 'START_SEND',
    fragments: fragmentList,
    platform: platform,
    delay: delay
  });
  
  document.getElementById('status').textContent = '▶️ Secuencia iniciada en background...';
  document.getElementById('startBtn').disabled = true;
  
  // Habilitar botón de stop
  document.getElementById('stopBtn').disabled = false;
});

document.getElementById('stopBtn').addEventListener('click', () => {
  chrome.runtime.sendMessage({ type: 'STOP_SEND' });
  document.getElementById('status').textContent = '⏹️ Deteniendo secuencia...';
  document.getElementById('stopBtn').disabled = true;
  setTimeout(() => {
    document.getElementById('startBtn').disabled = false;
  }, 1000);
});
