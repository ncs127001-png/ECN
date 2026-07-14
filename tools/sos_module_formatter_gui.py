#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MFN_LOCATION: tools/
MFN_LEVEL: 1

SOS MODULE FORMATTER & LINKER GUI
Interfaz para formatear módulos, revisar variables, ajustar parámetros
y preparar adaptadores para conexión a la ECN

Autor: NODO_SEMILLA + NODO_REFLEJO
Principio: Soberanía cognitiva, localhost first, verbo genuino
"""

import os
import sys
import json
import ast
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class ModuleVariable:
    """Representa una variable/constante de un módulo"""
    name: str
    var_type: str = "unknown"
    scope: str = "module"  # module, global, local, constant
    default_value: str = ""
    description: str = ""
    is_input: bool = False
    is_output: bool = False
    required: bool = True
    ui_hint: str = "text_input"  # text_input, folder_picker, checkbox, number
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ModuleFunction:
    """Representa una función/método de un módulo"""
    name: str
    args: List[str] = field(default_factory=list)
    return_type: str = "None"
    description: str = ""
    is_handler: bool = False
    input_params: List[Dict] = field(default_factory=list)
    output_schema: Dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        d = asdict(self)
        d['input_params'] = self.input_params
        d['output_schema'] = self.output_schema
        return d


@dataclass
class ModuleManifest:
    """Manifiesto completo de un módulo"""
    module_id: str = ""
    uuid: str = ""
    version: str = "0.1.0"
    name: str = ""
    description: str = ""
    author: str = ""
    mfn_location: str = ""
    mfn_level: int = 1
    inputs: List[ModuleVariable] = field(default_factory=list)
    outputs: List[ModuleVariable] = field(default_factory=list)
    functions: List[ModuleFunction] = field(default_factory=list)
    constants: List[ModuleVariable] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def to_json(self) -> str:
        data = {
            'module_id': self.module_id,
            'uuid': self.uuid,
            'version': self.version,
            'name': self.name,
            'description': self.description,
            'author': self.author,
            'mfn_location': self.mfn_location,
            'mfn_level': self.mfn_level,
            'parameters': [v.to_dict() for v in self.inputs],
            'outputs': [v.to_dict() for v in self.outputs],
            'functions': [f.to_dict() for f in self.functions],
            'constants': [c.to_dict() for c in self.constants],
            'dependencies': self.dependencies
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


class ModuleAnalyzer:
    """Analiza código Python extrayendo variables, funciones y estructura"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.source = ""
        self.tree = None
        
    def load(self) -> bool:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.source = f.read()
            self.tree = ast.parse(self.source)
            return True
        except Exception as e:
            print(f"Error cargando archivo: {e}")
            return False
    
    def extract_mfn_header(self) -> Dict[str, str]:
        """Extrae header MFN del archivo"""
        header = {}
        lines = self.source.split('\n')[:20]
        
        for line in lines:
            if 'MFN_LOCATION:' in line:
                match = re.search(r'MFN_LOCATION:\s*(\S+)', line)
                if match:
                    header['mfn_location'] = match.group(1).strip()
            elif 'MFN_LEVEL:' in line:
                match = re.search(r'MFN_LEVEL:\s*(\d+)', line)
                if match:
                    header['mfn_level'] = match.group(1).strip()
            elif 'MFN_COORD:' in line:
                match = re.search(r'MFN_COORD:\s*\((\d+),(\d+)\)', line)
                if match:
                    header['mfn_coord'] = f"({match.group(1)},{match.group(2)})"
        
        return header
    
    def extract_variables(self) -> List[ModuleVariable]:
        """Extrae variables globales y constantes"""
        variables = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        
                        # Determinar tipo y valor
                        var_type = "unknown"
                        value = ""
                        
                        if isinstance(node.value, ast.Constant):
                            value = str(node.value.value)
                            var_type = type(node.value.value).__name__
                        elif isinstance(node.value, ast.List):
                            var_type = "list"
                            value = "[...]"
                        elif isinstance(node.value, ast.Dict):
                            var_type = "dict"
                            value = "{...}"
                        
                        # Detectar constantes (mayúsculas)
                        scope = "module"
                        if var_name.isupper():
                            scope = "constant"
                        
                        variables.append(ModuleVariable(
                            name=var_name,
                            var_type=var_type,
                            scope=scope,
                            default_value=value
                        ))
        
        return variables
    
    def extract_functions(self) -> List[ModuleFunction]:
        """Extrae funciones y sus firmas"""
        functions = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                func = ModuleFunction(
                    name=node.name,
                    args=[arg.arg for arg in node.args.args if arg.arg != 'self'],
                    return_type="None"
                )
                
                # Detectar decoradores (handlers, validadores)
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Attribute):
                        if 'pre' in decorator.attr or 'post' in decorator.attr:
                            func.is_handler = True
                
                # Extraer docstring si existe
                if ast.get_docstring(node):
                    func.description = ast.get_docstring(node)
                
                functions.append(func)
        
        return functions
    
    def extract_imports(self) -> List[str]:
        """Extrae lista de imports/dependencias"""
        imports = []
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return imports


