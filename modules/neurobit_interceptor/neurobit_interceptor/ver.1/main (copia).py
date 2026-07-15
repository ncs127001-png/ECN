import tkinter as tk
from bitmap_extractor import BitmapExtractor
from matrix_mapper import MatrixMapper
from matrix_editor_gui import MatrixEditorGUI

class NeurobitNavigator:
    def __init__(self, root):
        self.root = root
        self.root.title("Neurobit Text Interceptor")
        self.root.geometry("800x50")
        self.root.configure(bg="#111111")
        
        # Configuración
        self.text_to_analyze = "HOLA MUNDO NEUROBIT" # Texto de prueba
        self.current_index = 0
        self.matrix_size = 13
        
        # Inicializar módulos
        self.extractor = BitmapExtractor(font_size=11) # Tamaño grande para mejor muestreo
        self.mapper = MatrixMapper(target_size=self.matrix_size)
        
        # Inicializar GUI de edición (ventana separada)
        self.editor_root = tk.Toplevel(root)
        self.editor = MatrixEditorGUI(self.editor_root, self.matrix_size)
        
        # UI Principal (Navegación)
        self.label = tk.Label(self.root, text="", font=("Consolas", 20), fg="white", bg="#111111")
        self.label.pack(pady=10)
        
        self.update_display()
        
        # Bindings de teclado
        self.root.bind("<Right>", lambda e: self.move_cursor(1))
        self.root.bind("<Left>", lambda e: self.move_cursor(-1))
        self.root.bind("<Up>", lambda e: self.move_cursor(10)) # Salto rápido
        self.root.bind("<Down>", lambda e: self.move_cursor(-10))

    def move_cursor(self, step):
        self.current_index += step
        if self.current_index < 0:
            self.current_index = 0
        elif self.current_index >= len(self.text_to_analyze):
            self.current_index = len(self.text_to_analyze) - 1
        self.update_display()

    def update_display(self):
        char = self.text_to_analyze[self.current_index]
        
        # Mostrar cursor cuadrado en el texto
        display_text = ""
        for i, c in enumerate(self.text_to_analyze):
            if i == self.current_index:
                display_text += f"[{c}]"
            else:
                display_text += f" {c} "
        self.label.config(text=display_text)
        
        # Procesar y enviar al editor
        bitmap, w, h = self.extractor.get_char_bitmap(char)
        matrix_13x13 = self.mapper.remap_to_matrix(bitmap, w, h)
        self.editor.update_matrix(matrix_13x13, char)

if __name__ == "__main__":
    root = tk.Tk()
    app = NeurobitNavigator(root)
    root.mainloop()
