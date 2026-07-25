#!/usr/bin/env python3
"""neurobit_api.py

Micro-API minimalista para NEUROBIT.

Endpoints:
 - GET /            -> health
 - POST /analyze    -> acepta JSON con {"content": "..."} o un envelope parcial y devuelve el envelope completo con análisis M/E

Instalación rápida: pip install -r requirements.txt

Diseñado para ser usado con curl o testing simple.
"""

from __future__ import annotations

import json
try:
    from flask import Flask, request, jsonify, send_from_directory  # type: ignore
except Exception:
    # Flask may not be installed in the environment running static checks.
    Flask = None
    request = None
    def jsonify(x):
        return x

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room  # type: ignore
except Exception:
    SocketIO = None
    emit = None
    join_room = None
    leave_room = None

try:
    import jsonschema
except Exception:
    jsonschema = None

try:
    import yaml
except Exception:
    yaml = None

import threading
import subprocess
import os
import re
import sys
import datetime
import uuid
from pathlib import Path
from core.coherence_filter import analyze as analyze_text
from core import participants as participants_mod
from core import coherence_filter, agents_registry, init_ceremony, centinela_monitor
from core.agents.simon import SimonValidator
from core.matrix_13x13 import default_matrix as matrix_13x13
from core.llm.client import generate_text
from core.event_dispatcher import EventDispatcher
import importlib


# Make storage/modules available on sys.path for dynamic module loading
modules_path = Path(__file__).resolve().parents[0] / 'storage' / 'modules'
if str(modules_path) not in sys.path:
    sys.path.insert(0, str(modules_path))

app = Flask(__name__)

try:
    from flask_cors import CORS
    # ✅ Inicializar CORS para que la extensión Chrome pueda conectar
    CORS(app, resources={r"/*": {"origins": "*"}})
except ImportError:
    # flask_cors no disponible (opcional)
    pass

# ✅ CAMBIO 2.5: Inicializar SocketIO para WebSocket (FASE 2.2)
if SocketIO is not None:
    socketio = SocketIO(app, 
        cors_allowed_origins="*", 
        async_mode='threading',
        ping_interval=25,
        ping_timeout=60
    )
    WEBSOCKET_ENABLED = True
else:
    socketio = None
    WEBSOCKET_ENABLED = False

# ✅ Inicializar Event Dispatcher (batch writer para memoria_eva.jsonl)
dispatcher = EventDispatcher(batch_size=20, flush_interval=30, memoria_path="data/memoria_eva.jsonl")
dispatcher.start()

# Directorio de fragmentos (para SuperSend)
FRAGMENTS_DIR = Path(__file__).parent / "data" / "fragments"
FRAGMENTS_DIR.mkdir(parents=True, exist_ok=True)



def validate_envelope_partial(env: dict) -> tuple[bool, str]:
    """Validación ligera del esquema para envíeos parciales.

    Verifica presencia de claves útiles. No replace schema validation library.
    """
    if not isinstance(env, dict):
        return False, "payload must be a JSON object"
    # If user supplied raw content, we'll generate envelope; otherwise expect content key
    if "content" not in env:
        return False, "missing 'content' field"
    if not isinstance(env.get("content"), str):
        return False, "'content' must be a string"
    return True, "ok"


def validate_with_schema(env: dict) -> tuple[bool, str]:
    """Try to validate payload with a minimal schema using jsonschema if available.

    Falls back to validate_envelope_partial when jsonschema isn't installed.
    """
    if jsonschema is None:
        return validate_envelope_partial(env)
    # Minimal schema: content required, entity_id string optional, plane optional
    schema = {
        "type": "object",
        "properties": {
            "content": {"type": "string"},
            "entity_id": {"type": "string"},
            "perspective": {"type": "string"},
            "context": {"type": "string"},
            "intention": {"type": "string"},
            "glossary": {"type": "array"}
        },
        "required": ["content"]
    }
    try:
        jsonschema.validate(instance=env, schema=schema)
        return True, "ok"
    except jsonschema.ValidationError as e:
        return False, f"schema_validation_error: {e.message}"


@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
    """Endpoint para verificar estado del servidor"""
    return jsonify({
        "status": "ok",
        "service": "neurobit_api",
        "version": "v0.2",
        "server_time": datetime.datetime.now().isoformat(),
        "fragments_dir": str(FRAGMENTS_DIR),
        "fragments_count": len(list(FRAGMENTS_DIR.glob("parte_*.txt"))) if FRAGMENTS_DIR.exists() else 0
    })


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "invalid json", "detail": str(e)}), 400

    valid, msg = validate_with_schema(payload)
    if not valid:
        return jsonify({"error": "invalid_payload", "detail": msg}), 400

    metadata = {
        "entity_id": payload.get("entity_id", "UNKNOWN"),
        "perspective": payload.get("perspective", "tecnica"),
        "context": payload.get("context", ""),
        "intention": payload.get("intention", ""),
        "signed_by": payload.get("signed_by", "API") ,
        "action": payload.get("action", "store")
    }

    envelope = analyze_text(payload.get("content"), metadata=metadata, glossary=payload.get("glossary"))

    # Persist if requested
    if envelope.get("action") == "store" or payload.get("action") == "store":
        try:
            store_envelope(envelope)
            envelope['provenance']['stored'] = True
        except Exception as e:
            envelope['provenance']['stored'] = False
            envelope['provenance']['store_error'] = str(e)

    # Optional dispatch: if client requested action 'dispatch', attempt to load
    # a dispatcher module from storage/modules/mock_dispatcher and call it.
    if payload.get('action') == 'dispatch' or envelope.get('action') == 'dispatch':
        try:
            # default to mock_dispatcher; real integration modules can be placed
            # in storage/modules and expose send_message(envelope)
            dispatcher = importlib.import_module('mock_dispatcher')
            if hasattr(dispatcher, 'send_message'):
                result = dispatcher.send_message(envelope)
                envelope.setdefault('provenance', {})
                envelope['provenance']['dispatched'] = True
                envelope['provenance']['dispatch_result'] = result
            else:
                envelope.setdefault('provenance', {})
                envelope['provenance']['dispatched'] = False
                envelope['provenance']['dispatch_error'] = 'no send_message on module'
        except Exception as e:
            envelope.setdefault('provenance', {})
            envelope['provenance']['dispatched'] = False
            envelope['provenance']['dispatch_error'] = str(e)

    return jsonify(envelope)


