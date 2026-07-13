# modules/cursor_auditor.py
import evdev
from evdev import ecodes

class CursorAuditor:
    def __init__(self, device_path='/dev/input/event3'):
        self.device = evdev.InputDevice(device_path)
        
    def listen(self, callback):
        """Escucha eventos de mouse en tiempo real"""
        for event in self.device.read_loop():
            if event.type == ecodes.EV_REL:
                if event.code == ecodes.REL_X:
                    callback('move_x', event.value)
                elif event.code == ecodes.REL_Y:
                    callback('move_y', event.value)
            elif event.type == ecodes.EV_KEY:
                if event.code == ecodes.BTN_LEFT:
                    callback('click', 'start' if event.value == 1 else 'end')