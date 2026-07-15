import tkinter as tk

class CharsetNavigator:
    def __init__(self, root, extractor, mapper, editor, persistence=None):
        self.root = root
        self.extractor = extractor
        self.mapper = mapper
        self.editor = editor
        self.persistence = persistence
        
        self.charset_range = range(32, 127)
        self.current_index = 0
        
        self.root.title("Neurobit Charset Navigator")
        self.root.geometry("900x150")
        self.root.configure(bg="#111111")
        
        # Frame superior
        self.nav_frame = tk.Frame(self.root, bg="#111111")
        self.nav_frame.pack(fill=tk.X, pady=10)
        
        self.prev_btn = tk.Button(self.nav_frame, text="◀ ANT", 
                                   command=lambda: self.move(-1),
                                   bg="#333", fg="#00ffcc", font=("Consolas", 12))
        self.prev_btn.pack(side=tk.LEFT, padx=20)
        
        self.char_label = tk.Label(self.nav_frame, text="", 
                                    font=("Consolas", 24), fg="white", bg="#111111")
        self.char_label.pack(side=tk.LEFT, expand=True)
        
        self.next_btn = tk.Button(self.nav_frame, text="SIG ▶", 
                                   command=lambda: self.move(1),
                                   bg="#333", fg="#00ffcc", font=("Consolas", 12))
        self.next_btn.pack(side=tk.RIGHT, padx=20)
        
        # Frame inferior
        self.info_frame = tk.Frame(self.root, bg="#111111")
        self.info_frame.pack(fill=tk.X)
        
        self.code_label = tk.Label(self.info_frame, text="", 
                                    font=("Consolas", 10), fg="#888", bg="#111111")
        self.code_label.pack()
        
        self.update_display()
        
        # Bindings
        self.root.bind("<Left>", lambda e: self.move(-1))
        self.root.bind("<Right>", lambda e: self.move(1))
        self.root.bind("<space>", lambda e: self.save_current_state())
        
    def move(self, step):
        self.current_index += step
        if self.current_index < 0:
            self.current_index = len(self.charset_range) - 1
        elif self.current_index >= len(self.charset_range):
            self.current_index = 0
        self.update_display()
        
    def update_display(self):
        char_code = self.charset_range[self.current_index]
        char = chr(char_code)
        
        self.char_label.config(text=f"[{char}]  (Code: {char_code})")
        self.code_label.config(text=f"ASCII: {char_code} | Bin: {bin(char_code)[2:].zfill(8)} | Presiona ESPACIO para guardar")
        
        # Extraer y mapear (CORREGIDO: usa get_char_bitmap sin _adaptive)
        bitmap, w, h = self.extractor.get_char_bitmap(char)
        matrix = self.mapper.remap_to_matrix(bitmap, w, h, center=True)
        self.editor.update_matrix(matrix, char)
        
    def save_current_state(self):
        """Guarda el estado actual de la matriz con font_size"""
        if self.persistence is None:
            print("⚠️  Persistence no disponible")
            return
            
        char_code = self.charset_range[self.current_index]
        char = chr(char_code)
        current_matrix = self.editor.matrix_data
        
        # Obtener font_size actual del extractor
        current_font_size = getattr(self.extractor, 'font_size', 13)
        
        # Guardar con font_size
        self.persistence.save_state(
            char_code, 
            current_matrix,
            font_size=current_font_size  # ← NUEVO
        )
        print(f"💾 Estado de '{char}' guardado exitosamente @ {current_font_size}px")
