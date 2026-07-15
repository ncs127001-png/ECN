import tkinter as tk
from PIL import ImageGrab, Image
import subprocess

class ScreenSectorCapture:
    def __init__(self, target_size=13):
        self.target_size = target_size
        self.cell_size = 40  # Tamaño visual de cada celda en la GUI
        
    def capture_window_sector(self, window_title, x_offset=0, y_offset=0, 
                               width=200, height=200):
        """
        Captura un sector de una ventana específica
        """
        # Obtener geometría de la ventana usando xdotool
        try:
            result = subprocess.run(
                ['xdotool', 'search', '--name', window_title],
                capture_output=True, text=True
            )
            window_id = result.stdout.strip().split('\n')[0]
            
            result = subprocess.run(
                ['xdotool', 'getwindowgeometry', window_id],
                capture_output=True, text=True
            )
            # Parsear output: "Position: 100,200 (screen: 0)"
            lines = result.stdout.split('\n')
            pos_line = [l for l in lines if 'Position' in l][0]
            coords = pos_line.split(':')[1].strip().split('(')[0].strip()
            win_x, win_y = map(int, coords.split(','))
            
            # Calcular coordenadas del sector
            sector_x = win_x + x_offset
            sector_y = win_y + y_offset
            
            # Capturar sector
            screenshot = ImageGrab.grab(bbox=(
                sector_x, sector_y,
                sector_x + width, sector_y + height
            ))
            
            return screenshot
            
        except Exception as e:
            print(f"❌ Error capturando sector: {e}")
            return None
    
    def sample_sector_to_matrix(self, image, threshold=128):
        """
        Muestrea una imagen a matriz 13x13
        threshold: valor de gris (0-255) para considerar "activo"
        """
        if image is None:
            return None
        
        # Redimensionar a 13x13 para muestreo directo
        resized = image.resize((self.target_size, self.target_size), Image.LANCZOS)
        
        # Convertir a escala de grises
        gray = resized.convert('L')
        
        # Muestrear cada celda
        matrix = []
        for y in range(self.target_size):
            row = []
            for x in range(self.target_size):
                pixel = gray.getpixel((x, y))
                # Invertir: píxel oscuro = activo (1)
                row.append(1 if pixel < threshold else 0)
            matrix.append(row)
        
        return matrix
    
    def capture_char_from_screen(self, window_title, char_position=(0, 0),
                                  char_width=20, char_height=20):
        """
        Captura un carácter específico en una ventana
        char_position: (col, row) en la cuadrícula de la ventana
        """
        x_offset = char_position[0] * char_width
        y_offset = char_position[1] * char_height
        
        screenshot = self.capture_window_sector(
            window_title, x_offset, y_offset, char_width, char_height
        )
        
        if screenshot:
            return self.sample_sector_to_matrix(screenshot)
        return None
