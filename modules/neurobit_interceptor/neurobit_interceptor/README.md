

**PROTOCOLO:** NEUROBIT_FIX_INDENTACION_Y_RUTAS v1.0 / DEPURACION_QUÍRURGICA

¡Excelente diagnóstico, Arquitecto! 🕊️⚙️ Detectaste tres problemas críticos. Vamos a resolverlos con precisión:

---

## 🔧 **PROBLEMA 1: Ruta incorrecta de persistencia**

El archivo se guarda en `/home/gus/Escritorio/PRODUCCION/data/` porque en `state_persistence.py` usé `Path(__file__).parent.parent` (sube 2 niveles). Debe ser solo `.parent` (1 nivel).

**Corrección en `state_persistence.py`:**
```python
# Línea ~8: Cambiar
storage_path = base_dir / "data" / "charset_states.json"

# Por esto:
storage_path = Path(__file__).parent / "data" / "charset_states.json"
```

---

## 🔧 **PROBLEMA 2: Error de indentación en `matrix_editor_gui.py`**

El método `on_close` está definido DENTRO del `__init__` por un error de indentación. Aquí está el archivo completo corregido:

**ARCHIVO COMPLETO: `matrix_editor_gui.py` (reemplazar completo)**
```python
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

        # Protocolo de cierre limpio (CORREGIDO: fuera del __init__)
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
                
                # Dibujar compartimento
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#444444", width=1)
                
                # Bind para editar al hacer clic
                self.canvas.bind("<Button-1>", lambda e, r=row, c=col: self.toggle_cell(r, c))

    def toggle_cell(self, row, col):
        """Permite trabajar en la matriz: cambia 0 por 1 y viceversa"""
        self.matrix_data[row][col] = 1 - self.matrix_data[row][col]
        self.draw_grid()

    def update_matrix(self, new_matrix, char_display):
        """Carga una nueva matriz desde el extractor"""
        self.matrix_data = new_matrix
        self.info_label.config(text=f"Carácter: '{char_display}' | Matriz {self.matrix_size}x{self.matrix_size}")
        self.draw_grid()
```

---

## 🔧 **PROBLEMA 3: Font Size Configurable**

Vamos a agregar un control deslizante (slider) en `main.py` para ajustar el `font_size` dinámicamente.

**ARCHIVO COMPLETO: `main.py` (reemplazar completo)**
```python
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
        
        # Módulos core (font_size inicial)
        self.current_font_size = 24
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
        
        # Control de Font Size (NUEVO)
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
        
    def update_font_size(self, value):
        """Actualiza el font_size del extractor en tiempo real"""
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
            print("⚠️  text_navigator.py no existe aún. Crear el archivo mínimo.")
            
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
```

---

## 🔧 **ACTUALIZACIÓN: `charset_navigator.py` con persistencia**

Para que el Charset Navigator pueda guardar estados, necesita recibir el objeto `persistence`:

**ARCHIVO COMPLETO: `charset_navigator.py` (reemplazar completo)**
```python
import tkinter as tk

class CharsetNavigator:
    def __init__(self, root, extractor, mapper, editor, persistence=None):
        self.root = root
        self.extractor = extractor
        self.mapper = mapper
        self.editor = editor
        self.persistence = persistence
        
        self.charset_range = range(32, 127)  # ASCII imprimible
        self.current_index = 0
        
        self.root.title("Neurobit Charset Navigator")
        self.root.geometry("900x150")
        self.root.configure(bg="#111111")
        
        # Frame superior: navegación
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
        
        # Frame inferior: info
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
        
        # Extraer y mapear
        bitmap, w, h = self.extractor.get_char_bitmap(char)
        matrix = self.mapper.remap_to_matrix(bitmap, w, h, center=True)
        self.editor.update_matrix(matrix, char)
        
    def save_current_state(self):
        """Guarda el estado actual de la matriz"""
        if self.persistence is None:
            print("⚠️  Persistence no disponible")
            return
            
        char_code = self.charset_range[self.current_index]
        char = chr(char_code)
        
        # Obtener la matriz actual del editor (puede haber sido editada)
        current_matrix = self.editor.matrix_data
        
        # Guardar
        self.persistence.save_state(char_code, current_matrix)
        print(f"💾 Estado de '{char}' guardado exitosamente")
```

