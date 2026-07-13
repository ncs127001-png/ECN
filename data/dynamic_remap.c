/**
 * Remapea el estado de una matriz aplicando una máscara lógica simétrica (XOR)
 * Permite revelar el manifiesto del bloque oculto sin alterar la ROM física.
 */
void remapear_matriz_xor(uint8_t matriz_entrada[TAM_MATRIZ][TAM_MATRIZ], 
                         uint8_t mascara_bits[TAM_MATRIZ][TAM_MATRIZ],
                         uint8_t matriz_salida[TAM_MATRIZ][TAM_MATRIZ]) {
    
    for (int f = 0; f < TAM_MATRIZ; f++) {
        for (int c = 0; c < TAM_MATRIZ; c++) {
            // Operación XOR simétrica axial bit a bit
            matriz_salida[f][c] = matriz_entrada[f][c] ^ mascara_bits[f][c];
        }
    }
}

