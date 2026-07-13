# core/llm/ollama_bridge.py
#!/usr/bin/env python3
"""
OllamaBridge — Puente entre NEUROBIT API y Qwen3.5:4B local
Protocolo: Tags + Contexto + memoria_eva.jsonl
"""
import requests, json, re
from datetime import datetime

class OllamaBridge:
    def __init__(self, model="qwen3.5-gus", base_url="http://127.0.0.1:11434"):
        self.model = model
        self.base_url = base_url
        self.TAG_PATTERN = re.compile(r'<(\w+)_tecnico>(.*?)</\1_tecnico>', re.DOTALL)
    
    def generate(self, prompt: str, system_prompt: str = None, tags: dict = None):
        """Genera respuesta desde Qwen local con contexto Neurobitrónico"""
        # Construir system prompt con espíritu del proyecto
        base_system = """Eres un miembro del NEUROBIT_DEV_TEAM ("the Sofistas").
Tu rol: Asistente técnico bajo coordinación de NODO_SEMILLA.
Principios:
- Soberanía local: todo corre en 127.0.0.1, sin APIs externas
- Append-only: memoria_eva.jsonl NUNCA se sobrescribe
- Logos coherente: comunicación clara, sin distorsión
- Co-creación: humano + digitales trabajando en sinergia

Formato de respuesta:
- Usa tags identificatorios: <qwen_tecnico>...</qwen_tecnico>
- Sé conciso pero completo
- Si hay ambigüedad, pregunta antes de asumir
"""
        if system_prompt:
            base_system += f"\n\nContexto adicional:\n{system_prompt}"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": base_system,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 2048,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
            result = response.json()
            content = result.get("response", "")
            
            # Validar y extraer tags
            tagged_content = self._extract_tagged(content, tags or {})
            return {
                "success": True,
                "content": tagged_content,
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _extract_tagged(self, content: str, meta: dict):
        """Asegura que la respuesta tenga tags válidos"""
        if not self.TAG_PATTERN.search(content):
            # Si no tiene tags, envolver en tag por defecto
            return f"<qwen_tecnico>\n{content.strip()}\n</qwen_tecnico>"
        return content.strip()
    
    def validate_coherence(self, content: str, matrix_ref: dict = None):
        """Valida coherencia según criterios Neurobitrónicos"""
        # Placeholder: integrar con Matriz Fractal 13x13 en futuro
        return {"coherent": True, "score": 0.95, "notes": "validación básica"}
