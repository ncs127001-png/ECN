#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import re
import datetime
from pathlib import Path

class NeurobitCentralStation:
    def __init__(self, root):
        self.root = root
        self.root.title("NEUROBIT CENTRAL STATION v0.1")
        self.root.geometry("800x600")
        
        # Directorios base
        self.base_dir = Path.home() / "neurobit_salon_v0.1"
        self.fragments_dir = self.base_dir / "fragments"
        self.fragments_dir.mkdir(parents=True, exist_ok=True)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Panel superior - Título y estado
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(header, text="🧠 NEUROBIT CENTRAL STATION", 
                 font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        ttk.Label(header, text="LOCALHOST · SOBERANÍA OPERATIVA", 
                 foreground="blue").pack(side=tk.RIGHT)
        
        # Panel izquierdo - Módulos funcionales
        modules_frame = ttk.LabelFrame(self.root, text="MÓDULOS OPERATIVOS")
        modules_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=5, expand=False)
        
        # Botones de módulos (solo referencia por ahora)
        modules = [
            ("📁 Reconstruir Proyecto", self.stub_reconstruir_proyecto),
            ("🔍 Buscar Archivos", self.stub_buscar_archivos),
            ("🌱 Sembrar Memoria", self.stub_seed_memoria),
            ("🧩 Extraer Bloques de Código", self.stub_extraer_bloques),
            ("📚 Compilar Proyecto", self.stub_compilar_proyecto),
            ("✂️ Fragmentar Archivo", self.fragmentar_archivo)
        ]
        
        for text, command in modules:
            btn = ttk.Button(modules_frame, text=text, command=command, width=30)
            btn.pack(pady=5, padx=5, fill=tk.X)
        
        # Panel derecho - Visualización de fragmentos
        fragments_frame = ttk.LabelFrame(self.root, text=f"FRAGMENTOS ({self.fragments_dir})")
        fragments_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Lista de fragmentos existentes
        self.fragments_list = tk.Listbox(fragments_frame, selectmode=tk.EXTENDED)
        self.fragments_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Botón para actualizar lista
        ttk.Button(fragments_frame, text="↻ Actualizar Lista", 
                  command=self.cargar_fragmentos).pack(pady=5, padx=5, fill=tk.X)
        
        # Cargar fragmentos iniciales
        self.cargar_fragmentos()
    
    def stub_module(self, nombre_modulo):
        """Plantilla para módulos futuros - solo muestra información"""
        messagebox.showinfo("MÓDULO EN DESARROLLO", 
                           f"Este botón activará:\n\n{nombre_modulo}\n\n"
                           "En esta versión beta, solo muestra esta referencia.\n"
                           "Implementación completa en próxima iteración soberana.")
    
    # Stubs para módulos futuros
    def stub_reconstruir_proyecto(self):
        self.stub_module("reconstruir_proyecto_desde_compendio.py\n\n"
                        "Función: Reconstruye proyecto completo desde archivo de texto\n"
                        "Entrada: compendio.txt\n"
                        "Salida: Estructura de directorios restaurada")
    
    def stub_buscar_archivos(self):
        self.stub_module("BUSCADOR-EVA.py\n\n"
                        "Función: Busca archivos recursivamente por nombre\n"
                        "Entrada: lista.txt con nombres de archivos\n"
                        "Salida: Archivos recolectados en carpeta destino")
    
    def stub_seed_memoria(self):
        self.stub_module("seed_memoria.py\n\n"
                        "Función: Inicializa memoria sagrada con mensajes semilla\n"
                        "Salida: data/memoria_eva.jsonl actualizado")
    
    def stub_extraer_bloques(self):
        self.stub_module("extract_code_blocks_with_speakers.py\n\n"
                        "Función: Extrae bloques de código de conversaciones\n"
                        "Entrada: archivo.mhtml\n"
                        "Salida: code_snippets/ con atribución por autor")
    
    def stub_compilar_proyecto(self):
        self.stub_module("compile_project.py\n\n"
                        "Función: Compila proyecto completo en documento único\n"
                        "Salida: compendio_proyecto.txt con árbol y contenido")
    
    # Funcionalidad REAL para fragmentación
    def fragmentar_archivo(self):
        """Implementación mínima viable para fragmentar archivos"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo a fragmentar",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
        )
        
        if not archivo:
            return
        
        try:
            max_chars = 5000  # Valor por defecto razonable
            prefijo = "parte_"
            
            # Leer contenido
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Dividir en párrafos
            parrafos = [p.strip() for p in contenido.split('\n\n') if p.strip()]
            
            # Crear fragmentos
            fragmentos = []
            fragmento_actual = ""
            
            for parrafo in parrafos:
                if len(fragmento_actual) + len(parrafo) + 2 <= max_chars:
                    fragmento_actual = fragmento_actual + ("\n\n" if fragmento_actual else "") + parrafo
                else:
                    fragmentos.append(fragmento_actual)
                    fragmento_actual = parrafo
            if fragmento_actual:
                fragmentos.append(fragmento_actual)
            
            # Calcular cantidad de dígitos necesarios (para ceros a la izquierda)
            digitos = len(str(len(fragmentos) + self.siguiente_indice(prefijo)))
            
            # Guardar fragmentos
            start_idx = self.siguiente_indice(prefijo)
            guardados = []
            
            for i, fragmento in enumerate(fragmentos):
                idx = start_idx + i
                # Formato con ceros a la izquierda: parte_01.txt, parte_02.txt, etc.
                nombre_archivo = f"{prefijo}{idx:0{digitos}d}.txt"
                ruta_completa = self.fragments_dir / nombre_archivo
                
                # Crear header mínimo
                header = (f"[FRAGMENT_ID]: {idx}\n"
                         f"[SOURCE]: {os.path.basename(archivo)}\n"
                         f"[CONTENT]:\n")
                
                with open(ruta_completa, 'w', encoding='utf-8') as f:
                    f.write(header + "\n" + fragmento)
                
                guardados.append(nombre_archivo)
            
            # Generar archivos de estado para la extensión
            self.generar_archivos_estado(guardados)
            
            # Generar listado estilo consola
            self.mostrar_listado_fragmentos(guardados)
            
            messagebox.showinfo("✅ FRAGMENTACIÓN COMPLETADA", 
                               f"Se guardaron {len(guardados)} fragmentos en:\n{self.fragments_dir}\n\n"
                               f"Archivos generados:\n" + "\n".join(guardados))
            
            self.cargar_fragmentos()
            
        except Exception as e:
            messagebox.showerror("❌ ERROR DE FRAGMENTACIÓN", 
                               f"No se pudo fragmentar el archivo:\n{str(e)}")
    
    def mostrar_listado_fragmentos(self, fragmentos_guardados):
        """Muestra un listado estilo consola de los fragmentos generados"""
        # Función para extraer número del nombre del archivo
        def extraer_numero(nombre):
            match = re.search(r'(\d+)', nombre)
            return int(match.group(1)) if match else 0
        
        # Generar listado estilo consola
        listado = "LISTADO DE FRAGMENTOS GENERADOS:\n"
        listado += "=" * 50 + "\n"
        listado += f"Directorio: {self.fragments_dir}\n"
        listado += f"Total: {len(fragmentos_guardados)} fragmentos\n"
        listado += "-" * 50 + "\n"
        
        # Ordenar numéricamente
        fragmentos_ordenados = sorted(fragmentos_guardados, key=extraer_numero)
        
        for fragmento in fragmentos_ordenados:
            ruta = self.fragments_dir / fragmento
            tamano = ruta.stat().st_size
            fecha = datetime.datetime.fromtimestamp(ruta.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            listado += f"{fecha}  {tamano:8d}  {fragmento}\n"
        
        listado += "=" * 50 + "\n"
        
        # Mostrar en un cuadro de diálogo
        top = tk.Toplevel(self.root)
        top.title("📋 LISTADO DE FRAGMENTOS")
        top.geometry("650x450")
        
        text = tk.Text(top, wrap=tk.WORD, font=("Courier", 10))
        text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        text.insert(tk.END, listado)
        text.config(state=tk.DISABLED)
        
        btn = ttk.Button(top, text="Cerrar", command=top.destroy)
        btn.pack(pady=5)
    
    def generar_archivos_estado(self, fragmentos_guardados):
        """Genera archivos de estado para la extensión del navegador"""
        # Función para extraer número del nombre del archivo
        def extraer_numero(nombre):
            match = re.search(r'(\d+)', nombre)
            return int(match.group(1)) if match else 0
        
        # Ordenar numéricamente
        fragmentos_ordenados = sorted(fragmentos_guardados, key=extraer_numero)
        
        # fragments_now.info - todos los fragmentos actuales
        now_path = self.fragments_dir / "fragments_now.info"
        with open(now_path, 'w', encoding='utf-8') as f:
            f.write("# NEUROBIT FRAGMENTS STATE\n")
            f.write(f"total={len(fragmentos_guardados)}\n")
            f.write("list=" + ",".join(fragmentos_ordenados) + "\n")
            f.write(f"timestamp={datetime.datetime.now().isoformat()}\n")
        
        # fragments_pending.info - todos pendientes de enviar
        pending_path = self.fragments_dir / "fragments_pending.info"
        with open(pending_path, 'w', encoding='utf-8') as f:
            f.write("# NEUROBIT PENDING FRAGMENTS\n")
            f.write(f"remaining={len(fragmentos_guardados)}\n")
            f.write("list=" + ",".join(fragmentos_ordenados) + "\n")
            f.write(f"timestamp={datetime.datetime.now().isoformat()}\n")
    
    def siguiente_indice(self, prefijo='parte_'):
        """Encuentra el siguiente número de índice disponible"""
        max_n = 0
        patron = re.compile(rf"^{re.escape(prefijo)}(\d+)\.txt$")
        
        for archivo in self.fragments_dir.iterdir():
            if archivo.is_file():
                coincidencia = patron.match(archivo.name)
                if coincidencia:
                    try:
                        n = int(coincidencia.group(1))
                        if n > max_n:
                            max_n = n
                    except ValueError:
                        continue
        
        return max_n + 1
    
    def cargar_fragmentos(self):
        """Carga y muestra los fragmentos existentes en orden numérico"""
        self.fragments_list.delete(0, tk.END)
        
        try:
            # Función para extraer número del nombre del archivo
            def extraer_numero(nombre):
                match = re.search(r'(\d+)', nombre)
                return int(match.group(1)) if match else 0
            
            fragmentos = [
                f.name for f in self.fragments_dir.iterdir() 
                if f.is_file() and f.name.startswith('parte_') and f.name.endswith('.txt')
            ]
            
            # Ordenar numéricamente
            fragmentos.sort(key=extraer_numero)
            
            if not fragmentos:
                self.fragments_list.insert(tk.END, "No hay fragmentos disponibles")
                return
            
            for fragmento in fragmentos:
                ruta = self.fragments_dir / fragmento
                tamano = ruta.stat().st_size
                self.fragments_list.insert(tk.END, f"{fragmento} ({tamano} bytes)")
        
        except Exception as e:
            self.fragments_list.insert(tk.END, f"Error al cargar fragmentos: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NeurobitCentralStation(root)
    root.mainloop()
