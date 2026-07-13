#!/usr/bin/env python3
from flask import Flask, jsonify, request, make_response
from pathlib import Path
import re
import json
import datetime  # ✅ IMPORTANTE: Falta este import en tu versión actual
import os
import logging

# ✅ Configurar logging para depuración
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
FRAGMENTS_DIR = Path.home() / "neurobit_salon_v0.1" / "fragments"

# ✅ Crear directorio si no existe
FRAGMENTS_DIR.mkdir(parents=True, exist_ok=True)
logger.info(f"📁 Directorio de fragmentos: {FRAGMENTS_DIR}")

# ✅ AÑADIR MIDDLEWARE CORS GLOBAL
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# ✅ MANEJAR PREFLIGHT REQUESTS (OPTIONS)
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    response = make_response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route('/get_fragments_state')
def get_fragments_state():
    """Devuelve lista de fragmentos disponibles"""
    try:
        logger.info("📡 Solicitando estado de fragmentos")
        
        # ✅ Verificar que el directorio existe
        if not FRAGMENTS_DIR.exists():
            logger.error(f"❌ Directorio no encontrado: {FRAGMENTS_DIR}")
            return jsonify({"error": f"Directorio no encontrado: {FRAGMENTS_DIR}"}), 500
        
        # ✅ Listar solo archivos .txt que comienzan con 'parte_'
        fragmentos = [
            f.name for f in FRAGMENTS_DIR.glob("parte_*.txt")
            if f.is_file() and not f.name.endswith('.info')
        ]
        
        logger.info(f"📄 Encontrados {len(fragmentos)} fragmentos")
        
        # ✅ Ordenar numéricamente con manejo de errores
        try:
            fragmentos.sort(key=lambda x: int(re.search(r'(\d+)', x).group(1)))
        except Exception as e:
            logger.warning(f"⚠️ Error al ordenar fragmentos: {e}")
            fragmentos.sort()  # Orden alfabético como fallback
        
        response_data = {
            "total": len(fragmentos),
            "fragments": fragmentos,
            "timestamp": datetime.datetime.now().isoformat(),
            "directory": str(FRAGMENTS_DIR)
        }
        
        logger.info(f"✅ Respuesta exitosa: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"❌ Error en get_fragments_state: {str(e)}", exc_info=True)
        return jsonify({"error": str(e), "traceback": str(e.__traceback__)}), 500

@app.route('/get_fragment_content')
def get_fragment_content():
    """Devuelve contenido de un fragmento específico"""
    name = request.args.get('name')
    if not name:
        logger.warning("⚠️ Solicitud sin parámetro 'name'")
        return "Nombre de fragmento requerido", 400
    
    try:
        logger.info(f"📖 Solicitando contenido de: {name}")
        
        # ✅ Validar nombre de archivo (seguridad básica)
        if '..' in name or name.startswith('/') or name.startswith('\\'):
            logger.warning(f"⚠️ Intento de path traversal: {name}")
            return "Nombre de archivo inválido", 400
        
        file_path = FRAGMENTS_DIR / name
        
        # ✅ Verificar que el archivo existe
        if not file_path.exists():
            logger.warning(f"⚠️ Archivo no encontrado: {file_path}")
            return f"Fragmento no encontrado: {name}", 404
        
        # ✅ Verificar que es un archivo (no un directorio)
        if not file_path.is_file():
            logger.warning(f"⚠️ No es un archivo: {file_path}")
            return f"Ruta no es un archivo: {name}", 400
        
        # ✅ Leer contenido con manejo de codificación
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"✅ Leído {len(content)} caracteres de {name}")
        except UnicodeDecodeError:
            logger.warning(f"⚠️ Error de codificación en {name}, intentando latin-1")
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        # ✅ Eliminar header NEUROBIT para dejar solo el contenido
        if "[CONTENT]:" in content:
            content = content.split("[CONTENT]:", 1)[1].strip()
            logger.debug("✂️ Eliminado header NEUROBIT")
        
        return content
    
    except Exception as e:
        logger.error(f"❌ Error en get_fragment_content: {str(e)}", exc_info=True)
        return f"Error al leer fragmento: {str(e)}", 500

@app.route('/health')
def health_check():
    """Endpoint para verificar estado del servidor"""
    return jsonify({
        "status": "ok",
        "server_time": datetime.datetime.now().isoformat(),
        "fragments_dir": str(FRAGMENTS_DIR),
        "fragments_count": len(list(FRAGMENTS_DIR.glob("parte_*.txt")))
    })

if __name__ == '__main__':
    # ✅ Mostrar información de inicio
    logger.info("="*50)
    logger.info("🚀 INICIANDO NEUROBIT FRAGMENT STATE SERVER")
    logger.info(f"🌍 URL: http://localhost:5000")
    logger.info(f"📁 Directorio de fragmentos: {FRAGMENTS_DIR}")
    logger.info(f"🔍 Endpoints disponibles:")
    logger.info("   GET /get_fragments_state")
    logger.info("   GET /get_fragment_content?name=archivo.txt")
    logger.info("   GET /health")
    logger.info("="*50)
    
    app.run(host='127.0.0.1', port=5000, debug=True)