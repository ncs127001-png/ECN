import numpy as np

# Definición inmutable de los Estados Fijos Cromáticos extraídos de Hoja1
ESTADOS_CROMATICOS = {
    # Formato del Token: (Identidad_3b, Tensión_2b) -> (Síntesis_5b, Salida_3b)
    ('000', '00'): ('00000', '000'),
    ('000', '01'): ('00001', '001'),
    ('000', '10'): ('00010', '010'),
    ('000', '11'): ('00011', 'NULL'), # Celda Azul / Máscara de absorción
    
    ('001', '00'): ('00100', '100'),
    ('001', '01'): ('00101', '101'),
    ('001', '10'): ('00110', '110'),
    ('001', '11'): ('00111', 'NULL'),
    
    ('010', '00'): ('01000', '000'),
    ('010', '01'): ('01001', '001'),
    ('010', '10'): ('01010', '010'),
    ('010', '11'): ('01011', 'NULL'),
    
    ('011', '00'): ('01100', '100'),
    ('011', '01'): ('01101', '101'),
    ('011', '10'): ('01110', '110'),
    ('011', '11'): ('01111', 'NULL'),
}

def decodificar_vector_chroma(identidad, tension):
    """
    Busca la correspondencia exacta en el mapa de estados fijos de la Hoja1.
    Elimina la incertidumbre estadística.
    """
    id_str = "".join(str(b) for b in identidad)
    ten_str = "".join(str(b) for b in tension)
    
    clave = (id_str, ten_str)
    resultado = ESTADOS_CROMATICOS.get(clave, ('00000', 'NULL'))
    
    return {
        "Bloque_Verde": id_str,
        "Bloque_Naranja": ten_str,
        "Bloque_Negro_Sintesis": resultado[0],
        "Bloque_Amarillo_Salida": resultado[1]
    }

if __name__ == "__main__":
    print("--- Inicializando Auditor Cromático Neurobit (Hoja1) ---")
    
    # Simulación de un pulso de entrada en el buffer local
    test_id = [0, 0, 1]      # Verde
    test_ten = [1, 0]      # Naranja
    
    estado_fijo = decodificar_vector_chroma(test_id, test_ten)
    
    print(f"\n[🟢 ENTRADA VERDE]   Identidad: {estado_fijo['Bloque_Verde']}")
    print(f"[🟠 ENTRADA NARANJA] Tensión:   {estado_fijo['Bloque_Naranja']}")
    print(f"[⚫ SÍNTESIS NEGRA]  Resultado: {estado_fijo['Bloque_Negro_Sintesis']}")
    print(f"[🟡 SALIDA AMARILLA] Destino:   {estado_fijo['Bloque_Amarillo_Salida']}")

