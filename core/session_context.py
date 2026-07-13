# core/session_context.py (nuevo módulo)
class SessionContext:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.context_file = f"data/sessions/{session_id}.jsonl"
    
    def save_turn(self, role: str, content: str, tags: dict):
        """Append-only por sesión"""
        pass
    
    def get_last_n_turns(self, n: int = 50):
        """Recupera contexto para AI (evita pérdida entre sesiones)"""
        pass

# Integración en MCP → exportar/importar sesiones entre instancias