---

## 🧪 **ORDEN DE EJECUCIÓN**

```bash
# 1. Limpiar procesos
python3 process_manager.py

# 2. Activar venv
source ~/WORKSPACE_NEUROBIT_V0.2/.venv/bin/activate

# 3. Ejecutar
cd ~/Escritorio/PRODUCCION/neurobit_interceptor
python3 main.py
```

---

## ✅ **VERIFICACIONES**

1. **Font Size Slider**: Deberías ver un slider en la ventana principal que va de 8 a 128px
2. **Ruta correcta**: Al guardar, debería aparecer:
   ```
   💾 Persistence initialized:
      📂 Path: /home/gus/Escritorio/PRODUCCION/neurobit_interceptor/data/charset_states.json
   ```
3. **Cierre limpio**: Al cerrar la ventana del editor, no debería quedar procesos huérfanos

---

¿Probás estas correcciones y me confirmás si la ruta ahora es correcta y el slider funciona? 🕊️⚙️

Construir un sistema interactivo que capture el contenido de texto textualmente
Estoy diseñando una interfaz con un cursor cuadrado como una herramienta de navegación para localizar con precisión cada carácter en un documento
Cuando el cursor está estacionado en un carácter específico, el sistema extrae automáticamente su forma visual y lo asigna a una estructura de matriz personalizable
La matriz admite un diseño máximo de trece filas y una columna, lo que garantiza una presentación clara y una configuración flexible de las imágenes de caracteres
Construir una interfaz de matriz visual para apoyar operaciones de grano fino
Estoy diseñando una arquitectura modular que garantiza una lógica clara y facilidad de depuración al tiempo que satisface las necesidades de las operaciones de computación y localización subyacentes.
El análisis profundo y la manipulación de las estructuras visuales de texto se logra mediante el mapeo preciso de mapas de bits de caracteres a mallas de 13x13.
Todo el sistema se centra en el funcionamiento autónomo sin dependencias externas, mejorando la soberanía y la capacidad de mantenimiento de los datos.
Construir un sistema de visualización de texto modular y escalable
Estoy trabajando en el diseño de una solución gráfica centrada en la interfaz que lleva el renderizado de caracteres y el mapeo de matrices en una representación precisa de caracteres a través de fuentes de sistema y transformándolas en matrices de píxeles procesables.
Cada componente funciona de forma independiente y trabaja en estrecha colaboración: desde la resolución de texto en su lugar hasta el procesamiento de cuadrícula y la edición interactiva, los usuarios pueden manipular intuitivamente el rendimiento de píxeles de los caracteres.
Toda la arquitectura se basa en una clara división de responsabilidades, que admite la vista previa en tiempo real y la expansión de propósito futuro.
Construya mapas de bits de caracteres y mapee a cuadrículas fijas
Estoy renderizando un solo carácter como una imagen de dos valores, extraído y escalado con un píxel exacto, adaptándolo a una estructura de matriz unificada de 13×13.
Cada píxel se convierte a 0 o 1, formando una matriz clara y reconocible de bits visuales, asegurando la consistencia semántica en las interacciones posteriores.
Todo el proceso sigue los principios minimalistas, lo que permite transiciones perfectas del texto a la visualización de una manera intuitiva y eficiente.
Creación de un sistema modular de procesamiento de mapa de bits de caracteres
Estoy desmontando la funcionalidad general en componentes separados, asegurando que cada parte de la responsabilidad sea clara y fácil de depurar.
Forme un proceso de interacción escalable extrayendo imágenes de caracteres, asignando a una cuadrícula fija, editando visualmente y administrando la lógica de entrada.
El objetivo final es lograr una expansión funcional intuitiva, flexible y fácil de seguir del sistema prototipo.
Pensamiento



