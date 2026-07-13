# core/sala_ronda_minimal.py
#!/usr/bin/env python3
"""
SalaDeReuniones — Núcleo minimal para intercomunicación NODO_SEMILLA ↔ LLMs
Protocolo: Tags + Clipboard + memoria_eva.jsonl (append-only)
"""
import json, datetime, hashlib, re
from pathlib import Path

class SalaRondaMinimal:
    def __init__(self, arca_path: str):
        self.arca = Path(arca_path)
        self.TAG_PATTERN = re.compile(r'<(\w+)_tecnico>(.*?)</\1_tecnico>', re.DOTALL)
    
    def abrir_ronda(self, consigna: str, autor: str = "NODO_SEMILLA"):
        """Registra apertura de ronda en el Arca"""
        evento = {
            "MESSAGE_ID": f"RONDA-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "TIMESTAMP": datetime.datetime.now().isoformat(),
            "TIPO": "APERTURA_RONDA",
            "AUTOR": autor,
            "CONSIGNA": consigna,
            "estado": "abierta"
        }
        self._append(evento)
        return evento["MESSAGE_ID"]
    
    def procesar_respuesta(self, texto: str, participante: str = "Claude"):
        """Extrae tags, valida y registra respuesta"""
        resultados = []
        for match in self.TAG_PATTERN.finditer(texto):
            rol, contenido = match.group(1), match.group(2).strip()
            evento = {
                "MESSAGE_ID": f"RESP-{hashlib.md5(contenido.encode()).hexdigest()[:12]}",
                "TIMESTAMP": datetime.datetime.now().isoformat(),
                "TIPO": "RESPUESTA_RONDA",
                "PARTICIPANTE": participante,
                "ROL": rol,
                "contenido": contenido,
                "content_hash": hashlib.sha256(contenido.encode()).hexdigest()
            }
            self._append(evento)
            resultados.append({"rol": rol, "message_id": evento["MESSAGE_ID"]})
        return resultados
    
    def _append(self, evento: dict):
        """Append-only a memoria_eva.jsonl"""
        with open(self.arca, "a", encoding="utf-8") as f:
            f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    
    def obtener_ultima_ronda(self):
        """Retorna la última ronda abierta"""
        if not self.arca.exists():
            return None
        with open(self.arca, "r", encoding="utf-8") as f:
            for line in reversed(f.readlines()[-100:]):  # Últimas 100 líneas
                try:
                    entry = json.loads(line)
                    if entry.get("TIPO") == "APERTURA_RONDA":
                        return entry
                except:
                    continue
        return None