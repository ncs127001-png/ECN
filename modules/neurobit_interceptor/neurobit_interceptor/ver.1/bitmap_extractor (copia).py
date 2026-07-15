from PIL import Image, ImageDraw, ImageFont

class BitmapExtractor:
    def __init__(self, font_path=None, font_size=24):
        # Carga la fuente. Si no se pasa, usa la default de PIL
        try:
            self.font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
        except IOError:
            self.font = ImageFont.load_default()
        self.font_size = font_size

    def get_char_bitmap(self, char):
        """
        Renderiza un carácter y devuelve un mapa de bits (lista de listas de 0 y 1).
        """
        # Crear un lienzo pequeño
        img = Image.new('L', (self.font_size, self.font_size), color=0)
        draw = ImageDraw.Draw(img)
        
        # Dibujar el carácter en blanco
        draw.text((0, 0), char, font=self.font, fill=255)
        
        # Convertir a matriz binaria (0 = fondo, 1 = trazo)
        width, height = img.size
        bitmap = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = img.getpixel((x, y))
                # Umbral: si el pixel es mayor a 128, es parte del carácter
                row.append(1 if pixel > 128 else 0)
            bitmap.append(row)
            
        return bitmap, width, height