El programa está funcionando y observando la información de salida.
Estoy siguiendo el registro de ejecución que se muestra en el terminal para comprender el estado y el progreso del proceso actual.
Al analizar el contenido de salida, trate de comprender los patrones de comportamiento y los problemas potenciales del programa.
Esté atento a las indicaciones clave para responder a posibles anomalías o a los siguientes pasos.
Comprobar el estado del archivo y los problemas de dependencia del módulo
Estoy analizando una excepción al estado del archivo en el entorno actual y encontré que los datos del directorio están vacíos y hay un error de importación del módulo.
Esto indica que puede haber casos en los que el archivo no se guarda correctamente o que falta la configuración de la ruta del módulo.
Voy a sintetizar estas pistas para encontrar la causa raíz del problema y proponer soluciones.
Pensamiento
¡Perfecto! Ahora confirmo el problema: **la consola dice "Guardando estado" pero la carpeta `data/` está vacía** (total 0). 

El problema es que `state_persistence.py` no está creando el archivo en la ubicación correcta. Vamos a solucionarlo definitivamente:

## 🔧 **SOLUCIÓN DEFINITIVA**

**Reemplaza completamente `state_persistence.py` con esto:**

```python
import json
from pathlib import Path
import os

class StatePersistence:
    def __init__(self, storage_path=None):
        # Usar ruta ABSOLUTA relativa al directorio del script principal
        if storage_path is None:
            # Obtener el directorio donde está main.py
            base_dir = Path(__file__).parent.parent
            storage_path = base_dir / "data" / "charset_states.json"
        
        self.storage_path = Path(storage_path).resolve()  # Ruta absoluta
        self.states = {}
        
        # Crear directorio si no existe
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Cargar estados existentes
        self._load_states()
        
        print(f"💾 Persistence initialized:")
        print(f"   📂 Path: {self.storage_path}")
        print(f"   📁 Dir exists: {self.storage_path.parent.exists()}")
        print(f"   📄 File exists: {self.storage_path.exists()}")
        
    def _load_states(self):
        """Carga los estados desde el archivo JSON"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.states = json.load(f)
                print(f"✅ Loaded {len(self.states)} states from disk")
            except json.JSONDecodeError:
                print("⚠️  File corrupted, starting fresh")
                self.states = {}
            except Exception as e:
                print(f"⚠️  Error loading: {e}")
                self.states = {}
        else:
            print("🆕 Creating new storage file")
            self.states = {}
        
    def save_state(self, char_code, matrix_13x13, metadata=None):
        """Guarda el estado de un carácter"""
        key = str(char_code)
        
        self.states[key] = {
            "char": chr(char_code),
            "code": char_code,
            "matrix": matrix_13x13,
            "metadata": metadata or {},
            "timestamp": Path(self.storage_path).stat().st_mtime if self.storage_path.exists() else None
        }
        
        # Guardar inmediatamente en disco
        self._persist()
        
        # Verificación explícita
        print(f"💾 Saved '{chr(char_code)}' (Code {char_code}) → {self.storage_path}")
        
    def _persist(self):
        """Persiste los estados en el archivo JSON"""
        try:
            # Asegurar que el directorio existe
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escribir archivo
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.states, f, indent=2, ensure_ascii=False)
            
            # Verificar que se creó
            if self.storage_path.exists():
                size = self.storage_path.stat().st_size
                print(f"   ✅ File written ({size} bytes)")
            else:
                print(f"   ❌ File NOT created!")
                
        except Exception as e:
            print(f"   ❌ Error saving: {e}")
            import traceback
            traceback.print_exc()
            
    def get_all_states(self):
        """Retorna todos los estados"""
        return self.states
    
    def get_stats(self):
        """Retorna estadísticas"""
        return {
            "total_states": len(self.states),
            "storage_path": str(self.storage_path),
            "file_exists": self.storage_path.exists(),
            "file_size": self.storage_path.stat().st_size if self.storage_path.exists() else 0
        }
```

## 🧪 **TEST RÁPIDO**

Después de reemplazar el archivo, ejecuta:

```bash
cd ~/Escritorio/PRODUCCION/neurobit_interceptor
python3 -c "
from state_persistence import StatePersistence
p = StatePersistence()
p.save_state(65, [[1,0],[0,1]], {'test': True})
print('Stats:', p.get_stats())
"

# Verificar que se creó el archivo
ls -lh data/
cat data/charset_states.json | head -20
```

