#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MFN_LOCATION: core/
MFN_LEVEL: 1
MFN_COORD: (7,7)

core/api_endpoint_manager.py
Gestor dinámico de endpoints para NEUROBIT API
"""

from flask import Flask, jsonify, request
from typing import Dict, Any, List
import deal
from core.module_connector import ModuleConnector

class APIEndpointManager:
    def __init__(self, connector: ModuleConnector):
        self.connector = connector
        self.app = Flask(__name__)
        self._register_dynamic_endpoints()
    
    @deal.post(lambda result: isinstance(result, Flask))
    def _register_dynamic_endpoints(self) -> Flask:
        """Registra endpoints dinámicamente desde el Conector."""
        for module_id, adapter in self.connector.get_adapters().items():
            metadata = adapter.get_metadata()
            
            for endpoint in metadata.get('endpoints', []):
                path = endpoint['path']
                methods = endpoint.get('methods', ['GET'])
                handler = endpoint['handler']
                
                # Crear endpoint dinámico
                self._create_endpoint(path, methods, handler, adapter)
        
        return self.app
    
    def _create_endpoint(self, path: str, methods: List[str], 
                        handler: str, adapter: Any):
        """Crea un endpoint Flask dinámico."""
        
        def dynamic_handler():
            try:
                # Validar precondiciones
                if request.method == 'POST':
                    payload = request.json
                    # Validar schema según module.json
                    if hasattr(adapter, 'validate_input'):
                        adapter.validate_input(payload)
                
                # Ejecutar handler del adaptador
                result = getattr(adapter, handler)()
                
                # Validar postcondiciones
                if hasattr(adapter, 'validate_output'):
                    adapter.validate_output(result)
                
                return jsonify(result), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Registrar en Flask
        self.app.add_url_rule(
            path,
            endpoint=handler,
            view_func=dynamic_handler,
            methods=methods
        )
    
    def run(self, host: str = '127.0.0.1', port: int = 5000):
        """Inicia el servidor."""
        self.app.run(host=host, port=port, debug=False)
