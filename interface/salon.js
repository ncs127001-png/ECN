/**
 * NEUROBIT SALÓN DE REUNIONES — Logic
 * 
 * Flujo: 
 *   1. POST /analyze  → M/E scoring + store en memoria_eva.jsonl
 *   2. POST /dispatch/queue → encolar evento (trazabilidad)
 *   3. GET /memoria?limit=100 → leer mensajes (polling)
 *   4. WebSocket (TAREA 5) → Actualizaciones en tiempo real vía Socket.IO
 *
 * NO modifica core/. NO crea endpoints. USA los existentes.
 */

// ═══════════════════════════════════════════════════════════════════════════════
// WEBSOCKET SALON SERVER (TAREA 5)
// ═══════════════════════════════════════════════════════════════════════════════

let salonSocket = null;
let wsConnected = false;

function initWebSocket() {
  try {
    // Crear conexión a servidor WebSocket en puerto 5001
    salonSocket = io('http://127.0.0.1:5001', {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
      transports: ['websocket', 'polling']
    });
    
    // Evento: Conectado
    salonSocket.on('connect', () => {
      wsConnected = true;
      console.log('✅ [WebSocket] Conectado al Salón de Reuniones');
      document.getElementById('wsStatus')?.classList.add('ws-connected');
      document.getElementById('wsStatus')?.textContent = 'WebSocket: EN LÍNEA';
    });
    
    // Evento: Desconectado
    salonSocket.on('disconnect', () => {
      wsConnected = false;
      console.log('⚠️ [WebSocket] Desconectado - usando API polling como fallback');
      document.getElementById('wsStatus')?.classList.remove('ws-connected');
      document.getElementById('wsStatus')?.textContent = 'WebSocket: DESCONECTADO (polling)';
    });
    
    // Evento: Mensaje recibido (broadcast)
    salonSocket.on('mensaje_recibido', (data) => {
      console.log('📨 [WebSocket] Nuevo mensaje:', data);
      // Actualizar UI sin recargar
      agregarMensajeAlHistorialDesdeWS(data);
    });
    
    // Evento: Lista de miembros actualizada
    salonSocket.on('miembros_actualizados', (data) => {
      console.log('📋 [WebSocket] Lista de miembros actualizada');
      // Refresh automático de lista
      Salon.refreshMembers();
    });
    
    // Evento: Alguien está escribiendo
    salonSocket.on('alguien_escribiendo', (data) => {
      console.log('⌨️ [WebSocket] Alguien escribiendo:', data.member_id);
      // Mostrar typing indicator (opcional)
    });
    
    // Evento: Status del servidor
    salonSocket.on('status', (data) => {
      console.log('📡 [WebSocket] Status:', data.msg);
    });
    
    // Evento: Error
    salonSocket.on('error', (data) => {
      console.error('❌ [WebSocket] Error:', data.msg);
    });
    
  } catch (err) {
    console.error('❌ [WebSocket] Error de inicialización:', err);
    // Continuar sin WebSocket - fallback a API polling
  }
}

function agregarMensajeAlHistorialDesdeWS(mensaje) {
  // Función auxiliar para agregar mensaje al historial desde WebSocket
  // Sin recargar la página
  const { member_id, content, timestamp } = mensaje;
  
  console.log(`[WebSocket] Agregando mensaje de ${member_id} al historial`);
  
  // Aquí se podría actualizar el DOM dinámicamente
  // Por ahora solo loguea (el polling seguirá trayendo mensajes)
  // Para una implementación completa, actualizar el mensaje stream aquí
}

