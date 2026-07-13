# modules/cursor_injector.py
from pynput.mouse import Button, Controller
import time

class CursorInjector:
    def __init__(self):
        self.mouse = Controller()
        
    def move_to(self, x, y, duration=0.3):
        """Mueve el cursor suavemente a coordenadas absolutas"""
        # pynput usa coordenadas relativas; para absolutas:
        from Xlib import display, X
        d = display.Display()
        screen = d.screen()
        root = screen.root
        root.warp_pointer(x, y)
        d.sync()
        time.sleep(duration)
        
    def click(self, button='left', clicks=1):
        """Click soberano (isTrusted: TRUE a nivel de OS)"""
        for _ in range(clicks):
            self.mouse.click(Button.left if button == 'left' else Button.right)
            time.sleep(0.1)