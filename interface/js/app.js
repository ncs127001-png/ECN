/**
 * NEUROBIT Central App
 * Orquestador principal - conecta todos los módulos
 */

import { initWebSocket, emitMessage } from './modules/websocket.js';
import { fetchMembers, registerMember, loadMessages } from './modules/api.js';
import { renderMembersList, renderMessages } from './modules/ui.js';

// Inicialización
document.addEventListener('DOMContentLoaded', async () => {
  console.log('🚀 [NEUROBIT] Iniciando...');
  
  // 1. Iniciar WebSocket
  const wsOk = initWebSocket();
  console.log(`WebSocket: ${wsOk ? '✅' : '❌'}`);
  
  // 2. Cargar miembros
  try {
    const members = await fetchMembers();
    renderMembersList(members.members || []);
    console.log(`Miembros cargados: ${members.members?.length || 0}`);
  } catch (e) {
    console.error('Error cargando miembros:', e);
  }
  
  // 3. Cargar mensajes
  try {
    const data = await loadMessages();
    renderMessages(data.items || []);
    console.log(`Mensajes cargados: ${data.items?.length || 0}`);
  } catch (e) {
    console.error('Error cargando mensajes:', e);
  }
});
