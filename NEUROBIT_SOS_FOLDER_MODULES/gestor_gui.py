#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from conector import SOSConector
from adapter_modulo_integrador import SOSAdaptadorModulo

class SOSGestorDeclaraciones(tk.Tk):
    def __init__(self):
        super().__init__()
        self.conector = SOSConector()
        self.adaptador = SOSAdaptadorModulo()
        
        self.title("SOS v0.3 - Mapeador Visual de Arquitectura Core")
        self.geometry("850x650")
        
        self.archivo_actual = None
        self.declaraciones_detectadas = []
        self.inputs_referencias = {}
        
        self.inicializar_interfaz()

    def inicializar_interfaz(self):
        # --- Top Panel ---
        panel_top = ttk.LabelFrame(self, text=" Control de Arquitectura SOS ", padding=10)
        panel_top.pack(fill="x", padx=15, pady=10)
        
        self.lbl_archivo = ttk.Label(panel_top, text="Ningún módulo cargado para análisis.", font=("Courier", 10, "italic"))
        self.lbl_archivo.pack(side="left", padx=5)
        
        btn_cargar = ttk.Button(panel_top, text="Examinar Módulo", command=self.cargar_archivo_modulo)
        btn_cargar.pack(side="right", padx=5)

        # --- Matriz Central ---
        contenedor_canvas = tk.Frame(self, bd=1, relief="sunken")
        contenedor_canvas.pack(fill="both", expand=True, padx=15, pady=5)
        
        self.canvas = tk.Canvas(contenedor_canvas, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(contenedor_canvas, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # --- Trazabilidad Log (Bottom) ---
        panel_bottom = ttk.LabelFrame(self, text=" Historial Append-Only ", padding=10)
        panel_bottom.pack(fill="x", padx=15, pady=10)
        
        ttk.Label(panel_bottom, text="Comentario de auditoría técnica obligatorio:").pack(anchor="w")
        self.txt_comentario = ttk.Entry(panel_bottom, font=("Helvetica", 10))
        self.txt_comentario.pack(fill="x", pady=5)
        
        self.btn_guardar = ttk.Button(panel_bottom, text="Refactorizar y Guardar Log", command=self.guardar_cambios, state="disabled")
        self.btn_guardar.pack(side="right", pady=5)

    def cargar_archivo_modulo(self):
        # Resuelve dinámicamente tu ruta de la terminal
        ruta_inicial = self.conector.modules_dir if self.conector.modules_dir.exists() else Path.home()
        archivo_sel = filedialog.askopenfilename(
            initialdir=ruta_inicial,
            title="Seleccionar Script SOS",
            filetypes=[("Scripts Python", "*.py"), ("Todos los archivos", "*.*")]
        )
        if not archivo_sel:
            return
            
        self.archivo_actual = Path(archivo_sel)
        self.lbl_archivo.config(text=f"Archivo: {self.archivo_actual.name}")
        self.renderizar_matriz()

    def renderizar_matriz(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()
        self.inputs_referencias.clear()
        
        # Consumir el Adaptador intermedio
        self.declaraciones_detectadas = self.adaptador.reformatear_y_extraer(self.archivo_actual)
        
        if not self.declaraciones_detectadas:
            ttk.Label(self.scrollable_frame, text="No se encontraron variables de riesgo de tipografía.", padding=10).pack()
            self.btn_guardar.config(state="disabled")
            return

        for idx, item in enumerate(self.declaraciones_detectadas):
            # Columna 1: Etiqueta original encontrada
            lbl = ttk.Label(self.scrollable_frame, text=item, font=("Courier", 10, "bold"), width=35, anchor="w")
            lbl.grid(row=idx, column=0, padx=10, pady=4, sticky="w")
            
            # Columna 2: Campo interactivo para corregir typos
            entry = ttk.Entry(self.scrollable_frame, font=("Courier", 10), width=40)
            entry.insert(0, item)
            entry.grid(row=idx, column=1, padx=10, pady=4, sticky="ew")
            
            self.inputs_referencias[item] = entry
            
        self.btn_guardar.config(state="normal")

    def guardar_cambios(self):
        comentario = self.txt_comentario.get().strip()
        if not comentario:
            messagebox.showwarning("Auditoría", "El sistema SOS requiere un comentario explicativo antes de impactar los archivos.")
            return

        mapeo_ui = {orig: widget.get().strip() for orig, widget in self.inputs_referencias.items()}
        reemplazos = self.adaptador.aplicar_refactorizacion_segura(self.archivo_actual, mapeo_ui)

        if reemplazos > 0:
            # Registrar externamente mediante el conector
            self.conector.registrar_trazabilidad(
                modulo=self.archivo_actual.parent.name,
                archivo=self.archivo_actual.name,
                cambio=f"Refactorizados {reemplazos} tokens tipográficos.",
                comentario=comentario
            )
            messagebox.showinfo("Éxito", f"Se aplicaron {reemplazos} cambios. Archivo .bak generado.")
            self.txt_comentario.delete(0, tk.END)
            self.renderizar_matriz()
        else:
            messagebox.showinfo("SOS", "No se detectaron variaciones en las cadenas de la columna 2.")

if __name__ == "__main__":
    app = SOSGestorDeclaraciones()
    app.mainloop()

