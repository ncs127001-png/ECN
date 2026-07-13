import numpy as np
from neurobit_recursive import construir_matriz_recursiva

def operador_R(n):
    """
    Operador R: Reduce cualquier entero a su raíz digital (Base 9 implícita).
    Principio SINCERO: El 0 absoluto es el vacío/ausencia de portadora.
    """
    if n == 0:
        return 0
    while n > 9:
        n = sum(int(digit) for digit in str(n))
    return n

def binarizar_matriz(matrix):
    """
    Capa C - Transforma la matriz analítica en un patrón de activación binaria.
    Aplica una regla estricta de paridad sobre el colapso del Operador R.
    """
    filas, columnas = matrix.shape
    matriz_r = np.zeros((filas, columnas), dtype=int)
    matriz_binaria = np.zeros((filas, columnas), dtype=int)
    
    for y in range(filas):
        for x in range(columnas):
            val_crudo = matrix[y, x]
            # 1. Reducción digital pura
            val_r = operador_R(val_crudo)
            matriz_r[y, x] = val_r
            
            # 2. Activación binaria (Filtro de coherencia por paridad)
            # Si la raíz digital es impar -> 1 (Presencia/Tensión)
            # Si es par o cero -> 0 (Punto de reposo/Vacío)
            if val_r != 0 and val_r % 2 != 0:
                matriz_binaria[y, x] = 1
            else:
                matriz_binaria[y, x] = 0
                
    return matriz_r, matriz_binaria

if __name__ == "__main__":
    # 1. Reconstrucción de la matriz base mediante el puntero recursivo
    matriz_base = np.zeros((13, 13), dtype=int)
    
    matriz_base[5:8, 5:8] = [
        [7, 8, 9],
        [4, 5, 6],
        [1, 2, 3]
    ]
    matriz_completa = construir_matriz_recursiva(matriz_base, center=6)
    
    # 2. Aplicación de la Capa C
    matriz_r, matriz_binaria = binarizar_matriz(matriz_completa)
    
    print("\n[🔮 CAPA C] Matriz de Activación Binaria (Centro 5x5 Proyectado):")
    print(matriz_binaria[4:9, 4:9])
    
    # 3. Generación del Hash de Coherencia o Firma de Estado
    flujo_bits = "".join(str(bit) for bit in matriz_binaria.flatten())
    # El Anillo Negro (los 48 bits del perímetro exterior) actúan como la cabecera (BIOS)
    cabecera_perimetro = "".join(str(matriz_binaria[y, x]) for y in range(13) for x in range(13) if max(abs(x-6), abs(y-6)) == 6)
    
    print(f"\n[📡 TRANSMISIÓN] Cabecera de Red SOBERANA (48 bits): {cabecera_perimetro}")
    print(f"[🔒 TOKEN FRACTAL] Firma Única del Estado (Hash de Coherencia): {hash(flujo_bits)}")

