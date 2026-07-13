/**
 * agents_management.js
 * 
 * Panel de Gestión de Agentes para ESTACIÓN CENTRAL v3.0
 * 
 * Funcionalidad:
 * - Registrar nuevos agentes (ChatGPT, Qwen, Gemini, Local Llama)
 * - Listar agentes activos/inactivos
 * - Verificar estado de conectividad
 * - Crear salas de sesión multi-agente
 * - Orquestar rondas de trabajo
 * 
 * Protocol: NEUROBIT v2.1
 * Validator: SIMON
 * 
 * Enero 2026
 */

class AgentsManagementPanel {
  constructor(containerId = '#agents-panel') {
    this.container = document.querySelector(containerId);
    this.agents = [];
    this.sessions = [];
    this.currentSession = null;
    this.currentRound = null;
    
    // Plataformas soportadas
    this.platforms = {
      'chatgpt': { name: 'OpenAI ChatGPT', icon: '🔵', requiresKey: true },
      'qwen': { name: 'Alibaba Qwen', icon: '🟠', requiresKey: true },
      'gemini': { name: 'Google Gemini', icon: '🔴', requiresKey: true },
      'local_llama': { name: 'Local Llama', icon: '🟡', requiresKey: false },
      'claude': { name: 'Anthropic Claude', icon: '🟣', requiresKey: true },
    };
    
    this.init();
  }
  
  // ========================================================================
  // INICIALIZACIÓN
  // ========================================================================
  
  init() {
    console.log('🧬 Inicializando panel de agentes...');
    this.render();
    this.loadAgents();
  }
  
  render() {
    this.container.innerHTML = `
      <div class="agents-management">
        <style>${this.getStyles()}</style>
        
        <!-- TAB: Registro de Agentes -->
        <div class="agents-tabs">
          <button class="tab-btn active" data-tab="register">
            ➕ Registrar Agente
          </button>
          <button class="tab-btn" data-tab="agents-list">
            📋 Agentes Activos
          </button>
          <button class="tab-btn" data-tab="sessions">
            🎭 Sala de Sesión
          </button>
        </div>
        
        <!-- TAB CONTENT: Register Agent -->
        <div class="tab-content active" id="tab-register">
          <h3>Registrar Nuevo Agente</h3>
          
          <div class="form-group">
            <label>Plataforma:</label>
            <select id="platform-select">
              <option value="">-- Seleccionar --</option>
              ${Object.entries(this.platforms).map(([key, p]) => 
                `<option value="${key}">${p.icon} ${p.name}</option>`
              ).join('')}
            </select>
          </div>
          
          <div class="form-group">
            <label>Nombre del Agente:</label>
            <input type="text" id="agent-name" placeholder="ej: GPT-4 Pro, Qwen Assistant...">
          </div>
          
          <div class="form-group" id="api-key-group" style="display: none;">
            <label>API Key:</label>
            <input type="password" id="api-key" placeholder="Proporcione su API key">
            <small>🔒 Se hashea y nunca se almacena en claro</small>
          </div>
          
          <div class="form-group">
            <label>Metadatos (JSON opcional):</label>
            <textarea id="agent-metadata" placeholder='{"model": "gpt-4", "version": "latest"}' rows="3"></textarea>
          </div>
          
          <button id="register-btn" class="btn btn-primary">
            🚀 Registrar Agente
          </button>
          
          <div id="register-status" class="status-message"></div>
        </div>
        
        <!-- TAB CONTENT: Agents List -->
        <div class="tab-content" id="tab-agents-list">
          <h3>Agentes Registrados</h3>
          
          <div class="filter-group">
            <button class="filter-btn active" data-filter="all">Todos</button>
            <button class="filter-btn" data-filter="active">🟢 Activos</button>
            <button class="filter-btn" data-filter="pending_verification">⏳ Verificación</button>
            <button class="filter-btn" data-filter="failed">🔴 Fallidos</button>
          </div>
          
          <div id="agents-container" class="agents-container">
            <p class="empty-state">Cargando agentes...</p>
          </div>
        </div>
        
        <!-- TAB CONTENT: Sala de Sesión -->
        <div class="tab-content" id="tab-sessions">
          <h3>Sala de Sesión Multi-Agente</h3>
          
          <div class="session-controls">
            <div class="form-group">
              <label>Nombre de la Sala:</label>
              <input type="text" id="session-name" placeholder="ej: Sesión de Investigación Q1 2026">
            </div>
            
            <div class="form-group">
              <label>Seleccionar Agentes:</label>
              <div id="agents-checklist" class="checklist">
                <p class="empty-state">Primero registra agentes</p>
              </div>
            </div>
            
            <button id="create-session-btn" class="btn btn-primary">
              🎭 Crear Sala
            </button>
          </div>
          
          <div id="session-container" class="session-container"></div>
        </div>
      </div>
    `;
    
    this.attachEventListeners();
  }
  
