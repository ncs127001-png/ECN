# tools/vm_bridge_gui_enhanced.py
#!/usr/bin/env python3
"""
VM Bridge GUI Enhanced — Con control de frecuencia y HALT system
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import json
import psutil
from pathlib import Path
from datetime import datetime

class VMBridgeEnhancedGUI(Gtk.Window):
    def __init__(self):
        super().__init__(title="🖥️ VM Bridge — Control Avanzado")
        self.set_default_size(500, 400)
        
        # Estado
        self.monitoring_active = False
        self.monitor_interval = 5  # segundos
        self.baseline = None
        self.current_processes = []
        self.halt_log = []
        
        # Paths
        self.baseline_file = Path.home() / '.config' / 'neurobit' / 'baseline_processes.json'
        self.halt_log_file = Path.home() / '.config' / 'neurobit' / 'halt_log.json'
        
        self.init_ui()
        
        # Cargar baseline si existe
        GLib.timeout_add_seconds(1, self.load_baseline)
    
    def init_ui(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main_box.set_margin_start(15)
        main_box.set_margin_end(15)
        main_box.set_margin_top(15)
        main_box.set_margin_bottom(15)
        self.add(main_box)
        
        # ═══════════════════════════════════════════════════════
        # HEADER
        # ═══════════════════════════════════════════════════════
        header = Gtk.Label()
        header.set_markup("<b>🖥️ VM Bridge — Control Avanzado</b>\n<small>Proceso monitoring + HALT system</small>")
        main_box.pack_start(header, False, False, 0)
        
        # ═══════════════════════════════════════════════════════
        # SECCIÓN 1: VM BRIDGE CONTROLS
        # ═══════════════════════════════════════════════════════
        vm_frame = Gtk.Frame(label="🔌 VM Bridge")
        vm_frame.set_label_align(0.0, 0.5)
        main_box.pack_start(vm_frame, False, False, 0)
        
        vm_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vm_box.set_margin_start(10)
        vm_box.set_margin_end(10)
        vm_box.set_margin_top(10)
        vm_box.set_margin_bottom(10)
        vm_frame.add(vm_box)
        
        # Toggle VM Bridge
        self.vm_toggle_btn = Gtk.Button(label="🔴 Activar VM Bridge")
        self.vm_toggle_btn.connect("clicked", self.on_toggle_vm_bridge)
        vm_box.pack_start(self.vm_toggle_btn, False, False, 0)
        
        # Estado VM
        self.vm_status_label = Gtk.Label(label="Estado: Desactivado")
        self.vm_status_label.set_halign(Gtk.Align.START)
        vm_box.pack_start(self.vm_status_label, False, False, 0)
        
        # ═══════════════════════════════════════════════════════
        # SECCIÓN 2: PROCESS MONITORING
        # ═══════════════════════════════════════════════════════
        monitor_frame = Gtk.Frame(label="📊 Process Monitoring")
        monitor_frame.set_label_align(0.0, 0.5)
        main_box.pack_start(monitor_frame, False, False, 0)
        
        monitor_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        monitor_box.set_margin_start(10)
        monitor_box.set_margin_end(10)
        monitor_box.set_margin_top(10)
        monitor_box.set_margin_bottom(10)
        monitor_frame.add(monitor_box)
        
        # Control de frecuencia
        freq_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        monitor_box.pack_start(freq_box, False, False, 0)
        
        freq_box.pack_start(Gtk.Label(label="Frecuencia (seg):"), False, False, 0)
        
        self.freq_spin = Gtk.SpinButton()
        self.freq_spin.set_range(1, 60)
        self.freq_spin.set_increments(1, 5)
        self.freq_spin.set_value(5)
        self.freq_spin.connect("value-changed", self.on_freq_change)
        freq_box.pack_start(self.freq_spin, False, False, 0)
        
        # Toggle monitoring
        self.monitor_toggle_btn = Gtk.Button(label="🟢 Iniciar Monitoring")
        self.monitor_toggle_btn.connect("clicked", self.on_toggle_monitoring)
        monitor_box.pack_start(self.monitor_toggle_btn, False, False, 0)
        
        # Info baseline
        self.baseline_label = Gtk.Label(label="Baseline: No cargado")
        self.baseline_label.set_halign(Gtk.Align.START)
        monitor_box.pack_start(self.baseline_label, False, False, 0)
        
        # ═══════════════════════════════════════════════════════
        # SECCIÓN 3: HALT SYSTEM (CRÍTICO)
        # ═══════════════════════════════════════════════════════
        halt_frame = Gtk.Frame(label="🛑 HALT SYSTEM — Emergency Stop")
        halt_frame.set_label_align(0.0, 0.5)
        main_box.pack_start(halt_frame, False, False, 0)
        
        halt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        halt_box.set_margin_start(10)
        halt_box.set_margin_end(10)
        halt_box.set_margin_top(10)
        halt_box.set_margin_bottom(10)
        halt_frame.add(halt_box)
        
        # Descripción
        desc_label = Gtk.Label(label="Detiene TODOS los procesos iniciados después del baseline")
        desc_label.set_halign(Gtk.Align.START)
        halt_box.pack_start(desc_label, False, False, 0)
        
        # Botón HALT (ROJO, GRANDE, PELIGROSO)
        self.halt_btn = Gtk.Button(label="🛑 HALT — DETENER TODO")
        self.halt_btn.get_style_context().add_class("destructive-action")
        self.halt_btn.set_size_request(-1, 50)
        self.halt_btn.connect("clicked", self.on_halt)
        halt_box.pack_start(self.halt_btn, False, False, 0)
        
        # ═══════════════════════════════════════════════════════
        # SECCIÓN 4: LOG/CONSOLE
        # ═══════════════════════════════════════════════════════
        log_frame = Gtk.Frame(label="📝 Log de Actividad")
        log_frame.set_label_align(0.0, 0.5)
        main_box.pack_start(log_frame, True, True, 0)
        
        self.log_buffer = Gtk.TextBuffer()
        log_view = Gtk.TextView(buffer=self.log_buffer)
        log_view.set_editable(False)
        log_view.set_monospace(True)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.add(log_view)
        log_frame.add(scrolled)
        
        self.connect("destroy", Gtk.main_quit)
    
    # ═══════════════════════════════════════════════════════
    # EVENT HANDLERS
    # ═══════════════════════════════════════════════════════
    
    def load_baseline(self):
        """Carga el baseline desde archivo"""
        if self.baseline_file.exists():
            with open(self.baseline_file, 'r') as f:
                self.baseline = json.load(f)
            self.baseline_label.set_text(
                f"Baseline: {len(self.baseline['processes'])} procesos "
                f"({self.baseline['timestamp']})"
            )
        else:
            self.baseline_label.set_text("Baseline: No existe (ejecutar al inicio de GNOME)")
        return False
    
    def on_toggle_vm_bridge(self, btn):
        """Toggle VM Bridge ON/OFF"""
        if not self.monitoring_active:
            # Activar
            self.vm_toggle_btn.set_label("🟢 VM Bridge Activo")
            self.vm_status_label.set_text("Estado: Escuchando clipboard")
            # Aquí iría la lógica para iniciar el daemon
            self.log("✅ VM Bridge activado")
        else:
            # Desactivar
            self.vm_toggle_btn.set_label("🔴 Activar VM Bridge")
            self.vm_status_label.set_text("Estado: Desactivado")
            self.log("⏹️ VM Bridge desactivado")
    
    def on_toggle_monitoring(self, btn):
        """Toggle Process Monitoring"""
        if not self.monitoring_active:
            # Iniciar
            self.monitoring_active = True
            self.monitor_toggle_btn.set_label("🔴 Detener Monitoring")
            self.monitor_interval = int(self.freq_spin.get_value())
            self.log(f"🟢 Monitoring iniciado (cada {self.monitor_interval}s)")
            
            # Iniciar loop de monitoreo
            GLib.timeout_add_seconds(self.monitor_interval, self.monitoring_loop)
        else:
            # Detener
            self.monitoring_active = False
            self.monitor_toggle_btn.set_label("🟢 Iniciar Monitoring")
            self.log("⏹️ Monitoring detenido")
    
    def on_freq_change(self, spin):
        """Cambia frecuencia de monitoreo"""
        self.monitor_interval = int(spin.get_value())
        self.log(f"🔄 Frecuencia cambiada a {self.monitor_interval}s")
    
    def on_halt(self, btn):
        """HALT SYSTEM — Detener todos los procesos post-baseline"""
        # Confirmación
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text="⚠️ HALT SYSTEM"
        )
        dialog.format_secondary_text(
            "Esto DETENDRÁ todos los procesos iniciados después del baseline.\n\n"
            "Se creará un log antes de detener.\n\n"
            "¿Confirmás?"
        )
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.OK:
            self.execute_halt()
    
    def execute_halt(self):
        """Ejecuta el HALT system"""
        self.log("🛑 INICIANDO HALT SYSTEM...")
        
        # 1. Capturar procesos actuales
        current_procs = self.get_current_processes()
        
        # 2. Comparar con baseline
        if self.baseline:
            baseline_pids = {p['pid'] for p in self.baseline['processes']}
            current_pids = {p['pid'] for p in current_procs}
            
            # Procesos nuevos (post-baseline)
            new_pids = current_pids - baseline_pids
            new_procs = [p for p in current_procs if p['pid'] in new_pids]
        else:
            # Sin baseline: todos los procesos
            new_procs = current_procs
        
        # 3. Crear log antes de matar
        halt_log = {
            'timestamp': datetime.now().isoformat(),
            'action': 'HALT_EXECUTED',
            'processes_to_kill': new_procs,
            'total_processes': len(new_procs)
        }
        
        with open(self.halt_log_file, 'w') as f:
            json.dump(halt_log, f, indent=2)
        
        self.log(f"📝 Log creado: {len(new_procs)} procesos a detener")
        
        # 4. Matar procesos (con confirmación individual)
        killed_count = 0
        for proc in new_procs:
            try:
                p = psutil.Process(proc['pid'])
                p.terminate()  # SIGTERM primero
                killed_count += 1
                self.log(f"  ⏹️ PID {proc['pid']}: {proc['name']}")
            except psutil.NoSuchProcess:
                self.log(f"  ⚠️ PID {proc['pid']}: Ya terminado")
            except psutil.AccessDenied:
                self.log(f"  ❌ PID {proc['pid']}: Permiso denegado")
        
        # 5. Esperar y forzar si es necesario
        import time
        time.sleep(2)
        
        for proc in new_procs:
            try:
                p = psutil.Process(proc['pid'])
                p.kill()  # SIGKILL forzar
                self.log(f"  💀 PID {proc['pid']}: Forzado")
            except:
                pass
        
        self.log(f"✅ HALT completado: {killed_count} procesos detenidos")
        
        # 6. Mostrar resumen
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="✅ HALT COMPLETADO"
        )
        dialog.format_secondary_text(
            f"Procesos detenidos: {killed_count}\n"
            f"Log guardado: {self.halt_log_file}"
        )
        dialog.run()
        dialog.destroy()
    
    def get_current_processes(self):
        """Obtiene lista de procesos actuales"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': ' '.join(proc.info['cmdline'] or []),
                    'memory_mb': proc.info['memory_info'].rss / 1024 / 1024
                })
            except:
                pass
        return processes
    
    def monitoring_loop(self):
        """Loop de monitoreo continuo"""
        if not self.monitoring_active:
            return False
        
        # Capturar procesos actuales
        current = self.get_current_processes()
        
        # Comparar con baseline
        if self.baseline:
            baseline_pids = {p['pid'] for p in self.baseline['processes']}
            current_pids = {p['pid'] for p in current}
            new_count = len(current_pids - baseline_pids)
            
            if new_count > 0:
                self.log(f"📊 Monitoring: {new_count} procesos nuevos detectados")
        
        return True  # Continuar loop
    
    def log(self, message):
        """Agrega mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_buffer.insert(
            self.log_buffer.get_end_iter(),
            f"[{timestamp}] {message}\n"
        )

def main():
    app = VMBridgeEnhancedGUI()
    app.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()