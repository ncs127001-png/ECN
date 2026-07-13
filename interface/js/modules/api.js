/**
 * NEUROBIT API Module
 * Módulo para comunicación con API REST
 */

const API_BASE = '';

export async function fetchMembers() {
  const resp = await fetch(`${API_BASE}/members/list?active_only=true`);
  return resp.json();
}

export async function registerMember(data) {
  const resp = await fetch(`${API_BASE}/members/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return resp.json();
}

export async function loadMessages(limit = 100) {
  const resp = await fetch(`${API_BASE}/memoria?limit=${limit}`);
  return resp.json();
}
