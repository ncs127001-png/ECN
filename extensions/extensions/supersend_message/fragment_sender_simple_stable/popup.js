document.addEventListener('DOMContentLoaded', () => {
  console.log('Intialized Minimal Fragment Sender');
  cargarFragmentos();
});

let fragmentList = [];

async function cargarFragmentos() {
  try {
    document.getElementById('status').textContent = '📡 Conectando con NEUROBIT...';
    
    const response = await fetch('http://localhost:5000/get_fragments_state', {
      mode: 'cors'
    });
    
    const data = await response.json();
    fragmentList = data.fragments || [];
    
    mostrarFragmentos();
    document.getElementById('status').textContent = `✅ ${fragmentList.length} fragmentos listos`;
    
  } catch (err) {
    console.error('Error:', err);
    document.getElementById('status').textContent = '❌ NEUROBIT no responde';
    document.getElementById('fragmentList').innerHTML = `
      <div style="text-align:center;padding:20px;color:#e74c3c">
        ❌ NEUROBIT no responde<br>
        Ejecuta: python3 fragment_state_server.py
      </div>
    `;
  }
}

function mostrarFragmentos() {
  const container = document.getElementById('fragmentList');
  if (!container) return;
  
  if (fragmentList.length === 0) {
    container.innerHTML = '<div style="text-align:center;padding:20px">No hay fragmentos</div>';
    return;
  }
  
  container.innerHTML = fragmentList.map(frag => `
    <div class="fragment-item">${frag}</div>
  `).join('');
}

async function sendFragmentToTab(platform, text) {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) throw new Error('Abre ChatGPT primero');
  
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: (platform, msg) => {
      let box = null;
      
      if (platform === 'chatgpt') {
        box = document.querySelector('[contenteditable="true"]');
      } else if (platform === 'gemini') {
        box = document.querySelector('div[role="textbox"]');
      }
      
      if (box) {
        box.textContent = msg;
        ['input', 'change'].forEach(eventName => {
          box.dispatchEvent(new Event(eventName, { bubbles: true }));
        });
        
        setTimeout(() => {
          const event = new KeyboardEvent('keydown', {
            key: 'Enter',
            bubbles: true
          });
          box.dispatchEvent(event);
        }, 200);
      }
    },
    args: [platform, text]
  });
}

document.getElementById('startBtn').addEventListener('click', async () => {
  if (fragmentList.length === 0) {
    document.getElementById('status').textContent = '⚠️ No hay fragmentos';
    return;
  }

  const platform = document.getElementById('platform').value;
  const delay = parseInt(document.getElementById('delay').value) || 3;
  
  document.getElementById('status').textContent = `▶️ Enviando ${fragmentList.length} fragmentos...`;
  document.getElementById('startBtn').disabled = true;
  
  try {
    for (let i = 0; i < fragmentList.length; i++) {
      const fragName = fragmentList[i];
      
      const response = await fetch(`http://localhost:5000/get_fragment_content?name=${encodeURIComponent(fragName)}`);
      const content = await response.text();
      
      const finalMessage = `[FRAGMENT: ${fragName}]\n${content}`;
      await sendFragmentToTab(platform, finalMessage);
      
      document.querySelectorAll(`.fragment-item`).forEach((el, idx) => {
        if (idx <= i) el.style.opacity = '0.6';
      });
      
      await new Promise(r => setTimeout(r, delay * 1000));
    }
    
    document.getElementById('status').textContent = '🎉 ¡FINALIZADO!';
    
  } catch (err) {
    document.getElementById('status').textContent = `❌ Error: ${err.message}`;
    console.error(err);
  } finally {
    document.getElementById('startBtn').disabled = false;
  }
});