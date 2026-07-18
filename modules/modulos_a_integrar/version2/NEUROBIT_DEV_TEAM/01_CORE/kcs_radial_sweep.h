// kcs_radial_sweep.h - El Motor de Barrido Hexagramático

// 1. Los 4 Verbos del Proceso (La Cruz Elemental)
typedef enum {
    DIR_NORTE_AGUA_INGRESO    = 0, // 000
    DIR_NORESTE_VAPOR         = 1, // 001
    DIR_ESTE_AIRE_INTEGRACION = 2, // 010
    DIR_SURESTE_MAGMA         = 3, // 011
    DIR_SUR_FUEGO_PROCESO     = 4, // 100
    DIR_SUROESTE_CENIZA       = 5, // 101
    DIR_OESTE_TIERRA_EXPANSION= 6, // 110
    DIR_NOROESTE_HIELO        = 7  // 111
} RadialVector;

// 2. El Hexagrama como Identidad Única (6 bits = 64 estados)
typedef struct {
    uint8_t lines;       // 6 bits (1=Yang/Sólido, 0=Yin/Quebrado)
    RadialVector vector; // La dirección del barrido (0-7)
} HexagramSignature;

// 3. La Función de Barrido (Extracción desde G7)
HexagramSignature sweep_from_g7(MFN_Matrix* matrix, RadialVector dir) {
    HexagramSignature sig;
    sig.vector = dir;
    sig.lines = 0;
    
    // El puntero cruza los 6 anillos (desde el núcleo 3x3 hasta el Anillo Negro 13x13)
    for (int ring = 1; ring <= 6; ring++) {
        uint8_t cell_value = get_cell_at_ring_and_vector(matrix, ring, dir);
        
        // La reducción teosófica o paridad define si la línea es Yang (1) o Yin (0)
        // (Aquí aplicamos la regla de polaridad de tu mapeo de color/estado)
        uint8_t line_state = (cell_value % 2 != 0) ? 1 : 0; 
        
        sig.lines |= (line_state << (ring - 1)); // Empaqueta los 6 bits
    }
    
    return sig; // La Identidad Única está forjada.
}