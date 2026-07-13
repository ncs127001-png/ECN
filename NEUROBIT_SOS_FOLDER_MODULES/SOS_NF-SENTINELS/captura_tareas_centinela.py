#!/usr/bin/env python3
"""
captura_tareas_centinela.py
Monitor de clipboard que detecta tags [add_tarea]{texto}
y las loggea a un archivo de registro para GUI de tareas.

PATRÓN: [add_tarea]{aqui va el texto de la tarea}

Uso:
    python3 modules/captura_tareas_centinela.py

Ejemplo de uso:
    1. Copiar texto: "Revisar [add_tarea]{errores de Central Station} en código"
    2. El monitor detecta y registra automáticamente
    3. Ver log: tail -f data/tareas_pendientes.jsonl

Archivo de salida:
    ~/WORKSPACE_NEUROBIT_V0.2/data/tareas_pendientes.jsonl
    (Append-only JSONL, una línea por tarea)
"""

import pyperclip
import time
import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import sys


class CapturaTareasCentinela:
    """Monitor de clipboard centinela para captura de tareas."""
    
    def __init__(self, log_file: str = "data/tareas_pendientes.jsonl", check_interval: int = 2):
        """
        Inicializar centinela de tareas.
        
        Args:
            log_file: Ruta al archivo JSONL de tareas
            check_interval: Segundos entre checks de clipboard
        """
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.check_interval = check_interval
        self.last_clipboard = ""
        self.running = False
        
        # Patrón para detectar [add_tarea]{texto}
        # Soporta variaciones: [add_tarea], [ADD_TAREA], [Agregar Tarea], etc.
        self.pattern = r'\[add[_\s]?tarea\]\{([^}]+)\}'
        
        # Estadísticas
        self.stats = {
            'tareas_detectadas': 0,
            'tareas_registradas': 0,
            'errores': 0,
            'inicio': datetime.now().isoformat()
        }
    
    def extract_tareas(self, text: str) -> List[str]:
        """
        Extrae todas las tareas del texto con tags [add_tarea]{...}.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de textos de tareas encontradas
        """
        matches = re.findall(self.pattern, text, re.IGNORECASE)
        return [match.strip() for match in matches if match.strip()]
    
    def log_tarea(self, tarea_text: str) -> Optional[Dict]:
        """
        Guarda tarea en archivo JSONL (append-only).
        
        Args:
            tarea_text: Texto de la tarea
            
        Returns:
            Diccionario del registro guardado o None si error
        """
        try:
            registro = {
                'id': f"tarea_{datetime.now().strftime('%Y%m%d_%H%M%S')}_centinela",
                'texto': tarea_text,
                'timestamp': datetime.now().isoformat(),
                'estado': 'pendiente',
                'fuente': 'centinela_clipboard',
                'prioridad': 'normal'
            }
            
            with self.log_file.open('a', encoding='utf-8') as f:
                f.write(json.dumps(registro, ensure_ascii=False) + '\n')
            
            self.stats['tareas_registradas'] += 1
            
            # Log en consola
            timestamp_short = datetime.now().strftime('%H:%M:%S')
            print(f"  [{timestamp_short}] ✅ Tarea registrada: {tarea_text[:50]}...")
            
            return registro
            
        except Exception as e:
            self.stats['errores'] += 1
            print(f"  ❌ Error guardando tarea: {e}")
            return None
    
    def monitor(self) -> None:
        """
        Monitor continuo del clipboard buscando tareas.
        Ejecuta hasta Ctrl+C.
        """
        print("\n" + "="*70)
        print("👁  CENTINELA DE TAREAS INICIADO")
        print("="*70)
        print(f"📝  Log file: {self.log_file.absolute()}")
        print(f"🔍  Patrón: [add_tarea]{{texto}}")
        print(f"⏱  Check interval: {self.check_interval} segundos")
        print("🛑  Presiona Ctrl+C para detener\n")
        
        self.running = True
        
        try:
            while self.running:
                try:
                    current = pyperclip.paste()
                    
                    # Solo procesar si cambió el clipboard
                    if current != self.last_clipboard:
                        self.last_clipboard = current
                        
                        # Extraer tareas
                        tareas = self.extract_tareas(current)
                        
                        if tareas:
                            self.stats['tareas_detectadas'] += len(tareas)
                            
                            for tarea in tareas:
                                self.log_tarea(tarea)
                    
                    time.sleep(self.check_interval)
                    
                except KeyboardInterrupt:
                    raise  # Re-raise para handler principal
                except pyperclip.PyperclipException as e:
                    # pyperclip falla en algunos entornos
                    print(f"❌ Error de clipboard: {e}")
                    print("   Nota: pyperclip requiere xclip/xsel en Linux")
                    time.sleep(self.check_interval)
                except Exception as e:
                    print(f"❌ Error inesperado: {e}")
                    time.sleep(self.check_interval)
                    
        except KeyboardInterrupt:
            self._show_stats()
    
    def _show_stats(self) -> None:
        """Mostrar estadísticas finales."""
        self.running = False
        print("\n" + "="*70)
        print("📊 ESTADÍSTICAS FINALES")
        print("="*70)
        print(f"  Tareas detectadas:  {self.stats['tareas_detectadas']}")
        print(f"  Tareas registradas: {self.stats['tareas_registradas']}")
        print(f"  Errores:            {self.stats['errores']}")
        print(f"  Inicio:             {self.stats['inicio']}")
        print(f"  Fin:                {datetime.now().isoformat()}")
        print("="*70)
        print("✅ Centinela finalizado correctamente\n")
    
    def stop(self) -> None:
        """Detener monitor."""
        self.running = False


def main():
    """Función principal."""
    try:
        # Verificar si pyperclip está disponible
        try:
            import pyperclip
        except ImportError:
            print("❌ ERROR: pyperclip no está instalado")
            print("   Instala con: pip install pyperclip")
            sys.exit(1)
        
        # Crear centinela
        centinela = CapturaTareasCentinela(
            log_file="data/tareas_pendientes.jsonl",
            check_interval=2
        )
        
        # Iniciar monitor (bloqueante hasta Ctrl+C)
        centinela.monitor()
        
    except KeyboardInterrupt:
        print("\n🛑 Centinela detenido por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