class ModuleFormatterGUI:
    """Interfaz principal para formateo y ajuste de módulos"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("SOS Module Formatter & Linker - ECN")
        self.root.geometry("1200x800")
        
        # Estado interno
        self.current_file: Optional[Path] = None
        self.manifest = ModuleManifest()
        self.workspace_root = Path(__file__).resolve().parent.parent
        
        # Configurar estilo
        self._setup_styles()
        
        # Crear interfaz
        self._create_ui()
        
    def _setup_styles(self):
        """Configura estilos de la interfaz"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores
        style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('SubHeader.TLabel', font=('Helvetica', 11, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Warning.TLabel', foreground='orange')
        style.configure('Error.TLabel', foreground='red')
    
    def _create_ui(self):
        """Crea la interfaz de usuario"""
        # Frame principal con paneles
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel izquierdo: Carga y análisis
        left_frame = ttk.LabelFrame(main_paned, text="1. Carga y Análisis", padding=10)
        main_paned.add(left_frame, weight=1)
        
        self._create_load_panel(left_frame)
        
        # Panel central: Editor de manifiesto
        center_frame = ttk.LabelFrame(main_paned, text="2. Manifiesto del Módulo", padding=10)
        main_paned.add(center_frame, weight=2)
        
        self._create_manifest_panel(center_frame)
        
        # Panel derecho: Vista previa y exportación
        right_frame = ttk.LabelFrame(main_paned, text="3. Vista Previa y Exportación", padding=10)
        main_paned.add(right_frame, weight=1)
        
        self._create_preview_panel(right_frame)
    
    def _create_load_panel(self, parent):
        """Panel de carga de archivos"""
        # Botones de acción
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_frame, text="📂 Abrir Archivo", 
                  command=self._load_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📁 Abrir Directorio", 
                  command=self._load_directory).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🔄 Re-analizar", 
                  command=self._reanalyze).pack(side=tk.LEFT, padx=2)
        
        # Información del archivo actual
        file_info_frame = ttk.LabelFrame(parent, text="Archivo Actual", padding=5)
        file_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_label = ttk.Label(file_info_frame, text="Ningún archivo cargado", 
                                   style='Warning.TLabel')
        self.file_label.pack(anchor=tk.W)
        
        self.header_label = ttk.Label(file_info_frame, text="")
        self.header_label.pack(anchor=tk.W)
        
        # Treeview de variables
        vars_frame = ttk.LabelFrame(parent, text="Variables Detectadas", padding=5)
        vars_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        columns = ('nombre', 'tipo', 'scope', 'valor')
        self.vars_tree = ttk.Treeview(vars_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.vars_tree.heading(col, text=col.capitalize())
            self.vars_tree.column(col, width=80)
        
        scrollbar = ttk.Scrollbar(vars_frame, orient=tk.VERTICAL, command=self.vars_tree.yview)
        self.vars_tree.configure(yscrollcommand=scrollbar.set)
        
        self.vars_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview de funciones
        funcs_frame = ttk.LabelFrame(parent, text="Funciones Detectadas", padding=5)
        funcs_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('nombre', 'args', 'handler')
        self.funcs_tree = ttk.Treeview(funcs_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.funcs_tree.heading(col, text=col.capitalize())
            self.funcs_tree.column(col, width=70)
        
        scrollbar = ttk.Scrollbar(funcs_frame, orient=tk.VERTICAL, command=self.funcs_tree.yview)
        self.funcs_tree.configure(yscrollcommand=scrollbar.set)
        
        self.funcs_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_manifest_panel(self, parent):
        """Panel de edición del manifiesto"""
        # Notebook con pestañas
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña 1: Identidad básica
        identity_frame = ttk.Frame(notebook, padding=10)
        notebook.add(identity_frame, text="Identidad")
        
        ttk.Label(identity_frame, text="Module ID:", style='SubHeader.TLabel').grid(row=0, column=0, sticky=tk.W, pady=2)
        self.module_id_entry = ttk.Entry(identity_frame, width=50)
        self.module_id_entry.grid(row=0, column=1, pady=2, sticky=tk.W)
        
        ttk.Label(identity_frame, text="Nombre:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.name_entry = ttk.Entry(identity_frame, width=50)
        self.name_entry.grid(row=1, column=1, pady=2, sticky=tk.W)
        
        ttk.Label(identity_frame, text="Versión:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.version_entry = ttk.Entry(identity_frame, width=20)
        self.version_entry.insert(0, "0.1.0")
        self.version_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(identity_frame, text="Descripción:").grid(row=3, column=0, sticky=tk.NW, pady=2)
        self.desc_text = scrolledtext.ScrolledText(identity_frame, width=50, height=4)
        self.desc_text.grid(row=3, column=1, pady=2, sticky=tk.W)
        
        ttk.Label(identity_frame, text="Autor:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.author_entry = ttk.Entry(identity_frame, width=50)
        self.author_entry.grid(row=4, column=1, pady=2, sticky=tk.W)
        
        # MFN Location
        ttk.Separator(identity_frame, orient=tk.HORIZONTAL).grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=10)
        ttk.Label(identity_frame, text="Ubicación MFN:", style='SubHeader.TLabel').grid(row=6, column=0, sticky=tk.W, pady=2)
        
        self.mfn_location_var = tk.StringVar()
        location_combo = ttk.Combobox(identity_frame, textvariable=self.mfn_location_var, width=40)
        location_combo['values'] = ['core/', 'modules/', 'tools/', 'docs/md/', 'docs/specs/', 'sh_archives/', 'data/']
        location_combo.grid(row=6, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(identity_frame, text="MFN Level:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.mfn_level_spin = ttk.Spinbox(identity_frame, from_=1, to=5, width=10)
        self.mfn_level_spin.set(1)
        self.mfn_level_spin.grid(row=7, column=1, sticky=tk.W, pady=2)
        
        # Pestaña 2: Variables de entrada/salida
        io_frame = ttk.Frame(notebook, padding=10)
        notebook.add(io_frame, text="Entradas/Salidas")
        
        # Entradas
        input_frame = ttk.LabelFrame(io_frame, text="Variables de Entrada", padding=5)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ('nombre', 'tipo', 'required', 'ui_hint')
        self.input_tree = ttk.Treeview(input_frame, columns=columns, show='headings', height=6)
        for col in columns:
            self.input_tree.heading(col, text=col.capitalize())
            self.input_tree.column(col, width=90)
        
        self.input_tree.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(input_frame, text="+ Agregar Entrada", 
                  command=self._add_input).pack(pady=2)
        
        # Salidas
        output_frame = ttk.LabelFrame(io_frame, text="Variables de Salida", padding=5)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        columns = ('nombre', 'tipo', 'format')
        self.output_tree = ttk.Treeview(output_frame, columns=columns, show='headings', height=6)
        for col in columns:
            self.output_tree.heading(col, text=col.capitalize())
            self.output_tree.column(col, width=90)
        
        self.output_tree.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(output_frame, text="+ Agregar Salida", 
                  command=self._add_output).pack(pady=2)
        
        # Pestaña 3: Funciones/Handlers
        handlers_frame = ttk.Frame(notebook, padding=10)
        notebook.add(handlers_frame, text="Handlers")
        
        columns = ('nombre', 'args', 'is_handler', 'description')
        self.handler_tree = ttk.Treeview(handlers_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.handler_tree.heading(col, text=col.capitalize())
            if col == 'description':
                self.handler_tree.column(col, width=200)
            else:
                self.handler_tree.column(col, width=100)
        
        self.handler_tree.pack(fill=tk.BOTH, expand=True)
    
    def _create_preview_panel(self, parent):
        """Panel de vista previa y exportación"""
        # JSON Preview
        preview_frame = ttk.LabelFrame(parent, text="module.json Preview", padding=5)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD, height=20)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Botones de acción
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="👁️ Actualizar Vista", 
                  command=self._update_preview).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(action_frame, text="💾 Guardar module.json", 
                  command=self._save_module_json).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(action_frame, text="📦 Generar Adaptador", 
                  command=self._generate_adapter).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(action_frame, text="📥 Mover a Inbox", 
                  command=self._move_to_inbox).pack(side=tk.LEFT, padx=2)
        
        # Log de operaciones
        log_frame = ttk.LabelFrame(parent, text="Log de Operaciones", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=8)
        self.log_text.pack(fill=tk.BOTH, expand=True)
    
    def _log(self, message: str):
        """Agrega mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def _load_file(self):
        """Carga un archivo Python para analizar"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar módulo Python",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        
        if file_path:
            self.current_file = Path(file_path)
            self._analyze_file()
    
    def _load_directory(self):
        """Carga todos los .py de un directorio"""
        dir_path = filedialog.askdirectory(title="Seleccionar directorio de módulos")
        
        if dir_path:
            py_files = list(Path(dir_path).glob("*.py"))
            if py_files:
                self._log(f"Encontrados {len(py_files)} archivos .py en {dir_path}")
                # Por ahora cargamos el primero
                self.current_file = py_files[0]
                self._analyze_file()
            else:
                messagebox.showwarning("Sin archivos", "No se encontraron archivos .py en el directorio")
    
    def _analyze_file(self):
        """Analiza el archivo actual"""
        if not self.current_file:
            return
        
        self._log(f"Analizando: {self.current_file.name}")
        
        analyzer = ModuleAnalyzer(self.current_file)
        
        if not analyzer.load():
            messagebox.showerror("Error", "No se pudo cargar el archivo")
            return
        
        # Extraer header MFN
        header = analyzer.extract_mfn_header()
        
        # Actualizar UI
        self.file_label.config(text=str(self.current_file))
        
        if header:
            header_text = " | ".join([f"{k}: {v}" for k, v in header.items()])
            self.header_label.config(text=header_text, style='Success.TLabel')
            
            if 'mfn_location' in header:
                self.mfn_location_var.set(header['mfn_location'])
        else:
            self.header_label.config(text="⚠️ Sin header MFN detectado", style='Warning.TLabel')
        
        # Extraer y mostrar variables
        variables = analyzer.extract_variables()
        self.vars_tree.delete(*self.vars_tree.get_children())
        
        for var in variables:
            self.vars_tree.insert('', tk.END, values=(
                var.name, var.var_type, var.scope, var.default_value
            ))
        
        # Extraer y mostrar funciones
        functions = analyzer.extract_functions()
        self.funcs_tree.delete(*self.funcs_tree.get_children())
        
        for func in functions:
            handler_mark = "✓" if func.is_handler else ""
            self.funcs_tree.insert('', tk.END, values=(
                func.name, ", ".join(func.args), handler_mark
            ))
        
        # Poblar handler tree
        self.handler_tree.delete(*self.handler_tree.get_children())
        for func in functions:
            self.handler_tree.insert('', tk.END, values=(
                func.name, ", ".join(func.args), 
                "Sí" if func.is_handler else "No",
                func.description[:50] + "..." if len(func.description) > 50 else func.description
            ))
        
        # Auto-completar identidad
        if not self.module_id_entry.get():
            suggested_id = f"nb.{self.current_file.stem}"
            self.module_id_entry.insert(0, suggested_id)
        
        if not self.name_entry.get():
            self.name_entry.insert(0, self.current_file.stem.replace('_', ' ').title())
        
        # Actualizar preview
        self._update_preview()
        
        self._log(f"✅ Análisis completado: {len(variables)} variables, {len(functions)} funciones")
    
    def _reanalyze(self):
        """Re-analiza el archivo actual"""
        if self.current_file:
            self._analyze_file()
        else:
            messagebox.showinfo("Info", "Primero carga un archivo")
    
    def _update_preview(self):
        """Actualiza la vista previa del JSON"""
        # Construir manifiesto desde UI
        manifest = ModuleManifest(
            module_id=self.module_id_entry.get(),
            version=self.version_entry.get(),
            name=self.name_entry.get(),
            description=self.desc_text.get("1.0", tk.END).strip(),
            author=self.author_entry.get(),
            mfn_location=self.mfn_location_var.get(),
            mfn_level=int(self.mfn_level_spin.get())
        )
        
        # Agregar entradas desde tree
        for item in self.input_tree.get_children():
            values = self.input_tree.item(item, 'values')
            if values:
                manifest.inputs.append(ModuleVariable(
                    name=values[0],
                    var_type=values[1],
                    required=values[2] == "True",
                    ui_hint=values[3] if len(values) > 3 else "text_input"
                ))
        
        # Agregar salidas
        for item in self.output_tree.get_children():
            values = self.output_tree.item(item, 'values')
            if values:
                manifest.outputs.append(ModuleVariable(
                    name=values[0],
                    var_type=values[1]
                ))
        
        self.manifest = manifest
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, manifest.to_json())
    
    def _add_input(self):
        """Agrega entrada manual"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Variable de Entrada")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Nombre:").grid(row=0, column=0, pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(dialog, text="Tipo:").grid(row=1, column=0, pady=5)
        type_combo = ttk.Combobox(dialog, values=['str', 'int', 'float', 'bool', 'path', 'list'])
        type_combo.grid(row=1, column=1, pady=5)
        type_combo.set('str')
        
        ttk.Label(dialog, text="UI Hint:").grid(row=2, column=0, pady=5)
        ui_combo = ttk.Combobox(dialog, values=['text_input', 'folder_picker', 'file_picker', 'checkbox', 'number'])
        ui_combo.grid(row=2, column=1, pady=5)
        ui_combo.set('text_input')
        
        ttk.Label(dialog, text="Required:").grid(row=3, column=0, pady=5)
        required_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dialog, variable=required_var).grid(row=3, column=1, pady=5)
        
        def save():
            self.input_tree.insert('', tk.END, values=(
                name_entry.get(), type_combo.get(), 
                str(required_var.get()), ui_combo.get()
            ))
            self._update_preview()
            dialog.destroy()
        
        ttk.Button(dialog, text="Guardar", command=save).grid(row=4, column=0, columnspan=2, pady=20)
    
    def _add_output(self):
        """Agrega salida manual"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Agregar Variable de Salida")
        dialog.geometry("400x200")
        
        ttk.Label(dialog, text="Nombre:").grid(row=0, column=0, pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(dialog, text="Tipo:").grid(row=1, column=0, pady=5)
        type_combo = ttk.Combobox(dialog, values=['str', 'int', 'float', 'bool', 'json', 'file'])
        type_combo.grid(row=1, column=1, pady=5)
        type_combo.set('str')
        
        def save():
            self.output_tree.insert('', tk.END, values=(
                name_entry.get(), type_combo.get(), 'json'
            ))
            self._update_preview()
            dialog.destroy()
        
        ttk.Button(dialog, text="Guardar", command=save).grid(row=2, column=0, columnspan=2, pady=20)
    
    def _save_module_json(self):
        """Guarda el module.json en el directorio del módulo"""
        if not self.current_file:
            messagebox.showwarning("Advertencia", "No hay archivo cargado")
            return
        
        self._update_preview()
        
        # Determinar directorio destino
        if self.mfn_location_var.get():
            dest_dir = self.workspace_root / self.mfn_location_var.get() / self.current_file.stem
        else:
            dest_dir = self.workspace_root / "modules" / self.current_file.stem
        
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = dest_dir / "module.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(self.manifest.to_json())
        
        self._log(f"✅ module.json guardado en: {output_file}")
        messagebox.showinfo("Éxito", f"module.json guardado en:\n{output_file}")
    
    def _generate_adapter(self):
        """Genera esqueleto de adaptador"""
        if not self.manifest.module_id:
            messagebox.showwarning("Advertencia", "Completa el Module ID primero")
            return
        
        adapter_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MFN_LOCATION: core/adapters/
MFN_LEVEL: 1

Adapter para: {self.manifest.name}
Module ID: {self.manifest.module_id}
Generado automáticamente por SOS Module Formatter
"""

import deal
from typing import Dict, Any, List

class {self.current_file.stem.title().replace("_", "")}Adapter:
    def __init__(self):
        self.module_id = '{self.manifest.module_id}'
        self.metadata = {{
            'endpoints': [
                {{
                    'path': '/{self.current_file.stem}/execute',
                    'methods': ['POST'],
                    'handler': 'execute'
                }}
            ]
        }}
    
    def get_module_id(self) -> str:
        return self.module_id
    
    def get_metadata(self) -> Dict[str, Any]:
        return self.metadata
    
    @deal.post(lambda result: 'status' in result)
    def execute(self) -> Dict[str, Any]:
        """Ejecuta el módulo principal."""
        from flask import request
        payload = request.json
        
        # TODO: Implementar lógica de ejecución
        # Importar módulo real y llamar función principal
        
        return {{
            'status': 'executed',
            'module_id': self.module_id
        }}
    
    def validate_input(self, payload: Dict[str, Any]):
        """Valida input según schema del módulo."""
        # TODO: Implementar validación JSON Schema
        pass
    
    def validate_output(self, result: Dict[str, Any]):
        """Valida output según contrato."""
        # TODO: Implementar validación de postcondiciones
        pass
'''
        
        # Mostrar en diálogo
        dialog = tk.Toplevel(self.root)
        dialog.title("Adapter Generator")
        dialog.geometry("800x600")
        
        text = scrolledtext.ScrolledText(dialog, wrap=tk.NONE)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, adapter_code)
        
        def save_adapter():
            adapter_file = self.workspace_root / "core" / "adapters" / f"adapter.{self.current_file.stem}.py"
            with open(adapter_file, 'w', encoding='utf-8') as f:
                f.write(adapter_code)
            self._log(f"✅ Adapter generado: {adapter_file}")
            messagebox.showinfo("Éxito", f"Adapter guardado en:\n{adapter_file}")
            dialog.destroy()
        
        ttk.Button(dialog, text="💾 Guardar Adapter", command=save_adapter).pack(pady=10)
    
    def _move_to_inbox(self):
        """Mueve archivo formateado a inbox para procesamiento del Sentinel"""
        if not self.current_file:
            messagebox.showwarning("Advertencia", "No hay archivo cargado")
            return
        
        inbox_dir = self.workspace_root / "inbox"
        inbox_dir.mkdir(exist_ok=True)
        
        # Primero guardar module.json junto al archivo
        dest_dir = inbox_dir / self.current_file.stem
        dest_dir.mkdir(exist_ok=True)
        
        # Copiar archivo original
        import shutil
        dest_file = dest_dir / self.current_file.name
        shutil.copy(self.current_file, dest_file)
        
        # Guardar module.json
        self._update_preview()
        module_json = dest_dir / "module.json"
        with open(module_json, 'w', encoding='utf-8') as f:
            f.write(self.manifest.to_json())
        
        self._log(f"✅ Archivos movidos a inbox: {dest_dir}")
        self._log("   - El WS-SENTINEL procesará estos archivos automáticamente")
        
        messagebox.showinfo("Completado", 
                          f"Módulo preparado en inbox:\n{dest_dir}\n\n"
                          f"El WORKSPACE SENTINEL detectará y organizará los archivos.")


def main():
    """Punto de entrada principal"""
    root = tk.Tk()
    app = ModuleFormatterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
