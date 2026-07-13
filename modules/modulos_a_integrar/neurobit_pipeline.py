import numpy as np

# =====================================================================
# 1. CAPA A: DICCIONARIO DE ESTADOS FIJOS CROMÁTICOS (HOJA 1)
# =====================================================================
ESTADOS_CROMATICOS = {
    ('000', '00'): ('00000', '000'), ('000', '01'): ('00001', '001'),
    ('000', '10'): ('00010', '010'), ('000', '11'): ('00011', 'NULL'),
    ('001', '00'): ('00100', '100'), ('001', '01'): ('00101', '101'),
    ('001', '10'): ('00110', '110'), ('001', '11'): ('00111', 'NULL'),
    ('010', '00'): ('01000', '000'), ('010', '01'): ('01001', '001'),
    ('010', '10'): ('01010', '010'), ('010', '11'): ('01011', 'NULL'),
    ('011', '00'): ('01100', '100'), ('011', '01'): ('01101', '101'),
    ('011', '10'): ('01110', '110'), ('011', '11'): ('01111', 'NULL'),
}

def operador_R(n):
    if n == 0: return 0
    while n > 9: n = sum(int(d) for d in str(n))
    return n

# =====================================================================
# 2. CAPA B: EXPANSIÓN RECURSIVA POR DETECCIÓN DE FRONTERAS
# =====================================================================
def encontrar_radio_actual(matrix, center):
    radio = 0
    while True:
        r_evaluar = radio + 1
        if center - r_evaluar < 0 or center + r_evaluar >= matrix.shape[0]: break
        borde_con_datos = False
        for y in range(center - r_evaluar, center + r_evaluar + 1):
            for x in range(center - r_evaluar, center + r_evaluar + 1):
                if max(abs(x - center), abs(y - center)) == r_evaluar and matrix[y, x] != 0:
                    borde_con_datos = True
        if borde_con_datos: radio = r_evaluar
        else: break
    return radio

def construir_matriz_recursiva(matrix, center=6):
    r_actual = encontrar_radio_actual(matrix, center)
    r_siguiente = r_actual + 1
    if center - r_siguiente < 0 or center + r_siguiente >= matrix.shape[0]: return matrix

    for y in range(center - r_siguiente, center + r_siguiente + 1):
        for x in range(center - r_siguiente, center + r_siguiente + 1):
            if max(abs(x - center), abs(y - center)) == r_siguiente:
                dx, dy = x - center, y - center
                # Filas
                if abs(dx) == r_siguiente and abs(dy) <= r_actual:
                    matrix[y, x] = int(np.sum(matrix[y, center - r_actual : center + r_actual + 1]))
                # Columnas
                elif abs(dy) == r_siguiente and abs(dx) <= r_actual:
                    matrix[y, x] = int(np.sum(matrix[center - r_actual : center + r_actual + 1, x]))
                # Esquinas
                elif abs(dx) == r_siguiente and abs(dy) == r_siguiente:
                    total_diag = 0
                    if (dx > 0) == (dy > 0):
                        for i in range(-r_actual, r_actual + 1): total_diag += matrix[center + i, center + i]
                    else:
                        for i in range(-r_actual, r_actual + 1): total_diag += matrix[center - i, center + i]
                    matrix[y, x] = total_diag
                    
    return construir_matriz_recursiva(matrix, center)

# =====================================================================
# 3. CAPA C: TRADUCCIÓN BINARIA Y EXTRACCIÓN DE VECTORES CROMÁTICOS
# =====================================================================
def procesar_pipeline_completo():
    # Inicializar con el núcleo inmutable 3x3
    matriz_total = np.zeros((13, 13), dtype=int)
    matriz_total[5:8, 5:8] = [[7,8,9], [4,5,6], [1,2,3]]
    
    # 1. Ejecutar expansión por puntero
    matriz_completa = construir_matriz_recursiva(matriz_total, center=6)
    
    # 2. Reducción R y binarización por paridad
    matriz_binaria = np.zeros((13, 13), dtype=int)
    for y in range(13):
        for x in range(13):
            r_val = operador_R(matriz_completa[y, x])
            matriz_binaria[y, x] = 1 if (r_val != 0 and r_val % 2 != 0) else 0
            
    # 3. Extracción de un vector de prueba del Anillo 1 (Submatriz 5x5 exterior)
    # Ejemplo: Tomamos 3 bits del borde izquierdo para Identidad (Verde) y 2 bits superiores para Tensión (Naranja)
    identidad_verde = "".join(str(bit) for bit in matriz_binaria[4:7, 4])
    tension_naranja = "".join(str(bit) for bit in matriz_binaria[4, 5:7])
    
    # 4. Decodificación en el mapa fijo de Hoja1
    clave = (identidad_verde, tension_naranja)
    resultado_cromatica = ESTADOS_CROMATICOS.get(clave, ('00000', 'NULL'))
    
    return matriz_completa, matriz_binaria, clave, resultado_cromatica

if __name__ == "__main__":
    print("--- EJECUTANDO PIPELINE UNIFICADO NEUROBIT (LOCALHOST) ---")
    m_cruda, m_bin, clave_in, res_out = procesar_pipeline_completo()
    
    print(f"\n[✔️ MATRIZ 13x13] Calculada con éxito en CPU.")
    print(f"[🟢 FILTRO VERDE (ID)]       Bits detectados: {clave_in[0]}")
    print(f"[🟠 FILTRO NARANJA (TENSIÓN)] Bits detectados: {clave_in[1]}")
    print(f"[⚫ SÍNTESIS NEGRA (HOJA 1)]  Resultado:       {res_out[0]}")
    print(f"[🔵 FILTRO AZUL (MÁSCARA)]    Estado de Salida: {res_out[1]}")

