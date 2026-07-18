// extensions/bitacora-eva/content/response-capture.js

/**
 * Módulo de Captura de Respuestas — NEUROBIT
 * Captura respuestas de IA en tiempo real y las registra en memoria local
 */

class ResponseCaptureModule {
    constructor() {
        this.observers = new Map();
        this.captureHistory = [];
        this.currentPID = this.getBrowserPID();
        this.storageKey = 'neurobit_response_history';
    }

    /**
     * Obtiene el PID del proceso del navegador (si está disponible)
     * Chrome/Opera: chrome://process-internals/
     * Firefox: about:processes
     */
    getBrowserPID() {
        // Nota: Las extensiones no pueden acceder directamente al PID
        // Pero podemos usar tabId como identificador único
        return new Promise((resolve) => {
            chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
                resolve({
                    tabId: tabs[0]?.id || 'unknown',
                    url: tabs[0]?.url || 'unknown',
                    timestamp: Date.now()
                });
            });
        });
    }

    /**
     * Inicia la observación del DOM para capturar respuestas
     */
    startCapture(selector) {
        const targetElement = document.querySelector(selector);
        if (!targetElement) {
            console.warn('[NEUROBIT] Elemento no encontrado:', selector);
            return false;
        }

        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' || mutation.type === 'characterData') {
                    this.handleDOMChange(mutation);
                }
            });
        });

        observer.observe(targetElement, {
            childList: true,
            characterData: true,
            subtree: true
        });

        this.observers.set(selector, observer);
        console.log('[NEUROBIT] Captura iniciada en:', selector);
        return true;
    }

    /**
     * Maneja los cambios en el DOM
     */
    async handleDOMChange(mutation) {
        const addedNodes = mutation.addedNodes;
        for (const node of addedNodes) {
            if (node.nodeType === Node.TEXT_NODE || node.nodeType === Node.ELEMENT_NODE) {
                const text = node.nodeType === Node.TEXT_NODE 
                    ? node.textContent 
                    : node.innerText;
                
                if (text && text.trim().length > 10) {
                    // Filtrar ruido (texto muy corto)
                    await this.captureResponse(text, node);
                }
            }
        }
    }

    /**
     * Captura y registra la respuesta
     */
    async captureResponse(text, sourceNode) {
        const captureData = {
            message_id: `resp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            timestamp: new Date().toISOString(),
            content: text,
            source: {
                tabId: this.currentPID.tabId,
                url: this.currentPID.url,
                selector: this.getNodeSelector(sourceNode)
            },
            type: 'ai_response',
            entity_id: 'NEUROBIT_D',
            perspective: 'complemento_bionico',
            action: 'store',
            provenance: {
                created: new Date().toISOString(),
                signed_by: 'BITACORA_EVA_RESPONSE_CAPTURE',
                stored: true,
                privacy: 'LOCAL_ONLY'
            }
        };

        // 1. Guardar en historial local (visible para el usuario)
        this.addToVisibleHistory(captureData);

        // 2. Enviar a memoria_eva.jsonl (vía API local)
        await this.sendToMemoria(captureData);

        // 3. Actualizar UI (panel sobre contenteditable)
        this.updateCapturePanel(captureData);

        console.log('[NEUROBIT] Respuesta capturada:', captureData.message_id);
    }

    /**
     * Añade al historial visible (panel sobre contenteditable)
     */
    addToVisibleHistory(captureData) {
        this.captureHistory.push(captureData);
        localStorage.setItem(this.storageKey, JSON.stringify(this.captureHistory));
    }

    /**
     * Envía a memoria_eva.jsonl vía API local
     */
    async sendToMemoria(captureData) {
        try {
            await fetch('http://127.0.0.1:5000/hid/capture', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    input_type: 'clipboard',
                    data: captureData.content,
                    metadata: captureData
                })
            });
        } catch (error) {
            console.warn('[NEUROBIT] No se pudo enviar a memoria:', error);
        }
    }

    /**
     * Actualiza el panel de captura visible
     */
    updateCapturePanel(captureData) {
        let panel = document.getElementById('neurobit-capture-panel');
        if (!panel) {
            panel = this.createCapturePanel();
        }

        const entry = document.createElement('div');
        entry.className = 'neurobit-capture-entry';
        entry.innerHTML = `
            <div class="neurobit-capture-meta">
                <span class="neurobit-timestamp">${new Date(captureData.timestamp).toLocaleTimeString()}</span>
                <span class="neurobit-source">${captureData.entity_id}</span>
            </div>
            <div class="neurobit-capture-content">${captureData.content.substring(0, 200)}...</div>
            <div class="neurobit-capture-actions">
                <button onclick="neurobitCapture.expand('${captureData.message_id}')">Ver completo</button>
                <button onclick="neurobitCapture.copy('${captureData.message_id}')">Copiar</button>
                <button onclick="neurobitCapture.inject('${captureData.message_id}')">Inyectar en prompt</button>
            </div>
        `;

        panel.insertBefore(entry, panel.firstChild);
    }

    /**
     * Crea el panel de captura visible
     */
    createCapturePanel() {
        const panel = document.createElement('div');
        panel.id = 'neurobit-capture-panel';
        panel.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            width: 350px;
            max-height: 400px;
            overflow-y: auto;
            background: rgba(255, 255, 255, 0.95);
            border: 2px solid #0b74de;
            border-radius: 8px;
            padding: 10px;
            z-index: 999999;
            font-family: system-ui, sans-serif;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;

        panel.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <strong style="color: #0b74de;">🧭 Bitácora EVA — Capturas</strong>
                <button onclick="document.getElementById('neurobit-capture-panel').remove()" 
                        style="background: none; border: none; cursor: pointer; font-size: 16px;">✕</button>
            </div>
            <div id="neurobit-capture-entries"></div>
        `;

        document.body.appendChild(panel);
        return panel;
    }

    /**
     * Obtiene el selector CSS único de un nodo
     */
    getNodeSelector(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            node = node.parentElement;
        }
        
        const parts = [];
        let current = node;
        
        while (current && current.nodeType === Node.ELEMENT_NODE) {
            let selector = current.nodeName.toLowerCase();
            
            if (current.id) {
                selector += `#${current.id}`;
                parts.unshift(selector);
                break;
            } else if (current.className) {
                selector += `.${current.className.split(' ').join('.')}`;
            }
            
            parts.unshift(selector);
            current = current.parentElement;
        }
        
        return parts.join(' > ');
    }

    /**
     * Detiene la captura
     */
    stopCapture(selector) {
        const observer = this.observers.get(selector);
        if (observer) {
            observer.disconnect();
            this.observers.delete(selector);
            console.log('[NEUROBIT] Captura detenida en:', selector);
        }
    }

    /**
     * Limpia todo
     */
    cleanup() {
        this.observers.forEach((observer) => observer.disconnect());
        this.observers.clear();
        this.captureHistory = [];
    }
}

// Exportar instancia global
window.neurobitCapture = new ResponseCaptureModule();