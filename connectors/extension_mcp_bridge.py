#!/usr/bin/env python3
"""
Conector MCP para la extensión Chrome - Estación Central
Sincroniza historial, validaciones y estado entre la extensión (navegador) y la Estación Central.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Importar el cliente MCP existente
try:
    from core.adapters import adapter_mcp
except ImportError:
    # Fallback si no está disponible en el entorno
    adapter_mcp = None

class ExtensionMCPConnector:
    """Conector bidireccional: Extensión ↔ MCP Server ↔ Estación Central"""
    
    def __init__(self, mcp_url: str = "http://127.0.0.1:8090"):
        """
        Inicializa el conector.
        
        Args:
            mcp_url: URL del servidor MCP (default: localhost:8090)
        """
        self.mcp_url = mcp_url
        self.client = adapter_mcp if adapter_mcp else None
    
    def push_extension_state(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía estado de la extensión al MCP (y luego al Arca).
        
        Formato esperado de envelope:
        {
            'MESSAGE_ID': 'EXT_MSG_<timestamp>_<uuid>',
            'content': '...',
            'SESSION_TAG': 'extension_session_001',
            'ORIGEN': 'EXTENSION_CHROME',
            'DESTINO': 'ESTACION_CENTRAL',
            'metadata': {
                'popup_state': {...},
                'history': [...],
                'validation_results': {...}
            }
        }
        """
        if not self.client:
            return {"error": "MCP client not available"}
        
        try:
            # Validar estructura mínima
            if 'MESSAGE_ID' not in envelope or 'content' not in envelope:
                return {
                    "status": "error",
                    "reason": "Missing MESSAGE_ID or content"
                }
            
            # Enriquecer envelope con timestamp de extensión
            envelope['TIMESTAMP'] = datetime.now().isoformat()
            envelope['ORIGEN'] = envelope.get('ORIGEN', 'EXTENSION_CHROME')
            envelope['DESTINO'] = envelope.get('DESTINO', 'ESTACION_CENTRAL')
            
            # Enviar via MCP (write_arca)
            result = self.client.send_message(envelope)
            
            return {
                "status": "success",
                "result": result,
                "message": f"Estado de extensión sincronizado: {envelope['MESSAGE_ID']}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def pull_arca_history(self, limit: int = 20) -> Dict[str, Any]:
        """
        Obtiene historial reciente del Arca (últimos N registros).
        
        Usado por la extensión para sincronizar/recuperar sesiones previas.
        """
        if not self.client:
            return {"error": "MCP client not available", "records": []}
        
        try:
            result = self.client.read_arca(limit)
            return {
                "status": "success",
                "count": result.get("count", 0),
                "records": result.get("records", [])
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "records": []
            }
    
    def validate_extension_message(self, content: str) -> Dict[str, Any]:
        """
        Valida un mensaje desde la extensión con reglas SIMON.
        """
        if not self.client:
            return {"is_valid": False, "reason": "MCP client not available"}
        
        try:
            # Llamar a SIMON validator via MCP
            from core.adapters import adapter_simon_validator
            
            envelope = {
                'content': content,
                'MESSAGE_ID': f'VALIDATE_{datetime.now().timestamp()}',
                'ORIGEN': 'EXTENSION_CHROME',
                'type': 'validation'
            }
            
            # SIMON retorna validez
            result = adapter_simon_validator.send_message(envelope)
            
            return {
                "is_valid": result.get("is_valid", False),
                "validation_result": result
            }
        except Exception as e:
            return {
                "is_valid": False,
                "reason": str(e)
            }
    
    def export_extension_session(self, session_id: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Exporta una sesión completa de la extensión como JSON o JSONL.
        """
        try:
            # Obtener historial del Arca para esta sesión
            history = self.pull_arca_history(limit=100)
            
            # Filtrar por SESSION_TAG
            filtered = [
                r for r in history.get('records', [])
                if r.get('session') == session_id
            ]
            
            export = {
                "session_id": session_id,
                "exported_at": datetime.now().isoformat(),
                "record_count": len(filtered),
                "records": filtered
            }
            
            if output_path:
                with open(output_path, 'w') as f:
                    json.dump(export, f, indent=2)
                return {
                    "status": "success",
                    "message": f"Sesión exportada a {output_path}",
                    "path": output_path,
                    "records": len(filtered)
                }
            else:
                return {
                    "status": "success",
                    "data": export,
                    "records": len(filtered)
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


def test_connector():
    """Test rápido del conector."""
    print("🔗 Probando ExtensionMCPConnector...")
    
    connector = ExtensionMCPConnector()
    
    # Prueba 1: Push de estado
    test_envelope = {
        'MESSAGE_ID': f'TEST_EXT_{int(datetime.now().timestamp())}',
        'content': 'Mensaje de prueba desde conector de extensión',
        'SESSION_TAG': 'TEST_SESSION_001'
    }
    
    print("\n1️⃣ Enviando estado al Arca...")
    result = connector.push_extension_state(test_envelope)
    print(f"   Resultado: {result}")
    
    # Prueba 2: Leer historial
    print("\n2️⃣ Leyendo historial...")
    history = connector.pull_arca_history(limit=3)
    print(f"   Registros: {history.get('count', 0)}")
    
    print("\n✅ Test completado")


if __name__ == "__main__":
    test_connector()
