#!/usr/bin/env python3
"""
agents_registry.py

Módulo de Registro de Agentes para ESTACIÓN CENTRAL v3.0

Gestiona:
- Registro de agentes en múltiples plataformas (ChatGPT, Qwen, Gemini, etc.)
- Verificación de conectividad con APIs externas
- Persistencia en JSONL append-only (data/agents_registry.jsonl)
- Estado de agentes (pending, active, failed, inactive)
- Sala de sesión multi-agente para orquestación de rondas

Protocolo: NEUROBIT v2.1
Validador: SIMON

Autor: Estación Central
Versión: 3.0 - Enero 2026
"""

from __future__ import annotations
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
import hashlib

# ============================================================================
# DOMINIO: DEFINICIONES
# ============================================================================

AGENTS_REGISTRY_PATH = Path(__file__).resolve().parent.parent / "data" / "agents_registry.jsonl"
SALA_SESION_PATH = Path(__file__).resolve().parent.parent / "data" / "sala_sesion_active.jsonl"

# Plataformas soportadas
SUPPORTED_PLATFORMS = {
    "chatgpt": {"base_url": "https://api.openai.com/v1", "requires_key": True, "name": "OpenAI ChatGPT"},
    "qwen": {"base_url": "https://dashscope.aliyuncs.com/api/v1", "requires_key": True, "name": "Alibaba Qwen"},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1", "requires_key": True, "name": "Google Gemini"},
    "local_llama": {"base_url": "http://127.0.0.1:8000", "requires_key": False, "name": "Local Llama"},
    "claude": {"base_url": "https://api.anthropic.com/v1", "requires_key": True, "name": "Anthropic Claude"},
    "teamviewer_extension": {"base_url": "http://127.0.0.1:5000", "requires_key": False, "name": "TEAMVIEWER SOBERANO (Chrome Extension)"},
}

# Estados posibles de un agente
AGENT_STATES = {
    "pending_verification": "Esperando verificación de conectividad",
    "active": "Agente activo y disponible",
    "inactive": "Agente registrado pero inactivo",
    "failed": "Error de conectividad",
    "suspended": "Suspendido por anomalía",
}

# ============================================================================
# DATACLASS: Agent
# ============================================================================

@dataclass
class Agent:
    """Representa un agente remoto en el ecosistema NEUROBIT."""
    
    id: str  # agent_XXXXXXXX
    platform: str  # chatgpt, qwen, gemini, etc.
    name: str  # Nombre amigable (ej: "GPT-4 Pro", "Qwen Assistant")
    api_key_hash: str  # SHA-256 del API key (nunca guardar en claro)
    status: str  # pending_verification, active, failed, etc.
    registered_at: str  # ISO timestamp
    last_heartbeat: Optional[str] = None  # Último ACK recibido
    round_id: Optional[str] = None  # ID de la ronda actual
    session_id: Optional[str] = None  # ID de la sala de sesión
    stats: Dict[str, int] = None  # {messages_sent: 0, messages_received: 0}
    metadata: Dict[str, Any] = None  # Datos adicionales por plataforma
    
    def __post_init__(self):
        if self.stats is None:
            self.stats = {"messages_sent": 0, "messages_received": 0}
        if self.metadata is None:
            self.metadata = {}
    
    def to_envelope(self) -> Dict[str, Any]:
        """Convierte a envelope NEUROBIT v2.1."""
        return {
            "MESSAGE_ID": f"agent_envelope_{self.id}",
            "TIMESTAMP": datetime.utcnow().isoformat() + "Z",
            "ORIGEN": "ESTACION_CENTRAL",
            "DESTINO": f"AGENT_{self.id}",
            "AGENT_ID": self.id,
            "PLATFORM": self.platform,
            "STATUS": self.status,
            "CONTENT": json.dumps(asdict(self)),
            "PROTOCOL_VERSION": "NEUROBIT_v2.1",
            "VALIDATOR": "SIMON"
        }


# ============================================================================
# CLASE: AgentRegistry
# ============================================================================

