from PIL import Image, ImageDraw, ImageFont

class BitmapExtractor:
    def __init__(self, font_path=None, font_size=13):  # ← CAMBIADO: 24 → 13
        self.font_size = font_size
        try:
            self.font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
        except IOError:
            self.font = ImageFont.load_default()
    
    def get_char_bitmap(self, char, target_resolution=None):
        """
        Extrae bitmap del carácter. Si target_resolution es None, usa font_size.
        """
        if target_resolution is None:
            target_resolution = (self.font_size, self.font_size)
        
        # Crear lienzo
        img = Image.new('L', target_resolution, color=0)
        draw = ImageDraw.Draw(img)
        
        # Dibujar carácter centrado
        draw.text((0, 0), char, font=self.font, fill=255)
        
        # Convertir a matriz binaria
        width, height = target_resolution
        bitmap = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = img.getpixel((x, y))
                row.append(1 if pixel > 128 else 0)
            bitmap.append(row)
        
        return bitmap, width, height
    
    def get_char_bitmap_adaptive(self, char, target_resolution=(16, 16)):
        """Versión adaptativa para diferentes resoluciones"""
        return self.get_char_bitmap(char, target_resolution)
