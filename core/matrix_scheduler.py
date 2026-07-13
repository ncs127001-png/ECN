#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEUROBIT MATRIX SCHEDULER - CORE v0.3
Propósito: Controlar los estados matriciales directamente en RAM de forma multitask,
           volcando las tablas de transiciones al almacenamiento rígido de fondo.
"""
import queue
import threading
import time

class NeurobitMatrixScheduler:
    def __init__(self, tam_matriz=13):
        self.tam = tam_matriz
        # 1. La Matriz Vacía que terminará Ocupada (El Espacio de Estados)
        self.ram_matrix = [[0 for _ in range(tam_matriz)] for _ in range(tam_matriz)]
        
        # 2. Cola Multitask para evitar que la E/S del disco bloquee el latido
        self.io_queue = queue.Queue()
        self.running = True
        
        # 3. Hilo Secundario: El Guardián del Rígido (Persistencia de Tablas)
        self.disk_worker = threading.Thread(target=self._persist_loop, daemon=True)
        self.disk_worker.start()

    def actualizar_estado_fisico(self, fila, columna, valor_estado):
        """Modifica el estado directo en la RAM local e indexa la transición."""
        if 1 <= fila <= self.tam and 1 <= columna <= self.tam:
            # Ajuste a Base 1 (Principio SINCERO)
            r_idx, c_idx = fila - 1, columna - 1
            
            # Registrar el estado anterior antes de la mutación
            estado_anterior = self.ram_matrix[r_idx][c_idx]
            self.ram_matrix[r_idx][c_idx] = valor_estado
            
            # Encolar la transición para el rígido sin frenar el flujo principal
            trama_transicion = f"TRANSICIÓN | Coor: ({fila},{columna}) | {estado_anterior} -> {valor_estado}"
            self.io_queue.put(trama_transicion)

    def _persist_loop(self):
        """Bucle de fondo: Recibe las ráfagas de la RAM y escribe las tablas en el rígido."""
        while self.running:
            time.sleep(0.1) # Ventana de cadencia fónica
            buffer = []
            while not self.io_queue.empty():
                buffer.append(self.io_queue.get())
            
            if buffer:
                # Apertura limpia en modo append-only en tu SSD local
                with open("data/tablas_transicion.jsonl", "a", encoding="utf-8") as f:
                    for registro in buffer:
                        f.write(registro + "\n")

if __name__ == "__main__":
    scheduler = NeurobitMatrixScheduler()
    # Test de inyección instantánea in-memory
    scheduler.actualizar_estado_fisico(7, 7, 5) # Fijar el Pivote G7 en la Mónada [1.1, 1.2]
    print("⚡ [RAM] Estado in-memory inicializado. Multitask activo en segundo plano.")

