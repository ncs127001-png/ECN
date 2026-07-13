// control.js - Gestión de nodos mediante pestañas (versión básica)
const nodeManager = {
  nodes: {},
  isMainNode: false,
  initialize: function() {
    if (!localStorage.getItem('mainNode')) {
      localStorage.setItem('mainNode', Date.now().toString());
      this.isMainNode = true;
      document.title = "✧ ESTACIÓN PRINCIPAL - The Sofistas ✧";
    } else {
      this.isMainNode = false;
      const nodeId = 'node_' + Math.random().toString(36).substr(2, 5);
      this.registerNode(nodeId);
      document.title = `✧ NODO ${nodeId} ✧`;
    }

    window.addEventListener('storage', this.handleStorageEvent.bind(this));

    if (this.isMainNode) this.broadcastSystemState();

    document.getElementById('processBtn').addEventListener('click', () => {
      this.processMessage();
    });

    setInterval(() => this.updateNodeStatus(), 5000);
  },

  registerNode: function(nodeId) {
    const nodeInfo = { id: nodeId, timestamp: Date.now(), role: this.assignRoleBasedOnTime(), status: 'activo' };
    localStorage.setItem(`node_${nodeId}`, JSON.stringify(nodeInfo));
    this.nodes[nodeId] = nodeInfo;
    return nodeInfo;
  },

  assignRoleBasedOnTime: function() {
    const second = new Date().getSeconds();
    const roles = ['validator', 'expander', 'dispatcher', 'sender'];
    return roles[second % roles.length];
  },

  processMessage: function() {
    const message = document.getElementById('messageInput').value || '';
    const tags = (message.match(/\w+:\w+/g) || []).slice(0, 6);

    if (this.isMainNode) {
      tags.forEach(tag => {
        const role = tag.split(':')[0];
        this.delegateTask(role, { message, tag });
      });
      document.getElementById('resultOutput').textContent = 'Mensaje delegado a nodos: ' + tags.join(', ');
    } else {
      // Procesamiento local de demostración
      const result = {
        original: message,
        processed_by: Object.keys(this.nodes)[0] || 'local',
        expansions: tags.map(tag => ({ tag, expanded: `${message} [Procesado por nodo ${tag}]` })),
        timestamp: Date.now()
      };
      document.getElementById('resultOutput').textContent = JSON.stringify(result, null, 2);
    }
  },

  delegateTask: function(role, taskData) {
    console.log(`[DELEGACIÓN] Rol ${role} - Tarea:`, taskData);
    localStorage.setItem(`task_${role}_${Date.now()}`, JSON.stringify(taskData));
  },

  updateNodeStatus: function() {
    const statusDiv = document.getElementById('nodeStatus');
    let html = '<ul>';
    Object.values(this.nodes).forEach(node => {
      html += `<li>NODO ${node.id}: <span class="role">${node.role.toUpperCase()}</span> <small>${new Date(node.timestamp).toLocaleTimeString()}</small></li>`;
    });
    html += '</ul>';
    statusDiv.innerHTML = html;
  },

  handleStorageEvent: function(e) {
    if (!e.key) return;
    if (e.key.startsWith('node_')) {
      const nodeId = e.key.replace('node_', '');
      if (e.newValue) this.nodes[nodeId] = JSON.parse(e.newValue);
      else delete this.nodes[nodeId];
    }
  },

  broadcastSystemState: function() {
    localStorage.setItem('systemState', JSON.stringify({ mainNode: localStorage.getItem('mainNode'), timestamp: Date.now(), activeNodes: Object.keys(this.nodes).length }));
  }
};

window.addEventListener('DOMContentLoaded', () => nodeManager.initialize());
