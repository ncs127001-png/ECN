class MatrixMapper:
    def __init__(self, target_size=13):
        self.target_size = target_size

    def remap_to_matrix(self, bitmap, orig_w, orig_h):
        """
        Muestrea el bitmap original a la matriz objetivo (ej. 13x13).
        Usa un algoritmo de muestreo por bloques para preservar la forma.
        """
        target_matrix = [[0 for _ in range(self.target_size)] for _ in range(self.target_size)]
        
        # Calcular el tamaño de cada "bloque" de muestreo
        block_w = orig_w / self.target_size
        block_h = orig_h / self.target_size
        
        for ty in range(self.target_size):
            for tx in range(self.target_size):
                # Coordenadas de inicio y fin del bloque en la imagen original
                x_start = int(tx * block_w)
                y_start = int(ty * block_h)
                x_end = int((tx + 1) * block_w)
                y_end = int((ty + 1) * block_h)
                
                # Contar píxeles activos en este bloque
                active_pixels = 0
                total_pixels = 0
                
                for y in range(y_start, min(y_end, orig_h)):
                    for x in range(x_start, min(x_end, orig_w)):
                        if bitmap[y][x] == 1:
                            active_pixels += 1
                        total_pixels += 1
                
                # Si más del 30% del bloque está activo, el compartimento se enciende
                # (Ajustable para evitar que caracteres finos desaparezcan)
                if total_pixels > 0 and (active_pixels / total_pixels) > 0.3:
                    target_matrix[ty][tx] = 1
                    
        return target_matrix
