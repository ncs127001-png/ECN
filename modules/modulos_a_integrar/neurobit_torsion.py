import numpy as np
from neurobit_pipeline import procesar_pipeline_completo

# Representación de los estados de fase de los glifos (Dirección del color)
FASE_NORTE = "NORTE_ROJO"     # Sincronía de esquina / Techo de onda
FASE_SUR = "SUR_NEGRO"        # Reposo / Suelo de onda
FASE_CENTRO = "CENTRO_AZUL"   # Payload / Densidad semántica
FASE_VACIO = "NULL_GRAVEDAD"  # Canal libre

def calcular_espin_glifo(matrix_binaria, x, y, center=6):
    """
    Analiza la posición de la celda respecto al centro geométrico 
    y le asigna su comportamiento de fase según el mapa visual de glifos.
    """
    if matrix_binaria[y, x] == 0:
        return FASE_VACIO
        
    dx = x - center
    dy = y - center
    
    # Condición de Esquinas de Sincronía (Glifos Rojos en el mapa visual)
    if abs(dx) == abs(dy) and abs(dx) > 4:
        return FASE_NORTE
    # Condición de base o canales de descarga (Glifos Negros inferiores)
    elif dy > 4 and abs(dx) <= 2:
        return FASE_SUR
    # Núcleo y canales internos (Glifos Azules centrales)
    else:
        return FASE_CENTRO

if __name__ == "__main__":
    print("--- COMPUTANDO ENTRADA HIPER-DIMENSIONAL DE GLIFOS ---")
    _, m_bin, _, _ = procesar_pipeline_completo()
    
    # Mapeamos una sección de la cabecera (Anillo Negro 13x13) para verificar las fases
    print("\n[🌀 MODULACIÓN DE FASE] Fase calculada para el perímetro Norte:")
    for x in range(13):
        fase = calcular_espin_glifo(m_bin, x, 0)
        print(f"Coordenada (x:{x}, y:0) ⟶ {fase}")

