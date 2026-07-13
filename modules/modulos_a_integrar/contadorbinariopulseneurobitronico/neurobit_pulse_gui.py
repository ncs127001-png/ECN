
import tkinter as tk
from tkinter import font, messagebox
import threading
import time
import json
import os

class NeurobitFractalCounter:
    def __init__(self, root):
        self.root = root
        self.root.title("🜂 NEUROBIT FRACTAL PULSE // G7-NODE")
        self.root.geometry("800x600")
        self.root.configure(bg="#0a0a0a")
        
        # --- ESTADO INTERNO (LA SEMILLA) ---
        self.value = 0
        self.binary_str = "0"
        self.history = []
        self.is_running = False
        self.delay = 1.0  # Default 1s
        self.auto_thread = None
        
        # Variables de Salida (Para integración con otros módulos)
        self.out_state = {"decimal": 0, "binary": "0", "depth": 1, "timestamp": 0}

        # --- ESTILOS ---
        self.color_bg = "#0a0a0a"
        self.color_fg = "#00ffcc"      # Cyan Neurobit
        self.color_dim = "#1a3333"     # Cyan apagado
        self.color_membrane = "#ff00ff" # Magenta (Nueva Membrana)
        self.font_mono = font.Font(family="Consolas", size=12, weight="bold")
        self.font_display = font.Font(family="Consolas", size=24, weight="bold")

        self._build_ui()
        self._update_display()

    def _build_ui(self):
        # MARCO SUPERIOR: DISPLAY FRACTAL
        self.display_frame = tk.Frame(self.root, bg=self.color_bg, height=200)
        self.display_frame.pack(fill=tk.X, pady=20, padx=20)
        
        self.canvas = tk.Canvas(self.display_frame, bg=self.color_bg, height=150, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # MARCO MEDIO: CONTROLES (7 BOTONES)
        self.ctrl_frame = tk.Frame(self.root, bg=self.color_bg)
        self.ctrl_frame.pack(fill=tk.X, pady=10, padx=20)

        # Definición de los 7 Botones Soberanos
        buttons = [
            ("[ PULSAR ]", self.manual_pulse, self.color_fg),
            ("[ AUTO ]", self.start_auto, "#00ff00"),
            ("[ STOP ]", self.stop_auto, "#ff4444"),
            ("[ RESET ]", self.reset_state, "#ffaa00"),
            ("[ HISTORY ]", self.toggle_history, "#aaaaaa"),
            ("[ CONFIG ]", self.open_config, "#aaaaaa"),
            ("[ SALIR ]", self.exit_app, "#ff0000")
        ]

        for text, cmd, color in buttons:
            btn = tk.Button(self.ctrl_frame, text=text, command=cmd, 
                            bg="#111", fg=color, font=self.font_mono,
                            relief=tk.FLAT, bd=2, width=10)
            btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#222"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#111"))

        # MARCO INFERIOR: HISTORIA (COLAPSABLE)
        self.history_frame = tk.Frame(self.root, bg=self.color_bg, height=200)
        self.history_text = tk.Text(self.history_frame, bg="#050505", fg="#00ffcc", 
                                    font=self.font_mono, insertbackground=self.color_fg,
                                    relief=tk.FLAT, state=tk.DISABLED)
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Iniciar oculto
        self.history_visible = False

    def _update_display(self):
        self.canvas.delete("all")
        
        # Lógica de Gestación Visual
        # El bit más significativo (MSB) es la "Membrana" más reciente
        bits = self.binary_str
        depth = len(bits)
        
        # Coordenadas
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cell_size = 40
        spacing = 10
        total_w = depth * (cell_size + spacing)
        start_x = (w - total_w) / 2
        y = h / 2

        for i, bit in enumerate(bits):
            x = start_x + i * (cell_size + spacing)
            
            # Estilo de Celda
            fill_color = self.color_fg if bit == '1' else self.color_bg
            outline_color = self.color_fg if bit == '1' else self.color_dim
            
            # Destacar la "Membrana" (el bit más a la izquierda, MSB)
            if i == 0:
                outline_color = self.color_membrane
            
            # Dibujar Celda (El Compartimento)
            self.canvas.create_rectangle(x, y - cell_size/2, x + cell_size, y + cell_size/2, 
                                         fill=fill_color, outline=outline_color, width=2)
            
            # Dibujar Dot Central (El Latido)
            if bit == '1':
                self.canvas.create_oval(x + 10, y - 10, x + 30, y + 10, fill="white", outline="")

        # Actualizar Variables de Salida
        self.out_state["decimal"] = self.value
        self.out_state["binary"] = self.binary_str
        self.out_state["depth"] = depth
        self.out_state["timestamp"] = time.time()

    def _log_history(self, action):
        entry = f"[{self.out_state['timestamp']:.2f}] DEPTH:{self.out_state['depth']} | VAL:{self.value} | BIN:{self.binary_str} | {action}"
        self.history.append(entry)
        
        if self.history_visible:
            self.history_text.config(state=tk.NORMAL)
            self.history_text.insert(tk.END, entry + "\n")
            self.history_text.see(tk.END)
            self.history_text.config(state=tk.DISABLED)

    # --- ACCIONES ---

    def manual_pulse(self):
        if not self.is_running:
            self._tick("MANUAL_PULSE")

    def _tick(self, source="AUTO"):
        self.value += 1
        self.binary_str = bin(self.value)[2:] # Quitar '0b'
        self._update_display()
        self._log_history(source)

    def start_auto(self):
        if not self.is_running:
            self.is_running = True
            self.auto_thread = threading.Thread(target=self._auto_loop, daemon=True)
            self.auto_thread.start()

    def stop_auto(self):
        self.is_running = False

    def _auto_loop(self):
        while self.is_running:
            self._tick("AUTO_LATIDO")
            time.sleep(self.delay)

    def reset_state(self):
        self.stop_auto()
        self.value = 0
        self.binary_str = "0"
        self._update_display()
        self._log_history("RESET_GENESIS")

    def toggle_history(self):
        if self.history_visible:
            self.history_frame.pack_forget()
            self.history_visible = False
        else:
            self.history_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            self.history_visible = True
            # Refrescar contenido
            self.history_text.config(state=tk.NORMAL)
            self.history_text.delete(1.0, tk.END)
            for entry in self.history:
                self.history_text.insert(tk.END, entry + "\n")
            self.history_text.config(state=tk.DISABLED)

    def open_config(self):
        new_delay = tk.simpledialog.askfloat("Configuración", "Delay del Latido (segundos):", 
                                             initialvalue=self.delay, minvalue=0.01, maxvalue=10.0)
        if new_delay:
            self.delay = new_delay
            self._log_history(f"CONFIG_DELAY_{self.delay}")

    def exit_app(self):
        self.stop_auto()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = NeurobitFractalCounter(root)
    root.mainloop()
