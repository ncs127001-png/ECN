# modules/neurobit_postman_daemon.py
"""
NEUROBIT POSTMAN — Cartero Consciente
Pasa cada 8 horas, recoge, clasifica, entrega
NO depende de servidores centrales
Integrado con EventDispatcher vía /dispatch/queue
"""

import schedule
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

class NeurobitPostman:
    def __init__(self, dispatcher_url="http://127.0.0.1:5000/dispatch/queue"):
        self.workspace = Path.home() / 'WORKSPACE_NEUROBIT_V0.2'
        self.bbs_dir = self.workspace / 'data' / 'bbs'
        self.sala_dir = self.workspace / 'data' / 'sala'
        self.archivos_dir = self.workspace / 'data' / 'archivos'
        
        # Dispatcher integration
        self.dispatcher_url = dispatcher_url if REQUESTS_AVAILABLE else None
        
        # Clasificación por PROPÓSITO (Logos)
        self.clasificacion = {
            'informes': self.bbs_dir / 'informes',
            'arquitectura': self.bbs_dir / 'arquitectura',
            'soluciones_8bit': self.bbs_dir / 'soluciones_8bit',
            'estado_equipo': self.sala_dir / 'estado',
            'discusiones': self.bbs_dir / 'discusiones',
        }
    
    def pasar(self):
        """El Cartero pasa, pregunta, recoge, entrega"""
        print(f"📬 POSTMAN — {datetime.now().isoformat()}")
        print("¿Hola, necesitas enviar algo al equipo?")
        
        # 1. Recoger mensajes pendientes
        pendientes = self.recoger_pendientes()
        
        # 2. Clasificar por propósito
        for mensaje in pendientes:
            destino = self.clasificar(mensaje)
            self.entregar(mensaje, destino)
        
        # 3. Reportar estado del equipo
        self.reportar_estado()
    
    def clasificar(self, mensaje):
        """Clasifica por PROPÓSITO, no por usuario"""
        contenido = mensaje.get('content', '').lower()
        
        if 'informe' in contenido or 'reporte' in contenido:
            return self.clasificacion['informes']
        elif 'arquitectura' in contenido:
            return self.clasificacion['arquitectura']
        elif '8-bit' in contenido or 'retro' in contenido:
            return self.clasificacion['soluciones_8bit']
        elif 'estado' in contenido or 'hola' in contenido:
            return self.clasificacion['estado_equipo']
        else:
            return self.clasificacion['discusiones']
    
    def recoger_pendientes(self):
        """Recoge lo que el NODO_SEMILLA preparó"""
        # Mock: retornar mensajes de prueba
        return [
            {
                'type': 'mensaje',
                'content': 'Informe de estado del sistema',
                'timestamp': datetime.now().isoformat()
            }
        ]
    
    def entregar(self, mensaje, destino):
        """Entrega en destino, guarda copia local + dispatcher"""
        # 1. Enviar al dispatcher si disponible
        if self.dispatcher_url and REQUESTS_AVAILABLE:
            try:
                event = {
                    'type': 'postman_delivery',
                    'content': mensaje.get('content', ''),
                    'destino': str(destino),
                    'timestamp': datetime.now().isoformat(),
                    'source': 'neurobit_postman_daemon'
                }
                
                response = requests.post(
                    self.dispatcher_url,
                    json={'events': [event]},
                    timeout=5
                )
                
                if response.status_code == 200:
                    print(f"✅ Postman → Dispatcher: {mensaje.get('content', '')[:40]}...")
                    return True
            except requests.RequestException as e:
                print(f"⚠️  Dispatcher unavailable ({e}), fallback a archivo local")
        
        # 2. FALLBACK: Guardar localmente (append-only)
        try:
            destino_path = Path(destino)
            destino_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(destino_path, 'a', encoding='utf-8') as f:
                f.write(f"{mensaje}\n")
            
            print(f"✅ Postman → Local: {str(destino_path)}")
            return True
        except Exception as e:
            print(f"❌ Error entregando: {e}")
            return False
    
    def reportar_estado(self):
        """Reporta quién está activo en el Dev_Team"""
        # Crear evento de estado para dispatcher
        event = {
            'type': 'postman_checkpoint',
            'content': 'Cartero paso completado',
            'timestamp': datetime.now().isoformat(),
            'source': 'neurobit_postman_daemon'
        }
        
        if self.dispatcher_url and REQUESTS_AVAILABLE:
            try:
                requests.post(
                    self.dispatcher_url,
                    json={'events': [event]},
                    timeout=5
                )
                print(f"✅ Postman checkpoint enviado al dispatcher")
            except:
                pass

# Programar cada 8 horas
postman = NeurobitPostman()
schedule.every(8).hours.do(postman.pasar)

while True:
    schedule.run_pending()
    time.sleep(60)