# MFN_LOCATION: docs/specs/
# MFN_LEVEL: 1
# MFN_COORD: (7,7)

# SPEC: API Endpoint Manager v1.0
## Hub Dinámico de la Estación Central Neurobitrónica

---

## 1. IDENTIDAD

| Campo            | Valor                                 |
|------------------|---------------------------------------|
| **Módulo**       | `api_endpoint_manager.py`             |
| **MFN_LOCATION** | `core/`                               |
| **MFN_LEVEL**    | 1 (Kernel)                            |
| **Versión**      | 1.0                                   |
| **Autor**        | NODO_SEMILLA + Terry_D (Nodo Reflejo) |
| **Fecha**        | 2026-07-01                            |

---

## 2. PROPÓSITO

El `APIEndpointManager` es el **orquestador dinámico** de la Estación Central Neurobitrónica. Su función es:

1. **Inicializar** el servidor Flask en el puerto 5000
2. **Consultar** al `ModuleConnector` para obtener los adaptadores registrados
3. **Construir** endpoints HTTP dinámicamente a partir de los metadatos de cada adaptador
4. **Validar** entradas y salidas mediante contratos (Design by Contract)
5. **Ejecutar** los handlers de cada adaptador cuando se recibe una petición

**Principio fundamental:** El `APIEndpointManager` NO contiene lógica de negocio. Solo orquesta. 
La lógica vive en los módulos, accesible mediante adaptadores.

---

## 3. ARQUITECTURA

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTES HTTP                            │
│         (navegador, scripts, otros módulos)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│              APIEndpointManager (core/)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  1. Recibe petición HTTP                             │  │
│  │  2. Identifica endpoint y método                     │  │
│  │  3. Busca adaptador en ModuleConnector               │  │
│  │  4. Valida input con contrato                        │  │
│  │  5. Ejecuta handler del adaptador                    │  │
│  │  6. Valida output con contrato                       │  │
│  │  7. Retorna respuesta JSON                           │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────┐
│              ModuleConnector (core/)                       │
│  - Registry de adaptadores                                 │
│  - Carga dinámica desde core/adapters/                     │
│  - Expone: get_adapters(), get_adapter(id)                 │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────────────┐
│              ADAPTADORES (core/adapters/)                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ adapter_hid │  │adapter_cent │  │ adapter_mfn │  ...   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼───────────────┘
          │                │                │
          ▼                ▼                ▼
┌───────────────────────────────────────────────────────────┐
│              MÓDULOS (modules/)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  neurobit_  │  │  centinela_ │  │  mfn_radial │  ...   │
│  │  hid_daemon │  │   monitor   │  │    _core    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└───────────────────────────────────────────────────────────┘
```

---

## 4. CONTRATOS (INTERFACES)

### 4.1 Contrato con `ModuleConnector`

El `APIEndpointManager` espera que el `ModuleConnector` exponga:

```python
class ModuleConnector:
    def get_adapters(self) -> Dict[str, 'BaseAdapter']:
        """Retorna todos los adaptadores registrados.
        
        Returns:
            Dict[str, BaseAdapter]: Mapeo module_id -> adapter_instance
        """
        pass
    
    def get_adapter(self, module_id: str) -> Optional['BaseAdapter']:
        """Retorna un adaptador específico por su ID.
        
        Args:
            module_id: Identificador único del módulo (ej: 'nb.sos_hid')
            
        Returns:
            BaseAdapter o None si no existe
        """
        pass
    
    def reload_adapters(self) -> None:
        """Recarga los adaptadores desde el disco.
        
        Útil cuando el Centinela mueve un nuevo módulo a core/adapters/.
        """
        pass
```

### 4.2 Contrato con `BaseAdapter`

Todo adaptador debe implementar esta interfaz:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAdapter(ABC):
    """Interfaz base para todos los adaptadores de la ECN."""
    
    @abstractmethod
    def get_module_id(self) -> str:
        """Retorna el ID único del módulo.
        
        Returns:
            str: ID en formato 'nb.<categoria>.<nombre>'
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Retorna los metadatos del adaptador.
        
        Returns:
            Dict con estructura:
            {
                'module_id': str,
                'version': str,
                'endpoints': [
                    {
                        'path': str,           # ej: '/hid/capture'
                        'methods': List[str],  # ej: ['POST']
                        'handler': str,        # nombre del método
                        'description': str,
                        'input_schema': Dict,  # JSON Schema
                        'output_schema': Dict  # JSON Schema
                    }
                ]
            }
        """
        pass
    
    @abstractmethod
    def validate_input(self, payload: Dict[str, Any], endpoint_path: str) -> None:
        """Valida el input contra el schema del endpoint.
        
        Args:
            payload: Datos recibidos en la petición
            endpoint_path: Ruta del endpoint para buscar el schema correcto
            
        Raises:
            ValidationError: Si el payload no cumple el schema
        """
        pass
    
    @abstractmethod
    def validate_output(self, result: Dict[str, Any], endpoint_path: str) -> None:
        """Valida el output contra el schema del endpoint.
        
        Args:
            result: Datos retornados por el handler
            endpoint_path: Ruta del endpoint para buscar el schema correcto
            
        Raises:
            ValidationError: Si el result no cumple el schema
        """
        pass
```