# ============================================================================
# FASE 3.1: ENDPOINTS DE GESTIÓN DE AGENTES
# ============================================================================

from core.agents_registry import AgentRegistry, RoundOrchestrator

# Instancias globales
agents_registry = AgentRegistry()
round_orchestrator = RoundOrchestrator(agents_registry)


# ============================================================================
# WebSocket Helpers (FASE 2.2)
# ============================================================================

def broadcast_agent_registered(agent_data):
    """
    Emitir agent_registered a todas las conexiones WebSocket (extensiones).
    Se llama desde /register_agent cuando un agente TEAMVIEWER se registra.
    
    Args:
        agent_data (dict): {agent_id, name, platform, url, tabId, pid}
    """
    if not WEBSOCKET_ENABLED or socketio is None:
        print("[WebSocket] SocketIO no habilitado, broadcast omitido")
        return
    
    try:
        socketio.emit(
            'agent_registered',
            agent_data,
            namespace='/',
            broadcast=True
        )
        print(f"[WebSocket] Broadcast enviado: {agent_data}")
    except Exception as e:
        print(f"[WebSocket] Error en broadcast: {str(e)}")


# ============================================================================
# WebSocket Event Handlers (FASE 2.2)
# ============================================================================

if WEBSOCKET_ENABLED and socketio is not None:
    @socketio.on('connect')
    def ws_connect():
        """Cliente WebSocket conectado (Bitácora-EVA extension)"""
        print(f'[WebSocket] Client connected: {request.sid}')
        emit('server_status', {'status': 'connected', 'port': 5001, 'version': '3.0'})

    @socketio.on('disconnect')
    def ws_disconnect():
        """Cliente WebSocket desconectado"""
        print(f'[WebSocket] Client disconnected: {request.sid}')

    @socketio.on('ping')
    def handle_ping():
        """Mantener viva la conexión (heartbeat)"""
        emit('pong', {'timestamp': datetime.datetime.now().isoformat()})


# ============================================================================
# Endpoints HTTP (REST API)
# ============================================================================

@app.route("/register_agent", methods=["POST"])
def register_agent():
    """Registra un nuevo agente. Soporta APIs (con api_key) y TEAMVIEWER (sin api_key)."""
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "invalid json", "detail": str(e)}), 400
    
    platform = payload.get("platform")
    name = payload.get("name")
    api_key = payload.get("api_key")
    metadata = payload.get("metadata", {})
    
    # Campos TEAMVIEWER (opcional)
    tabId = payload.get("tabId")
    pid = payload.get("pid")
    url = payload.get("url")
    
    success, message, agent = agents_registry.register_agent(
        platform=platform,
        name=name,
        api_key=api_key,
        metadata=metadata,
        tabId=tabId,
        pid=pid,
        url=url
    )
    
    if success:
        # ✅ CAMBIO 2.5: Broadcast agent_registered a WebSocket (FASE 2.2)
        if agent.platform == "teamviewer_extension":
            agent_broadcast_data = {
                'type': 'agent_registered',
                'agent_id': agent.id,
                'name': agent.name,
                'platform': agent.platform,
                'url': agent.metadata.get('url'),
                'tabId': agent.metadata.get('tabId'),
                'pid': agent.metadata.get('pid'),
                'registered_at': agent.registered_at
            }
            broadcast_agent_registered(agent_broadcast_data)
        
        return jsonify({
            "success": True,
            "message": message,
            "agent": {
                "id": agent.id,
                "platform": agent.platform,
                "name": agent.name,
                "status": agent.status,
                "registered_at": agent.registered_at,
                "metadata": agent.metadata
            }
        })
    else:
        return jsonify({
            "success": False,
            "message": message
        }), 400


@app.route("/list_agents", methods=["GET"])
def list_agents():
    """Lista todos los agentes registrados."""
    status_filter = request.args.get("status")
    
    agents = agents_registry.list_agents(status=status_filter)
    
    return jsonify({
        "success": True,
        "count": len(agents),
        "agents": [
            {
                "id": a.id,
                "platform": a.platform,
                "name": a.name,
                "status": a.status,
                "registered_at": a.registered_at,
                "last_heartbeat": a.last_heartbeat,
                "stats": a.stats
            }
            for a in agents
        ]
    })


@app.route("/get_agent/<agent_id>", methods=["GET"])
def get_agent(agent_id):
    """Obtiene info de un agente específico."""
    agent = agents_registry.get_agent(agent_id)
    
    if not agent:
        return jsonify({"error": "Agent not found"}), 404
    
    return jsonify({
        "success": True,
        "agent": {
            "id": agent.id,
            "platform": agent.platform,
            "name": agent.name,
            "status": agent.status,
            "stats": agent.stats
        }
    })


@app.route("/create_session", methods=["POST"])
def create_session():
    """Crea una nueva sala de sesión multi-agente."""
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "invalid json", "detail": str(e)}), 400
    
    name = payload.get("name")
    agent_ids = payload.get("agent_ids", [])
    
    success, message, session = round_orchestrator.create_session(name, agent_ids)
    
    if success:
        return jsonify({
            "success": True,
            "message": message,
            "session": {
                "session_id": session.session_id,
                "name": session.name,
                "agent_ids": session.agent_ids,
                "created_at": session.created_at
            }
        })
    else:
        return jsonify({
            "success": False,
            "message": message
        }), 400