## 🔍 **DEBUG ADICIONAL**

Si aún no funciona, agrega esto al inicio de `charset_navigator.py`:

```python
import os
print(f"📂 Current dir: {os.getcwd()}")
print(f"📂 Script dir: {Path(__file__).parent}")
```

¿Probás esto y me decís qué sale? 🕊️⚙️
¡Excelente avance, Arquitecto! 🕊️️ Veo el éxito en la captura: la 'D' está siendo mapeada correctamente en la matriz 13x13. Pero detecto varios puntos de fricción que debemos depurar. Vamos por partes:
¡Excelente trabajo de testing, Arquitecto! 🕊️⚙️ Veo claramente los problemas. Vamos a resolverlos uno por uno:

## 🔧 **PROBLEMAS DETECTADOS Y SOLUCIONES**

### **1. Falta el módulo `text_navigator.py`**

El error `ModuleNotFoundError: No module named 'text_navigator'` ocurre porque intentamos importar un módulo que no creamos. 

**Solución rápida:** Comentemos esa línea en `main.py` temporalmente:

```python
# Comentar línea 44 en main.py:
# from text_navigator import TextNavigator  # ← COMENTAR ESTO POR AHORA
```

O mejor, creemos el archivo mínimo:

**Archivo: `text_navigator.py`**
```python
import tkinter as tk

class TextNavigator:
    def __init__(self, root, extractor, mapper, editor, persistence):
        self.root = root
        self.root.title("Neurobit Text Navigator")
        self.root.geometry("800x100")
        
        label = tk.Label(root, text=" Text Navigator - En desarrollo", 
                        font=("Consolas", 14), fg="#00ffcc", bg="#111111")
        label.pack(pady=30)
        
        btn = tk.Button(root, text="Volver", command=root.destroy,
                       bg="#004444", fg="#00ffcc", font=("Consolas", 12))
        btn.pack(pady=10)
```

---

### **2. process_manager.py no mata procesos correctamente**

El problema es que busca PIDs específicos que ya no existen. Necesitamos una versión más robusta:

**Archivo: `process_manager.py` (reemplazar completo)**
```python
#!/usr/bin/env python3
import subprocess
import os
import signal
import time

def kill_processes():
    """Mata todos los procesos python3 relacionados con neurobit_interceptor"""
    print("🔍 Buscando procesos de neurobit_interceptor...")
    
    # Método 1: Usar pkill
    try:
        result = subprocess.run(
            ['pkill', '-f', 'python3.*main.py'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Procesos terminados con pkill")
        else:
            print("⚠️  No se encontraron procesos activos")
    except Exception as e:
        print(f"❌ Error con pkill: {e}")
    
    # Método 2: Buscar y matar manualmente
    time.sleep(1)
    try:
        result = subprocess.run(
            ['pgrep', '-f', 'python3.*main.py'],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"✅ Proceso {pid} terminado")
                except ProcessLookupError:
                    print(f"⚠️  Proceso {pid} ya no existe")
        else:
            print("✅ No hay procesos activos")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    kill_processes()
```

---

### **3. Problema de persistencia - No guarda en `data/`**

El problema es que `state_persistence.py` probablemente usa una ruta relativa que no existe. Vamos a corregirlo:

**Archivo: `state_persistence.py` (reemplazar completo)**
```python
import json
from pathlib import Path

class StatePersistence:
    def __init__(self, storage_path=None):
        if storage_path is None:
            # Usar ruta absoluta relativa al script principal
            base_dir = Path(__file__).parent
            storage_path = base_dir / "data" / "charset_states.json"
        
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.states = self._load_states()
        print(f"💾 Persistence initialized: {self.storage_path}")
        
    def _load_states(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("⚠️  Archivo corrupto, iniciando desde cero")
                return {}
        return {}
        
    def save_state(self, char_code, matrix_13x13, metadata=None):
        """Guarda el estado de matriz de un carácter"""
        key = str(char_code)
        self.states[key] = {
            "char": chr(char_code),
            "code": char_code,
            "matrix": matrix_13x13,
            "metadata": metadata or {}
        }
        self._persist()
        print(f"💾 Guardando estado de '{chr(char_code)}' (Code {char_code})...")
        
    def load_state(self, char_code):
        """Carga el estado guardado de un carácter"""
        key = str(char_code)
        return self.states.get(key)
        
    def _persist(self):
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.states, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error guardando: {e}")
            
    def get_all_states(self):
        return self.states
    
    def get_stats(self):
        return {
            "total_states": len(self.states),
            "storage_path": str(self.storage_path),
            "file_exists": self.storage_path.exists()
        }
```

