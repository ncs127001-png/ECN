#!/usr/bin/env python3
"""
adapter_rebuild_spec.py

NEUROBIT v2.1 - Adapter para Reconstrucción desde Especificación

Función: Exponer ReconstructorFromSpec como módulo integrado en el ecosistema NEUROBIT
Patrón: Spec → Archivos (complementario a adapter_descompilador_extension.py)

Conexiones:
- Entrada: Especificación Markdown (formato de INTEGRATION_PLAN.md)
- Salida: Árbol de archivos reconstruido
- Flujo: Estación Central → compendio_inteligente_v23.py → [opcionalmente] → reconstruir_desde_especificacion.py

Uso como módulo:
    from core.adapters.adapter_rebuild_spec import rebuild_from_specification_file
    
    resultado = rebuild_from_specification_file(
        spec_path="INTEGRATION_PLAN.md",
        project_root="neurobit_reconstructed",
        dry_run=False
    )
    
    if resultado['success']:
        print(f"✅ {resultado['files_created']} archivos reconstruidos")
    else:
        print(f"❌ Errores: {resultado['errors']}")

Principios NEUROBIT:
- Soberanía técnica (cero dependencias corporativas)
- Documentación ejecutable (spec → código bidireccional)
- Integridad (validación de rutas, errores explícitos)
"""

import sys
from pathlib import Path

# Importar el reconstructor desde tools/
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

try:
    from reconstruir_desde_especificacion import ReconstructorFromSpec
except ImportError as e:
    raise ImportError(f"No se pudo importar ReconstructorFromSpec: {str(e)}")


def rebuild_from_specification_file(
    spec_path: str,
    project_root: str = "neurobit_reconstructed",
    dry_run: bool = False,
    verbose: bool = False
) -> dict:
    """
    Reconstruye proyecto desde especificación Markdown.
    
    Args:
        spec_path (str): Ruta al archivo .md con especificación
        project_root (str): Nombre del directorio raíz a crear
        dry_run (bool): Si True, simula sin escribir en disco
        verbose (bool): Si True, muestra detalles
    
    Returns:
        dict: {
            'success': bool,
            'files_created': int,
            'files': [lista de archivos],
            'errors': [lista de errores],
            'warnings': [lista de advertencias],
            'project_root': str
        }
    """
    reconstructor = ReconstructorFromSpec(project_root=project_root)
    
    # Cargar especificación
    if not reconstructor.load_specification(spec_path):
        return {
            'success': False,
            'files_created': 0,
            'files': [],
            'errors': reconstructor.errors,
            'warnings': reconstructor.warnings,
            'project_root': project_root
        }
    
    # Ejecutar reconstrucción
    if dry_run:
        success = True
        files_created = len(reconstructor.file_entries)
    else:
        success = reconstructor.reconstruct()
        files_created = len(reconstructor.file_entries) if success else 0
    
    return {
        'success': success,
        'files_created': files_created,
        'files': [fp for fp, _ in reconstructor.file_entries],
        'errors': reconstructor.errors,
        'warnings': reconstructor.warnings,
        'project_root': str(reconstructor.project_root)
    }


def rebuild_from_specification_envelope(envelope: dict) -> dict:
    """
    Interfaz NEUROBIT: Recibe envelope con especificación y retorna envelope procesado.
    
    Envelope esperado:
    {
        'ORIGEN': 'estacion-central' o 'mcp-server',
        'DESTINO': 'adapter-rebuild-spec',
        'SESSION_TAG': 'sesion_xxx',
        'content': 'ruta/a/especificacion.md',
        'config': {
            'project_root': 'nombre_proyecto',
            'dry_run': False,
            'verbose': False
        }
    }
    
    Retorna envelope enriquecido:
    {
        'ORIGEN': 'adapter-rebuild-spec',
        'DESTINO': 'estacion-central' o 'mcp-server',
        'SESSION_TAG': 'sesion_xxx',
        'content': {resultados},
        'status': 'success' o 'error',
        'TIMESTAMP': ISO8601
    }
    """
    from datetime import datetime
    import hashlib
    
    try:
        spec_path = envelope.get('content')
        config = envelope.get('config', {})
        
        if not spec_path:
            raise ValueError("Envelope debe contener 'content' (ruta a especificación)")
        
        # Ejecutar reconstrucción
        resultado = rebuild_from_specification_file(
            spec_path=spec_path,
            project_root=config.get('project_root', 'neurobit_reconstructed'),
            dry_run=config.get('dry_run', False),
            verbose=config.get('verbose', False)
        )
        
        # Construir envelope de respuesta
        respuesta = {
            'ORIGEN': 'adapter-rebuild-spec',
            'DESTINO': envelope.get('ORIGEN', 'estacion-central'),
            'SESSION_TAG': envelope.get('SESSION_TAG', 'no-session'),
            'TIMESTAMP': datetime.utcnow().isoformat() + 'Z',
            'content': resultado,
            'status': 'success' if resultado['success'] else 'error'
        }
        
        # Calcular MESSAGE_HASH (SHA-1 del content)
        content_str = str(resultado).encode('utf-8')
        respuesta['MESSAGE_HASH'] = hashlib.sha1(content_str).hexdigest()
        
        return respuesta
    
    except Exception as e:
        return {
            'ORIGEN': 'adapter-rebuild-spec',
            'DESTINO': envelope.get('ORIGEN', 'estacion-central'),
            'SESSION_TAG': envelope.get('SESSION_TAG', 'no-session'),
            'TIMESTAMP': datetime.utcnow().isoformat() + 'Z',
            'content': {
                'success': False,
                'error': str(e),
                'files_created': 0
            },
            'status': 'error'
        }


def validate_specification_format(spec_path: str) -> dict:
    """
    Valida que un archivo .md tenga el formato correcto de especificación.
    
    Returns:
        {
            'valid': bool,
            'total_blocks': int,
            'files_detected': int,
            'format_errors': [lista],
            'warnings': [lista]
        }
    """
    import re
    
    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrones a buscar
        pattern_headers = r"##\s+\d+\.\s+"
        pattern_paths = r"\(([^)]+?)\)"
        pattern_blocks = r"```"
        
        headers = re.findall(pattern_headers, content)
        paths = re.findall(pattern_paths, content)
        blocks = re.findall(pattern_blocks, content)
        
        # Validación básica
        errors = []
        if len(blocks) % 2 != 0:
            errors.append("Número impar de bloques ``` detectados (posible código incompleto)")
        
        if len(headers) != len(paths):
            errors.append(f"Mismatch: {len(headers)} encabezados vs {len(paths)} rutas")
        
        return {
            'valid': len(errors) == 0,
            'total_blocks': len(blocks) // 2,
            'files_detected': len(headers),
            'format_errors': errors,
            'warnings': []
        }
    
    except Exception as e:
        return {
            'valid': False,
            'total_blocks': 0,
            'files_detected': 0,
            'format_errors': [f"Error leyendo archivo: {str(e)}"],
            'warnings': []
        }


if __name__ == "__main__":
    # Test básico
    import json
    
    print("🧪 Test de adapter_rebuild_spec.py\n")
    
    # Test 1: Validar formato
    print("Test 1: Validar formato de especificación")
    print("-" * 50)
    validation = validate_specification_format("INTEGRATION_PLAN.md")
    print(json.dumps(validation, indent=2, ensure_ascii=False))
    
    print("\n✅ Adapter cargado correctamente")
    print("📄 Para usar: from core.adapters.adapter_rebuild_spec import rebuild_from_specification_file")
