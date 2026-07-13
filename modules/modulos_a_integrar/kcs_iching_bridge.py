import numpy as np

# Tabla de correspondencia indexada (Muestra del Diccionario Fijo de 64 posibilidades)
DICCIONARIO_ICHING = {
    "966669": {"Gua_Inferior": "Zhen (Thunder ☳)", "Gua_Superior": "Gen (Mountain ☶)", "Significado": "Balance entre Acción y Stillness"}
}

def extraer_gua_nucleares(hexagrama_str):
    """
    Sigue las directivas de Alfred Huang:
    Usa las líneas del medio para construir la raíz del movimiento.
    """
    if len(hexagrama_str) != 6:
        return "Firma_Invalida"
        
    # Las líneas se cuentan de abajo hacia arriba (índices invertidos en string)
    lineas = list(hexagrama_str)[::-1]
    
    # Gua Inferior: líneas 2, 3, 4 (índices 1, 2, 3)
    gua_inf_nuclear = "".join([lineas[1], lineas[2], lineas[3]])
    # Gua Superior: líneas 3, 4, 5 (índices 2, 3, 4)
    gua_sup_nuclear = "".join([lineas[2], lineas[3], lineas[4]])
    
    return gua_inf_nuclear, gua_sup_nuclear

if __name__ == "__main__":
    print("--- ADAPTADOR MFN: PUENTE RECOLECTOR I CHING ---")
    
    # El token exacto del ensayo de Robert Hale
    token_prueba = "966669"
    
    inf_nuc, sup_nuc = extraer_gua_nucleares(token_prueba)
    meta = DICCIONARIO_ICHING.get(token_prueba, {"Significado": "Frecuencia_Desconocida"})
    
    print(f"\n[⚡ CÓDIGO CRUDO] Hexagrama: {token_prueba}")
    print(f"[☳ GUA INFERIOR] {meta['Gua_Inferior']}")
    print(f"[☶ GUA SUPERIOR] {meta['Gua_Superior']}")
    print(f"[🔮 CORE TAOÍSTA] {meta['Significado']}")
    print(f"[🧬 LÍNEAS NUCLEARES (Huang)] Inferior (2-4): {inf_nuc} | Superior (3-5): {sup_nuc}")