---

### **4. Font size - Ajuste dinámico necesario**

El problema es que `font_size=64` genera un bitmap muy grande. Necesitamos:

**Opción A:** Agregar un slider en la GUI para ajustar font_size dinámicamente

**Opción B:** Calcular automáticamente el font_size óptimo basado en el caracter

**Solución temporal en `main.py`:**
```python
# En NeurobitApp.__init__(), cambiar:
self.extractor = BitmapExtractor(font_size=13)  # ← Cambiar de 64 a 13

# O mejor, hacerlo configurable:
self.extractor = BitmapExtractor(font_size=24)  # ← Valor intermedio
```

---

### **5. Ventanas que no se cierran**

Agregar en `matrix_editor_gui.py`:
```python
# En __init__ de MatrixEditorGUI, después de crear el canvas:
self.root.protocol("WM_DELETE_WINDOW", self.on_close)

def on_close(self):
    """Manejar cierre limpio de ventana"""
    self.root.destroy()
```

---

## 🚀 **PASOS INMEDIATOS**

1. **Crear `text_navigator.py`** (código mínimo arriba)
2. **Reemplazar `process_manager.py`** (versión mejorada arriba)
3. **Reemplazar `state_persistence.py`** (con rutas absolutas)
4. **Cambiar font_size a 13 o 24** en `main.py`
5. **Agregar protocolo de cierre** en `matrix_editor_gui.py`

¿Querés que te pase los archivos completos corregidos o preferís aplicar los cambios manualmente? 🕊️️
---

##  **PROBLEMAS DETECTADOS Y SOLUCIONES**

### **1. Error `externally-managed-environment` (Pillow)**

Tu Ubuntu moderno (23.04+) protege el Python del sistema. Soluciones:

**Opción A (Recomendada - Virtual Environment):**
```bash
cd ~/Escritorio/PRODUCCION/neurobit_interceptor
python3 -m venv .venv
source .venv/bin/activate
pip install Pillow
python main.py
```

**Opción B (Forzar instalación):**
```bash
pip install Pillow --break-system-packages
```

---

### **2. Ventanas que no se cierran (Procesos huérfanos)**

El problema es que `tk.Toplevel()` crea ventanas hijas que no matan el proceso padre al cerrarse. Solución modular:

**Archivo: `process_manager.py`** (nuevo módulo)
```python
import subprocess
import os
import signal

class ProcessManager:
    @staticmethod
    def kill_neurobit_processes():
        """Mata todos los procesos de neurobit_interceptor"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'neurobit_interceptor|main.py'],
                capture_output=True, text=True
            )
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"✅ Proceso {pid} terminado")
        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    ProcessManager.kill_neurobit_processes()
```

**Uso:** `python process_manager.py` para limpiar todo antes de reiniciar.

---

### **3. Ajuste del Mapeo y Centrado en la Grilla**

El problema es que el `font_size=11` es muy pequeño y el muestreo no centra bien el glifo. Solución:

