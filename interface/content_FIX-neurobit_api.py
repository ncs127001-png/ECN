# Modificación quirúrgica para core/event_dispatcher.py o neurobit_api.py
import queue
import threading
import time

class AsyncBatchWriter:
    def __init__(self, target_path="data/memoria_eva.jsonl", flush_interval=2.0):
        self.target_path = target_path
        self.flush_interval = flush_interval
        self.queue = queue.Queue()
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def enqueue_event(self, event_data):
        """Recibe ráfagas masivas del daemon HID sin bloquear el hilo de Socket.IO."""
        self.queue.put(event_data)

    def _worker_loop(self):
        while self.running:
            time.sleep(self.flush_interval)
            buffer = []
            while not self.queue.empty():
                buffer.append(self.queue.get())
            
            if buffer:
                # Escritura única por lote nativa (Bypass de E/S bloqueante)
                with open(self.target_path, 'a', encoding='utf-8') as f:
                    for event in buffer:
                        f.write(event + "\n")