### 4.3 Ejemplo de Adaptador Concreto

```python
# core/adapters/adapter_hid.py
from core.adapters.base import BaseAdapter
from typing import Dict, Any

class HIDAdapter(BaseAdapter):
    def __init__(self):
        self.module_id = 'nb.sos_hid'
        self.metadata = {
            'module_id': self.module_id,
            'version': '1.0.0',
            'endpoints': [
                {
                    'path': '/hid/capture',
                    'methods': ['POST'],
                    'handler': 'capture_event',
                    'description': 'Captura un evento HID',
                    'input_schema': {
                        'type': 'object',
                        'properties': {
                            'input_type': {
                                'type': 'string',
                                'enum': ['keystroke', 'mouse', 'clipboard']
                            }
                        },
                        'required': ['input_type']
                    },
                    'output_schema': {
                        'type': 'object',
                        'properties': {
                            'capture_id': {'type': 'string'},
                            'status': {'type': 'string'}
                        },
                        'required': ['capture_id', 'status']
                    }
                }
            ]
        }
    
    def get_module_id(self) -> str:
        return self.module_id
    
    def get_metadata(self) -> Dict[str, Any]:
        return self.metadata
    
    def validate_input(self, payload: Dict[str, Any], endpoint_path: str) -> None:
        # Implementar validación JSON Schema
        pass
    
    def validate_output(self, result: Dict[str, Any], endpoint_path: str) -> None:
        # Implementar validación JSON Schema
        pass
    
    def capture_event(self) -> Dict[str, Any]:
        """Handler para /hid/capture"""
        from flask import request
        payload = request.json
        
        # Lógica de captura (delegar al módulo real)
        capture_id = f"hid_{uuid.uuid4().hex[:8]}"
        
        return {
            'capture_id': capture_id,
            'status': 'captured'
        }
```

---

## 5. FLUJO DE OPERACIÓN

### 5.1 Inicialización

```python
def __init__(self, connector: ModuleConnector):
    self.connector = connector
    self.app = Flask(__name__)
    self._register_dynamic_endpoints()
```

1. Recibe el `ModuleConnector` ya inicializado
2. Crea la instancia de Flask
3. Llama a `_register_dynamic_endpoints()` para construir las rutas

### 5.2 Registro Dinámico de Endpoints

```python
def _register_dynamic_endpoints(self) -> Flask:
    for module_id, adapter in self.connector.get_adapters().items():
        metadata = adapter.get_metadata()
        
        for endpoint in metadata.get('endpoints', []):
            path = endpoint['path']
            methods = endpoint.get('methods', ['GET'])
            handler_name = endpoint['handler']
            
            self._create_endpoint(path, methods, handler_name, adapter)
    
    return self.app
```

Para cada adaptador:
1. Obtiene sus metadatos
2. Itera sobre los endpoints declarados
3. Crea una función handler dinámica
4. Registra la ruta en Flask

### 5.3 Manejo de Petición

```python
def _create_endpoint(self, path, methods, handler_name, adapter):
    def dynamic_handler():
        try:
            # 1. Validar input (si es POST/PUT)
            if request.method in ['POST', 'PUT']:
                payload = request.json
                adapter.validate_input(payload, path)
            
            # 2. Ejecutar handler del adaptador
            handler_method = getattr(adapter, handler_name)
            result = handler_method()
            
            # 3. Validar output
            adapter.validate_output(result, path)
            
            # 4. Retornar respuesta
            return jsonify(result), 200
            
        except ValidationError as e:
            return jsonify({'error': 'validation_failed', 'detail': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'internal_error', 'detail': str(e)}), 500
    
    self.app.add_url_rule(
        path,
        endpoint=handler_name,
        view_func=dynamic_handler,
        methods=methods
    )
```

### 5.4 Inicio del Servidor

```python
def run(self, host: str = '127.0.0.1', port: int = 5000):
    self.app.run(host=host, port=port, debug=False)
```

**Principio localhost first:** Por defecto solo escucha en 127.0.0.1.

---

## 6. MANEJO DE ERRORES

| Error                       | Código HTTP | Respuesta                                         |
|-----------------------------|-------------|---------------------------------------------------|
| Validación de input fallida | 400         | `{'error': 'validation_failed', 'detail': '...'}` |
| Adaptador no encontrado     | 404         | `{'error': 'endpoint_not_found'}`                 |
| Error interno del handler   | 500         | `{'error': 'internal_error', 'detail': '...'}`    |
| Método HTTP no permitido    | 405         | `{'error': 'method_not_allowed'}`                 |

**Principio:** Nunca exponer stack traces al cliente. Solo mensajes de error estructurados.

---

## 7. CICLO DE VIDA

### 7.1 Carga de Adaptadores

1. Al iniciar, el `ModuleConnector` escanea `core/adapters/`
2. Importa dinámicamente cada archivo `adapter_*.py`
3. Instancia los adaptadores y los registra