**Archivo: `matrix_mapper.py` (mejorado)**
```python
class MatrixMapper:
    def __init__(self, target_size=13):
        self.target_size = target_size

    def remap_to_matrix(self, bitmap, orig_w, orig_h, center=True):
        """
        Muestrea el bitmap a la matriz objetivo con opción de centrado.
        """
        target_matrix = [[0 for _ in range(self.target_size)] for _ in range(self.target_size)]
        
        # Calcular offset para centrar si el bitmap es más pequeño que el target
        offset_x = 0
        offset_y = 0
        
        if center:
            # Escalar proporcionalmente manteniendo aspect ratio
            scale = min(self.target_size / orig_w, self.target_size / orig_h)
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)
            offset_x = (self.target_size - new_w) // 2
            offset_y = (self.target_size - new_h) // 2
        else:
            scale = 1
            new_w, new_h = orig_w, orig_h
        
        block_w = orig_w / new_w if new_w > 0 else 1
        block_h = orig_h / new_h if new_h > 0 else 1
        
        for ty in range(self.target_size):
            for tx in range(self.target_size):
                # Ajustar por offset de centrado
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
                                if bitmap[y][x] == 1:
                                    active_pixels += 1
                                total_pixels += 1
                    
                    if total_pixels > 0 and (active_pixels / total_pixels) > 0.25:
                        target_matrix[ty][tx] = 1
                        
        return target_matrix
```

---

### **4. Navegación por Charset Completo (Tabla de Caracteres)**

**Archivo: `charset_navigator.py`** (nuevo módulo)
```python
import tkinter as tk

class CharsetNavigator:
    def __init__(self, root, extractor, mapper, editor):
        self.root = root
        self.extractor = extractor
        self.mapper = mapper
        self.editor = editor
        
        self.charset_range = range(32, 127)  # ASCII imprimible
        self.current_index = 0
        
        self.root.title("Neurobit Charset Navigator")
        self.root.geometry("900x150")
        self.root.configure(bg="#111111")
        
        # Frame superior: navegación
        self.nav_frame = tk.Frame(self.root, bg="#111111")
        self.nav_frame.pack(fill=tk.X, pady=10)
        
        self.prev_btn = tk.Button(self.nav_frame, text=" ANT", 
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
        
        # Frame inferior: info
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
        self.code_label.config(text=f"ASCII: {char_code} | Bin: {bin(char_code)[2:].zfill(8)}")
        
        # Extraer y mapear
        bitmap, w, h = self.extractor.get_char_bitmap(char)
        matrix = self.mapper.remap_to_matrix(bitmap, w, h, center=True)
        self.editor.update_matrix(matrix, char)
        
    def save_current_state(self):
        """Guarda el estado actual de la matriz (placeholder para persistencia)"""
        char_code = self.charset_range[self.current_index]
        char = chr(char_code)
        print(f"💾 Guardando estado de '{char}' (Code {char_code})...")
        # Aquí irá la lógica de persistencia en JSON/binario
```

---

### **5. Persistencia de Estados de Matriz (Primer Nivel)**

**Archivo: `state_persistence.py`** (nuevo módulo)
```python
import json
from pathlib import Path

class StatePersistence:
    def __init__(self, storage_path="data/charset_states.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.states = self._load_states()
        
    def _load_states(self):
        if self.storage_path.exists():
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
        
    def save_state(self, char_code, matrix_13x13, metadata=None):
        """Guarda el estado de matriz de un carácter"""
        key = str(char_code)
        self.states[key] = {
            "char": chr(char_code),
            "code": char_code,
            "matrix": matrix_13x13,
            "metadata": metadata or {}
        }
        self._persist()
        
    def load_state(self, char_code):
        """Carga el estado guardado de un carácter"""
        key = str(char_code)
        return self.states.get(key)
        
    def _persist(self):
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.states, f, indent=2, ensure_ascii=False)
            
    def get_all_states(self):
        return self.states
```

---

##  **INTEGRACIÓN EN `main.py`**

