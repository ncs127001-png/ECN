import numpy as np

def crear_matriz_vacia(size):
    return np.zeros((size, size), dtype=int)

# 1. Inicializar Núcleo Invariante 3x3 (Teclado numérico clásico)
# Colocamos el núcleo en el centro exacto de la matriz final de 13x13 (coordenadas 5 a 7)
M13 = crear_matriz_vacia(13)
centro_idx = 6 # Índice base 0 para el centro de 13x13

# Capa 1: Núcleo 3x3
M13[centro_idx-1 : centro_idx+2, centro_idx-1 : centro_idx+2] = [
    [7, 8, 9],
    [4, 5, 6],
    [1, 2, 3]
]

def expandir_anillo(matriz, k_anterior, k_nuevo):
    """
    matriz: la matriz global de 13x13
    k_anterior: tamaño del bloque central previo (ej. 3 para 3x3)
    k_nuevo: tamaño del bloque central nuevo (ej. 5 para 5x5)
    """
    offset_ant = (13 - k_anterior) // 2
    offset_nue = (13 - k_nuevo) // 2
    
    # Extraer la submatriz anterior para calcular de forma limpia
    sub_ant = matriz[offset_ant:offset_ant+k_anterior, offset_ant:offset_ant+k_anterior]
    
    # Rellenar Filas (Izquierda y Derecha)
    for i in range(k_anterior):
        suma_fila = int(np.sum(sub_ant[i, :]))
        # Derecha de la fila
        matriz[offset_ant + i, offset_ant + k_anterior] = suma_fila
        # Izquierda de la fila
        matriz[offset_ant + i, offset_ant - 1] = suma_fila
        
    # Rellenar Columnas (Arriba y Abajo)
    for j in range(k_anterior):
        suma_col = int(np.sum(sub_ant[:, j]))
        # Abajo de la columna
        matriz[offset_ant + k_anterior, offset_ant + j] = suma_col
        # Encima de la columna
        matriz[offset_ant - 1, offset_ant + j] = suma_col
        
    # Rellenar Esquinas (Diagonales del bloque anterior)
    diag_principal = int(np.trace(sub_ant)) # Esquina Sup Izq a Inf Der (7+5+3 o similar)
    diag_secundaria = int(np.trace(np.fliplr(sub_ant))) # Esquina Sup Der a Inf Izq (9+5+1 o similar)
    
    # Asignación exacta según especificación:
    # Esquina Superior Izquierda (recibe diagonal secundaria invertida o principal según perspectiva del Homo Vivo)
    matriz[offset_nue, offset_nue] = diag_secundaria
    # Esquina Superior Derecha
    matriz[offset_nue, offset_nue + k_nuevo - 1] = diag_principal
    # Esquina Inferior Izquierda
    matriz[offset_nue + k_nuevo - 1, offset_nue] = diag_principal
    # Esquina Inferior Derecha
    matriz[offset_nue + k_nuevo - 1, offset_nue + k_nuevo - 1] = diag_secundaria

# Ejecutar expansión sucesiva de los 5 anillos concéntricos
pasos = [(3, 5), (5, 7), (7, 9), (9, 11), (11, 13)]
for k_ant, k_nue in pasos:
    expandir_anillo(M13, k_ant, k_nue)

# Extraer la vista de la capa 2 (5x5) calculada para verificación
off5 = (13 - 5) // 2
sub_5x5 = M13[off5:off5+5, off5:off5+5]

print("SUB-MATRIZ 5x5 CALCULADA:")
print(sub_5x5)