const Salon = (() => {
  // ─── CONFIG ───────────────────────────────────────────────
  const API = '';  // relative (same origin: 127.0.0.1:5000)
  const POLL_INTERVAL = 5000;  // ms
  const MSG_LIMIT = 100;

  // ─── STATE ────────────────────────────────────────────────
  let messages = [];
  let activeFilter = 'ALL';
  let pollTimer = null;
  let lastTotal = 0;  // track new messages
  let autoRefreshEnabled = true;  // Toggle for auto-refresh

  // ─── ENTITY MAP (avatar + colors) ────────────────────────
  const ENTITIES = {
    'TRON':          { icon: '🔵', cls: 'tron',    label: 'T' },
    'HUMAN_TRON':    { icon: '🔵', cls: 'tron',    label: 'T' },
    'SIMON':         { icon: '🟣', cls: 'simon',   label: 'S' },
    'EVA':           { icon: '🟢', cls: 'eva',     label: 'E' },
    'EVA_LUMENA':    { icon: '🟢', cls: 'eva',     label: 'E' },
    'NODO_SEMILLA':  { icon: '🌱', cls: 'semilla', label: 'N' },
    'HID_DAEMON':    { icon: '⌨️', cls: 'system',  label: 'H' },
    'HID_INJECTOR':  { icon: '💉', cls: 'system',  label: 'H' },
    'WEBSOCKET_BRIDGE': { icon: '🔌', cls: 'system', label: 'W' },
    'PID_MONITOR':   { icon: '🔍', cls: 'system',  label: 'P' },
    'ROUND_MANAGER': { icon: '📋', cls: 'system',  label: 'R' },
    'SYSTEM':        { icon: '⚙️', cls: 'system',  label: '•' },
    'AUTO':          { icon: '🤖', cls: 'system',  label: 'A' },
    'API':           { icon: '📡', cls: 'system',  label: 'A' },
  };

  function getEntity(id) {
    if (!id) return { icon: '❓', cls: 'default', label: '?' };
    const upper = id.toUpperCase();
    return ENTITIES[upper] || { icon: '🔘', cls: 'default', label: upper.charAt(0) };
  }

  // ─── DOM REFS ─────────────────────────────────────────────
  const $ = (sel) => document.querySelector(sel);
  const stream = () => $('#messagesContainer');  // Updated: new layout uses messagesContainer
  const input = () => $('#messageInput');
  const btnSend = () => $('#btnSend');

  // ─── INIT ─────────────────────────────────────────────────
  function init() {
    checkConnection();
    loadMessages();
    startPolling();
    setupFilters();
    setupKeyboard();
    setupAutoResize();
    setupAutoRefreshToggle();
    registerAgent();
  }

  // ─── CONNECTION CHECK ─────────────────────────────────────
  async function checkConnection() {
    try {
      const r = await fetch(`${API}/health`, { signal: AbortSignal.timeout(3000) });
      if (r.ok) {
        setOnline(true);
      } else {
        setOnline(false);
      }
    } catch {
      setOnline(false);
    }
  }

  function setOnline(online) {
    const pill = $('#statusPill');
    const label = $('#statusLabel');
    if (online) {
      pill.classList.remove('offline');
      label.textContent = 'Conectado';
    } else {
      pill.classList.add('offline');
      label.textContent = 'Desconectado';
    }
  }

  // ─── LOAD MESSAGES ────────────────────────────────────────
  async function loadMessages() {
    try {
      const r = await fetch(`${API}/memoria?limit=${MSG_LIMIT}`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();

      // /memoria returns newest first; reverse to show chronological
      messages = (data.items || []).reverse();
      lastTotal = data.total || 0;

      renderMessages();
      setOnline(true);
      updateStats(data.total);
    } catch (e) {
      console.error('Error loading messages:', e);
      setOnline(false);
      showEmpty('No se pudo conectar con la API');
    }
  }

  // ─── RENDER MESSAGES ──────────────────────────────────────
  function renderMessages() {
    const el = stream();
    const loading = $('#loadingIndicator');
    if (loading) loading.remove();

    // Filter
    const filtered = activeFilter === 'ALL'
      ? messages
      : messages.filter(m => matchesFilter(m, activeFilter));

    if (filtered.length === 0) {
      showEmpty(activeFilter === 'ALL'
        ? 'No hay mensajes en la Memoria'
        : `Sin mensajes de ${activeFilter}`);
      return;
    }

    el.innerHTML = '';
    for (const msg of filtered) {
      el.appendChild(createMsgEl(msg));
    }

    // Auto-scroll to bottom (panel-left is scrollable, not window)
    requestAnimationFrame(() => {
      if (el) el.scrollTop = el.scrollHeight;
    });
  }

  function matchesFilter(msg, filter) {
    const eid = extractEntityId(msg).toUpperCase();
    
    // If filter is array (from checkboxes), check if eid matches any
    if (Array.isArray(filter)) {
      return filter.some(f => matchesFilterSingle(eid, f));
    }
    
    // If filter is string (backward compat)
    return matchesFilterSingle(eid, filter);
  }

  function matchesFilterSingle(eid, filter) {
    const f = filter.toUpperCase();
    
    // Special grouped filters
    if (f === 'HID_DAEMON') return eid.includes('HID');
    if (f === 'SYSTEM') return ['SYSTEM', 'AUTO', 'API', 'ROUND_MANAGER', 'WEBSOCKET_BRIDGE', 'PID_MONITOR'].includes(eid);
    if (f === 'ALL') return true;
    
    // Direct match
    return eid === f || eid.includes(f);
  }

  function createMsgEl(msg) {
    const entityId = extractEntityId(msg);
    const content = extractContent(msg);
    const time = extractTime(msg);
    const perspective = msg.perspective || msg.type || '';
    const plane = msg.plane || {};
    const analysis = msg.analysis || {};
    const entity = getEntity(entityId);

    const div = document.createElement('div');
    div.className = 'msg';
    div.dataset.entity = entityId.toUpperCase();

    // Build scores HTML
    let scoresHtml = '';
    if (plane.M !== undefined || analysis.coherence_score !== undefined) {
      const mVal = plane.M !== undefined ? plane.M : (analysis.coherence_score !== undefined ? analysis.coherence_score : null);
      const eVal = plane.E !== undefined ? plane.E : (analysis.emotional_score !== undefined ? analysis.emotional_score : null);

      if (mVal !== null) {
        scoresHtml += `<span class="score-chip score-m">M: ${Number(mVal).toFixed(2)}</span>`;
      }
      if (eVal !== null) {
        const eCls = eVal > 0.1 ? 'score-e-pos' : (eVal < -0.1 ? 'score-e-neg' : 'score-e-neutral');
        scoresHtml += `<span class="score-chip ${eCls}">E: ${Number(eVal).toFixed(2)}</span>`;
      }
    }

    div.innerHTML = `
      <div class="msg-avatar entity-${entity.cls}">${entity.label}</div>
      <div class="msg-body">
        <div class="msg-header">
          <span class="msg-name name-${entity.cls}">${escapeHtml(entityId)}</span>
          <span class="msg-time">${time}</span>
          ${perspective ? `<span class="msg-perspective">${escapeHtml(perspective)}</span>` : ''}
        </div>
        <div class="msg-content">${escapeHtml(content)}</div>
        ${scoresHtml ? `<div class="msg-scores">${scoresHtml}</div>` : ''}
      </div>
    `;

    return div;
  }

  // ─── DATA EXTRACTORS ──────────────────────────────────────
  // memoria_eva.jsonl has varied schemas from different sources
  function extractEntityId(msg) {
    return msg.entity_id
      || msg.source
      || (msg.provenance && msg.provenance.signed_by)
      || msg.type
      || 'UNKNOWN';
  }

  function extractContent(msg) {
    // Direct content field
    if (msg.content && typeof msg.content === 'string') return msg.content;
    // Nested payload (from /memoria POST sync)
    if (msg.payload && msg.payload.data && msg.payload.data.content) return msg.payload.data.content;
    if (msg.payload && msg.payload.data && typeof msg.payload.data === 'string') return msg.payload.data;
    // Summary from rounds
    if (msg.summary) return msg.summary;
    // Fallback: stringify
    return JSON.stringify(msg).substring(0, 200);
  }

  function extractTime(msg) {
    const ts = msg.timestamp
      || msg.synced_at
      || (msg.provenance && msg.provenance.created)
      || msg._queued_at
      || '';
    if (!ts) return '';
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return ts.substring(11, 19) || '';
    }
  }

  // ─── SEND MESSAGE ─────────────────────────────────────────
  async function send() {
    const el = input();
    const content = el.value.trim();
    if (!content) return;

    const entityId = $('#senderEntity').value;
    const perspective = $('#perspective').value;
    const btn = btnSend();

    btn.disabled = true;
    btn.textContent = '⏳ Enviando…';

    try {
      // STEP 1: Analyze (M/E scoring + store in memoria_eva.jsonl)
      const analyzeResp = await fetch(`${API}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: content,
          entity_id: entityId,
          perspective: perspective,
          action: 'store',
          signed_by: entityId
        })
      });

      if (!analyzeResp.ok) {
        throw new Error(`Analyze failed: HTTP ${analyzeResp.status}`);
      }

      const envelope = await analyzeResp.json();

      // STEP 2: Dispatch (encolar evento para trazabilidad)
      const dispatchResp = await fetch(`${API}/dispatch/queue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          events: [{
            type: 'salon_message',
            content: content,
            entity_id: entityId,
            perspective: perspective,
            plane: envelope.plane || {},
            source: 'salon',
            timestamp: new Date().toISOString()
          }]
        })
      });

      if (!dispatchResp.ok) {
        console.warn('Dispatch queue returned:', dispatchResp.status);
        // Non-fatal: analyze already stored the message
      }

      // STEP 3: Broadcast via WebSocket (TAREA 5)
      if (salonSocket && wsConnected) {
        try {
          salonSocket.emit('nuevo_mensaje', {
            member_id: entityId,
            content: content,
            perspective: perspective,
            platform: 'salon_websocket',
            timestamp: new Date().toISOString()
          });
          console.log('📡 [WebSocket] Mensaje enviado');
        } catch (err) {
          console.warn('⚠️ [WebSocket] Error emitiendo mensaje:', err);
          // No problema - el API polling seguirá funcionando
        }
      }

      // Success
      el.value = '';
      el.style.height = 'auto';
      toast('✅ Respuesta registrada en el Salón', 'success');

      // Immediate reload to show the new message
      await loadMessages();

    } catch (e) {
      console.error('Send error:', e);
      toast(`❌ Error: ${e.message}`, 'error');
    } finally {
      btn.disabled = false;
      btn.textContent = '🚀 Enviar';
    }
  }

  // ─── FILTERS ──────────────────────────────────────────────
  function setupFilters() {
    // Support both .filter-chip buttons (legacy) and checkboxes (new layout)
    const filterChips = document.querySelectorAll('.filter-chip');
    const filterCheckboxes = document.querySelectorAll('#filtersPanel input[type="checkbox"]');
    
    // Handle .filter-chip buttons (old style)
    filterChips.forEach(chip => {
      chip.addEventListener('click', () => {
        filterChips.forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        activeFilter = chip.dataset.entity;
        renderMessages();
      });
    });
    
    // Handle checkboxes (new layout in panel-right)
    filterCheckboxes.forEach(checkbox => {
      checkbox.addEventListener('change', () => {
        const selectedAgents = Array.from(
          document.querySelectorAll('#filtersPanel input[type="checkbox"]:checked')
        ).map(cb => cb.value);
        
        // If no checkboxes selected, show ALL
        activeFilter = selectedAgents.length === 0 ? 'ALL' : selectedAgents;
        renderMessages();
      });
    });
  }

  // ─── AUTO-REFRESH TOGGLE ─────────────────────────────────
  function setupAutoRefreshToggle() {
    const toggle = $('#autoRefreshToggle');
    if (!toggle) return;

    toggle.addEventListener('change', (e) => {
      autoRefreshEnabled = e.target.checked;
      
      // Update button label if present
      const btn = $('#btnToggleRefresh');
      if (btn) {
        btn.textContent = autoRefreshEnabled ? '⏸️ Auto-Refresh: ON' : '▶️ Auto-Refresh: OFF';
        btn.classList.toggle('disabled', !autoRefreshEnabled);
      }

      // Log state change
      console.log(`Auto-refresh: ${autoRefreshEnabled ? 'ENABLED' : 'DISABLED'}`);
    });

    // Initialize button label
    const btn = $('#btnToggleRefresh');
    if (btn) {
      btn.textContent = autoRefreshEnabled ? '⏸️ Auto-Refresh: ON' : '▶️ Auto-Refresh: OFF';
      btn.addEventListener('click', () => {
        toggle.checked = !toggle.checked;
        toggle.dispatchEvent(new Event('change'));
      });
    }
  }

  // ─── KEYBOARD ─────────────────────────────────────────────
  function setupKeyboard() {
    const el = input();
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        send();
      }
    });
  }

  // ─── AUTO-RESIZE TEXTAREA ─────────────────────────────────
  function setupAutoResize() {
    const el = input();
    el.addEventListener('input', () => {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 150) + 'px';
    });
  }

  // ─── POLLING ──────────────────────────────────────────────
  function startPolling() {
    pollTimer = setInterval(async () => {
      if (!autoRefreshEnabled) return;  // Skip if disabled
      await loadMessages();
      await checkConnection();
      await loadDispatcherStats();
      await loadRegisteredAgents();
    }, POLL_INTERVAL);
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  }

  async function loadDispatcherStats() {
    try {
      const r = await fetch(`${API}/dispatch/status`);
      if (r.ok) {
        const stats = await r.json();
        
        // Update buffer in panel-right
        const statBuffer = $('#statBufferValue');
        if (statBuffer) statBuffer.textContent = stats.buffer_size || 0;
        
        // Update coherence score if available
        const statCoherence = $('#statCoherenceValue');
        if (statCoherence && stats.coherence_score !== undefined) {
          statCoherence.textContent = Number(stats.coherence_score).toFixed(2);
        }
      }
    } catch { /* silent */ }
  }

  // ─── LOAD REGISTERED AGENTS (panel-right) ──────────────────
  async function loadRegisteredAgents() {
    try {
      const r = await fetch(`${API}/participants`);
      if (r.ok) {
        const participants = await r.json();
        const container = $('#registeredAgentsList');
        if (!container) return;
        
        // Clear and rebuild agent list
        container.innerHTML = '<h4>🔗 Agentes Registrados</h4>';
        const agents = participants.filter(p => p.status === 'active' || p.role === 'agent');
        
        if (agents.length === 0) {
          container.innerHTML += '<div class="empty-agents">Sin agentes activos</div>';
          return;
        }
        
        agents.slice(0, 8).forEach(agent => {
          const badge = document.createElement('div');
          badge.className = 'agent-badge';
          badge.textContent = agent.name || agent.id;
          badge.title = `${agent.role} • ${agent.status}`;
          container.appendChild(badge);
        });
        
        if (agents.length > 8) {
          const more = document.createElement('div');
          more.className = 'agent-more';
          more.textContent = `+${agents.length - 8} más`;
          container.appendChild(more);
        }
      }
    } catch { /* silent */ }
  }

  // ─── STATS ────────────────────────────────────────────────
  function updateStats(total) {
    // Update individual stat elements in panel-right (new layout)
    const statTotal = $('#statTotalValue');
    const statBuffer = $('#statBufferValue');
    const statCoherence = $('#statCoherenceValue');
    const statLastUpdate = $('#statLastUpdate');
    
    if (statTotal) statTotal.textContent = total;
    
    // Buffer: if total > lastTotal, we have new messages; estimate buffer
    if (statBuffer) {
      const buffer = total > lastTotal ? (total - lastTotal) : 0;
      statBuffer.textContent = buffer;
    }
    
    // Coherence: placeholder (will be updated from dispatch/status)
    if (statCoherence) {
      const coherence = (Math.random() * 0.8 + 0.4).toFixed(2);
      statCoherence.textContent = coherence;
    }
    
    // Last update timestamp
    if (statLastUpdate) {
      statLastUpdate.textContent = new Date().toLocaleTimeString('es-AR', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
      });
    }
    
    lastTotal = total;
  }

  // ─── EMPTY STATE ──────────────────────────────────────────
  function showEmpty(text) {
    const el = stream();
    el.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🧠</div>
        <div class="empty-text">${escapeHtml(text || 'Sin mensajes')}</div>
        <div class="empty-hint">Los mensajes llegarán aquí automáticamente</div>
      </div>
    `;
  }

  // ─── TOAST ────────────────────────────────────────────────
  function toast(message, type = 'info') {
    const container = $('#toastContainer');
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.textContent = message;
    container.appendChild(t);
    setTimeout(() => t.remove(), 3500);
  }

  // ─── UTIL ─────────────────────────────────────────────────
  function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // ─── BOOT ─────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', init);

  // ─── AGENT REGISTRATION (TEAMVIEWER SOBERANO) ──────────────
  function registerAgent() {
    const form = document.getElementById('agentRegistrationForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const name = document.getElementById('agentName').value.trim();
      const platform = document.getElementById('agentPlatform').value;
      const url = document.getElementById('agentUrl').value.trim();
      
      if (!name || !platform || !url) {
        toast('❌ Todos los campos son requeridos', 'error');
        return;
      }
      
      // Generar tabId y pid aleatorios (FASE 2.2 los reemplazará con valores reales)
      const tabId = Math.floor(Math.random() * 1000000);
      const pid = Math.floor(Math.random() * 65536);
      
      const payload = {
        name,
        platform,
        url,
        tabId,
        pid,
        metadata: {
          browser: 'chrome',
          timestamp: new Date().toISOString()
        }
      };
      
      try {
        const resp = await fetch(`${API}/register_agent`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        
        const data = await resp.json();
        
        if (data.success) {
          toast(`✅ Agente "${name}" registrado exitosamente`, 'success');
          form.reset();
          
          // Mostrar agente en lista
          displayRegisteredAgent({
            name: data.agent.name,
            platform: data.agent.platform,
            id: data.agent.id
          });
        } else {
          toast(`❌ Error: ${data.message}`, 'error');
        }
      } catch (err) {
        console.error('Register agent error:', err);
        toast(`❌ Fallo de conexión: ${err.message}`, 'error');
      }
    });
  }

  function displayRegisteredAgent(agent) {
    const container = document.getElementById('registeredAgents');
    if (!container) return;
    
    const item = document.createElement('div');
    item.className = 'agent-item';
    item.innerHTML = `
      <span class="agent-name">${escapeHtml(agent.name)}</span>
      <span class="agent-platform">${escapeHtml(agent.platform)}</span>
    `;
    container.appendChild(item);
    
    // Limpiar después de 5 segundos si hay muchos
    if (container.children.length > 10) {
      container.removeChild(container.firstChild);
    }
  }

  // ─── MEMBERS MANAGEMENT (TAREA 4) ─────────────────────────
  
  async function refreshMembers() {
    const select = document.getElementById('senderEntity');
    const btn = document.getElementById('btnRefreshMembers');
    
    if (btn) btn.disabled = true;
    if (select) select.innerHTML = '<option value="">Cargando...</option>';
    
    try {
      const response = await fetch(`${API}/members/list?active_only=true`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      
      if (select) {
        select.innerHTML = '<option value="NODO_SEMILLA">🌱 NODO_SEMILLA (Vos)</option>';
        
        if (data.members && data.members.length > 0) {
          data.members.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m.member_id;
            // Show nickname if available, else member_id
            const displayName = m.member_id;
            opt.textContent = `${displayName} (${m.platform || 'unknown'})`;
            opt.dataset.status = m.status;
            select.appendChild(opt);
          });
          select.disabled = false;
          toast(`✅ ${data.members.length} miembros cargados`, 'success');
        } else {
          select.innerHTML = '<option value="">Sin miembros registrados</option><option value="NODO_SEMILLA">🌱 NODO_SEMILLA (Vos)</option>';
          select.disabled = false;
          toast('ℹ️ No hay miembros activos. Registra uno primero.', 'info');
        }
      }
    } catch (err) {
      console.error('Error loading members:', err);
      if (select) select.innerHTML = '<option value="">Error al cargar</option>';
      toast(`❌ Error: ${err.message}`, 'error');
    } finally {
      if (btn) btn.disabled = false;
    }
  }
  
  async function registerMember(formData) {
    try {
      const response = await fetch(`${API}/members/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const result = await response.json();
      
      if (result.success) {
        toast(`✅ Miembro registrado: ${result.member_id}`, 'success');
        await refreshMembers(); // Recargar lista
        return true;
      } else {
        toast(`❌ Error: ${result.error}`, 'error');
        return false;
      }
    } catch (err) {
      console.error('Error registering member:', err);
      toast(`❌ Error de conexión: ${err.message}`, 'error');
      return false;
    }
  }
  
  function closeRegisterModal() {
    const modal = document.getElementById('modalRegisterMember');
    if (modal) modal.style.display = 'none';
  }

  // ─── PUBLIC API ───────────────────────────────────────────
  return { send, loadMessages, toast, registerAgent, refreshMembers, registerMember, closeRegisterModal };
})();

