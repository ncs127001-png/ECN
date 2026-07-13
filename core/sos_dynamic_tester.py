#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOS CORE - Módulo de Auditoría Dinámica de Endpoints (Fase 2)
Función: Iniciar (si es necesario) y testear los endpoints de neurobit_api.py.
Principio: Observación no destructiva. Localhost first (127.0.0.1).
"""
import os
import sys
import json
import time
import signal
import subprocess
import requests
from pathlib import Path

# Import relativo (funciona desde core/)
from path_resolver import PathResolver

class SOSDynamicTester:
    def __init__(self):
        # Sube 2 niveles: core/ → ECN/
        self.root_path = Path(__file__).resolve().parent.parent
        self.path_resolver = PathResolver(self.root_path)
        self.api_file = self.path_resolver.resolve("neurobit_api.py")
        self.api_url = "http://127.0.0.1:5000"
        self.report = {
            "api_status": "unknown",
            "endpoints_tested": [],
            "errors": []
        }
        self.api_process = None

    def is_api_running(self):
        """Verifica si la API ya está corriendo en el puerto 5000."""
        try:
            r = requests.get(f"{self.api_url}/health", timeout=2)
            return r.status_code == 200
        except requests.ConnectionError:
            return False

    def start_api(self):
        """Inicia la API en un subprocess si no está corriendo."""
        if not self.api_file.exists():
            self.report["errors"].append("neurobit_api.py no encontrado.")
            return False
        
        print("🚀 Iniciando neurobit_api.py en background...")
        try:
            # Usamos el entorno virtual si existe, sino el sistema
            venv_python = self.root_path / ".venv" / "bin" / "python3"
            python_cmd = str(venv_python) if venv_python.exists() else sys.executable
            
            self.api_process = subprocess.Popen(
                [python_cmd, str(self.api_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.root_path)
            )
            # Esperar a que el servidor levante (máximo 5 segundos)
            for _ in range(10):
                if self.is_api_running():
                    print("✅ API iniciada correctamente.")
                    return True
                time.sleep(0.5)
            
            self.report["errors"].append("La API no respondió en el tiempo esperado.")
            return False
        except Exception as e:
            self.report["errors"].append(f"Error al iniciar API: {str(e)}")
            return False

    def stop_api(self):
        """Detiene la API si fue iniciada por este script."""
        if self.api_process:
            print("🛑 Deteniendo API de prueba...")
            self.api_process.send_signal(signal.SIGTERM)
            self.api_process.wait()
            self.api_process = None

    def test_endpoint(self, method, path, payload=None):
        """Testea un endpoint específico."""
        url = f"{self.api_url}{path}"
        try:
            if method == "GET":
                r = requests.get(url, timeout=3)
            elif method == "POST":
                r = requests.post(url, json=payload, timeout=3)
            
            status = "ok" if 200 <= r.status_code < 300 else "fail"
            return {
                "endpoint": path,
                "method": method,
                "status_code": r.status_code,
                "result": status,
                "response_time_ms": round(r.elapsed.total_seconds() * 1000, 2)
            }
        except Exception as e:
            return {
                "endpoint": path,
                "method": method,
                "status_code": 0,
                "result": "error",
                "error_msg": str(e)
            }

    def run_dynamic_tests(self):
        """Ejecuta la batería de tests sobre los endpoints críticos."""
        endpoints_to_test = [
            ("GET", "/health", None),
            ("GET", "/memoria?limit=1", None),
            ("GET", "/participants", None),
            ("GET", "/centinela_status", None),
            ("GET", "/mcp/status", None),
            ("GET", "/dispatch/status", None),
            ("POST", "/analyze", {"content": "test_sos_dynamic", "entity_id": "SOS_TESTER"}),
            ("POST", "/matrix/encode", {"text": "Logos"}),
            ("GET", "/members/list?active_only=true", None)
        ]

        print("🔍 Ejecutando batería de tests dinámicos...")
        for method, path, payload in endpoints_to_test:
            print(f"   -> {method} {path} ... ", end="")
            result = self.test_endpoint(method, path, payload)
            self.report["endpoints_tested"].append(result)
            
            if result["result"] == "ok":
                print(f"✅ {result['status_code']} ({result['response_time_ms']}ms)")
            else:
                print(f"❌ {result['status_code']} ({result.get('error_msg', 'fail')})")

    def generate_report(self, output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        return output_path

if __name__ == "__main__":
    tester = SOSDynamicTester()
    
    print("\n SOS DYNAMIC TESTER - FASE 2")
    print("=" * 40)
    
    api_was_running = tester.is_api_running()
    
    if not api_was_running:
        if not tester.start_api():
            print("❌ No se pudo iniciar la API. Abortando tests dinámicos.")
            sys.exit(1)
    else:
        print("✅ API ya estaba corriendo. No se reiniciará.")

    try:
        tester.run_dynamic_tests()
        out_file = tester.generate_report(tester.root_path / "data" / "sos_dynamic_report.json")
        print(f"\n📊 Reporte dinámico generado en: {out_file}")
    finally:
        if not api_was_running:
            tester.stop_api()
            
    print("✅ Fase 2 completada.")
