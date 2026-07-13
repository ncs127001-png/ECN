# modules/websocket_pid_bridge.py
"""
Puente WebSocket entre extensión y backend
Identifica pestaña por tabId (no PID real, pero funcional)
"""

import asyncio
import websockets
import json
from datetime import datetime

class WebSocketPIDBridge:
    def __init__(self, port=5001):
        self.port = port
        self.tab_states = {}  # tabId → estado ghost
    
    async def handle_connection(self, websocket, path):
        """Manejar conexión desde extensión"""
        async for message in websocket:
            data = json.loads(message)
            tab_id = data.get('tabId')
            event_type = data.get('type')
            
            # Crear/actualizar estado ghost
            if tab_id not in self.tab_states:
                self.tab_states[tab_id] = {
                    'tabId': tab_id,
                    'url': data.get('url'),
                    'keystrokes': [],
                    'created_at': datetime.now().isoformat()
                }
            
            # Agregar evento al estado ghost
            self.tab_states[tab_id]['keystrokes'].append({
                'type': event_type,
                'content': data.get('content'),
                'timestamp': data.get('timestamp')
            })
            
            # Guardar en memoria_eva.jsonl
            self.save_to_memoria(tab_id, data)
    
    def save_to_memoria(self, tab_id, data):
        """Guardar evento en memoria_eva.jsonl"""
        with open('data/memoria_eva.jsonl', 'a') as f:
            f.write(json.dumps({
                'type': f'ghost_event_{data.get("type")}',
                'tabId': tab_id,
                'url': data.get('url'),
                'content': data.get('content'),
                'entity_id': 'WEBSOCKET_BRIDGE',
                'perspective': 'audit',
                'provenance': {
                    'created': datetime.now().isoformat(),
                    'signed_by': 'WEBSOCKET_BRIDGE'
                }
            }) + '\n')
    
    async def start(self):
        """Iniciar servidor WebSocket"""
        async with websockets.serve(self.handle_connection, '127.0.0.1', self.port):
            print(f"WebSocket PID Bridge escuchando en puerto {self.port}")
            await asyncio.Future()