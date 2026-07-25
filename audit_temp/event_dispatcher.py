#!/usr/bin/env python3
"""
NEUROBIT EVENT DISPATCHER
Patrón: Buffer + Batch Write para reducir I/O
"""

import threading
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from queue import Queue, Empty

class EventDispatcher:
    def __init__(self, 
                 batch_size: int = 20,
                 flush_interval: int = 30,
                 memoria_path: str = "data/memoria_eva.jsonl"):
        
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.memoria_path = Path(memoria_path)
        
        # Buffer en memoria (thread-safe)
        self.buffer: Queue = Queue()
        self.buffer_lock = threading.Lock()
        
        # Estado del dispatcher
        self.running = False
        self.worker_thread = None
        
        # Estadísticas
        self.stats = {
            'events_received': 0,
            'events_written': 0,
            'batches_flushed': 0,
            'last_flush': None
        }
        
        # Asegurar directorio
        self.memoria_path.parent.mkdir(parents=True, exist_ok=True)
    
    def start(self):
        """Iniciar worker thread en background"""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        print(f"✅ Event Dispatcher iniciado (batch={self.batch_size}, interval={self.flush_interval}s)")
    
    def stop(self):
        """Detener dispatcher con flush forzado"""
        if not self.running:
            return
        
        self.running = False
        self._flush_buffer()  # Flush final
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        print(f"✅ Event Dispatcher detenido. Eventos escritos: {self.stats['events_written']}")
    
    def queue_event(self, event: Dict[str, Any]):
        """
        Encolar evento (NO bloqueante)
        Usado por: keylogger, bitácora, centinela, HID
        """
        # Agregar metadata automática
        event['_queued_at'] = datetime.now().isoformat()
        event['_source'] = event.get('source', 'unknown')
        
        self.buffer.put(event)
        self.stats['events_received'] += 1
        
        # Debug opcional (solo en desarrollo)
        # print(f"📥 Evento encolado: {event.get('type', 'unknown')}")
    
    def _worker_loop(self):
        """Loop principal del worker thread"""
        last_flush = time.time()
        batch = []
        
        while self.running:
            try:
                # Intentar obtener evento (timeout corto para verificar flush_interval)
                event = self.buffer.get(timeout=1.0)
                batch.append(event)
                
                # Condición 1: Batch lleno
                if len(batch) >= self.batch_size:
                    self._write_batch(batch)
                    batch = []
                    last_flush = time.time()
                
            except Empty:
                # Timeout: verificar si pasó flush_interval
                pass
            
            # Condición 2: Timeout alcanzado
            if time.time() - last_flush >= self.flush_interval and batch:
                self._write_batch(batch)
                batch = []
                last_flush = time.time()
        
        # Flush final (cualquier evento restante)
        if batch:
            self._write_batch(batch)
    
    def _write_batch(self, batch: List[Dict[str, Any]]):
        """Escribir batch en disco (append-only)"""
        if not batch:
            return
        
        try:
            with open(self.memoria_path, 'a', encoding='utf-8') as f:
                for event in batch:
                    # Remover metadata interna antes de guardar
                    event_clean = {k: v for k, v in event.items() if not k.startswith('_')}
                    f.write(json.dumps(event_clean, ensure_ascii=False) + '\n')
            
            self.stats['events_written'] += len(batch)
            self.stats['batches_flushed'] += 1
            self.stats['last_flush'] = datetime.now().isoformat()
            
            # Debug opcional
            # print(f"💾 Batch escrito: {len(batch)} eventos")
            
        except Exception as e:
            print(f"❌ Error escribiendo batch: {e}")
            # Re-encolar eventos fallidos (opcional)
            for event in batch:
                self.buffer.put(event)
    
    def _flush_buffer(self):
        """Flush forzado de todo el buffer"""
        batch = []
        while not self.buffer.empty():
            try:
                event = self.buffer.get_nowait()
                batch.append(event)
            except Empty:
                break
        
        if batch:
            self._write_batch(batch)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del dispatcher"""
        return {
            **self.stats,
            'buffer_size': self.buffer.qsize(),
            'worker_alive': self.worker_thread.is_alive() if self.worker_thread else False
        }