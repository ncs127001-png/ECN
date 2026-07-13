from flask import Flask, request, jsonify, send_file
import os
import subprocess
import threading
from pathlib import Path
import json

app = Flask(__name__)

# 🔑 Rutas correctas según tu estructura
BASE_DIR = Path(__file__).parent.parent.absolute()
UPLOADS_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"

# ✅ Crear directorios si no existen
UPLOADS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

@app.route('/')
def hello():
    return f"""
    ✅ ¡SERVICIO NEUROBIT ACTIVO! 
    Ruta actual: {os.getcwd()}
    UPLOADS_DIR: {UPLOADS_DIR}
    RESULTS_DIR: {RESULTS_DIR}
    Endpoints disponibles:
    - /test : Verifica estado del servicio
    - /search-files : Busca archivos desde lista .txt
    - /generate-compendium : Genera compendio inteligente
    - /download/<filename> : Descarga resultados
    """

@app.route('/test')
def test():
    return {
        "status": "success",
        "working_dir": str(BASE_DIR),
        "uploads_dir": str(UPLOADS_DIR),
        "results_dir": str(RESULTS_DIR),
        "user": os.getenv('USER', 'unknown'),
        "python_version": os.popen('python3 --version 2>&1').read().strip()
    }

@app.route('/search-files', methods=['POST'])
def search_files():
    """Endpoint para búsqueda recursiva de archivos"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No se recibieron datos JSON"}), 400
        
        file_list = data.get('file_list', '')
        source_dir = data.get('source_dir', str(BASE_DIR))
        dest_folder = data.get('dest_folder', 'archivos_recuperados')
        
        if not file_list.strip():
            return jsonify({"error": "La lista de archivos está vacía"}), 400
        
        # Validar que el directorio de origen existe
        if not os.path.exists(source_dir):
            return jsonify({"error": f"El directorio de origen no existe: {source_dir}"}), 400
        
        # Crear lista temporal
        list_path = UPLOADS_DIR / "temp_list.txt"
        with open(list_path, 'w', encoding='utf-8') as f:
            f.write(file_list)
        
        # Directorio de resultados
        result_path = RESULTS_DIR / dest_folder
        result_path.mkdir(exist_ok=True)
        
        # Comando para ejecutar el script de búsqueda
        cmd = [
            'python3', str(BASE_DIR / 'backend/file_search.py'),
            '--list', str(list_path),
            '--source', source_dir,
            '--dest', str(result_path)
        ]
        
        # Ejecutar en segundo plano
        def run_search():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"✅ Búsqueda completada. Salida:\n{result.stdout}")
                if result.stderr:
                    print(f"⚠️ Advertencias:\n{result.stderr}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error en búsqueda:\n{e.stderr}")
            except Exception as e:
                print(f"❌ Error inesperado: {str(e)}")
        
        threading.Thread(target=run_search, daemon=True).start()
        
        return jsonify({
            "status": "started",
            "message": "Búsqueda iniciada en segundo plano",
            "result_folder": str(result_path),
            "estimated_time": "Depende de la cantidad de archivos"
        })
    
    except Exception as e:
        return jsonify({"error": f"Error en /search-files: {str(e)}"}), 500

@app.route('/generate-compendium', methods=['POST'])
def generate_compendium():
    """Endpoint para generar compendio con OCR y procesamiento de PDFs"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No se recibieron datos JSON"}), 400
        
        source_dir = data.get('source_dir', str(UPLOADS_DIR))
        compendium_name = data.get('name', 'compendio_neurobit')
        
        # Validar directorio de origen
        if not os.path.exists(source_dir):
            return jsonify({"error": f"El directorio de origen no existe: {source_dir}"}), 400
        
        # Comando para ejecutar el script de compendio
        cmd = [
            'python3', str(BASE_DIR / 'backend/compendium_v22.py'),
            '--source', source_dir,
            '--output', str(RESULTS_DIR / compendium_name)
        ]
        
        # Ejecutar en segundo plano
        def run_compendium():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"✅ Compendio generado. Salida:\n{result.stdout}")
                if result.stderr:
                    print(f"⚠️ Advertencias:\n{result.stderr}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error en generación de compendio:\n{e.stderr}")
            except Exception as e:
                print(f"❌ Error inesperado: {str(e)}")
        
        threading.Thread(target=run_compendium, daemon=True).start()
        
        return jsonify({
            "status": "started",
            "message": "Generación de compendio iniciada en segundo plano",
            "compendium_name": compendium_name,
            "estimated_time": "Depende de la cantidad y tipo de documentos"
        })
    
    except Exception as e:
        return jsonify({"error": f"Error en /generate-compendium: {str(e)}"}), 500

@app.route('/download/<path:filename>')
def download_file(filename):
    """Permite descargar resultados"""
    try:
        # Ruta segura para evitar directory traversal
        safe_path = RESULTS_DIR / filename
        
        if not safe_path.exists():
            return jsonify({"error": f"El archivo no existe: {filename}"}), 404
        
        if safe_path.is_dir():
            # Si es un directorio, comprimirlo primero
            zip_path = RESULTS_DIR / f"{filename}.zip"
            subprocess.run(['zip', '-r', str(zip_path), str(safe_path)], check=True)
            return send_file(zip_path, as_attachment=True)
        
        return send_file(safe_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({"error": f"Error al descargar: {str(e)}"}), 500

if __name__ == '__main__':
    print(f"🚀 Iniciando Neurobit API en http://0.0.0.0:5000")
    print(f"📁 Directorio base: {BASE_DIR}")
    print(f"📤 Directorio uploads: {UPLOADS_DIR}")
    print(f"📥 Directorio results: {RESULTS_DIR}")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)


@app.route('/service-status')
def service_status():
    """Verifica el estado del servicio systemd"""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', 'neurobit-api.service'],
            capture_output=True,
            text=True
        )
        return jsonify({
            'active': result.stdout.strip() == 'active',
            'status': result.stdout.strip()
        })
    except Exception as e:
        return jsonify({
            'active': False,
            'error': str(e)
        })