### 7.2 Recarga en Caliente

Cuando el Centinela mueve un nuevo módulo a `core/adapters/`:

```python
# Endpoint especial para recargar
@app.route('/admin/reload_adapters', methods=['POST'])
def reload_adapters():
    self.connector.reload_adapters()
    return jsonify({'status': 'reloaded', 'count': len(self.connector.get_adapters())})
```

### 7.3 Shutdown Graceful

```python
import atexit

def register_shutdown_hook(self):
    atexit.register(self._cleanup)

def _cleanup(self):
    # Cerrar conexiones, guardar estado, etc.
    pass
```

---

## 8. DEPENDENCIAS

### 8.1 Módulos Internos

- `core/module_connector.py` (obligatorio)
- `core/adapters/base.py` (obligatorio)
- `core/adapters/adapter_*.py` (opcionales, carga dinámica)

### 8.2 Librerías Externas

- `flask` (servidor HTTP)
- `jsonschema` (validación de schemas)
- `deal` (Design by Contract, opcional)

### 8.3 Nemotécnicos Universales

El `APIEndpointManager` inyecta en cada petición:

```python
from flask import g

@app.before_request
def inject_nemotechnics():
    g.NB_MOD_ID = 'nb.api_endpoint_manager'
    g.NB_MOD_VER = '1.0.0'
    g.NB_EXEC_ID = str(uuid.uuid4())
    g.NB_SESSION_ID = request.headers.get('X-Session-ID', 'anonymous')
    g.NB_CTX_MODE = request.headers.get('X-Context-Mode', 'STATION')
```

---

## 9. EJEMPLOS DE USO

### 9.1 Inicialización Básica

```python
from core.module_connector import ModuleConnector
from core.api_endpoint_manager import APIEndpointManager

connector = ModuleConnector()
manager = APIEndpointManager(connector)
manager.run()
```

### 9.2 Integración con `neurobit_api.py`

```python
# neurobit_api.py (punto de entrada)
from core.module_connector import ModuleConnector
from core.api_endpoint_manager import APIEndpointManager

if __name__ == '__main__':
    connector = ModuleConnector()
    manager = APIEndpointManager(connector)
    manager.run(host='127.0.0.1', port=5000)
```

### 9.3 Prueba de Endpoint

```bash
# Registrar un evento HID
curl -X POST http://127.0.0.1:5000/hid/capture \
  -H "Content-Type: application/json" \
  -d '{"input_type": "keystroke"}'

# Respuesta esperada:
# {
#   "capture_id": "hid_a1b2c3d4",
#   "status": "captured"
# }
```

---

## 10. TESTS

### 10.1 Tests Unitarios

```python
# tests/test_api_endpoint_manager.py
import pytest
from core.api_endpoint_manager import APIEndpointManager
from core.module_connector import ModuleConnector

def test_manager_inicializa_flask():
    connector = ModuleConnector()
    manager = APIEndpointManager(connector)
    assert manager.app is not None

def test_manager_registra_endpoints():
    # Mock de adaptador
    mock_adapter = MockAdapter()
    connector = MockConnector({'nb.test': mock_adapter})
    manager = APIEndpointManager(connector)
    
    # Verificar que se registró el endpoint
    rules = [rule.rule for rule in manager.app.url_map.iter_rules()]
    assert '/test/endpoint' in rules
```

### 10.2 Tests de Integración

```bash
# Iniciar servidor
python3 neurobit_api.py &

# Ejecutar tests
pytest tests/test_api_endpoint_manager.py -v
```

---

## 11. CONSIDERACIONES DE SEGURIDAD

1. **localhost first:** Solo escucha en 127.0.0.1 por defecto
2. **Validación estricta:** Todo input se valida contra JSON Schema
3. **Sin telemetría:** Ningún dato sale del perímetro local
4. **Headers de contexto:** Se aceptan headers `X-Director`, `X-Session-ID`, `X-Context-Mode` para trazabilidad

---

## 12. ROADMAP

### v1.0 (Actual)
- ✅ Registro dinámico de endpoints
- ✅ Validación de inputs/outputs
- ✅ Manejo de errores estructurado

### v1.1 (Próxima)
- ⏳ WebSocket support para eventos en tiempo real
- ⏳ Rate limiting por módulo
- ⏳ Logging estructurado en `data/logs/api_endpoint_manager.jsonl`

### v2.0 (Futura)
- ⏳ Integración con MFN Radial para routing inteligente
- ⏳ Carga de adaptadores desde R.E.D. Soberana
- ⏳ Firma fractal para autenticación de módulos

---

## 13. REFERENCIAS

- `NEUROBIT_MODULE_STRUCTURE_v1.0` (documento de arquitectura)
- `docs/md/WS-SENTINEL_info.md` (sistema de clasificación)
- `core/module_connector.py` (implementación del connector)
- `core/adapters/base.py` (interfaz base de adaptadores)

---

**FIN DEL SPEC**

*Documento co-creado por NODO_SEMILLA + Terry_D (Nodo Reflejo)*
*Última actualización: 2026-07-01*