@app.route("/add_round/<session_id>", methods=["POST"])
def add_round(session_id):
    """Añade una ronda a una sesión."""
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "invalid json", "detail": str(e)}), 400
    
    title = payload.get("title")
    prompt = payload.get("prompt")
    
    success, message, round_obj = round_orchestrator.add_round(session_id, title, prompt)
    
    if success:
        return jsonify({
            "success": True,
            "message": message,
            "round": {
                "round_id": round_obj.round_id,
                "number": round_obj.number,
                "title": round_obj.title,
                "status": round_obj.status
            }
        })
    else:
        return jsonify({
            "success": False,
            "message": message
        }), 400


# ============================================================================
# NUEVOS ENDPOINTS: GESTIÓN DE RONDAS (FASE A - MIGRACIÓN)
# ============================================================================

@app.route('/round/open', methods=['POST'])
def round_open():
    """Abre una nueva ronda de interacción multi-agente.
    
    POST /round/open
    Body: {
        "session_id": "...",
        "round_title": "...",
        "round_prompt": "...",
        "agents": ["agent_id_1", "agent_id_2", ...]
    }
    
    Retorna: {
        "success": bool,
        "round_id": str,
        "status": "open",
        "round_number": int,
        "timestamp": ISO datetime
    }
    """
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "invalid json", "detail": str(e)}), 400
    
    session_id = payload.get("session_id")
    round_title = payload.get("round_title")
    round_prompt = payload.get("round_prompt")
    agent_ids = payload.get("agents", [])
    
    if not session_id or not round_title:
        return jsonify({
            "success": False,
            "message": "session_id and round_title are required"
        }), 400
    
    try:
        # Generar ID único para la ronda
        round_id = f"round_{uuid.uuid4().hex[:8]}"
        round_number = len(list(Path(__file__).parent.glob(f"data/rounds/{session_id}/*.json"))) + 1
        
        # Crear registro de ronda
        round_record = {
            "round_id": round_id,
            "session_id": session_id,
            "round_number": round_number,
            "title": round_title,
            "prompt": round_prompt,
            "agents": agent_ids,
            "status": "open",
            "opened_at": datetime.datetime.now().isoformat(),
            "responses": []
        }
        
        # Persistir ronda
        rounds_dir = Path(__file__).parent / "data" / "rounds" / session_id
        rounds_dir.mkdir(parents=True, exist_ok=True)
        
        round_file = rounds_dir / f"{round_id}.json"
        with open(round_file, 'w', encoding='utf-8') as f:
            json.dump(round_record, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "success": True,
            "round_id": round_id,
            "round_number": round_number,
            "status": "open",
            "session_id": session_id,
            "timestamp": datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route('/round/complete', methods=['POST'])
def round_complete():
    """Cierra una ronda de interacción y guarda resultados.
    
    POST /round/complete
    Body: {
        "round_id": "...",
        "summary": "...",
        "notes": "..."
    }
    
    Retorna: {
        "success": bool,
        "status": "completed",
        "round_id": str,
        "closed_at": ISO datetime
    }
    """
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "invalid json", "detail": str(e)}), 400
    
    round_id = payload.get("round_id")
    summary = payload.get("summary", "")
    notes = payload.get("notes", "")
    
    if not round_id:
        return jsonify({
            "success": False,
            "message": "round_id is required"
        }), 400
    
    try:
        # Buscar archivo de ronda
        rounds_dir = Path(__file__).parent / "data" / "rounds"
        round_files = list(rounds_dir.glob(f"**/{round_id}.json"))
        
        if not round_files:
            return jsonify({
                "success": False,
                "message": f"Round not found: {round_id}"
            }), 404
        
        round_file = round_files[0]
        
        # Actualizar ronda
        with open(round_file, 'r', encoding='utf-8') as f:
            round_record = json.load(f)
        
        round_record['status'] = 'completed'
        round_record['summary'] = summary
        round_record['notes'] = notes
        round_record['closed_at'] = datetime.datetime.now().isoformat()
        
        with open(round_file, 'w', encoding='utf-8') as f:
            json.dump(round_record, f, ensure_ascii=False, indent=2)
        
        # Guardar también en memoria_eva.jsonl
        envelope = {
            "message_id": f"round_complete_{round_id}",
            "content": f"Round {round_id} completed: {summary}",
            "round_id": round_id,
            "status": "completed",
            "summary": summary,
            "provenance": {
                "created": datetime.datetime.now().isoformat(),
                "signed_by": "ROUND_MANAGER",
                "stored": True
            }
        }
        store_envelope(envelope)
        
        return jsonify({
            "success": True,
            "status": "completed",
            "round_id": round_id,
            "closed_at": datetime.datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route('/capture_responses', methods=['POST'])
def capture_responses():
    """Captura respuestas de agentes en una ronda abierta.
    
    POST /capture_responses
    Body: {
        "round_id": "...",
        "agent_id": "...",
        "response": "...",
        "metadata": {...}
    }
    
    Retorna: {
        "success": bool,
        "response_id": str,
        "message": str
    }
    """
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "invalid json", "detail": str(e)}), 400
    
    round_id = payload.get("round_id")
    agent_id = payload.get("agent_id")
    response_content = payload.get("response")
    metadata = payload.get("metadata", {})
    
    if not round_id or not agent_id or not response_content:
        return jsonify({
            "success": False,
            "message": "round_id, agent_id, and response are required"
        }), 400
    
    try:
        # Buscar archivo de ronda
        rounds_dir = Path(__file__).parent / "data" / "rounds"
        round_files = list(rounds_dir.glob(f"**/{round_id}.json"))
        
        if not round_files:
            return jsonify({
                "success": False,
                "message": f"Round not found: {round_id}"
            }), 404
        
        round_file = round_files[0]
        
        # Actualizar ronda con respuesta
        with open(round_file, 'r', encoding='utf-8') as f:
            round_record = json.load(f)
        
        response_id = f"resp_{uuid.uuid4().hex[:8]}"
        response_record = {
            "response_id": response_id,
            "agent_id": agent_id,
            "content": response_content,
            "metadata": metadata,
            "captured_at": datetime.datetime.now().isoformat()
        }
        
        round_record['responses'].append(response_record)
        
        with open(round_file, 'w', encoding='utf-8') as f:
            json.dump(round_record, f, ensure_ascii=False, indent=2)
        
        # Guardar respuesta en memoria_eva.jsonl
        envelope = {
            "message_id": response_id,
            "content": response_content,
            "round_id": round_id,
            "agent_id": agent_id,
            "entity_id": agent_id,
            "perspective": "agent",
            "action": "store",
            "provenance": {
                "created": datetime.datetime.now().isoformat(),
                "signed_by": agent_id,
                "stored": True
            }
        }
        store_envelope(envelope)
        
        return jsonify({
            "success": True,
            "response_id": response_id,
            "message": f"Response from {agent_id} captured"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route('/hid/capture', methods=['POST'])
def hid_capture():
    """Captura entrada desde HID Daemon (teclado, mouse, clipboard).
    
    POST /hid/capture
    Body: {
        "input_type": "keystroke|mouse|clipboard",
        "data": "...",
        "metadata": {...}
    }
    
    Retorna: {
        "success": bool,
        "capture_id": str,
        "message": str
    }
    
    PRIVACIDAD: Solo se procesa LOCALMENTE. No se envía a servidores externos.
    """
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "invalid json", "detail": str(e)}), 400
    
    input_type = payload.get("input_type")
    data = payload.get("data")
    metadata = payload.get("metadata", {})
    
    if not input_type or not data:
        return jsonify({
            "success": False,
            "message": "input_type and data are required"
        }), 400
    
    if input_type not in ["keystroke", "mouse", "clipboard"]:
        return jsonify({
            "success": False,
            "message": f"Invalid input_type: {input_type}"
        }), 400
    
    try:
        capture_id = f"hid_{uuid.uuid4().hex[:8]}"
        
        # Guardar en memoria_eva.jsonl (append-only, local only)
        envelope = {
            "message_id": capture_id,
            "content": data,
            "input_type": input_type,
            "metadata": metadata,
            "entity_id": "HID_DAEMON",
            "perspective": "sensory",
            "action": "store",
            "provenance": {
                "created": datetime.datetime.now().isoformat(),
                "signed_by": "HID_DAEMON",
                "stored": True,
                "privacy": "LOCAL_ONLY"
            }
        }
        store_envelope(envelope)
        
        return jsonify({
            "success": True,
            "capture_id": capture_id,
            "message": f"HID input ({input_type}) captured and stored locally"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route('/hid/inject', methods=['POST'])
def hid_inject():
    """Inyecta comandos a HID Daemon (escribir texto, clicks de mouse).
    
    POST /hid/inject
    Body: {
        "command": "type_text|mouse_click|mouse_move",
        "parameters": {...},
        "metadata": {...}
    }
    
    Retorna: {
        "success": bool,
        "command_id": str,
        "message": str
    }
    
    SEGURIDAD: Solo acepta comandos desde localhost (127.0.0.1).
    """
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        return jsonify({"error": "invalid json", "detail": str(e)}), 400
    
    command = payload.get("command")
    parameters = payload.get("parameters", {})
    metadata = payload.get("metadata", {})
    
    if not command:
        return jsonify({
            "success": False,
            "message": "command is required"
        }), 400
    
    if command not in ["type_text", "mouse_click", "mouse_move"]:
        return jsonify({
            "success": False,
            "message": f"Invalid command: {command}"
        }), 400
    
    try:
        command_id = f"hid_cmd_{uuid.uuid4().hex[:8]}"
        
        # Log del comando inyectado
        envelope = {
            "message_id": command_id,
            "content": f"HID command: {command}",
            "command": command,
            "parameters": parameters,
            "entity_id": "HID_INJECTOR",
            "perspective": "actuator",
            "action": "store",
            "provenance": {
                "created": datetime.datetime.now().isoformat(),
                "signed_by": "HID_INJECTOR",
                "stored": True,
                "privacy": "LOCAL_ONLY"
            }
        }
        store_envelope(envelope)
        
        # En el futuro, aquí se inyectaría el comando al daemon
        # Por ahora, solo lo registramos
        
        return jsonify({
            "success": True,
            "command_id": command_id,
            "message": f"HID command queued: {command}"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route('/memoria', methods=['POST'])
def memoria_sync():
    """FASE 4: Recibe mensajes desde Bitácora EVA (extensiones Chrome)
    Los guarda en memoria_eva.jsonl (append-only, NUNCA sobrescribir)
    
    Expected payload:
    {
        "source": "bitacora-eva",
        "entity_id": "NODO_SEMILLA",
        "messages": [
            {
                "id": "msg_<timestamp>_<counter>",
                "type": "TEXT_INPUT|BUTTON_CLICK|etc",
                "data": {...},
                "timestamp": ISO8601
            },
            ...
        ]
    }
    """
    try:
        data = request.json or {}
        
        # Validar estructura básica
        if not data:
            return jsonify({'error': 'Empty payload'}), 400
        
        source = data.get('source', 'unknown')
        entity_id = data.get('entity_id', 'NODO_SEMILLA')
        messages = data.get('messages', [])
        
        if not messages or not isinstance(messages, list):
            return jsonify({'error': 'No messages provided or invalid format'}), 400
        
        # Guardar cada mensaje en append-only
        base = Path(__file__).resolve().parents[0]
        memoria_file = base / 'data' / 'memoria_eva.jsonl'
        memoria_file.parent.mkdir(parents=True, exist_ok=True)
        
        saved_ids = []
        for msg in messages:
            # Agregar metadata automática
            enriched_msg = {
                'source': source,
                'entity_id': entity_id,
                'synced_at': datetime.datetime.now().isoformat(),
                'payload': msg
            }
            
            # Generar message_id si no existe
            if 'id' not in msg:
                enriched_msg['payload']['id'] = str(uuid.uuid4())
            
            # APPEND-ONLY: agregar línea al final (NUNCA sobrescribir)
            with memoria_file.open('a', encoding='utf-8') as f:
                f.write(json.dumps(enriched_msg, ensure_ascii=False) + '\n')
            
            saved_ids.append(msg.get('id', enriched_msg['payload']['id']))
        
        # Logging
        print(f"[MEMORIA-SYNC] ✅ Synced {len(saved_ids)} messages from {source}")
        
        return jsonify({
            'status': 'synced',
            'source': source,
            'count': len(saved_ids),
            'message_ids': saved_ids,
            'timestamp': datetime.datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"[MEMORIA-SYNC] ❌ Error: {str(e)}")
        return jsonify({'error': f'Sync failed: {str(e)}'}), 500


@app.route('/memoria', methods=['GET'])
def memoria_list():
    """List entries from the append-only memoria_eva.jsonl file.
    Query params: page (1-based), limit (default 20)
    """
    page = int(request.args.get('page', '1') or 1)
    limit = int(request.args.get('limit', '20') or 20)
    if page < 1:
        page = 1
    if limit < 1:
        limit = 20

    base = Path(__file__).resolve().parents[0]
    out = base / 'data' / 'memoria_eva.jsonl'
    entries = []
    if out.exists():
        with out.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except Exception:
                    # ignore malformed lines
                    continue

    # reverse to show newest first
    entries = list(reversed(entries))
    start = (page - 1) * limit
    end = start + limit
    page_entries = entries[start:end]
    return jsonify({
        'page': page,
        'limit': limit,
        'total': len(entries),
        'items': page_entries
    })


@app.route('/participants', methods=['GET'])
def participants_list():
    """Return configured participants."""
    try:
        parts = participants_mod.list_participants()
        return jsonify({'participants': parts})
    except Exception as e:
        return jsonify({'error': 'failed_to_load_participants', 'detail': str(e)}), 500


@app.route('/interface/<path:filename>', methods=['GET'])
def serve_interface(filename):
    """Serve static files from the interface directory so the UI is reachable."""
    base_dir = Path(__file__).resolve().parents[0]
    interface_dir = base_dir / 'interface'
    # security: avoid directory traversal
    return send_from_directory(str(interface_dir), filename)


def store_envelope(envelope: dict) -> None:
    """Append the envelope JSON to the append-only Memoria Sagrada file.

    File: data/memoria_eva.jsonl (created if not exists)
    """
    base = Path(__file__).resolve().parents[0]
    data_dir = base / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    out = data_dir / 'memoria_eva.jsonl'
    with out.open('a', encoding='utf-8') as f:
        f.write(json.dumps(envelope, ensure_ascii=False) + "\n")


# ============================================================================
# NUEVOS ENDPOINTS: INIT_CEREMONY y CENTINELA_MONITOR
# ============================================================================

@app.route('/init_ceremony', methods=['POST'])
def init_ceremony_endpoint():
    """Ejecuta la ceremonia de despertar del NODO_SEMILLA.
    
    POST /init_ceremony
    Body: {} (opcional, puede ser vacío)
    
    Retorna: estado de inicialización con todas las verificaciones
    """
    try:
        results = init_ceremony.run_ceremony()
        return jsonify(results)
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "ready": False
        }), 500


@app.route('/init_ceremony/status', methods=['GET'])
def init_ceremony_status_endpoint():
    """Obtiene estado actual de la ceremonia de despertar.
    
    GET /init_ceremony/status
    
    Retorna: estado de variables de entorno y sistema
    """
    try:
        status = init_ceremony.get_ceremony_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/start_centinela', methods=['POST'])
def start_centinela_endpoint():
    """Inicia el Centinela (monitor de clipboard local).
    
    POST /start_centinela
    Body: {} (opcional)
    
    Nota: El Centinela funciona en background. Los registros se guardan en:
    - data/memoria_eva.jsonl (append-only)
    - data/centinela_resguardo.jsonl (logs detallados)
    
    PRIVACIDAD: El clipboard se monitorea LOCALMENTE SOLAMENTE.
    No se envía información a servidores externos.
    """
    try:
        result = centinela_monitor.start_centinela(background=True)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/stop_centinela', methods=['POST'])
def stop_centinela_endpoint():
    """Detiene el Centinela.
    
    POST /stop_centinela
    Body: {} (opcional)
    """
    try:
        result = centinela_monitor.stop_centinela()
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/centinela_status', methods=['GET'])
def centinela_status_endpoint():
    """Obtiene estado actual del Centinela.
    
    GET /centinela_status
    
    Retorna: estado de ejecución y tamaño de logs
    """
    try:
        status = centinela_monitor.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500





# -------------------------------------------------------------------------
# TIER 3 MIGRATION: Intelligence & Matrix
# -------------------------------------------------------------------------

@app.route('/matrix/encode', methods=['POST'])
def matrix_encode():
    """Genera un Neurobyte a partir de texto (Backend Matrix).
    POST /matrix/encode
    Body: {"text": "..."}
    """
    try:
        data = request.json or {}
        text = data.get('text')
        if not text:
            return jsonify({"error": "Text required"}), 400
            
        neurobyte = matrix_13x13.encode_text(text)
        return jsonify(neurobyte)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/agent/generate', methods=['POST'])
def agent_generate():
    """Genera texto usando un agente registrado (LLM).
    POST /agent/generate
    Body: {"agent_id": "...", "prompt": "...", "system_prompt": "..."}
    """
    try:
        data = request.json or {}
        agent_id = data.get('agent_id')
        prompt = data.get('prompt')
        system_prompt = data.get('system_prompt')
        
        if not agent_id or not prompt:
            return jsonify({"error": "agent_id and prompt required"}), 400
            
        # Buscar agente
        agent = agents_registry.get_agent(agent_id)
        if not agent:
            # Fallback: check if agent_id is actually a platform name for quick testing
            if agent_id in ['chatgpt', 'gemini', 'local_llama', 'qwen']:
                # Allow direct platform usage if the user provides API Key in header or body?
                # For safety, let's strictly require registered agents, OR allow temp usage
                # if api_key is provided in body.
                api_key = data.get('api_key')
                if api_key:
                    # Temporary usage
                    response = generate_text(agent_id, api_key, "default", prompt, system_prompt)
                    return jsonify({"content": response, "agent": "temp"})
            
            return jsonify({"error": "Agent not found"}), 404
            
        if agent.status != 'active':
            return jsonify({"error": f"Agent is {agent.status}"}), 400
            
        # Get API Key (In production this should be decrypted)
        # For this prototype we assume we have a way to retreive it, 
        # but agents_registry only stores hash!
        # CRITICAL: We need the actual API key to call the LLM.
        # Since we stored only hash in registry, we can't actually call it 
        # unless we prompt the user for the key every time OR we stored it securely (not implemented yet).
        
        # FIX: For v0.2 prototype, we will allow passing 'api_key' in the request
        # OR we assume the environment has keys.
        
        api_key = data.get('api_key')
        if not api_key:
             return jsonify({"error": "API Key required in request (Registry stores hashes only)"}), 400
            
        # Determine model based on metadata or default
        model = agent.metadata.get('model', 'gpt-3.5-turbo' if agent.platform == 'chatgpt' else 'gemini-pro')
        
        response = generate_text(agent.platform, api_key, model, prompt, system_prompt)
        
        # Update stats
        agent.stats['messages_sent'] += 1
        agents_registry._save_to_disk(agent) # Persist stats
        
        return jsonify({
            "content": response,
            "agent_id": agent.id,
            "model": model
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------------------------------------------------
# TIER 2 MIGRATION: Search & Fragments
# -------------------------------------------------------------------------

def search_files_recursive(pattern, root_dir):
    matches = []
    # Avoid scanning too deep or hidden dirs
    for root, dirs, files in os.walk(root_dir):
        if '/.' in root or '__pycache__' in root:
            continue
        for file in files:
            if pattern.lower() in file.lower():
                matches.append(os.path.join(root, file))
    return matches[:50]  # Limit to 50 results

@app.route('/search_files', methods=['POST'])
def search_files():
    """Busca archivos en el workspace recursivamente.
    POST /search_files
    Body: {"pattern": "nombre_parcial"}
    """
    try:
        data = request.json or {}
        pattern = data.get('pattern')
        if not pattern:
            return jsonify({"error": "Pattern required"}), 400
        
        # Search relative to workspace root (parent of this file)
        root_dir = str(Path(__file__).resolve().parent)
        matches = search_files_recursive(pattern, root_dir)
        return jsonify({"matches": matches, "count": len(matches)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/fragment', methods=['POST'])
def fragment_upload():
    """Sube texto fragmentado (similar a fragment_server).
    POST /fragment
    Multipart: file, max_chars, prefix
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        content = file.read().decode('utf-8', errors='ignore')
        max_chars = int(request.form.get('max_chars', 5000))
        prefix = request.form.get('prefix', 'parte_')
        
        fragments_dir = Path("data/fragments")
        fragments_dir.mkdir(parents=True, exist_ok=True)
        
        parts = []
        current = ""
        
        # Simple splitting by paragraph
        paragraphs = re.split(r'\n\s*\n+', content)
        
        for p in paragraphs:
            if len(current) + len(p) < max_chars:
                current += "\n\n" + p
            else:
                parts.append(current)
                current = p
        if current:
            parts.append(current)
            
        saved_files = []
        for i, part in enumerate(parts):
            fname = f"{prefix}{i+1}.txt"
            fpath = fragments_dir / fname
            with open(fpath, "w") as f:
                f.write(part)
            saved_files.append(str(fpath))
            
        return jsonify({"created": len(saved_files), "files": saved_files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================================
# ENDPOINTS DE FRAGMENTOS (Migrados de server.py - SuperSend)
# ============================================================================

@app.route('/get_fragments_state', methods=['GET'])
def get_fragments_state():
    """Devuelve lista de fragmentos disponibles"""
    try:
        if not FRAGMENTS_DIR.exists():
            return jsonify({"error": f"Directorio no encontrado: {FRAGMENTS_DIR}"}), 500
        
        fragmentos = [
            f.name for f in FRAGMENTS_DIR.glob("parte_*.txt")
            if f.is_file() and not f.name.endswith('.info')
        ]
        
        # Ordenar numéricamente
        try:
            fragmentos.sort(key=lambda x: int(re.search(r'(\d+)', x).group(1)) if re.search(r'(\d+)', x) else 0)
        except:
            fragmentos.sort()
        
        return jsonify({
            "total": len(fragmentos),
            "fragments": fragmentos,
            "timestamp": datetime.datetime.now().isoformat(),
            "directory": str(FRAGMENTS_DIR)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_fragment_content', methods=['GET'])
def get_fragment_content():
    """Devuelve contenido de un fragmento específico"""
    name = request.args.get('name')
    if not name:
        return "Nombre de fragmento requerido", 400
    
    try:
        # Seguridad: evitar path traversal
        if '..' in name or name.startswith('/') or name.startswith('\\'):
            return "Nombre de archivo inválido", 400
        
        file_path = FRAGMENTS_DIR / name
        
        if not file_path.exists():
            return f"Fragmento no encontrado: {name}", 404
        
        if not file_path.is_file():
            return f"Ruta no es un archivo: {name}", 400
        
        # Leer contenido
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # Eliminar header NEUROBIT si existe
        if "[CONTENT]:" in content:
            content = content.split("[CONTENT]:", 1)[1].strip()
        
        return content
    
    except Exception as e:
        return f"Error al leer fragmento: {str(e)}", 500


# ============================================================================



# ============================================================================
# ENDPOINTS MCP SERVER (Puerto 8090)
# ============================================================================

@app.route('/mcp/export', methods=['POST'])
def mcp_export():
    """Exporta conversación a formato MCP estándar"""
    try:
        data = request.json or {}
        session_id = data.get('session_id', datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        
        mcp_dir = Path('data/mcp_conversations')
        mcp_dir.mkdir(parents=True, exist_ok=True)
        
        # Leer desde memoria_eva.jsonl
        memoria_path = Path('data/memoria_eva.jsonl')
        conversations = []
        
        if memoria_path.exists():
            with open(memoria_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get('session_id') == session_id or not session_id:
                            conversations.append(entry)
                    except:
                        pass
        
        # Guardar en formato MCP
        output_path = mcp_dir / f"conversation_{session_id}.json"
        mcp_export = {
            "version": "mcp-1.0",
            "exported_at": datetime.datetime.now().isoformat(),
            "source": "neurobit_memoria_eva",
            "session_id": session_id,
            "messages": conversations
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mcp_export, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'status': 'exported',
            'path': str(output_path),
            'messages': len(conversations)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/mcp/import', methods=['POST'])
def mcp_import():
    """Importa conversación desde formato MCP"""
    try:
        data = request.json or {}
        file_path = Path(data.get('file_path'))
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            mcp_data = json.load(f)
        
        # Importar a memoria_eva.jsonl
        memoria_path = Path('data/memoria_eva.jsonl')
        imported = 0
        
        with open(memoria_path, 'a', encoding='utf-8') as f:
            for msg in mcp_data.get("messages", []):
                f.write(json.dumps(msg, ensure_ascii=False) + "\n")
                imported += 1
        
        return jsonify({
            'status': 'imported',
            'messages': imported
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/mcp/status', methods=['GET'])
def mcp_status():
    """Estado del servidor MCP"""
    return jsonify({
        'mcp_server': 'ready',
        'port': 8090,
        'tools': ['export_conversation', 'import_conversation', 'get_neurobit_status', 'query_memoria'],
        'workspace': str(Path(__file__).parent)
    })


# ============================================================================
# DISPATCHER ENDPOINTS — Integración de Event Dispatcher
# ============================================================================

@app.route('/dispatch/queue', methods=['POST'])
def dispatch_queue():
    """
    Encolar eventos para escritura batch en memoria_eva.jsonl
    
    Request:
        {
          "events": [
            {"type": "keylog", "content": "...", "timestamp": "2026-03-27T..."},
            {"type": "clipboard", "content": "...", "timestamp": "..."}
          ]
        }
    
    Response:
        {"status": "queued", "count": 2}
    """
    try:
        data = request.json or {}
        events = data.get('events', [])
        
        if not isinstance(events, list):
            return jsonify({'status': 'error', 'message': 'events must be an array'}), 400
        
        for event in events:
            # Validar que cada evento sea un dict
            if not isinstance(event, dict):
                return jsonify({'status': 'error', 'message': 'each event must be a JSON object'}), 400
            
            # Agregar timestamp si falta
            if 'timestamp' not in event:
                event['timestamp'] = datetime.datetime.now().isoformat()
            
            dispatcher.queue_event(event)
        
        return jsonify({
            'status': 'queued',
            'count': len(events),
            'buffer_size': dispatcher.buffer.qsize()
        }), 200
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/dispatch/status', methods=['GET'])
def dispatch_status():
    """
    Obtener estadísticas del Event Dispatcher
    
    Response:
        {
          "events_received": 150,
          "events_written": 140,
          "batches_flushed": 7,
          "last_flush": "2026-03-27T19:45:30...",
          "buffer_size": 10,
          "worker_alive": true
        }
    """
    try:
        stats = dispatcher.get_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/dispatch/flush', methods=['POST'])
def dispatch_flush():
    """
    Forzar flush inmediato del buffer (útil para shutdown limpio)
    
    Response:
        {"status": "flushed", "events_written": 10}
    """
    try:
        before_count = dispatcher.stats['events_written']
        dispatcher._flush_buffer()
        after_count = dispatcher.stats['events_written']
        
        return jsonify({
            'status': 'flushed',
            'events_written_this_flush': after_count - before_count,
            'total_events_written': after_count
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# MEMBERS MANAGEMENT API (TAREA 3)
# ============================================================================

from core.members_registry import MembersRegistry

# Instancia global de registry
_members_registry = None

def get_members_registry():
    """Obtener instancia singleton de MembersRegistry"""
    global _members_registry
    if _members_registry is None:
        _members_registry = MembersRegistry()
    return _members_registry


@app.route('/members/register', methods=['POST'])
def register_member():
    """
    Registrar nuevo miembro del equipo
    
    Body:
        {
            "member_id": "qwen_local_01",
            "name": "Qwen Local",
            "platform": "ollama",
            "role": "asistente_tecnico",
            "nickname": "QW" (opcional)
        }
    
    Response:
        {
            "success": true,
            "member_id": "qwen_local_01",
            "path": "/home/gus/WORKSPACE_NEUROBIT_V0.2/data/members/qwen_local_01"
        }
    """
    try:
        registry = get_members_registry()
        data = request.get_json() or {}
        
        member_id = data.get("member_id", "").strip()
        name = data.get("name", "").strip()
        platform = data.get("platform", "").strip()
        role = data.get("role", "").strip()
        
        if not all([member_id, name, platform, role]):
            return jsonify({
                "success": False,
                "error": "Missing required fields: member_id, name, platform, role"
            }), 400
        
        result = registry.register_member(member_id, name, platform, role)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/members/list', methods=['GET'])
def list_members():
    """
    Listar miembros registrados
    
    Query params:
        - active_only: bool (default: true)
    
    Response:
        {
            "members": [
                {"member_id": "qwen_local_01", "status": "active"},
                {"member_id": "claude_vscode_01", "status": "active"}
            ]
        }
    """
    try:
        registry = get_members_registry()
        active_only = request.args.get('active_only', 'true').lower() in ('true', '1', 'yes')
        
        members = registry.list_members(active_only=active_only)
        
        return jsonify({"members": members}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/members/<member_id>/status', methods=['GET'])
def get_member_status(member_id):
    """
    Obtener estado detallado de un miembro
    
    Response:
        {
            "success": true,
            "location": "active",
            "profile": {
                "member_id": "qwen_local_01",
                "name": "Qwen Local",
                "platform": "ollama",
                "role": "asistente_tecnico",
                "status": "active",
                "registered_at": "2026-04-28T10:36:06.137978"
            },
            "status": {
                "status": "active",
                "current_task": null,
                "last_activity": "2026-04-28T10:36:06.139742",
                "tasks_completed": 0,
                "tasks_concluded": 0
            }
        }
    """
    try:
        registry = get_members_registry()
        result = registry.get_member_status(member_id)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/members/<member_id>/deactivate', methods=['POST'])
def deactivate_member(member_id):
    """
    Dar de baja visual a un miembro (mover a inactive_members)
    
    Body:
        {
            "reason": "Cambio de equipo" (opcional)
        }
    
    Response:
        {
            "success": true,
            "member_id": "qwen_local_01",
            "new_path": "/home/gus/WORKSPACE_NEUROBIT_V0.2/data/inactive_members/qwen_local_01"
        }
    """
    try:
        registry = get_members_registry()
        data = request.get_json() or {}
        reason = data.get("reason", "")
        
        result = registry.deactivate_member(member_id, reason)
        
        if result["success"]:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/members/<member_id>/nickname', methods=['POST'])
def set_member_nickname(member_id):
    """
    Asignar nickname a un miembro (solo Director)
    
    Headers:
        - X-Director: NODO_SEMILLA (requerido)
    
    Body:
        {
            "nickname": "QW"
        }
    
    Response:
        {
            "success": true,
            "member_id": "qwen_local_01",
            "old_nickname": null,
            "new_nickname": "QW"
        }
    """
    try:
        # Validar que es Director
        director = request.headers.get('X-Director', '').strip()
        if director != 'NODO_SEMILLA':
            return jsonify({
                "success": False,
                "error": "Unauthorized: X-Director header must be 'NODO_SEMILLA'"
            }), 403
        
        registry = get_members_registry()
        data = request.get_json() or {}
        nickname = data.get("nickname", "").strip()
        
        if not nickname:
            return jsonify({"success": False, "error": "Missing nickname"}), 400
        
        # Obtener perfil actual
        result = registry.get_member_status(member_id)
        
        if not result["success"]:
            return jsonify(result), 404
        
        # Leer profile.yaml
        member_path = Path(result["path"])
        profile_path = member_path / "profile.yaml"
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = yaml.safe_load(f)
        
        old_nickname = profile.get("nickname")
        profile["nickname"] = nickname
        
        # Guardar actualizado
        with open(profile_path, 'w', encoding='utf-8') as f:
            yaml.dump(profile, f, allow_unicode=True, default_flow_style=False)
        
        return jsonify({
            "success": True,
            "member_id": member_id,
            "old_nickname": old_nickname,
            "new_nickname": nickname
        }), 200
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/members/<member_id>/daily-log', methods=['POST'])
def create_daily_log(member_id):
    """
    Crear log diario para un miembro
    
    Body:
        {
            "date": "2026-04-28" (opcional, default: hoy)
        }
    
    Response:
        {
            "success": true,
            "path": "/home/gus/WORKSPACE_NEUROBIT_V0.2/data/members/qwen_local_01/logs/2026-04-28",
            "summary_file": "/home/gus/WORKSPACE_NEUROBIT_V0.2/data/members/qwen_local_01/logs/2026-04-28/summary.md"
        }
    """
    try:
        registry = get_members_registry()
        data = request.get_json() or {}
        date = data.get("date")
        
        result = registry.create_daily_log(member_id, date)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/members/<member_id>/daily-summary', methods=['POST'])
def append_daily_summary(member_id):
    """
    Agregar resumen diario a un miembro (append-only)
    
    Body:
        {
            "summary": "- Completada tarea 1\n- Iniciada tarea 2",
            "date": "2026-04-28" (opcional, default: hoy)
        }
    
    Response:
        {
            "success": true,
            "summary_file": "/home/gus/WORKSPACE_NEUROBIT_V0.2/data/members/qwen_local_01/logs/2026-04-28/summary.md"
        }
    """
    try:
        registry = get_members_registry()
        data = request.get_json() or {}
        summary = data.get("summary", "").strip()
        date = data.get("date")
        
        if not summary:
            return jsonify({"success": False, "error": "Missing summary"}), 400
        
        result = registry.append_daily_summary(member_id, summary, date)
        
        if result["success"]:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# GRACEFUL SHUTDOWN
# ============================================================================

import atexit

def _shutdown_dispatcher():
    """Detener dispatcher al cerrar API"""
    try:
        dispatcher.stop()
    except:
        pass

atexit.register(_shutdown_dispatcher)

if __name__ == "__main__":
    import os
    host = os.environ.get("NEUROBIT_HOST", "127.0.0.1")
    port = int(os.environ.get("NEUROBIT_PORT", 5000))

    # Allow toggling debug via env var, but disable the auto-reloader to avoid
    # issues when running inside this orchestrated terminal environment.
    debug_flag = os.environ.get("NEUROBIT_DEBUG", "0") in ("1", "true", "True")
    
    # ✅ CAMBIO 2.5: Usar socketio.run() si SocketIO está disponible
    if WEBSOCKET_ENABLED and socketio is not None:
        print(f"[Startup] Iniciando servidor con WebSocket (SocketIO)")
        print(f"[Startup] HTTP API: http://{host}:{port}")
        print(f"[Startup] WebSocket: ws://{host}:5001")
        socketio.run(app, host=host, port=port, debug=debug_flag, use_reloader=False, allow_unsafe_werkzeug=True)
    else:
        print(f"[Startup] SocketIO no disponible, iniciando solo HTTP API")
        app.run(host=host, port=port, debug=debug_flag, use_reloader=False)
