# tools/vm_bridge_gui.py

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import json
from pathlib import Path

class VMBridgeGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="🖥️ VM Bridge Monitor — NEUROBIT")
        self.set_default_size(900, 700)
        
        # Estado
        self.vms = {}  # vm_id -> {'process': proc, 'log': []}
        self.active_vm = None
        
        # UI Principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_box)
        
        # Header
        header = Gtk.Label()
        header.set_markup("<b>🖥️ VM Bridge Monitor</b>")
        header.set_halign(Gtk.Align.START)
        header.get_style_context().add_class("title")
        main_box.pack_start(header, False, False, 10)
        
        # Notebook (solapas)
        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        main_box.pack_start(self.notebook, True, True, 0)
        
        # Botón agregar VM
        add_btn = Gtk.Button(label="+ Nueva VM")
        add_btn.connect("clicked", self.on_add_vm)
        main_box.pack_start(add_btn, False, False, 5)
        
        # Consola global (debajo de las solapas)
        console_frame = Gtk.Frame(label="📋 Consola de Actividad")
        main_box.pack_start(console_frame, False, False, 0)
        
        self.console_text = Gtk.TextView()
        self.console_text.set_editable(False)
        self.console_text.set_monospace(True)
        self.console_text.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        
        scroll_console = Gtk.ScrolledWindow()
        scroll_console.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_console.set_vexpand(False)
        scroll_console.set_hexpand(True)
        scroll_console.add(self.console_text)
        
        console_frame.add(scroll_console)
        
        # Auto-refresh cada 2s
        GLib.timeout_add_seconds(2, self.refresh_all_vms)
    
    def on_add_vm(self, button):
        """Agrega nueva VM al notebook"""
        vm_id = f"VM_{len(self.vms) + 1}"
        
        # Crear frame para la VM
        vm_frame = Gtk.Frame(label=vm_id)
        vm_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vm_box.set_margin_start(10)
        vm_box.set_margin_end(10)
        vm_box.set_margin_top(10)
        vm_box.set_margin_bottom(10)
        vm_frame.add(vm_box)
        
        # Estado de la VM
        status_label = Gtk.Label(label="Estado: 🔴 OFF")
        vm_box.pack_start(status_label, False, False, 0)
        
        # Info de recursos
        info_grid = Gtk.Grid()
        info_grid.set_column_spacing(10)
        info_grid.set_row_spacing(5)
        
        info_grid.attach(Gtk.Label(label="PID:"), 0, 0, 1, 1)
        pid_label = Gtk.Label(label="—")
        info_grid.attach(pid_label, 1, 0, 1, 1)
        
        info_grid.attach(Gtk.Label(label="CPU:"), 0, 1, 1, 1)
        cpu_label = Gtk.Label(label="—")
        info_grid.attach(cpu_label, 1, 1, 1, 1)
        
        info_grid.attach(Gtk.Label(label="RAM:"), 0, 2, 1, 1)
        ram_label = Gtk.Label(label="—")
        info_grid.attach(ram_label, 1, 2, 1, 1)
        
        vm_box.pack_start(info_grid, False, False, 5)
        
        # Consola específica de esta VM
        vm_console = Gtk.TextView()
        vm_console.set_editable(False)
        vm_console.set_monospace(True)
        
        scroll_vm = Gtk.ScrolledWindow()
        scroll_vm.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_vm.set_vexpand(True)
        scroll_vm.add(vm_console)
        
        vm_box.pack_start(scroll_vm, True, True, 0)
        
        # Agregar al notebook
        page_num = self.notebook.append_page(vm_frame, Gtk.Label(label=vm_id))
        
        # Guardar referencias
        self.vms[vm_id] = {
            'frame': vm_frame,
            'status': status_label,
            'pid': pid_label,
            'cpu': cpu_label,
            'ram': ram_label,
            'console': vm_console,
            'log': []
        }
        
        self.log_to_console(f"✅ VM {vm_id} creada")
    
    def refresh_all_vms(self):
        """Actualiza estado de todas las VMs"""
        for vm_id, vm_data in self.vms.items():
            # Aquí iría la lógica para obtener stats reales
            # Por ahora, simulamos
            pass
        
        return True  # Continuar refresh
    
    def log_to_console(self, message: str):
        """Agrega mensaje a la consola global"""
        buffer = self.console_text.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, f"{message}\n")
        
        # Auto-scroll
        self.console_text.scroll_to_iter(end_iter, 0.0, False, 0.0, 0.0)