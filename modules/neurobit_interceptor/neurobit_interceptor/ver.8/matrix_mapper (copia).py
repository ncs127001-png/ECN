class MatrixMapper:
    def __init__(self, target_size=13):
        self.target_size = target_size
        self.base_threshold = 0.3
    
    def remap_to_matrix(self, bitmap, orig_w, orig_h, center=True):
        """Muestreo con centrado inteligente y umbral adaptativo"""
        target_matrix = [[0 for _ in range(self.target_size)] for _ in range(self.target_size)]
        
        # Calcular ratio de muestreo
        sample_ratio = max(orig_w, orig_h) / self.target_size
        
        # Umbral adaptativo según ratio
        if sample_ratio < 0.8:
            threshold = 0.1  # Expansión: ser permisivo
        elif sample_ratio > 1.5:
            threshold = 0.5  # Contracción: ser estricto
        else:
            threshold = self.base_threshold  # Correspondencia 1:1
        
        # Calcular offset para centrado
        offset_x = 0
        offset_y = 0
        
        if center:
            scale = min(self.target_size / orig_w, self.target_size / orig_h)
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)
            offset_x = (self.target_size - new_w) // 2
            offset_y = (self.target_size - new_h) // 2
        else:
            new_w, new_h = orig_w, orig_h
        
        block_w = orig_w / new_w if new_w > 0 else 1
        block_h = orig_h / new_h if new_h > 0 else 1
        
        for ty in range(self.target_size):
            for tx in range(self.target_size):
                src_tx = tx - offset_x
                src_ty = ty - offset_y
                
                if 0 <= src_tx < new_w and 0 <= src_ty < new_h:
                    x_start = int(src_tx * block_w)
                    y_start = int(src_ty * block_h)
                    x_end = int((src_tx + 1) * block_w)
                    y_end = int((src_ty + 1) * block_h)
                    
                    active_pixels = 0
                    total_pixels = 0
                    
                    for y in range(y_start, min(y_end, orig_h)):
                        for x in range(x_start, min(x_end, orig_w)):
                            if 0 <= y < len(bitmap) and 0 <= x < len(bitmap[0]):
                                active_pixels += bitmap[y][x]
                                total_pixels += 1
                    
                    if total_pixels > 0 and (active_pixels / total_pixels) > threshold:
                        target_matrix[ty][tx] = 1
        
        return target_matrix
