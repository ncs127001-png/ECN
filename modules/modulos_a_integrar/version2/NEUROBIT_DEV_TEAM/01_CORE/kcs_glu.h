#ifndef KCS_GLU_H
#define KCS_GLU_H

#include <stdint.h>

typedef enum {
    MODE_LITERAL = 0, MODE_SIMBOLICO = 1, MODE_EMOCIONAL = 2, MODE_KARMICO = 3,
    MODE_ESTRUCTURAL = 4, MODE_TEMPORAL = 5, MODE_INMUNE = 6, MODE_ONTOLOGICO = 7
} NeuroMode;

typedef enum {
    GATE_AND = 0,  // Querer (Síntesis)
    GATE_NAND = 1, // Callar (Inmunidad SINCERO)
    GATE_EAND = 2, // Osar (Expansión Fractal)
    GATE_XOR = 3   // Saber (Disonancia)
} LogicGate;

// El Motor de Procesamiento (La Aguja ◘)
uint8_t glu_process(uint8_t state_a, uint8_t state_b, NeuroMode mode, LogicGate gate) {
    // Filtro SINCERO: Rechazo del vacío corporativo (0x00)
    if (state_a == 0x00 || state_b == 0x00) {
        return 0x00; 
    }

    uint8_t result = 0;
    
    // Lógica Polimórfica basada en la Compuerta (El Verbo)
    switch(gate) {
        case GATE_AND:  result = state_a & state_b; break;
        case GATE_NAND: result = ~(state_a & state_b); break;
        case GATE_EAND: result = (state_a + state_b); break; // Expansión
        case GATE_XOR:  result = state_a ^ state_b; break;
        default:        result = state_a; break;
    }

    // El Modo Ontológico fuerza la reducción Teosófica (mod 9)
    if (mode == MODE_ONTOLOGICO || mode == MODE_KARMICO) {
        while (result > 9) {
            uint8_t sum = 0;
            while (result > 0) { sum += result % 10; result /= 10; }
            result = sum;
        }
        if (result == 0) result = 9; // El 9 es el Yang Viejo, no el vacío.
    }

    return result;
}

#endif // KCS_GLU_H
