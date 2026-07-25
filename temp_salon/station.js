/**
 * station.js — Lógica de la Estación Central NEUROBIT v2.1
 * 
 * Conecta la UI con el backend Flask (neurobit_api.py).
 * Maneja: Ceremonia, Mensajería, Agentes, Matriz.
 */

const API_BASE = 'http://127.0.0.1:5000';

const Station = {

    // ════════════════════════════════════════════════════════
    // 1. INICIALIZACIÓN Y NAVEGACIÓN
    // ════════════════════════════════════════════════════════

    init: () => {
        console.log('📡 Inicializando Estación Central...');
        Station.checkConnection();
        Station.setupNavigation();

        // Polling de estado cada 5s
        setInterval(Station.checkConnection, 5000);

        // Inicializar Matriz si la librería existe
        if (typeof MatrizUI !== 'undefined') {
            new MatrizUI('#matriz-container', 13);
        }
    },

    setupNavigation: () => {
        const tabs = document.querySelectorAll('.nav-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                // Update tabs
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                // Update panels
                const panelId = `panel-${tab.dataset.panel}`;
                document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
                document.getElementById(panelId).classList.add('active');

                // Load data if needed
                if (tab.dataset.panel === 'memoria') Station.loadMemoria();
                if (tab.dataset.panel === 'agentes') Station.loadAgents();
            });
        });
    },

    checkConnection: async () => {
        const dot = document.getElementById('statusDot');
        const text = document.getElementById('statusText');

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 2000);

            const res = await fetch(`${API_BASE}/`, { signal: controller.signal });
            clearTimeout(timeoutId);

            if (res.ok) {
                dot.classList.remove('offline');
                text.textContent = 'CONECTADO: LOCALHOST'; // Soberanía local

                // Update ceremony status if not yet done
                Station.checkCeremonyStatus();
            } else {
                throw new Error('API Error');
            }
        } catch (e) {
            dot.classList.add('offline');
            text.textContent = 'DESCONECTADO (Revisar backend)';
        }
    },

    // ════════════════════════════════════════════════════════
    // 2. CEREMONIA DE DESPERTAR
    // ════════════════════════════════════════════════════════

    checkCeremonyStatus: async () => {
        try {
            const res = await fetch(`${API_BASE}/init_ceremony/status`);
            const data = await res.json();

            if (data.initialized) {
                Station.updateCeremonyUI(true);
            }
        } catch (e) {
            console.warn('No se pudo verificar estado de ceremonia');
        }
    },

    runCeremony: async () => {
        const btn = document.getElementById('btnCeremony');
        const logCard = document.getElementById('ceremonyLogCard');
        const log = document.getElementById('ceremonyLog');

        btn.disabled = true;
        btn.textContent = '🔮 Ejecutando...';

        try {
            const res = await fetch(`${API_BASE}/init_ceremony`, { method: 'POST' });
            const data = await res.json();

            logCard.style.display = 'block';

            // Construir log visual
            let logContent = '';
            const checks = data.checks || {};

            // Update visual checks
            Station.updateCheckIcon('Memoria Sagrada', checks.memoria_sagrada);
            Station.updateCheckIcon('Corpus Referencia', checks.corpus);
            Station.updateCheckIcon('Módulos Críticos', checks.modules);
            Station.updateCheckIcon('Entorno Config', checks.environment);
            Station.updateCheckIcon('Registro Agentes', checks.agents_registry);

            // Fill text log
            logContent += `[${new Date().toISOString()}] INICIO CEREMONIA\n`;
            if (checks.memoria_sagrada) logContent += `✓ Memoria Sagrada: ${checks.memoria_sagrada.size} bytes\n`;
            if (checks.corpus) logContent += `✓ Corpus: ${checks.corpus.path}\n`;
            if (checks.modules) logContent += `✓ Módulos Core: ${checks.modules.found.length} encontrados\n`;
            if (checks.environment) logContent += `✓ Entorno: ${JSON.stringify(checks.environment)}\n`;

            if (data.ready) {
                logContent += `\n✨ CEREMONIA COMPLETADA CON ÉXITO\n`;
                logContent += `   NODO_SEMILLA ACTIVO | SISTEMA OPERATIVO\n`;
                Station.showToast('Ceremonia completada. El Salón está abierto.', 'success');
                Station.updateCeremonyUI(true);
            } else {
                logContent += `\n❌ FALLO EN CEREMONIA: ${data.error}\n`;
                Station.showToast('Error en la ceremonia. Revisa el log.', 'error');
            }

            log.textContent = logContent;

        } catch (e) {
            Station.showToast(`Error de conexión: ${e.message}`, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = '🔮 Ejecutar Ceremonia de Despertar';
        }
    },

    updateCheckIcon: (label, result) => {
        // Busca el div que contiene el span con el texto 'label'
        const items = document.querySelectorAll('.ceremony-check');
        for (let item of items) {
            if (item.querySelector('span').textContent.includes(label)) {
                const icon = item.querySelector('.check-icon');
                icon.className = 'check-icon'; // reset
                if (result) {
                    icon.classList.add('ok');
                    icon.textContent = '✓';
                } else {
                    icon.classList.add('error');
                    icon.textContent = '✕';
                }
            }
        }
    },

    updateCeremonyUI: (ready) => {
        if (ready) {
            const btn = document.getElementById('btnCeremony');
            btn.classList.add('btn-green');
            btn.innerHTML = '✨ Salón Operativo (Reiniciar)';
        }
    },

    // ════════════════════════════════════════════════════════
    // 3. MENSAJERÍA Y ANÁLISIS
    // ════════════════════════════════════════════════════════

    sendMessage: async (e) => {
        e.preventDefault();

        const sender = document.getElementById('senderName').value;
        const content = document.getElementById('messageContent').value;
        const perspective = document.getElementById('perspective').value;

        if (!content.trim()) {
            Station.showToast('El mensaje no puede estar vacío', 'error');
            return;
        }

        const statusBadge = document.getElementById('analysisStatus');
        statusBadge.className = 'card-badge badge-amber';
        statusBadge.textContent = 'Analizando...';

        try {
            const res = await fetch(`${API_BASE}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content,
                    entity_id: sender,
                    perspective,
                    action: 'store'
                })
            });

            const envelope = await res.json();

            // Mostrar resultado
            Station.renderAnalysis(envelope);
            Station.showToast('Mensaje analizado y guardado en Arca', 'success');

            statusBadge.className = 'card-badge badge-green';
            statusBadge.textContent = 'Completado';

            // Limpiar input (opcional)
            // document.getElementById('messageContent').value = '';

        } catch (e) {
            Station.showToast(`Error al enviar: ${e.message}`, 'error');
            statusBadge.className = 'card-badge badge-red';
            statusBadge.textContent = 'Error';
        }
    },

    renderAnalysis: (env) => {
        const container = document.getElementById('analysisResult');
        const coherence = env.analysis.coherence_score;
        const emotion = env.analysis.emotional_score;

        let coherenceColor = '#ef4444';
        if (coherence > 0.6) coherenceColor = '#f59e0b';
        if (coherence > 0.8) coherenceColor = '#22c55e';

        container.innerHTML = `
      <div style="animation: fadeIn 0.5s">
        <div style="font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); margin-bottom: 10px;">
          ID: ${env.message_id} | HASH: ${env.provenance.signed_by}
        </div>
        
        <div class="grid-2" style="margin-bottom: 16px;">
          <div class="stat-card" style="padding: 12px;">
            <div class="stat-value" style="font-size: 24px; color: ${coherenceColor}">${(coherence * 100).toFixed(0)}%</div>
            <div class="stat-label">Coherencia</div>
          </div>
          <div class="stat-card" style="padding: 12px;">
            <div class="stat-value" style="font-size: 24px;">${emotion.toFixed(2)}</div>
            <div class="stat-label">Valencia Emocional</div>
          </div>
        </div>
        
        <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; font-size: 13px;">
          <strong>Ambigüedades detectadas:</strong>
          ${env.analysis.identified_ambiguities.length > 0
                ? `<ul style="margin-left: 20px; margin-top: 5px;">${env.analysis.identified_ambiguities.map(a => `<li>${a.term} (${a.reason})</li>`).join('')}</ul>`
                : '<span style="color: var(--accent-green); margin-left: 8px;">Ninguna detectada ✓</span>'
            }
        </div>
      </div>
    `;
    },

    clearForm: () => {
        document.getElementById('messageContent').value = '';
        document.getElementById('analysisResult').innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📊</div>
        <p>Envía un mensaje para ver el análisis M/E</p>
      </div>
    `;
    },

    // ════════════════════════════════════════════════════════
    // 4. MEMORIA / ARCA
    // ════════════════════════════════════════════════════════

    loadMemoria: async () => {
        const list = document.getElementById('memoriaList');
        list.innerHTML = '<div class="empty-state"><p>Cargando registros...</p></div>';

        try {
            const res = await fetch(`${API_BASE}/memoria?limit=50`);
            const data = await res.json();

            if (!data.items || data.items.length === 0) {
                list.innerHTML = '<div class="empty-state"><p>La memoria está vacía.</p></div>';
                return;
            }

            // Update stats
            document.getElementById('statTotal').textContent = data.total;

            const coherences = data.items.map(i => i.plane?.M || 0).filter(v => v !== 0);
            const avgCoherence = coherences.length
                ? (coherences.reduce((a, b) => a + b, 0) / coherences.length).toFixed(2)
                : '-';
            document.getElementById('statCoherence').textContent = avgCoherence;

            const lastDate = new Date(data.items[0]?.provenance?.created || data.items[0]?.timestamp || Date.now());
            document.getElementById('statLast').textContent = lastDate.toLocaleTimeString();

            // Render items
            list.innerHTML = data.items.map(item => {
                // ✅ VALIDACIÓN DEFENSIVA - Extraer content con fallbacks
                const getContent = () => {
                    if (item.content) return item.content;
                    if (item.payload?.content) return item.payload.content;
                    if (typeof item.payload === 'string') return item.payload;
                    if (typeof item.payload === 'object') return JSON.stringify(item.payload);
                    return 'Sin contenido';
                };
                
                const content = getContent();
                const contentEscaped = String(content).replace(/'/g, "\\'").substring(0, 100);
                const contentDisplay = String(content).substring(0, 200);
                
                return `
        <div class="memoria-entry" onclick="alert('${contentEscaped}...')">
          <div class="memoria-meta">
            <span>${new Date(item?.provenance?.created || item?.timestamp || Date.now()).toLocaleString()}</span>
            <span>${item.entity_id} • ${item.perspective || item.source || 'N/A'}</span>
          </div>
          <div class="memoria-content">${contentDisplay}</div>
          <div class="memoria-scores">
            ${item.plane ? `
              <span class="score-chip" style="background:rgba(58,109,240,0.2); color:#3a6df0">M: ${item.plane.M}</span>
              <span class="score-chip" style="background:rgba(168,85,247,0.2); color:#a855f7">E: ${item.plane.E}</span>
            ` : ''}
            <span class="score-chip" style="background:rgba(255,255,255,0.1); color:#fff">ID: ${item?.message_id?.substring(0, 8) || "N/A"}</span>
          </div>
        </div>
      `;
            }).join('');

        } catch (e) {
            list.innerHTML = `<div class="empty-state" style="color:var(--accent-red)"><p>Error cargando memoria: ${e.message}</p></div>`;
        }
    },

    exportMemoria: () => {
        window.open(`${API_BASE}/memoria?limit=1000`, '_blank');
    },

    // ════════════════════════════════════════════════════════
    // 5. AGENTES
    // ════════════════════════════════════════════════════════

    registerAgent: async (e) => {
        e.preventDefault();

        const platform = document.getElementById('agentPlatform').value;
        const name = document.getElementById('agentName').value;
        const key = document.getElementById('agentKey').value;

        if (!platform || !name) {
            Station.showToast('Plataforma y Nombre son obligatorios', 'error');
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/register_agent`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ platform, name, api_key: key })
            });

            const data = await res.json();

            if (data.success) {
                Station.showToast('Agente registrado con éxito', 'success');
                document.getElementById('agentName').value = '';
                document.getElementById('agentKey').value = '';
                Station.loadAgents();
            } else {
                Station.showToast(`Error: ${data.message}`, 'error');
            }
        } catch (e) {
            Station.showToast(`Error de conexión: ${e.message}`, 'error');
        }
    },

    loadAgents: async () => {
        const list = document.getElementById('agentsList');

        try {
            const res = await fetch(`${API_BASE}/list_agents`);
            const data = await res.json();

            document.getElementById('agentCount').textContent = data.count || 0;

            if (!data.agents || data.agents.length === 0) {
                list.innerHTML = '<div class="empty-state"><p>Sin agentes registrados</p></div>';
                return;
            }

            list.innerHTML = data.agents.map(a => `
        <div class="agent-card">
          <div class="agent-icon">🤖</div>
          <div class="agent-name">${a.name}</div>
          <div class="agent-platform">${a.platform} • ${a.status}</div>
          <div style="font-size:11px; color:#555; margin-top:8px">ID: ${a.id}</div>
        </div>
      `).join('');

        } catch (e) {
            console.error(e);
        }
    },

    // ════════════════════════════════════════════════════════
    // UTILS
    // ════════════════════════════════════════════════════════

    showToast: (msg, type = 'info') => {
        const container = document.getElementById('toasts');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = msg;
        container.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3500);
    }
};

// Auto-init on load
document.addEventListener('DOMContentLoaded', Station.init);
