#include "fuente_neurobit.h"

// Inicialización del Charset en la ROM/RAM local
EstadoMatrizCaracter CharsetSoberano[TOTAL_ESTADOS];

/**
 * Extrae la configuración física de una matriz mediante movimiento de puntero
 * @param indice_unicode Código numérico capturado de la secuencia de entrada (Code Point)
 * @param buffer_salida Matriz local 13x13 expandida para procesamiento lógico
 */
void extraer_estado_fuente(uint32_t indice_unicode, uint8_t buffer_salida[TAM_MATRIZ][TAM_MATRIZ]) {
    // Mapeo directo: Limitar el índice al espacio del charset local (0-255)
    uint8_t idx = (uint8_t)(indice_unicode % TOTAL_ESTADOS);
    
    // Apuntar directamente al core del in-memory charset
    EstadoMatrizCaracter *glifo = &CharsetSoberano[idx];
    
    // Desempaquetar el flujo binario compacto de 22 bytes hacia la cuadrícula 13x13
    int bit_actual = 0;
    for (int f = 0; f < TAM_MATRIZ; f++) {
        for (int c = 0; c < TAM_MATRIZ; c++) {
            int byte_pos = bit_actual / 8;
            int bit_pos = bit_actual % 8;
            
            // Leer el estado del bit (0 o 1) en el compartimento
            uint8_t bit = (glifo->bitmap_crudo[byte_pos] >> (7 - bit_pos)) & 0x01;
            buffer_salida[f][c] = bit;
            
            bit_actual++;
        }
    }
}

