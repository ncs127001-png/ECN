#!/usr/bin/env python3
"""
WebSocket Salon Server — NEUROBIT_V0.2 TASK 5
Servidor SocketIO para actualizaciones en tiempo real del Salón de Reuniones

Principios:
  - SOBERANÍA: Solo localhost (127.0.0.1)
  - APPEND-ONLY: Cada mensaje se registra en memoria_eva.jsonl
  - LIVIANO: No sobrecarga, solo puente de comunicación
  - FALLBACK: Si falla, el sistema funciona vía API polling
"""

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import json
import os
from pathlib import Path
from datetime import datetime
from threading import Lock

# ═══════════════════════════════════════════════════════════════════════════════
# INICIALIZACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

app = Flask(__name__)
app.config['SECRET_KEY'] = 'neurobit_salon_secret_key'

# CORS: Solo permitir localhost
CORS(app, resources={
    r"/*": {
        "origins": ["http://127.0.0.1:5000", "http://localhost:5000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# SocketIO con async mode threading
socketio = SocketIO(
    app,
    cors_allowed_origins=["http://127.0.0.1:5000", "http://localhost:5000"],
    async_mode='threading',
    ping_interval=25,
    ping_timeout=60,
    engineio_logger=False,
    socketio_logger=False
)

# ═══════════════════════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

state = {
    'clients_connected': 0,
    'messages_broadcast': 0,
    'last_activity': None,
}

state_lock = Lock()

# Paths
WORKSPACE = Path(__file__).parent.parent
MEMORIA_FILE = WORKSPACE / 'data' / 'memoria_eva.jsonl'
LOG_FILE = WORKSPACE / 'data' / 'logs' / 'websocket_salon.log'

# Crear directorio de logs si no existe
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log_event(event_type: str, data: dict):
    """Log interno del servidor WebSocket"""
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'data': data
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"[WebSocket] Error logging: {e}")

def save_to_memoria(message_data: dict):
    """Guardar mensaje en memoria_eva.jsonl (append-only)"""
    try:
        with open(MEMORIA_FILE, 'a', encoding='utf-8') as f:
            evento = {
                'timestamp': datetime.now().isoformat(),
                'source': 'websocket_salon',
                'type': 'mensaje_sala',
                'member_id': message_data.get('member_id'),
                'content': message_data.get('content'),
                'perspective': message_data.get('perspective'),
            }
            f.write(json.dumps(evento, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"[WebSocket] Error saving to memoria: {e}")
        log_event('error_saving_memoria', {'error': str(e)})

# ═══════════════════════════════════════════════════════════════════════════════
# SOCKET.IO HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

@socketio.on('connect')
def handle_connect():
    """Cliente conecta al servidor"""
    with state_lock:
        state['clients_connected'] += 1
    
    client_id = request.sid
    print(f"[WebSocket] Cliente conectado: {client_id}")
    print(f"[WebSocket] Clientes activos: {state['clients_connected']}")
    
    log_event('client_connected', {
        'client_id': client_id,
        'total_clients': state['clients_connected']
    })
    
    # Enviar confirmación
    emit('status', {
        'msg': '✅ Conectado al Salón de Reuniones (WebSocket)',
        'timestamp': datetime.now().isoformat(),
        'client_id': client_id
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconecta"""
    with state_lock:
        state['clients_connected'] -= 1
    
    client_id = request.sid
    print(f"[WebSocket] Cliente desconectado: {client_id}")
    print(f"[WebSocket] Clientes activos: {state['clients_connected']}")
    
    log_event('client_disconnected', {
        'client_id': client_id,
        'remaining_clients': state['clients_connected']
    })


@socketio.on('nuevo_mensaje')
def handle_nuevo_mensaje(data):
    """Recibir nuevo mensaje del Salón y broadcastearlo"""
    client_id = request.sid
    
    try:
        # Validar datos
        member_id = data.get('member_id')
        content = data.get('content')
        
        if not member_id or not content:
            emit('error', {'msg': 'Datos incompletos: falta member_id o content'})
            return
        
        # Enriquecer mensaje
        mensaje_completo = {
            'timestamp': datetime.now().isoformat(),
            'client_id': client_id,
            'member_id': member_id,
            'content': content,
            'perspective': data.get('perspective', 'tecnica'),
            'platform': data.get('platform', 'websocket')
        }
        
        # Guardar en memoria_eva.jsonl (APPEND-ONLY)
        save_to_memoria(mensaje_completo)
        
        # Actualizar estado
        with state_lock:
            state['messages_broadcast'] += 1
            state['last_activity'] = datetime.now().isoformat()
        
        # Broadcast a TODOS los clientes
        emit('mensaje_recibido', mensaje_completo, broadcast=True)
        
        # Log
        print(f"[WebSocket] Mensaje broadcast: {member_id} → {len(data)} clientes")
        log_event('mensaje_broadcast', {
            'member_id': member_id,
            'content_length': len(content),
            'total_messages_broadcast': state['messages_broadcast']
        })
        
    except Exception as e:
        print(f"[WebSocket] Error en handle_nuevo_mensaje: {e}")
        log_event('error_nuevo_mensaje', {'error': str(e)})
        emit('error', {'msg': f'Error procesando mensaje: {e}'})


@socketio.on('actualizar_miembros')
def handle_actualizar_miembros(data):
    """Notificar que la lista de miembros cambió (broadcast)"""
    try:
        # Broadcast a todos: lista de miembros se actualizó
        emit('miembros_actualizados', {
            'timestamp': datetime.now().isoformat(),
            'msg': '📋 La lista de miembros se actualizó. Refresca tu lista.'
        }, broadcast=True)
        
        log_event('miembros_actualizados', {
            'trigger': data.get('trigger', 'unknown')
        })
        
    except Exception as e:
        print(f"[WebSocket] Error en handle_actualizar_miembros: {e}")
        log_event('error_actualizar_miembros', {'error': str(e)})


@socketio.on('escribiendo')
def handle_escribiendo(data):
    """Notificar que alguien está escribiendo (typing indicator)"""
    try:
        member_id = data.get('member_id')
        emit('alguien_escribiendo', {
            'member_id': member_id,
            'timestamp': datetime.now().isoformat()
        }, broadcast=True, include_self=False)
        
    except Exception as e:
        print(f"[WebSocket] Error en handle_escribiendo: {e}")


@socketio.on('ping')
def handle_ping():
    """Responder a pings para mantener conexión viva"""
    emit('pong', {'timestamp': datetime.now().isoformat()})


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP ENDPOINTS (para monitoreo)
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/health', methods=['GET'])
def health():
    """Health check del servidor WebSocket"""
    return {
        'status': 'ok',
        'service': 'websocket_salon',
        'clients_connected': state['clients_connected'],
        'messages_broadcast': state['messages_broadcast'],
        'last_activity': state['last_activity'],
        'timestamp': datetime.now().isoformat()
    }, 200


@app.route('/stats', methods=['GET'])
def stats():
    """Estadísticas del servidor"""
    return {
        'uptime_seconds': 'N/A',  # Implementar si es necesario
        'clients_connected': state['clients_connected'],
        'messages_broadcast': state['messages_broadcast'],
        'last_activity': state['last_activity'],
        'memoria_file_size': MEMORIA_FILE.stat().st_size if MEMORIA_FILE.exists() else 0,
        'timestamp': datetime.now().isoformat()
    }, 200


# ═══════════════════════════════════════════════════════════════════════════════
# STARTUP / SHUTDOWN
# ═══════════════════════════════════════════════════════════════════════════════

def on_startup():
    """Al iniciar el servidor"""
    print("\n" + "="*80)
    print("🧠 NEUROBIT WebSocket Salon Server")
    print("="*80)
    print(f"✅ Servidor WebSocket iniciado en ws://127.0.0.1:5001")
    print(f"✅ CORS: http://127.0.0.1:5000")
    print(f"✅ Memoria: {MEMORIA_FILE}")
    print(f"✅ Logs: {LOG_FILE}")
    print("="*80 + "\n")
    
    log_event('server_started', {
        'port': 5001,
        'cors_origins': ['http://127.0.0.1:5000']
    })


def on_shutdown():
    """Al cerrar el servidor"""
    print("\n[WebSocket] Servidor apagándose...")
    log_event('server_shutdown', {
        'final_clients': state['clients_connected'],
        'total_messages': state['messages_broadcast']
    })


if __name__ == '__main__':
    on_startup()
    
    try:
        # Iniciar servidor en puerto 5001 (solo localhost)
        socketio.run(
            app,
            host='127.0.0.1',
            port=5001,
            debug=False,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n[WebSocket] Interrupción del usuario")
        on_shutdown()
    except Exception as e:
        print(f"\n[WebSocket] Error fatal: {e}")
        on_shutdown()
        raise