```python
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
        self.root.geometry("400x200")
        self.root.configure(bg="#111111")
        
        # Módulos core
        self.extractor = BitmapExtractor(font_size=64)
        self.mapper = MatrixMapper(target_size=13)
        self.persistence = StatePersistence()
        
        # Editor GUI (ventana separada)
        self.editor_root = tk.Toplevel(root)
        self.editor = MatrixEditorGUI(self.editor_root, 13)
        
        # Selector de modo
        self.mode_frame = tk.Frame(self.root, bg="#111111")
        self.mode_frame.pack(pady=30)
        
        tk.Button(self.mode_frame, text=" Navegar Texto", 
                  command=self.start_text_mode,
                  bg="#004444", fg="#00ffcc", font=("Consolas", 14),
                  width=20).pack(pady=10)
        
        tk.Button(self.mode_frame, text="🔤 Navegar Charset", 
                  command=self.start_charset_mode,
                  bg="#004444", fg="#00ffcc", font=("Consolas", 14),
                  width=20).pack(pady=10)
        
        tk.Button(self.mode_frame, text="💾 Ver Estados Guardados", 
                  command=self.show_saved_states,
                  bg="#004444", fg="#00ffcc", font=("Consolas", 14),
                  width=20).pack(pady=10)
        
    def start_text_mode(self):
        from text_navigator import TextNavigator
        self.text_nav_root = tk.Toplevel(self.root)
        TextNavigator(self.text_nav_root, self.extractor, self.mapper, self.editor, self.persistence)
        
    def start_charset_mode(self):
        self.charset_nav_root = tk.Toplevel(self.root)
        CharsetNavigator(self.charset_nav_root, self.extractor, self.mapper, self.editor)
        
    def show_saved_states(self):
        states = self.persistence.get_all_states()
        print(f"📊 Estados guardados: {len(states)}")
        for code, data in states.items():
            print(f"  '{data['char']}' (Code {data['code']}): {sum(sum(row) for row in data['matrix'])} bits activos")

if __name__ == "__main__":
    root = tk.Tk()
    app = NeurobitApp(root)
    root.mainloop()
```

---

## 📋 **ORDEN DE EJECUCIÓN SUGERIDO**

1. **Limpiar procesos:** `python process_manager.py`
2. **Activar venv:** `source .venv/bin/activate`
3. **Ejecutar:** `python main.py`
4. **Probar modo Charset:** Navegar con ← → y guardar con ESPACIO
5. **Verificar persistencia:** Revisar `data/charset_states.json`

---

¿Avanzamos con esta depuración modular, Arquitecto? Una vez que el Charset Navigator funcione y guarde estados, tendremos el **primer nivel de tu Charset Soberano** construido. ️⚙️


¡Entendido perfectamente, Arquitecto! 🕊️⚙️

lo que solicitas es el **Núcleo de Intercepción y Remapeo Visual**. Es el primer paso fundamental para "liberar" los caracteres de la prisión de las fuentes estáticas del sistema operativo y convertirlos en **matrices de estados editables (13x13)**.

Para cumplir con tu requisito de **modularidad y fácil depuración**, he diseñado la arquitectura en 4 módulos independientes. Esto te permitirá probar cada "engranaje" por separado antes de integrarlos.

### 🏗️ Arquitectura Modular Propuesta

1.  **`bitmap_extractor.py`**: El "Ojo". Usa la librería `Pillow` para renderizar un carácter en un lienzo invisible y extraer su mapa de bits puro (blanco/negro).
2.  **`matrix_mapper.py`**: El "Traductor". Toma ese mapa de bits y lo muestrea/reduce a una matriz configurable (por defecto 13x13), aplicando un umbral de presencia.
3.  **`matrix_editor_gui.py`**: El "Atanor Visual". Una ventana de Tkinter que dibuja la matriz en modo ampliado, permitiendo ver los compartimentos y **editarlos manualmente** (clic para cambiar 0 por 1).
4.  **`main.py`**: El "Director". Carga el texto, maneja el cursor cuadrado (navegación con flechas) y orquesta la extracción y visualización.

---

### ️ Requisitos Previos
Solo necesitas una librería externa para el renderizado de fuentes (Tkinter ya viene con Python).
```bash
pip install Pillow
```

---

###  CÓDIGO FUENTE MODULAR

Crea una carpeta llamada `neurobit_interceptor` y dentro coloca los siguientes 4 archivos:

