// ARCHIVO : content.js
// -----------------------------------------

// Escucha mensajes desde popup.js
window.addEventListener("message", (event) => {
  if (event.data.type === "EVA_SEND") {
    const { dest, msg } = event.data;

    const box = document.querySelector("div[contenteditable='true']");
    if (box) {
      box.innerHTML = `${msg}\n\n(Destinatario: ${dest})`;
      box.dispatchEvent(new InputEvent("input", { bubbles: true }));

      // Encontrar botón de enviar
      const sendBtn = document.querySelector("button[data-testid='send-button']");
      if (sendBtn) sendBtn.click();
    }
  }
});

// content.js - observar respuestas y enviar texto al background
(function(){
  console.log('[EVA] content script: observer for copy-based capture ready');

  // selectores probables para el botón "copiar"
  const COPY_SELECTORS = [
    'button[aria-label="Copiar"]',
    'button[aria-label="Copy"]',
    'button[title="Copiar"]',
    'button[aria-label*="Copiar"]',
    'button[data-testid*="copy"]',
    'button[aria-label*="Copy"]'
  ];

  // intenta encontrar texto de respuesta desde el nodo (recorrido heurístico)
  function findResponseTextFromNode(node){
    if(!node) return null;
    // primer intento: buscar un elemento con clase que parezca "text-base"
    let txt = node.querySelector && ( node.querySelector('.text-base') || node.querySelector('[data-testid="message-text"]') || node.querySelector('div[class*="text-"]') );
    if(txt && txt.innerText && txt.innerText.trim()) return txt.innerText.trim();

    // segundo intento: buscar cualquier <pre> o div con texto dentro del nodo
    const candidates = node.querySelectorAll ? node.querySelectorAll('pre,div') : [];
    for(const c of candidates){
      if(c.innerText && c.innerText.trim().length > 10){
        return c.innerText.trim();
      }
    }

    // tercer intento: subir por ancestros y buscar .text-base
    let anc = node;
    for(let i=0;i<6 && anc; i++){
      if(anc.querySelector){
        const t = anc.querySelector('.text-base, [data-testid="message-text"], div[class*="text-"]');
        if(t && t.innerText && t.innerText.trim()) return t.innerText.trim();
      }
      anc = anc.parentElement;
    }

    // fallback: return node.innerText if suficiente
    if(node.innerText && node.innerText.trim().length > 10) return node.innerText.trim();

    return null;
  }

  function alreadySaved(node){
    try { return node.dataset && node.dataset.evaSaved === '1'; } catch(e){ return false; }
  }
  function markSaved(node){
    try { if(node.dataset) node.dataset.evaSaved = '1'; } catch(e){}
  }

// content.js (agregado al codigo por sugerencia de tu último mensaje)

function getLastResponseText() {
  // Selecciona todos los botones de copiar (en español)
  const copyBtns = document.querySelectorAll('button[aria-label="Copiar"]');
  if (!copyBtns.length) return null;

  // Último botón = último mensaje de la conversación
  const lastBtn = copyBtns[copyBtns.length - 1];

  // Simula un click para copiar al portapapeles
  lastBtn.click();

  // Ahora intentamos leer desde el portapapeles
  return navigator.clipboard.readText();
}

window.addEventListener("message", async (event) => {
  if (event.data.type === "EVA_GET_LAST") {
    try {
      const text = await getLastResponseText();
      window.postMessage({ type: "EVA_LAST_TEXT", text }, "*");
    } catch (err) {
      console.error("Error al leer último mensaje:", err);
      window.postMessage({ type: "EVA_LAST_TEXT", text: null }, "*");
    }
  }
});




  // procesar un nodo nuevo que probablemente contenga una respuesta
  function processAddedNode(node){
    if(node.nodeType !== 1) return;
    // buscar botones copy dentro
    for(const s of COPY_SELECTORS){
      const btns = node.querySelectorAll ? node.querySelectorAll(s) : [];
      if(btns.length){
        for(const btn of btns){
          if(alreadySaved(btn)) continue;
          // encontrar contenedor de mensaje más cercano (heurístico)
          const container = btn.closest('[data-testid]') || btn.closest('article') || btn.parentElement;
          const text = findResponseTextFromNode(container) || findResponseTextFromNode(node);
          if(text){
            // preparar entrada
            const entry = {
              source: 'chatgpt-reply',
              ts: Date.now(),
              text: text
            };
            // enviar al background para guardar
            chrome.runtime.sendMessage({ type: 'EVA_SAVE_REPLY', entry }, (resp) => {
              // opcional: log
              console.log('[EVA] saved reply to background', resp);
            });
            markSaved(btn);
          } else {
            // marcar para no reintentar infinitamente
            markSaved(btn);
          }
        }
        // ya procesamos buttons dentro de este selector
      }
    }
  }

  // observer: vigilar el contenedor de conversaciones
  function attachObserver() {
    // heurística para el contenedor principal de mensajes (varía según UI)
    const possible = [
      document.querySelector('div[data-testid="conversation-turns"]'),
      document.querySelector('div[class*="conversation"]'),
      document.querySelector('main')
    ];
    let root = possible.find(x=>x);
    if(!root){
      root = document.body;
      console.warn('[EVA] no conversation-turns encontrado, observando document.body (menos eficiente)');
    } else {
      console.log('[EVA] observando nodo de conversación:', root);
    }

    const observer = new MutationObserver((mutations)=>{
      for(const m of mutations){
        for(const n of m.addedNodes){
          processAddedNode(n);
        }
      }
    });

    observer.observe(root, { childList: true, subtree: true });
    // también, procesar lo ya presente (inicial scan)
    Array.from(document.querySelectorAll(COPY_SELECTORS.join(','))).forEach(btn=>{
      const container = btn.closest('[data-testid]') || btn.closest('article') || btn.parentElement;
      const text = findResponseTextFromNode(container) || findResponseTextFromNode(btn);
      if(text){
        chrome.runtime.sendMessage({ type: 'EVA_SAVE_REPLY', entry: { source:'initial-scan', ts:Date.now(), text }});
        markSaved(btn);
      }
    });
  }

  // esperar que el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attachObserver);
  } else {
    attachObserver();
    attachObserver();
    attachObserver();
  }

})();


// Observa nuevas respuestas de ChatGPT
const chatContainer = document.querySelector("div[data-testid='conversation-turns']");
if (chatContainer) {
  const observer = new MutationObserver(() => {
    console.log("Nueva respuesta detectada en ChatGPT");
  });
  observer.observe(chatContainer, { childList: true, subtree: true });
}
