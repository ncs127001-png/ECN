/**
 * NEUROBIT UI Module
 * Módulo para renderizado de interfaz
 */

export function renderMembersList(members) {
  const select = document.getElementById('senderEntity');
  if (!select) return;
  
  select.innerHTML = '<option value="NODO_SEMILLA">🌱 NODO_SEMILLA (Vos)</option>';
  
  members.forEach(m => {
    const opt = document.createElement('option');
    opt.value = m.member_id;
    opt.textContent = `${m.member_id} (${m.platform || 'unknown'})`;
    select.appendChild(opt);
  });
}

export function renderMessages(messages) {
  const container = document.getElementById('messagesContainer');
  if (!container) return;
  
  container.innerHTML = '';
  messages.forEach(msg => {
    const div = document.createElement('div');
    div.className = 'msg';
    div.innerHTML = `
      <div class="msg-content">${escapeHtml(msg.content)}</div>
      <div class="msg-time">${extractTime(msg)}</div>
    `;
    container.appendChild(div);
  });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function extractTime(msg) {
  try {
    return new Date(msg.timestamp).toLocaleTimeString('es-AR');
  } catch {
    return '';
  }
}