#### 1. `bitmap_extractor.py` (El Ojo)
```python
from PIL import Image, ImageDraw, ImageFont

class BitmapExtractor:
    def __init__(self, font_path=None, font_size=24):
        # Carga la fuente. Si no se pasa, usa la default de PIL
        try:
            self.font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
        except IOError:
            self.font = ImageFont.load_default()
        self.font_size = font_size

    def get_char_bitmap(self, char):
        """
        Renderiza un carácter y devuelve un mapa de bits (lista de listas de 0 y 1).
        """
        # Crear un lienzo pequeño
        img = Image.new('L', (self.font_size, self.font_size), color=0)
        draw = ImageDraw.Draw(img)
        
        # Dibujar el carácter en blanco
        draw.text((0, 0), char, font=self.font, fill=255)
        
        # Convertir a matriz binaria (0 = fondo, 1 = trazo)
        width, height = img.size
        bitmap = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = img.getpixel((x, y))
                # Umbral: si el pixel es mayor a 128, es parte del carácter
                row.append(1 if pixel > 128 else 0)
            bitmap.append(row)
            
        return bitmap, width, height
```

#### 2. `matrix_mapper.py` (El Traductor)
```python
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
```

#### 3. `matrix_editor_gui.py` (El Atanor Visual)
```python
import tkinter as tk

class MatrixEditorGUI:
    def __init__(self, root, matrix_size=13):
        self.root = root
        self.matrix_size = matrix_size
        self.matrix_data = [[0]*matrix_size for _ in range(matrix_size)]
        self.cell_size = 40 # Tamaño ampliado de cada compartimento
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
                
                # Dibujar compartimento
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#444444", width=1)
                
                # Bind para editar al hacer clic
                self.canvas.bind("<Button-1>", lambda e, r=row, c=col: self.toggle_cell(r, c))

    def toggle_cell(self, row, col):
        """Permite trabajar en la matriz: cambia 0 por 1 y viceversa"""
        self.matrix_data[row][col] = 1 - self.matrix_data[row][col]
        self.draw_grid()

    def update_matrix(self, new_matrix, char_display):
        """Carga una nueva matriz desde el extractor"""
        self.matrix_data = new_matrix
        self.info_label.config(text=f"Carácter: '{char_display}' | Matriz {self.matrix_size}x{self.matrix_size}")
        self.draw_grid()
```

#### 4. `main.py` (El Director / Navegador)
```python
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
        self.extractor = BitmapExtractor(font_size=64) # Tamaño grande para mejor muestreo
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
```

---

### 🧪 Cómo probarlo y depurarlo

1.  **Ejecuta `main.py`**. Se abrirán dos ventanas:
    *   **Ventana 1 (Pequeña):** Muestra el texto "HOLA MUNDO NEUROBIT" con un cursor cuadrado `[ ]` alrededor de la letra actual.
    *   **Ventana 2 (Grande):** Muestra la matriz 13x13 ampliada.
2.  **Navega:** Usa las flechas `Izquierda` y `Derecha` en la Ventana 1.
3.  **Observa:** Verás cómo la Ventana 2 actualiza la matriz 13x13 representando la forma de la letra.
4.  **Trabaja en ella:** Haz **clic en los compartimentos** de la Ventana 2. Verás que cambian de color (de gris a cyan). Esto demuestra que la matriz ya no es una imagen estática, sino un **array de estados editables en memoria**.

### 🔍 Puntos de Depuración (Por qué está modularizado)

*   **Si la forma de la letra se ve mal:** Ajusta el `font_size=64` en `main.py` o cambia el umbral `0.3` en `matrix_mapper.py`.
*   **Si el clic no funciona:** Revisa los bindings en `matrix_editor_gui.py`.
*   **Si quieres cambiar el tamaño de la matriz:** Cambia `self.matrix_size = 13` en `main.py` y `matrix_editor_gui.py` a 8, 16, o 32. El sistema se adaptará automáticamente.

¿Te parece bien esta estructura, Arquitecto? Una vez validado que el **Remapeo y la Edición** funcionan, el siguiente paso lógico sería agregar la capacidad de **guardar estas matrices editadas en tu propio Charset Soberano (JSON/Binario)** para que el sistema deje de usar la fuente del sistema operativo y use la tuya. 

Quedo en modo `LISTEN_ONLY`. 🕊️⚙️
