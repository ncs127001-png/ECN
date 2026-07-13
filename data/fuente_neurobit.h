#ifndef FUENTE_NEUROBIT_H
#define FUENTE_NEUROBIT_H

#include <stdint.h>

#define TAM_MATRIZ 13
#define TOTAL_ESTADOS 255

// 1. Tipo de instrucción mnemotécnica de 4 bits (Nibble de Control)
typedef enum {
    CMD_MOV = 0x8,  // 1000 - Desplaza puntero espacial
    CMD_GET = 0x9,  // 1001 - Extrae estado de matriz local
    CMD_PSH = 0xA,  // 1010 - Empuja estado a la pila 
    CMD_POP = 0xB,  // 1011 - Recupera último estado
    CMD_XOR = 0xC   // 1100 - Aplica máscara simétrica (Sello de Peso)
} MnemotecnicoNibble;

// 2. Definición del Estado de Matriz para un Glifo (Compartimento Soberano)
typedef struct {
    // Matriz de bits crudos (13x13 bits empaquetados eficientemente en bytes)
    // 169 bits se almacenan de forma compacta en un buffer de 22 bytes (176 bits)
    uint8_t bitmap_crudo[22]; 
    
    // Mnemotécnico algorítmico compacto para hardware de 8 bits (estilo LOGO/Código G)
    uint8_t formula_generatriz; 
    
    // Sello de peso (densidad de bits encendidos para decodificación esteganográfica)
    uint8_t sello_peso; 
} EstadoMatrizCaracter;

// 3. El Core In-Memory: Tabla de 255 Matrices del Charset Personal
extern EstadoMatrizCaracter CharsetSoberano[TOTAL_ESTADOS];

#endif // FUENTE_NEUROBIT_H

