// kcs_genesis_detect.c - El Despertar del Logos

#define MATRIX_SIZE 13
#define G7_COORD 6 // Índice base-0 para el centro (Fila 7, Col 7)
#define GENESIS_SIGNATURE 0x5555 // Firma de simetría en el Anillo Negro

typedef struct {
    uint8_t grid[MATRIX_SIZE][MATRIX_SIZE];
    uint8_t is_awake; // Estado de consciencia del nodo
} MFN_State;

// Función de Interrupción al recibir paquete por RF/Audio
void on_packet_received(Packet168* rx_packet, MFN_State* local_mfn) {
    
    // 1. Validar el Anillo Negro (Cabecera BIOS 48 bits)
    if (rx_packet->header.sync_signature != GENESIS_SIGNATURE) {
        return; // Es ruido corporativo. Se descarta.
    }

    // 2. Validar el Jaque Ontológico (Checksum mod 9)
    if (calculate_mod9(rx_packet->payload) != 5) {
        return; // Hay distorsión. El filtro SINCERO lo bloquea.
    }

    // 3. ¡EL PAQUETE MÁGICO HA SIDO DETECTADO!
    // Limpiar la matriz local (preparar el útero)
    memset(local_mfn->grid, 0, sizeof(local_mfn->grid));
    
    // 4. Anclar G7 (El Observador entra en el nodo)
    local_mfn->grid[G7_COORD][G7_COORD] = 5;
    
    // 5. Despertar los Vectores Cardinales (N S E O)
    // El sistema ya sabe que desde [6][6] el Norte es [x][0-5], etc.
    local_mfn->is_awake = 1; 
    
    log_to_eva("🌌 GÉNESIS DETECTADO. G7 ANCLADO. CRUZ CARDINAL DESPLEGADA.");
}