class AgentRegistry:
    """Gestor centralizado de registro de agentes."""
    
    def __init__(self, registry_path: Path = AGENTS_REGISTRY_PATH):
        self.registry_path = registry_path
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.agents: Dict[str, Agent] = {}
        self._load_from_disk()
    
    def _load_from_disk(self):
        """Carga agentes registrados desde JSONL."""
        if not self.registry_path.exists():
            self.registry_path.touch()
            return
        
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        agent = Agent(**data)
                        self.agents[agent.id] = agent
        except Exception as e:
            print(f"⚠️  Error cargando registry: {e}")
    
    def _save_to_disk(self, agent: Agent):
        """Escribe agente al JSONL (append-only)."""
        try:
            with open(self.registry_path, 'a', encoding='utf-8') as f:
                line = json.dumps(asdict(agent))
                f.write(line + "\n")
        except Exception as e:
            print(f"❌ Error guardando agente: {e}")
            return False
        return True
    
    def hash_api_key(self, api_key: str) -> str:
        """Hashea un API key con SHA-256."""
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]
    
    def register_agent(self, platform: str, name: str, api_key: Optional[str] = None,
                      metadata: Optional[Dict] = None, tabId: Optional[int] = None,
                      pid: Optional[int] = None, url: Optional[str] = None) -> Tuple[bool, str, Optional[Agent]]:
        """
        Registra un nuevo agente.
        
        Para TEAMVIEWER: proporcionar tabId, pid, url
        Para APIs: proporcionar api_key
        
        Returns:
            (success: bool, message: str, agent: Optional[Agent])
        """
        
        # Validar plataforma
        if platform not in SUPPORTED_PLATFORMS:
            return False, f"Plataforma no soportada: {platform}", None
        
        # Validar API key si es requerido
        if SUPPORTED_PLATFORMS[platform]["requires_key"] and not api_key:
            return False, f"Plataforma {platform} requiere API key", None
        
        # Crear agente
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        api_key_hash = self.hash_api_key(api_key) if api_key else "none"
        
        # Agregar campos TEAMVIEWER a metadata (si existen)
        if platform == "teamviewer_extension":
            metadata = metadata or {}
            metadata["tabId"] = tabId
            metadata["pid"] = pid
            metadata["url"] = url
        
        agent = Agent(
            id=agent_id,
            platform=platform,
            name=name,
            api_key_hash=api_key_hash,
            status="pending_verification",
            registered_at=datetime.utcnow().isoformat() + "Z",
            metadata=metadata or {}
        )
        
        # Intentar verificar conectividad
        is_reachable = self._verify_connectivity(platform, api_key)
        
        if is_reachable:
            agent.status = "active"
            agent.last_heartbeat = datetime.utcnow().isoformat() + "Z"
            message = f"✅ Agente {name} registrado y ACTIVO"
        else:
            agent.status = "failed"
            message = f"⚠️  Agente {name} registrado pero FALLÓ verificación de conectividad"
        
        # Guardar
        self.agents[agent.id] = agent
        self._save_to_disk(agent)
        
        return True, message, agent
    
    def _verify_connectivity(self, platform: str, api_key: Optional[str]) -> bool:
        """
        Intenta conectar con la API de la plataforma para verificar credenciales.
        (Implementación stub - será completada con integraciones reales)
        """
        try:
            if platform == "local_llama":
                # Para Llama local, verificar que el servidor esté escuchando
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(("127.0.0.1", 8000))
                sock.close()
                return result == 0
            
            # Para APIs remotas, esto requeriría requests + try-catch real
            # Por ahora, asumir que si hay API key, es válida (mejora en producción)
            return bool(api_key)
        
        except Exception as e:
            print(f"⚠️  Verificación fallida para {platform}: {e}")
            return False
    
    def list_agents(self, status: Optional[str] = None) -> List[Agent]:
        """Lista agentes, opcionalmente filtrados por estado."""
        result = list(self.agents.values())
        if status:
            result = [a for a in result if a.status == status]
        return result
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Obtiene un agente por ID."""
        return self.agents.get(agent_id)
    
    def update_agent_status(self, agent_id: str, new_status: str) -> bool:
        """Actualiza el estado de un agente."""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        agent.status = new_status
        agent.last_heartbeat = datetime.utcnow().isoformat() + "Z"
        self._save_to_disk(agent)
        return True
    
    def update_agent_round(self, agent_id: str, round_id: str, session_id: str) -> bool:
        """Asigna un agente a una ronda y sesión."""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        agent.round_id = round_id
        agent.session_id = session_id
        self._save_to_disk(agent)
        return True


# ============================================================================
# CLASE: SalaSession (Multi-Agent Round Orchestrator)
# ============================================================================

@dataclass
class Round:
    """Define una ronda de trabajo."""
    
    round_id: str  # round_001, round_002, etc.
    number: int  # 1, 2, 3...
    title: str  # "Brainstorm", "Conclusiones", etc.
    prompt: str  # Instrucción para los agentes
    agent_ids: List[str]  # [agent_001, agent_002, ...]
    status: str  # pending, in_progress, completed
    responses: Dict[str, str] = None  # {agent_id: respuesta}
    created_at: str = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        if self.responses is None:
            self.responses = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"


@dataclass
class SalaSession:
    """Sesión de sala (multi-agente, multi-ronda)."""
    
    session_id: str  # session_XXXXXXXX
    name: str  # "Sesión de Investigación Q1 2026"
    agent_ids: List[str]  # IDs de agentes participantes
    rounds: List[Round] = None  # Rondas definidas
    status: str = "created"  # created, in_progress, completed
    created_at: str = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.rounds is None:
            self.rounds = []
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat() + "Z"
        if self.metadata is None:
            self.metadata = {}
    
    def to_envelope(self) -> Dict[str, Any]:
        """Convierte a envelope NEUROBIT v2.1."""
        return {
            "MESSAGE_ID": f"sala_envelope_{self.session_id}",
            "TIMESTAMP": datetime.utcnow().isoformat() + "Z",
            "ORIGEN": "ESTACION_CENTRAL",
            "DESTINO": "SALA_SESSION_BROADCAST",
            "SESSION_ID": self.session_id,
            "AGENTS": self.agent_ids,
            "ROUNDS_COUNT": len(self.rounds),
            "STATUS": self.status,
            "PROTOCOL_VERSION": "NEUROBIT_v2.1",
            "VALIDATOR": "SIMON"
        }


class RoundOrchestrator:
    """Orquestador de rondas."""
    
    def __init__(self, registry: AgentRegistry, sala_path: Path = SALA_SESION_PATH):
        self.registry = registry
        self.sala_path = sala_path
        self.sala_path.parent.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, SalaSession] = {}
        self._load_sessions()
    
    def _load_sessions(self):
        """Carga sesiones activas desde JSONL."""
        if not self.sala_path.exists():
            return
        
        try:
            with open(self.sala_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        # Parsing simplificado (mejora en producción)
                        pass
        except Exception:
            pass
    
    def create_session(self, name: str, agent_ids: List[str]) -> Tuple[bool, str, Optional[SalaSession]]:
        """Crea una nueva sesión de sala."""
        
        # Validar que existan los agentes
        for agent_id in agent_ids:
            if not self.registry.get_agent(agent_id):
                return False, f"Agente no encontrado: {agent_id}", None
        
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        session = SalaSession(
            session_id=session_id,
            name=name,
            agent_ids=agent_ids
        )
        
        self.sessions[session_id] = session
        return True, f"✅ Sala '{name}' creada con {len(agent_ids)} agentes", session
    
    def add_round(self, session_id: str, title: str, prompt: str) -> Tuple[bool, str, Optional[Round]]:
        """Añade una ronda a una sesión."""
        
        if session_id not in self.sessions:
            return False, f"Sesión no encontrada: {session_id}", None
        
        session = self.sessions[session_id]
        round_num = len(session.rounds) + 1
        round_id = f"round_{session_id}_{round_num:03d}"
        
        round_obj = Round(
            round_id=round_id,
            number=round_num,
            title=title,
            prompt=prompt,
            agent_ids=session.agent_ids,
            status="pending"
        )
        
        session.rounds.append(round_obj)
        return True, f"✅ Ronda #{round_num} '{title}' añadida", round_obj
    
    def start_session(self, session_id: str) -> bool:
        """Inicia una sesión (marcar como in_progress)."""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        session.status = "in_progress"
        session.started_at = datetime.utcnow().isoformat() + "Z"
        return True


# ============================================================================
# HELPERS
# ============================================================================

def print_agent_info(agent: Agent):
    """Imprime info formateada de un agente."""
    print(f"""
    🤖 AGENTE: {agent.name}
       ID: {agent.id}
       Plataforma: {agent.platform}
       Estado: {agent.status}
       Registrado: {agent.registered_at}
       Último heartbeat: {agent.last_heartbeat or 'nunca'}
       Stats: {agent.stats}
    """)


if __name__ == "__main__":
    # Test básico
    print("\n🧬 NEUROBIT v2.1 - Agents Registry")
    print("=" * 60)
    
    registry = AgentRegistry()
    
    # Registrar agente de prueba
    success, msg, agent = registry.register_agent(
        platform="local_llama",
        name="Llama 3 Local",
        metadata={"model": "llama-3-70b", "context_window": 8192}
    )
    
    print(msg)
    if agent:
        print_agent_info(agent)
    
    # Listar agentes
    print("\n📋 Agentes activos:")
    for agent in registry.list_agents(status="active"):
        print(f"  • {agent.name} ({agent.id})")

