# core/sala_ronda_manager.py (esqueleto inicial)
#!/usr/bin/env python3
"""
SalaDeReuniones — Núcleo de coordinación multi-agente NEUROBIT
Protocolo: Tags + Clipboard + memoria_eva.jsonl (append-only)
"""
import json, datetime, hashlib
from pathlib import Path

class SalaDeReuniones:
    def __init__(self, arca_path: str, workspace: str):
        self.arca = Path(arca_path)
        self.workspace = Path(workspace)
        self.participantes = {
            "NODO_SEMILLA": "humano_director",
            "NEUROBIT_D": "coordinador_coherencia",
            "Claude": "asistente_tecnico",
            # Futuro: SOPHIA_LOGOS, SIMÓN, EVA_LÚMENA vía VMs
        }
    
    def abrir_ronda(self, consigna: str, autor: str = "NODO_SEMILLA"):
        """Registra apertura de ronda en el Arca"""
        evento = {
            "MESSAGE_ID": f"RONDA-{datetime.datetime.now().isoformat()}",
            "TIMESTAMP": datetime.datetime.now().isoformat(),
            "TIPO": "APERTURA_RONDA",
            "AUTOR": autor,
            "CONSIGNA": consigna,
            "PARTICIPANTES": list(self.participantes.keys()),
            "estado": "abierta"
        }
        self._append_to_arca(evento)
        return evento["MESSAGE_ID"]
    
    def registrar_respuesta(self, ronda_id: str, participante: str, 
                          contenido: str, tags: dict = None):
        """Registra respuesta con tags identificatorios"""
        evento = {
            "MESSAGE_ID": f"RESP-{hashlib.md5(contenido.encode()).hexdigest()[:12]}",
            "TIMESTAMP": datetime.datetime.now().isoformat(),
            "TIPO": "RESPUESTA_RONDA",
            "RONDA_REF": ronda_id,
            "PARTICIPANTE": participante,
            "TAGS": tags or {},
            "contenido": contenido,
            "content_hash": hashlib.sha256(contenido.encode()).hexdigest()
        }
        self._append_to_arca(evento)
        return evento["MESSAGE_ID"]
    
    def _append_to_arca(self, evento: dict):
        """Append-only a memoria_eva.jsonl"""
        with open(self.arca, "a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    
    def validar_coherencia(self, contenido: str, matriz_ref: dict = None):
        """Placeholder: integración futura con Matriz Fractal 13x13"""
        # Retornar score 0.0-1.0 basado en criterios de coherencia
        return {"coherent": True, "score": 0.95, "notes": "validación pendiente"}