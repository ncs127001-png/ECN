import tkinter as tk

class MatrixEditorGUI:
    def __init__(self, root, matrix_size=13):
        self.root = root
        self.matrix_size = matrix_size
        self.matrix_data = [[0]*matrix_size for _ in range(matrix_size)]
        self.cell_size = 40
        self.padding = 20
        
        self.root.title("Neurobit Matrix Editor (13x13)")
        self.root.geometry("600x650")
        self.root.configure(bg="#1a1a1a")
        
        self.canvas = tk.Canvas(self.root, width=600, height=600, bg="#0a0a0a", highlightthickness=0)
        self.canvas.pack(pady=20)
        
        self.info_label = tk.Label(self.root, text="Carácter: -", font=("Consolas", 14), fg="#00ffcc", bg="#1a1a1a")
        self.info_label.pack()

        # Dibujar la cuadrícula inicial
        self.draw_grid()

        # Protocolo de cierre limpio
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Manejar cierre limpio de ventana"""
        self.root.destroy()

    def draw_grid(self):
        self.canvas.delete("all")
        offset = self.padding
        
        for row in range(self.matrix_size):
            for col in range(self.matrix_size):
                x1 = offset + col * self.cell_size
                y1 = offset + row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                color = "#00ffcc" if self.matrix_data[row][col] == 1 else "#222222"
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#444444", width=1)
                self.canvas.bind("<Button-1>", lambda e, r=row, c=col: self.toggle_cell(r, c))

    def toggle_cell(self, row, col):
        """Permite trabajar en la matriz"""
        self.matrix_data[row][col] = 1 - self.matrix_data[row][col]
        self.draw_grid()

    def update_matrix(self, new_matrix, char_display):
        """Carga una nueva matriz desde el extractor"""
        self.matrix_data = new_matrix
        self.info_label.config(text=f"Carácter: '{char_display}' | Matriz {self.matrix_size}x{self.matrix_size}")
        self.draw_grid()