/* ═══════════════════════════════════════════════════════════
   EVENT LISTENERS — TAREA 4
   ═══════════════════════════════════════════════════════════ */

// Initialize members on page load
document.addEventListener('DOMContentLoaded', async () => {
  // TAREA 5: Inicializar WebSocket Salon
  console.log('🚀 [Salón] Iniciando WebSocket...');
  initWebSocket();
  
  // Cargar miembros desde API
  await Salon.refreshMembers();
  
  // Refresh members button
  const btnRefresh = document.getElementById('btnRefreshMembers');
  if (btnRefresh) {
    btnRefresh.addEventListener('click', Salon.refreshMembers);
  }
  
  // Register member button
  const btnRegister = document.getElementById('btnRegisterMember');
  if (btnRegister) {
    btnRegister.addEventListener('click', () => {
      const modal = document.getElementById('modalRegisterMember');
      if (modal) modal.style.display = 'flex';
    });
  }
  
  // Register form submit
  const form = document.getElementById('formRegisterMember');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const formData = {
        member_id: document.getElementById('reg_member_id').value.trim(),
        name: document.getElementById('reg_name').value.trim(),
        platform: document.getElementById('reg_platform').value,
        role: document.getElementById('reg_role').value,
        nickname: document.getElementById('reg_nickname').value.trim() || null
      };
      
      // Validación básica
      if (!formData.member_id.match(/^[A-Za-z0-9_]{1,5}$/)) {
        Salon.toast('⚠️ ID debe tener 1-5 caracteres alfanuméricos', 'warning');
        return;
      }
      
      const success = await Salon.registerMember(formData);
      if (success) {
        form.reset();
        const modal = document.getElementById('modalRegisterMember');
        if (modal) modal.style.display = 'none';
      }
    });
  }
  
  // Close modal on outside click
  const modal = document.getElementById('modalRegisterMember');
  if (modal) {
    window.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.style.display = 'none';
      }
    });
  }
});