  getStyles() {
    return `
      .agents-management {
        font-family: 'Courier New', monospace;
        color: #e0e0e0;
        background: #1a1a1a;
        padding: 20px;
        border-radius: 8px;
      }
      
      .agents-tabs {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        border-bottom: 2px solid #333;
        padding-bottom: 10px;
      }
      
      .tab-btn {
        background: transparent;
        border: none;
        color: #999;
        cursor: pointer;
        padding: 10px 15px;
        border-bottom: 3px solid transparent;
        transition: all 0.3s;
      }
      
      .tab-btn.active {
        color: #4ade80;
        border-bottom-color: #4ade80;
      }
      
      .tab-btn:hover {
        color: #e0e0e0;
      }
      
      .tab-content {
        display: none;
      }
      
      .tab-content.active {
        display: block;
      }
      
      .form-group {
        margin-bottom: 15px;
      }
      
      .form-group label {
        display: block;
        margin-bottom: 5px;
        color: #4ade80;
        font-weight: bold;
      }
      
      .form-group input,
      .form-group select,
      .form-group textarea {
        width: 100%;
        padding: 8px;
        background: #222;
        border: 1px solid #333;
        color: #e0e0e0;
        border-radius: 4px;
        font-family: inherit;
      }
      
      .form-group small {
        display: block;
        margin-top: 3px;
        color: #666;
        font-size: 12px;
      }
      
      .btn {
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s;
      }
      
      .btn-primary {
        background: #4ade80;
        color: #000;
      }
      
      .btn-primary:hover {
        background: #22c55e;
      }
      
      .status-message {
        margin-top: 15px;
        padding: 10px;
        border-radius: 4px;
        display: none;
      }
      
      .status-message.success {
        background: #0f3a1a;
        border-left: 3px solid #4ade80;
        color: #4ade80;
        display: block;
      }
      
      .status-message.error {
        background: #3a0f0f;
        border-left: 3px solid #ef4444;
        color: #ef4444;
        display: block;
      }
      
      .agents-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 15px;
        margin-top: 15px;
      }
      
      .agent-card {
        background: #222;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 15px;
        transition: all 0.3s;
      }
      
      .agent-card:hover {
        border-color: #4ade80;
        box-shadow: 0 0 10px rgba(74, 222, 128, 0.1);
      }
      
      .agent-card h4 {
        margin: 0 0 10px 0;
        color: #4ade80;
      }
      
      .agent-status {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        margin: 5px 0;
      }
      
      .agent-status.active {
        background: #0f3a1a;
        color: #4ade80;
      }
      
      .agent-status.pending {
        background: #3a3a0f;
        color: #eab308;
      }
      
      .agent-status.failed {
        background: #3a0f0f;
        color: #ef4444;
      }
      
      .filter-group {
        display: flex;
        gap: 10px;
        margin-bottom: 15px;
      }
      
      .filter-btn {
        background: #222;
        border: 1px solid #333;
        color: #999;
        padding: 8px 12px;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s;
      }
      
      .filter-btn.active {
        background: #4ade80;
        color: #000;
        border-color: #4ade80;
      }
      
      .checklist {
        background: #222;
        border: 1px solid #333;
        border-radius: 4px;
        padding: 10px;
        max-height: 200px;
        overflow-y: auto;
      }
      
      .checklist-item {
        display: flex;
        align-items: center;
        padding: 8px;
        border-bottom: 1px solid #333;
      }
      
      .checklist-item:last-child {
        border-bottom: none;
      }
      
      .checklist-item input {
        margin-right: 10px;
      }
      
      .round-definition {
        background: #222;
        border: 1px solid #333;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 15px;
      }
      
      .empty-state {
        text-align: center;
        color: #666;
        padding: 20px;
      }
    `;
  }
  
  // ========================================================================
  // EVENT LISTENERS
  // ========================================================================
  
  attachEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
    });
    
    // Platform selector
    document.getElementById('platform-select').addEventListener('change', (e) => {
      const platform = e.target.value;
      const apiKeyGroup = document.getElementById('api-key-group');
      if (this.platforms[platform]?.requiresKey) {
        apiKeyGroup.style.display = 'block';
      } else {
        apiKeyGroup.style.display = 'none';
      }
    });
    
    // Register agent button
    document.getElementById('register-btn').addEventListener('click', () => this.registerAgent());
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
      btn.addEventListener('click', (e) => this.filterAgents(e.target.dataset.filter));
    });
    
    // Create session button
    document.getElementById('create-session-btn').addEventListener('click', () => this.createSession());
  }
  
  switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(t => {
      t.classList.remove('active');
    });
    
    // Deactivate all buttons
    document.querySelectorAll('.tab-btn').forEach(b => {
      b.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(`tab-${tabName}`).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Refresh data if needed
    if (tabName === 'agents-list') {
      this.loadAgents();
    } else if (tabName === 'sessions') {
      this.loadSessions();
    }
  }
  
  // ========================================================================
  // AGENT REGISTRATION
  // ========================================================================
  
  async registerAgent() {
    const platform = document.getElementById('platform-select').value;
    const name = document.getElementById('agent-name').value;
    const apiKey = document.getElementById('api-key').value;
    const metadataStr = document.getElementById('agent-metadata').value;
    
    if (!platform || !name) {
      this.showStatus('❌ Falta plataforma o nombre', 'error');
      return;
    }
    
    let metadata = {};
    if (metadataStr) {
      try {
        metadata = JSON.parse(metadataStr);
      } catch (e) {
        this.showStatus('❌ Metadatos JSON inválidos', 'error');
        return;
      }
    }
    
    try {
      const response = await fetch('/register_agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform, name, api_key: apiKey, metadata })
      });
      
      const result = await response.json();
      
      if (result.success) {
        this.showStatus(`✅ ${result.message}`, 'success');
        // Limpiar formulario
        document.getElementById('platform-select').value = '';
        document.getElementById('agent-name').value = '';
        document.getElementById('api-key').value = '';
        document.getElementById('agent-metadata').value = '';
        
        // Recargar lista
        this.loadAgents();
      } else {
        this.showStatus(`❌ Error: ${result.message}`, 'error');
      }
    } catch (error) {
      this.showStatus(`❌ Error de conexión: ${error}`, 'error');
    }
  }
  
  // ========================================================================
  // AGENT LISTING
  // ========================================================================
  
  async loadAgents() {
    try {
      const response = await fetch('/list_agents');
      const result = await response.json();
      this.agents = result.agents || [];
      this.renderAgentsList();
      this.renderAgentsChecklist();
    } catch (error) {
      console.error('Error cargando agentes:', error);
    }
  }
  
  renderAgentsList() {
    const container = document.getElementById('agents-container');
    
    if (this.agents.length === 0) {
      container.innerHTML = '<p class="empty-state">No hay agentes registrados aún</p>';
      return;
    }
    
    container.innerHTML = this.agents.map(agent => `
      <div class="agent-card">
        <h4>${this.platforms[agent.platform]?.icon || '🤖'} ${agent.name}</h4>
        <div class="agent-status ${agent.status}">
          ${this.getStatusEmoji(agent.status)} ${agent.status}
        </div>
        <div style="font-size: 12px; color: #999; margin-top: 10px;">
          <p>ID: <code>${agent.id}</code></p>
          <p>Plataforma: ${this.platforms[agent.platform]?.name || agent.platform}</p>
          <p>Registrado: ${new Date(agent.registered_at).toLocaleString()}</p>
          <p>Mensajes: ${agent.stats?.messages_sent || 0} enviados</p>
        </div>
      </div>
    `).join('');
  }
  
  renderAgentsChecklist() {
    const container = document.getElementById('agents-checklist');
    
    if (this.agents.length === 0) {
      container.innerHTML = '<p class="empty-state">Primero registra agentes</p>';
      return;
    }
    
    container.innerHTML = this.agents.map(agent => `
      <div class="checklist-item">
        <input type="checkbox" value="${agent.id}" class="agent-checkbox">
        <label style="margin: 0; color: #e0e0e0;">
          ${this.platforms[agent.platform]?.icon || '🤖'} ${agent.name}
        </label>
      </div>
    `).join('');
  }
  
  filterAgents(filter) {
    // Update button state
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
    
    // Filter and render
    const filtered = filter === 'all' 
      ? this.agents 
      : this.agents.filter(a => a.status === filter);
    
    const container = document.getElementById('agents-container');
    container.innerHTML = filtered.map(agent => `
      <div class="agent-card">
        <h4>${this.platforms[agent.platform]?.icon || '🤖'} ${agent.name}</h4>
        <div class="agent-status ${agent.status}">
          ${this.getStatusEmoji(agent.status)} ${agent.status}
        </div>
        <div style="font-size: 12px; color: #999; margin-top: 10px;">
          <p>ID: <code>${agent.id}</code></p>
          <p>Plataforma: ${this.platforms[agent.platform]?.name || agent.platform}</p>
        </div>
      </div>
    `).join('');
  }
  
  // ========================================================================
  // SESSION MANAGEMENT
  // ========================================================================
  
  async createSession() {
    const sessionName = document.getElementById('session-name').value;
    const selectedAgents = Array.from(document.querySelectorAll('.agent-checkbox:checked'))
      .map(cb => cb.value);
    
    if (!sessionName || selectedAgents.length === 0) {
      this.showStatus('❌ Nombre de sala y agentes requeridos', 'error');
      return;
    }
    
    try {
      const response = await fetch('/create_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: sessionName, agent_ids: selectedAgents })
      });
      
      const result = await response.json();
      
      if (result.success) {
        this.currentSession = result.session;
        this.renderSessionUI();
        this.showStatus(`✅ Sala creada con ${selectedAgents.length} agentes`, 'success');
      } else {
        this.showStatus(`❌ Error: ${result.message}`, 'error');
      }
    } catch (error) {
      this.showStatus(`❌ Error de conexión: ${error}`, 'error');
    }
  }
  
  renderSessionUI() {
    const container = document.getElementById('session-container');
    
    if (!this.currentSession) {
      container.innerHTML = '';
      return;
    }
    
    container.innerHTML = `
      <div style="margin-top: 20px;">
        <h4>🎭 ${this.currentSession.name}</h4>
        <p>ID Sesión: <code>${this.currentSession.session_id}</code></p>
        <p>Agentes: ${this.currentSession.agent_ids.length}</p>
        
        <div style="margin-top: 15px;">
          <h5>Definir Rondas:</h5>
          <div id="rounds-definition" class="rounds-definition"></div>
          <button onclick="window.agentPanel.addRoundUI()" class="btn btn-primary" style="margin-top: 10px;">
            ➕ Añadir Ronda
          </button>
        </div>
      </div>
    `;
    
    this.renderRoundsUI();
  }
  
  renderRoundsUI() {
    const container = document.getElementById('rounds-definition');
    
    if (!this.currentSession.rounds || this.currentSession.rounds.length === 0) {
      container.innerHTML = '<p class="empty-state">Sin rondas definidas aún</p>';
      return;
    }
    
    container.innerHTML = this.currentSession.rounds.map((round, idx) => `
      <div class="round-definition">
        <h5>Ronda ${round.number}: ${round.title}</h5>
        <p>${round.prompt}</p>
        <p style="color: #666; font-size: 12px;">
          Estado: <strong>${round.status}</strong> | Agentes: ${round.agent_ids.length}
        </p>
      </div>
    `).join('');
  }
  
  addRoundUI() {
    const title = prompt('Título de la ronda (ej: Brainstorm, Conclusiones):');
    if (!title) return;
    
    const prompt = prompt('Instrucción/Prompt para los agentes:');
    if (!prompt) return;
    
    this.currentSession.rounds = this.currentSession.rounds || [];
    this.currentSession.rounds.push({
      number: this.currentSession.rounds.length + 1,
      title,
      prompt,
      status: 'pending',
      agent_ids: this.currentSession.agent_ids,
      responses: {}
    });
    
    this.renderRoundsUI();
    this.showStatus(`✅ Ronda "${title}" añadida`, 'success');
  }
  
  async loadSessions() {
    // Stub para cargar sesiones existentes
    console.log('Cargando sesiones...');
  }
  
  // ========================================================================
  // UTILITIES
  // ========================================================================
  
  showStatus(message, type = 'info') {
    const statusDiv = document.getElementById('register-status') || 
                     document.createElement('div');
    statusDiv.id = 'register-status';
    statusDiv.className = `status-message ${type}`;
    statusDiv.textContent = message;
    
    if (!document.getElementById('register-status')) {
      document.getElementById('tab-register').appendChild(statusDiv);
    }
  }
  
  getStatusEmoji(status) {
    const emojis = {
      'active': '🟢',
      'pending_verification': '⏳',
      'failed': '🔴',
      'inactive': '⚫',
      'suspended': '🟤'
    };
    return emojis[status] || '❓';
  }
}

// ============================================================================
// AUTO-INIT
// ============================================================================

window.addEventListener('DOMContentLoaded', () => {
  // Crear contenedor si no existe
  if (!document.getElementById('agents-panel')) {
    const container = document.createElement('div');
    container.id = 'agents-panel';
    document.body.appendChild(container);
  }
  
  window.agentPanel = new AgentsManagementPanel('#agents-panel');
  console.log('✅ AgentsManagementPanel inicializado');
});
