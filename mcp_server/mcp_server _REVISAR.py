#!/usr/bin/env python3
"""
Servidor MCP (Model Connection Protocol) para integración con LLMs locales
Permite a VSCode/CodeLLM comunicarse con el sistema NEUROBIT
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Configuración base
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "neurobit_config.json"
DATA_DIR = PROJECT_ROOT / "data"
MEMORIA_PATH = DATA_DIR / "memoria_eva.jsonl"

# Cargar configuración
try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"❌ Archivo de configuración no encontrado: {CONFIG_PATH}")
    sys.exit(1)


class MCPHandler(BaseHTTPRequestHandler):
    """Manejador de solicitudes para el servidor MCP"""

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        """Manejar solicitudes OPTIONS para CORS"""
        self._set_headers(204)

    def do_GET(self):
        """Manejar solicitudes GET"""
        parsed_path = urlparse(self.path)
        query = parse_qs(parsed_path.query)

        if parsed_path.path == '/read_arca':
            self._read_arca(query)
        elif parsed_path.path == '/status':
            self._get_status()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint no encontrado"}).encode())

    def do_POST(self):
        """Manejar solicitudes POST"""
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/write_arca':
            self._write_arca()
        elif parsed_path.path == '/validate_with_simon':
            self._validate_with_simon()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint no encontrado"}).encode())

    def _read_arca(self, query):
        """Leer los últimos N registros de la memoria"""
        try:
            limit = int(query.get('limit', [5])[0])
            records = []

            if MEMORIA_PATH.exists():
                with open(MEMORIA_PATH, 'r') as f:
                    lines = f.readlines()
                    # Obtener los últimos N registros
                    for line in lines[-limit:]:
                        try:
                            records.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue

            self._set_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "count": len(records),
                "records": records
            }).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "error": f"Error al leer el Arca: {str(e)}"
            }).encode())

    def _write_arca(self):
        """Escribir un nuevo registro en la memoria"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # Validar datos mínimos
            required_fields = ['MESSAGE_ID', 'content']
            if not all(field in data for field in required_fields):
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "error": f"Campos requeridos: {', '.join(required_fields)}"
                }).encode())
                return

            # Preparar registro
            record = {
                "timestamp": datetime.now().isoformat(),
                "session": data.get("SESSION_TAG", "DEFAULT_SESSION"),
                "message_id": data["MESSAGE_ID"],
                "origin": data.get("ORIGEN", "HOMO_VIVO"),
                "destination": data.get("DESTINO", "ESTACION_CENTRAL"),
                "content": data["content"],
                "version": config.get("version", "2.1")
            }

            # Escribir en memoria (append-only)
            with open(MEMORIA_PATH, 'a') as f:
                f.write(json.dumps(record) + '\n')

            self._set_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "message": f"Registro {data['MESSAGE_ID']} guardado"
            }).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "error": f"Error al escribir en el Arca: {str(e)}"
            }).encode())

    def _validate_with_simon(self):
        """Validar contenido con reglas de coherencia SIMON"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            content = data.get("content", "")
            if not content:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    "error": "Contenido vacío para validar"
                }).encode())
                return

            # Reglas básicas de validación SIMON (extensible)
            is_valid = True
            reasons = []

            # Regla 1: Longitud mínima
            if len(content.strip()) < 10:
                is_valid = False
                reasons.append("contenido_demasiado_corto")

            # Regla 2: No permitir contenido repetitivo simple
            if len(set(content.split())) < 3 and len(content) > 20:
                is_valid = False
                reasons.append("contenido_repetitivo")

            # Regla 3: Verificar protocolo mínimo
            required_headers = ["MESSAGE_ID", "TIMESTAMP", "ORIGEN", "DESTINO"]
            missing_headers = [h for h in required_headers if h not in content]
            if missing_headers:
                is_valid = False
                reasons.append(f"headers_faltantes:{','.join(missing_headers)}")

            response = {
                "status": "success",
                "is_valid": is_valid,
                "validation_time": datetime.now().isoformat()
            }

            if not is_valid:
                response["reasons"] = reasons

            self._set_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "error": f"Error en validación SIMON: {str(e)}"
            }).encode())

    def _get_status(self):
        """Obtener estado del sistema"""
        try:
            record_count = 0
            last_update = "Nunca"

            if MEMORIA_PATH.exists():
                record_count = sum(1 for _ in open(MEMORIA_PATH))
                last_update = datetime.fromtimestamp(
                    os.path.getmtime(MEMORIA_PATH)
                ).isoformat()

            status = {
                "status": "operativo",
                "version": config.get("version", "2.1"),
                "environment": config.get("environment", "unknown"),
                "memory_records": record_count,
                "last_update": last_update,
                "ollama_endpoint": config.get("ollama", {}).get("endpoint", "no_configurado"),
                "timestamp": datetime.now().isoformat()
            }

            self._set_headers()
            self.wfile.write(json.dumps(status).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({
                "error": f"Error al obtener estado: {str(e)}"
            }).encode())


def run_server(port=8090):
    """Iniciar servidor MCP"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MCPHandler)
    print(f"🧠 Servidor MCP NEUROBIT activo en http://localhost:{port}")
    print(f"📦 Arca ubicada en: {MEMORIA_PATH}")
    print("⌨️  Presiona Ctrl+C para detener")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Apagando servidor MCP...")
        httpd.server_close()


if __name__ == "__main__":
    # Validar que existan los directorios necesarios
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True)
        print(f"✅ Creado directorio de datos: {DATA_DIR}")

    if not MEMORIA_PATH.exists():
        MEMORIA_PATH.touch()
        print(f"✅ Creado archivo de memoria: {MEMORIA_PATH}")

    # Iniciar servidor
    run_server()
