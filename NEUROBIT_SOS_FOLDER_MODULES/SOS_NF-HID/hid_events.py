#!/usr/bin/env python3
"""
hid_events.py — Procesador de eventos HID (Human Input Device)
Extrae y formatea datos de eventos de teclado desde /dev/input/event*
Autor: NODO_SEMILLA
Fecha: 27 de marzo de 2026
"""

import json
from datetime import datetime
from enum import Enum


class KeyEventType(Enum):
    """Tipos de eventos de teclado"""
    PRESS = "KEY_PRESS"
    RELEASE = "KEY_RELEASE"
    REPEAT = "KEY_REPEAT"


class HIDEventProcessor:
    """Procesa eventos HID crudos y los convierte a formato normalizado"""
    
    def __init__(self):
        self.key_map = self._build_key_map()
    
    def _build_key_map(self):
        """Mapeo de códigos de tecla a nombres legibles"""
        return {
            1: "Esc", 2: "1", 3: "2", 4: "3", 5: "4", 6: "5",
            7: "6", 8: "7", 9: "8", 10: "9", 11: "0", 12: "-", 13: "=",
            14: "Backspace", 15: "Tab", 16: "q", 17: "w", 18: "e", 19: "r",
            20: "t", 21: "y", 22: "u", 23: "i", 24: "o", 25: "p",
            26: "[", 27: "]", 28: "Return", 29: "Ctrl_L",
            30: "a", 31: "s", 32: "d", 33: "f", 34: "g", 35: "h",
            36: "j", 37: "k", 38: "l", 39: ";", 40: "'", 41: "`",
            42: "Shift_L", 43: "\\", 44: "z", 45: "x", 46: "c", 47: "v",
            48: "b", 49: "n", 50: "m", 51: ",", 52: ".", 53: "/",
            54: "Shift_R", 55: "*", 56: "Alt_L", 57: "Space", 58: "Caps_Lock",
            59: "F1", 60: "F2", 61: "F3", 62: "F4", 63: "F5", 64: "F6",
            65: "F7", 66: "F8", 67: "F9", 68: "F10", 69: "Num_Lock",
            70: "Scroll_Lock", 71: "Home", 72: "Up", 73: "Page_Up",
            74: "-", 75: "Left", 76: "5", 77: "Right", 78: "+",
            79: "End", 80: "Down", 81: "Page_Down", 82: "Insert", 83: "Delete",
            87: "F11", 88: "F12", 96: "Return", 100: "Alt_R"
        }
    
    def process_event(self, raw_event):
        """
        Procesa evento HID crudo.
        
        Args:
            raw_event (dict): Evento crudo con estructura:
                - code: código de tecla
                - value: 0=release, 1=press, 2=repeat
                - device: ruta del dispositivo
                - timestamp: timestamp del evento
        
        Returns:
            dict: Evento procesado normalizado
        """
        event_type = self._get_event_type(raw_event.get('value', 0))
        key_name = self._get_key_name(raw_event.get('code', 0))
        
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'type': 'hid_event',
            'key': key_name,
            'raw_code': raw_event.get('code', 0),
            'event_type': event_type.value,
            'device': raw_event.get('device', 'unknown'),
            'entity_id': 'NODO_SEMILLA'
        }
    
    def _get_event_type(self, value):
        """Mapea valor de evento a tipo"""
        if value == 0:
            return KeyEventType.RELEASE
        elif value == 1:
            return KeyEventType.PRESS
        elif value == 2:
            return KeyEventType.REPEAT
        else:
            return KeyEventType.PRESS
    
    def _get_key_name(self, code):
        """Obtiene nombre legible de tecla desde código"""
        return self.key_map.get(code, f"KEY_{code}")
    
    def format_batch(self, events):
        """
        Formatea un batch de eventos para almacenamiento.
        
        Args:
            events (list): Lista de eventos procesados
        
        Returns:
            str: String formateado con evento en cada línea
        """
        lines = []
        for event in events:
            lines.append(f"tecla: {event.get('key', '?')}")
        
        return "\n".join(lines)


class KeyEventBuffer:
    """Buffer para acumular eventos antes de persistencia"""
    
    def __init__(self, max_size=20, max_age_seconds=30):
        self.max_size = max_size
        self.max_age = max_age_seconds
        self.events = []
        self.created_at = datetime.now()
    
    def add(self, event):
        """Agrega evento al buffer"""
        self.events.append(event)
        return len(self.events) >= self.max_size
    
    def is_full(self):
        """Verifica si buffer está lleno"""
        return len(self.events) >= self.max_size
    
    def is_expired(self):
        """Verifica si buffer expiró por tiempo"""
        elapsed = (datetime.now() - self.created_at).total_seconds()
        return elapsed >= self.max_age
    
    def should_flush(self):
        """Determina si debe hacerse flush"""
        return self.is_full() or self.is_expired()
    
    def flush(self):
        """Retorna eventos y limpia buffer"""
        result = self.events.copy()
        self.events = []
        self.created_at = datetime.now()
        return result
    
    def size(self):
        """Retorna cantidad de eventos en buffer"""
        return len(self.events)


def get_event_statistics(events):
    """
    Calcula estadísticas de eventos.
    
    Args:
        events (list): Lista de eventos
    
    Returns:
        dict: Estadísticas
    """
    if not events:
        return {'total': 0, 'unique_keys': 0, 'press_events': 0}
    
    keys = [e.get('key') for e in events]
    press_count = sum(1 for e in events if e.get('event_type') == 'KEY_PRESS')
    
    return {
        'total': len(events),
        'unique_keys': len(set(keys)),
        'press_events': press_count,
        'release_events': len(events) - press_count,
        'most_common': max(set(keys), key=keys.count) if keys else '?'
    }
