#!/usr/bin/env python3
"""
neurobit_gnome_widget.py
GUI nativa para GNOME (sin navegador)
Captura rondas, mensajes, headers automáticamente
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import requests
import json
from pathlib import Path
from datetime import datetime

class NeurobitWidget(Gtk.Window):
    def __init__(self):
        super().__init__(title="🧠 NEUROBIT Widget")
        self.set_default_size(400, 600)
        self.set_keep_above(True)  # Siempre visible
        # self.set_opacity(0.95)  # ⚠️ DEPRECATION WARNING - comentar si molesta
        
        # Estado
        self.current_round = None
        self.message_count = 0
        self.api_url = "http://localhost:5000"
        
        # UI
        self.init_ui()
        
        # WebSocket connection (opcional)
        self.ws_connected = False
        
    def init_ui(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        self.add(box)
        
        # Header
        header = Gtk.Label()
        header.set_markup("<b>🧠 NEUROBIT Widget</b>\n<small>R.E.D. SOBERANA</small>")
        box.pack_start(header, False, False, 0)
        
        # Estado de conexión
        self.status_label = Gtk.Label(label="🔴 Desconectado")
        self.status_label.set_halign(Gtk.Align.START)
        box.pack_start(self.status_label, False, False, 0)
        
        # Ronda actual
        round_frame = Gtk.Frame(label="Ronda Actual")
        box.pack_start(round_frame, False, False, 0)
        
        round_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        round_frame.add(round_box)
        
        self.round_label = Gtk.Label(label="Ninguna")
        round_box.pack_start(self.round_label, False, False, 0)
        
        btn_open = Gtk.Button(label="📢 Abrir")
        btn_open.connect("clicked", self.on_open_round)
        round_box.pack_start(btn_open, False, False, 0)
        
        btn_close = Gtk.Button(label="✅ Cerrar")
        btn_close.connect("clicked", self.on_close_round)
        round_box.pack_start(btn_close, False, False, 0)
        
        # Contador de mensajes
        msg_frame = Gtk.Frame(label="Mensajes en Ronda")
        box.pack_start(msg_frame, False, False, 0)
        
        self.msg_count_label = Gtk.Label(label="0")
        msg_frame.add(self.msg_count_label)
        
        # Botón capturar
        btn_capture = Gtk.Button(label="🎯 Capturar Respuestas")
        btn_capture.connect("clicked", self.on_capture)
        box.pack_start(btn_capture, False, False, 0)
        
        # Historial reciente
        hist_frame = Gtk.Frame(label="Últimas Capturas")
        box.pack_start(hist_frame, False, False, 0)
        
        self.hist_list = Gtk.ListBox()
        self.hist_list.set_selection_mode(Gtk.SelectionMode.NONE)
        hist_frame.add(self.hist_list)
        
        # Scroll
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        box.pack_start(scrolled, True, True, 0)
        
        # Check connection and check_vm
        GLib.timeout_add_seconds(5, self.check_connection)
        GLib.timeout_add_seconds(10, self.check_vm_status)
        
    def check_connection(self):
        try:
            resp = requests.get(f"{self.api_url}/health", timeout=2)
            if resp.status_code == 200:
                self.status_label.set_label("🟢 Conectado")
                self.ws_connected = True
        except:
            self.status_label.set_label("🔴 Desconectado")
            self.ws_connected = False
        return True

    def check_vm_status(self):
        """Verificar si hay VMs activas"""
        try:
            resp = requests.get(f"{self.api_url}/vms/status", timeout=2)
            if resp.status_code == 200:
                vms = resp.json().get('vms', [])
                active_vms = [vm for vm in vms if vm.get('estado') == 'active']
                
                if active_vms:
                    vm_label = Gtk.Label(label=f"🖥️ {len(active_vms)} VM(s) activa(s)")
                    vm_label.set_halign(Gtk.Align.START)
                    self.status_label.get_parent().pack_start(vm_label, False, False, 0)
        except:
            pass
        return True

    def on_open_round(self, button):
        self.message_count = 0
        self.current_round = f"R{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        payload = {
            "round_id": self.current_round,
            "round_number": self.message_count,
            "scrum_master": "NODO_SEMILLA",
            "opened_at": datetime.now().isoformat(),
            "participants": ["ollama", "chatgpt", "gemini"],
            "status": "open"
        }
        
        try:
            requests.post(f"{self.api_url}/round/open", json=payload, timeout=2)
            self.round_label.set_label(self.current_round)
            self.msg_count_label.set_label("0")
            print(f"✅ Ronda abierta: {self.current_round}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def on_close_round(self, button):
        if self.current_round:
            try:
                requests.post(f"{self.api_url}/round/complete", 
                            json={"round_id": self.current_round}, timeout=2)
                self.round_label.set_label("Ninguna")
                self.current_round = None
                print(f"✅ Ronda cerrada: {self.current_round}")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def on_capture(self, button):
        """Capturar respuestas vía HID daemon"""
        print("🎯 Capturando respuestas...")
        
        # 1. Leer último mensaje del clipboard (Centinela)
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard_text = clipboard.wait_for_text()
        
        # 2. Enviar a API para registro
        payload = {
            "round_id": self.current_round,
            "message": clipboard_text,
            "timestamp": datetime.now().isoformat(),
            "source": "GNOME_WIDGET"
        }
        
        try:
            resp = requests.post(
                f"{self.api_url}/api/capture",
                json=payload,
                timeout=2
            )
            
            # 3. Agregar al historial
            if resp.status_code == 200:
                self.message_count += 1
                self.msg_count_label.set_label(str(self.message_count))
                
                # Agregar entrada al ListBox
                entry = Gtk.Label(
                    label=f"✅ Capturado {self.message_count} - {datetime.now().strftime('%H:%M')}"
                )
                entry.set_halign(Gtk.Align.START)
                self.hist_list.add(entry)
                self.hist_list.show_all()
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    win = NeurobitWidget()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
