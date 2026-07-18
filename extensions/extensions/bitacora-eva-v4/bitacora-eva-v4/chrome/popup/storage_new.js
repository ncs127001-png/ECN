// ============================================================================
// STORAGE.JS - MULTI-LAYER STORAGE (3 CAPAS)
// ============================================================================
// 
// ARQUITECTURA:
// CAPA 1: sessionBuffer (RAM) — Ultra-rápido, temporal
// CAPA 2: chrome.storage.local (Checkpoints) — Cache local persistente
// CAPA 3: memoria_eva.jsonl (NODO_SEMILLA) — Fuente de verdad, append-only
//
// Principio: NUNCA sobrescribir memoria_eva.jsonl
// Integración: neurobit_api.py /memoria endpoint sincroniza las capas
// ============================================================================

export const Storage = {
    // ====================================================================
    // CAPA 1: SESSION BUFFER (RAM)
    // ====================================================================
    
    sessionBuffer: [],
    messageIdCounter: 0,
    
    /**
     * Agregar evento al buffer de sesión
     * @param {Object} event - Evento a registrar {type, data, timestamp}
     */
    addToBuffer(event) {
        const enrichedEvent = {
            id: this.generateMessageId(),
            timestamp: Date.now(),
            ...event
        };
        this.sessionBuffer.push(enrichedEvent);
        return enrichedEvent;
    },
    
    /**
     * Obtener buffer actual
     */
    getBuffer() {
        return [...this.sessionBuffer];
    },
    
    /**
     * Obtener buffer completo y limpiar
     */
    flushBuffer() {
        const buffer = [...this.sessionBuffer];
        this.sessionBuffer = [];
        return buffer;
    },
    
    /**
     * Obtener últimos N eventos del buffer
     */
    getLastN(n = 10) {
        return this.sessionBuffer.slice(-n);
    },
    
    /**
     * Contar eventos en buffer
     */
    getBufferLength() {
        return this.sessionBuffer.length;
    },
    
    // ====================================================================
    // CAPA 2: CHROME STORAGE CHECKPOINTS
    // ====================================================================
    
    /**
     * Guardar checkpoint (recuperable si popup se cierra)
     * @param {string} label - Descripción del checkpoint (e.g., "POST_GUARDAR")
     * @param {string} content - Contenido a recuperar
     */
    async saveCheckpoint(label, content) {
        try {
            const checkpoint = {
                id: this.generateMessageId(),
                label: label,
                content: content,
                timestamp: Date.now(),
                sequence: this.messageIdCounter
            };
            
            // Guardar checkpoint actual
            await chrome.storage.local.set({
                bitacora_checkpoint: checkpoint
            });
            
            // Guardar histórico (últimos 20)
            const history = await this.getCheckpointHistory();
            history.push(checkpoint);
            const trimmedHistory = history.slice(-20);
            
            await chrome.storage.local.set({
                bitacora_checkpoint_history: trimmedHistory
            });
            
            return checkpoint;
        } catch (e) {
            console.error('[STORAGE] Checkpoint save failed:', e);
            return null;
        }
    },
    
    /**
     * Recuperar checkpoint actual
     */
    async recoverCheckpoint() {
        try {
            const result = await chrome.storage.local.get(['bitacora_checkpoint']);
            return result.bitacora_checkpoint || null;
        } catch (e) {
            console.error('[STORAGE] Checkpoint recover failed:', e);
            return null;
        }
    },
    
    /**
     * Obtener historial de checkpoints
     */
    async getCheckpointHistory() {
        try {
            const result = await chrome.storage.local.get(['bitacora_checkpoint_history']);
            return result.bitacora_checkpoint_history || [];
        } catch (e) {
            console.error('[STORAGE] Checkpoint history failed:', e);
            return [];
        }
    },
    
    /**
     * Limpiar checkpoints (después de sincronizar exitosamente)
     */
    async clearCheckpoints() {
        try {
            await chrome.storage.local.set({
                bitacora_checkpoint: null,
                bitacora_checkpoint_history: []
            });
        } catch (e) {
            console.error('[STORAGE] Checkpoint clear failed:', e);
        }
    },
    
    // ====================================================================
    // CAPA 3: SYNC A MEMORIA_EVA.JSONL (APPEND-ONLY)
    // ====================================================================
    
    /**
     * Sincronizar buffer a memoria_eva.jsonl
     * @param {Array} messages - Mensajes a sincronizar
     * @param {Object} options - {dryRun: bool, retries: int}
     */
    async syncToMemoria(messages = null, options = {}) {
        const { dryRun = false, retries = 1 } = options;
        
        // Usar buffer actual si no se especifican mensajes
        const toSync = messages || this.getBuffer();
        
        if (toSync.length === 0) {
            console.log('[STORAGE] Buffer vacío, nada que sincronizar');
            return { success: true, synced: 0 };
        }
        
        const payload = {
            source: 'bitacora-eva',
            entity_id: 'NODO_SEMILLA',
            messages: toSync,
            timestamp: new Date().toISOString(),
            _dryRun: dryRun
        };
        
        return this.syncWithRetry(payload, retries);
    },
    
    /**
     * Sincronizar con retry logic
     */
    async syncWithRetry(payload, maxRetries = 3) {
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                const response = await fetch('http://127.0.0.1:5000/memoria', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                
                if (response.ok) {
                    const result = await response.json();
                    console.log('[STORAGE] Sync exitoso:', result);
                    
                    // Limpiar buffer después de sincronización exitosa
                    if (!payload._dryRun && result.messages_synced > 0) {
                        this.sessionBuffer = this.sessionBuffer.slice(payload.messages.length);
                    }
                    
                    return {
                        success: true,
                        synced: result.messages_synced || 0,
                        attempt: attempt
                    };
                } else {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
            } catch (e) {
                console.error(`[STORAGE] Sync intento ${attempt} falló:`, e);
                
                if (attempt < maxRetries) {
                    // Esperar exponencial: 1s, 2s, 4s, etc.
                    const waitMs = Math.pow(2, attempt - 1) * 1000;
                    console.log(`[STORAGE] Reintentando en ${waitMs}ms...`);
                    await new Promise(r => setTimeout(r, waitMs));
                } else {
                    return {
                        success: false,
                        synced: 0,
                        error: e.message,
                        attempt: attempt
                    };
                }
            }
        }
    },
    
    /**
     * Sincronización automática cada N eventos o cada T segundos
     */
    autoSyncConfig: {
        batchSize: 20,          // Sincronizar cada 20 eventos
        timeInterval: 30000,    // O cada 30 segundos
        enabled: true
    },
    
    autoSyncTimeout: null,
    
    /**
     * Iniciar sincronización automática
     */
    startAutoSync() {
        if (this.autoSyncTimeout) clearInterval(this.autoSyncTimeout);
        
        this.autoSyncTimeout = setInterval(async () => {
            // Sincronizar por tiempo
            if (this.sessionBuffer.length > 0) {
                console.log('[STORAGE] Auto-sync por timeout');
                await this.syncToMemoria();
            }
        }, this.autoSyncConfig.timeInterval);
        
        console.log('[STORAGE] Auto-sync iniciado');
    },
    
    /**
     * Detener sincronización automática
     */
    stopAutoSync() {
        if (this.autoSyncTimeout) {
            clearInterval(this.autoSyncTimeout);
            this.autoSyncTimeout = null;
        }
        console.log('[STORAGE] Auto-sync detenido');
    },
    
    /**
     * Verificar si debe sincronizar (por batch size)
     */
    shouldAutoSyncByBatch() {
        return this.sessionBuffer.length >= this.autoSyncConfig.batchSize;
    },
    
    /**
     * Disparar sincronización si cumple condición de batch
     */
    async triggerAutoSyncIfNeeded() {
        if (this.shouldAutoSyncByBatch()) {
            console.log('[STORAGE] Auto-sync por batch size');
            await this.syncToMemoria();
        }
    },
    
    // ====================================================================
    // UTILITIES: ID GENERATION
    // ====================================================================
    
    /**
     * Generar ID único para cada mensaje
     * Formato: msg_<timestamp_base36>_<counter_base36>
     * Ejemplo: msg_1g3c5q4_b
     */
    generateMessageId() {
        this.messageIdCounter++;
        const timestamp = Date.now().toString(36);
        const counter = this.messageIdCounter.toString(36);
        return `msg_${timestamp}_${counter}`;
    },
    
    /**
     * Obtener siguiente ID (sin incrementar buffer)
     */
    getNextId() {
        return this.generateMessageId();
    },
    
    /**
     * Resetear contador (NO HACER - solo para testing)
     */
    resetCounter() {
        this.messageIdCounter = 0;
        console.warn('[STORAGE] Counter reseteado (testing)');
    },
    
    // ====================================================================
    // DEBUG & MONITORING
    // ====================================================================
    
    /**
     * Obtener estadísticas
     */
    async getStats() {
        const checkpoint = await this.recoverCheckpoint();
        const history = await this.getCheckpointHistory();
        
        return {
            bufferSize: this.sessionBuffer.length,
            messageIdCounter: this.messageIdCounter,
            currentCheckpoint: checkpoint ? checkpoint.label : null,
            checkpointHistorySize: history.length,
            lastSync: checkpoint ? new Date(checkpoint.timestamp).toISOString() : null,
            autoSyncEnabled: this.autoSyncConfig.enabled
        };
    },
    
    /**
     * Imprimir estado para debugging
     */
    async printState() {
        const stats = await this.getStats();
        console.log('[STORAGE] === ESTADO ACTUAL ===');
        console.log('[STORAGE] Buffer:', stats.bufferSize, 'eventos');
        console.log('[STORAGE] Message ID Counter:', stats.messageIdCounter);
        console.log('[STORAGE] Checkpoint:', stats.currentCheckpoint);
        console.log('[STORAGE] Historial checkpoints:', stats.checkpointHistorySize);
        console.log('[STORAGE] Último sync:', stats.lastSync);
        console.log('[STORAGE] Auto-sync:', stats.autoSyncEnabled ? 'ON' : 'OFF');
        return stats;
    },
    
    /**
     * Exportar estado para análisis
     */
    async exportState() {
        const checkpoint = await this.recoverCheckpoint();
        const history = await this.getCheckpointHistory();
        
        return {
            buffer: this.sessionBuffer,
            checkpoint: checkpoint,
            checkpointHistory: history,
            counter: this.messageIdCounter,
            timestamp: new Date().toISOString()
        };
    }
};

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

// Iniciar auto-sync cuando se carga el módulo
if (typeof document !== 'undefined' && document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        Storage.startAutoSync();
        console.log('[STORAGE] ✅ Storage inicializado con auto-sync');
    });
} else {
    // Ya está cargado
    Storage.startAutoSync();
}

// Exportar para uso global
if (typeof window !== 'undefined') {
    window.NeurobitStorage = Storage;
}
