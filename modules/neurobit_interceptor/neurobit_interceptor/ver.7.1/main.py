import tkinter as tk
from bitmap_extractor import BitmapExtractor
from matrix_mapper import MatrixMapper
from matrix_editor_gui import MatrixEditorGUI
from charset_navigator import CharsetNavigator
from state_persistence import StatePersistence

class NeurobitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Neurobit System")
        self.root.geometry("450x300")
        self.root.configure(bg="#111111")
        
        # Módulos core (font_size óptimo = 13)
        self.current_font_size = 13  # ← CAMBIADO: 24 → 13
        self.extractor = BitmapExtractor(font_size=self.current_font_size)
        self.mapper = MatrixMapper(target_size=13)
        self.persistence = StatePersistence()
        
        # Editor GUI (ventana separada)
        self.editor_root = tk.Toplevel(root)
        self.editor = MatrixEditorGUI(self.editor_root, 13)
        
        # Selector de modo
        self.mode_frame = tk.Frame(self.root, bg="#111111")
        self.mode_frame.pack(pady=20)
        
        tk.Button(self.mode_frame, text="📝 Navegar Texto", 
                  command=self.start_text_mode,
                  bg="#004444", fg="#00ffcc", font=("Consolas", 14),
                  width=20).pack(pady=5)
        
        tk.Button(self.mode_frame, text="🔤 Navegar Charset", 
                  command=self.start_charset_mode,
                  bg="#004444", fg="#00ffcc", font=("Consolas", 14),
                  width=20).pack(pady=5)
        
        tk.Button(self.mode_frame, text="💾 Ver Estados Guardados", 
                  command=self.show_saved_states,
                  bg="#004444", fg="#00ffcc", font=("Consolas", 14),
                  width=20).pack(pady=5)
        
        # Control de Font Size
        self.font_frame = tk.Frame(self.root, bg="#111111")
        self.font_frame.pack(pady=10)
        
        tk.Label(self.font_frame, text="Font Size:", 
                font=("Consolas", 12), fg="#00ffcc", bg="#111111").pack(side=tk.LEFT, padx=10)
        
        self.font_var = tk.IntVar(value=self.current_font_size)
        self.font_slider = tk.Scale(self.font_frame, from_=8, to=128, 
                                    orient=tk.HORIZONTAL, 
                                    variable=self.font_var,
                                    command=self.update_font_size,
                                    bg="#111111", fg="#00ffcc",
                                    troughcolor="#222222",
                                    highlightthickness=0)
        self.font_slider.pack(side=tk.LEFT, padx=10)
        
        self.font_label = tk.Label(self.font_frame, text=f"{self.current_font_size}px", 
                                   font=("Consolas", 12), fg="white", bg="#111111")
        self.font_label.pack(side=tk.LEFT, padx=10)
        
        # Bindings para control por teclado
        self.root.bind("<Up>", lambda e: self.adjust_font_size(1))
        self.root.bind("<Down>", lambda e: self.adjust_font_size(-1))
        
    def adjust_font_size(self, delta):
        """Ajusta font_size con delta"""
        new_size = self.current_font_size + delta
        if new_size < 8:
            new_size = 8
        elif new_size > 128:
            new_size = 128
        
        self.current_font_size = new_size
        self.extractor.font_size = self.current_font_size
        self.font_var.set(self.current_font_size)
        self.font_label.config(text=f"{self.current_font_size}px")
        print(f"🔤 Font size ajustado a: {self.current_font_size}px")
    
    def update_font_size(self, value):
        """Actualiza font_size desde slider"""
        self.current_font_size = int(value)
        self.extractor.font_size = self.current_font_size
        self.font_label.config(text=f"{self.current_font_size}px")
        print(f"🔤 Font size actualizado a: {self.current_font_size}px")
        
    def start_text_mode(self):
        try:
            from text_navigator import TextNavigator
            self.text_nav_root = tk.Toplevel(self.root)
            TextNavigator(self.text_nav_root, self.extractor, self.mapper, self.editor, self.persistence)
        except ImportError:
            print("⚠️  text_navigator.py no existe")
            
    def start_charset_mode(self):
        self.charset_nav_root = tk.Toplevel(self.root)
        CharsetNavigator(self.charset_nav_root, self.extractor, self.mapper, self.editor, self.persistence)
        
    def show_saved_states(self):
        states = self.persistence.get_all_states()
        print(f"\n📊 Estados guardados: {len(states)}")
        for code, data in states.items():
            active_bits = sum(sum(row) for row in data['matrix'])
            print(f"  '{data['char']}' (Code {data['code']}): {active_bits} bits activos")
        print()

if __name__ == "__main__":
    root = tk.Tk()
    app = NeurobitApp(root)
    root.mainloop()
