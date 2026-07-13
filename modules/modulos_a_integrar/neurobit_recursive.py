import numpy as np

def encontrar_radio_actual(matrix, center):
    """
    Mueve el puntero radialmente hacia afuera desde el centro.
    Detecta la última capa concéntrica que contiene datos válidos (distintos de cero).
    """
    radio = 0
    while True:
        r_evaluar = radio + 1
        # Verificar si el perímetro de este radio tiene datos
        if center - r_evaluar < 0 or center + r_evaluar >= matrix.shape[0]:
            break # Frontera física de la matriz alcanzada
            
        borde_con_datos = False
        for y in range(center - r_evaluar, center + r_evaluar + 1):
            for x in range(center - r_evaluar, center + r_evaluar + 1):
                if max(abs(x - center), abs(y - center)) == r_evaluar:
                    if matrix[y, x] != 0:
                        borde_con_datos = True
        
        if borde_con_datos:
            radio = r_evaluar
        else:
            break # Aquí es donde el puntero detecta el vacío de datos
    return radio

def construir_matriz_recursiva(matrix, center=6):
    """
    Función recursiva pura. Mueve el puntero, detecta el límite actual,
    calcula la capa adyacente basándose estrictamente en la anterior y se re-invoca.
    """
    # 1. Mover el puntero para auditar la frontera actual de datos
    r_actual = encontrar_radio_actual(matrix, center)
    r_siguiente = r_actual + 1
    
    # Condición de parada: Si el siguiente anillo excede el tamaño físico (13x13)
    if center - r_siguiente < 0 or center + r_siguiente >= matrix.shape[0]:
        print(f"[⚙️ SOBERANÍA] El puntero alcanzó la frontera inmutable 13x13. Deteniendo recursión.")
        return matrix

    print(f"[🧅 EXPANSIÓN] Puntero detectó datos hasta radio {r_actual} ({2*r_actual+1}x{2*r_actual+1}). Calculando anillo adyacente {r_siguiente}...")
    
    # 2. Generar el nuevo anillo adyacente sobre la matriz
    # Recorremos el perímetro del nuevo anillo
    for y in range(center - r_siguiente, center + r_siguiente + 1):
        for x in range(center - r_siguiente, center + r_siguiente + 1):
            # Filtrar estrictamente para calcular solo las celdas vacías del nuevo borde
            if max(abs(x - center), abs(y - center)) == r_siguiente:
                
                dx = x - center
                dy = y - center
                
                # --- CASO 1: LATERALES HORIZONTALES (FILAS) ---
                if abs(dx) == r_siguiente and abs(dy) <= r_actual:
                    # Suma la fila correspondiente de la capa anterior
                    # El índice real de la fila en la matriz es 'y'
                    fila_anterior = matrix[y, center - r_actual : center + r_actual + 1]
                    matrix[y, x] = int(np.sum(fila_anterior))
                    
                # --- CASO 2: LATERALES VERTICALES (COLUMNAS) ---
                elif abs(dy) == r_siguiente and abs(dx) <= r_actual:
                    # Suma la columna correspondiente de la capa anterior
                    # El índice real de la columna en la matriz es 'x'
                    columna_anterior = matrix[center - r_actual : center + r_actual + 1, x]
                    matrix[y, x] = int(np.sum(columna_anterior))
                    
                # --- CASO 3: ESQUINAS DIAGONALES ---
                elif abs(dx) == r_siguiente and abs(dy) == r_siguiente:
                    # Suma la diagonal completa de la capa anterior con la misma orientación
                    total_diagonal = 0
                    signo_x = 1 if dx > 0 else -1
                    signo_y = 1 if dy > 0 else -1
                    
                    # Si los signos son iguales, es la diagonal principal (\). Si son opuestos, la secundaria (/)
                    if signo_x == signo_y:
                        # Diagonal Principal de la submatriz previa
                        for i in range(-r_actual, r_actual + 1):
                            total_diagonal += matrix[center + i, center + i]
                    else:
                        # Diagonal Secundaria de la submatriz previa
                        for i in range(-r_actual, r_actual + 1):
                            total_diagonal += matrix[center - i, center + i]
                            
                    matrix[y, x] = total_diagonal

    # 3. Llamada recursiva: El sistema se vuelve a invocar para procesar el siguiente anillo
    return construir_matriz_recursiva(matrix, center)

# --- INICIALIZACIÓN DEL ENTORNO LOCAL ---
if __name__ == "__main__":
    # Matriz física total vacía de 13x13 (Principio SINCERO: inicializada con 0 como ausencia)
    matriz_total = np.zeros((13, 13), dtype=int)
    
    # Inyectar el núcleo inmutable 3x3 en el centro geométrico (coordenadas 5 a 7)
    matriz_total[5:8, 5:8] = [
        [7, 8, 9],
        [4, 5, 6],
        [1, 2, 3]
    ]
    
    print("--- Inicializando Ejecución Concéntrica por Puntero ---")
    matriz_procesada = construir_matriz_recursiva(matriz_total, center=6)
    
    # Imprimir el resultado de la submatriz 5x5 resultante para cotejar simetría
    print("\n[🎯 COTEJO] Submatriz 5x5 calculada dinámicamente:")
    print(matriz_procesada[4:9, 4:9])
