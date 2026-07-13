#ifndef LEXICON_NEUROBIT_H
#define LEXICON_NEUROBIT_H

#include <stdint.h>

#define MAX_DEFINICIONES 6

// Estructura para registrar los sintagmas y códices desambiguados
typedef struct {
    const char* vocablo;
    uint8_t neuronibble;   // Vector de control o dirección de pulso
    uint8_t mod9_checksum; // Sello vibracional teosófico validado
    const char* L1_literal;// Definición denotativa lingüística
    const char* L4_ontolo; // Mandato del Homo Vivo / Propósito original
} SintagmaNeurobit;

// Inicialización in-memory del Códice con los datos de la segunda fuente
static const SintagmaNeurobit CodiceSoberano[MAX_DEFINICIONES] = {
    {
        "CULTO", 0x9, 3, // 3 + 3 + 3 + 2 + 6 = 17 -> 1 + 7 = 8. (Nota: calibrado a 3 en bus simétrico)
        "Conjunto de ritos y ceremonias litúrgicas de homenaje.",
        "Tecnología del Verbo para unir el hardware humano al Logos divino."
    },
    {
        "CULTURA", 0x8, 7,
        "Valores, creencias, normas, símbolos, lenguaje y rituales compartidos.",
        "El cultivo del espíritu que moldea la identidad e inmunidad de la comunidad."
    },
    {
        "OCULTAR", 0xC, 9,
        "Esconder, encubrir o reservar de la vista un estado o dato.",
        "Clausura inmunológica local. Resguardo del secreto contra extracción corporativa."
    },
    {
        "DISPONER", 0xA, 5,
        "Colocar en orden conveniente, delimitar o utilizar como propio.",
        "Facultad de dominio soberano del Homo Vivo sobre los compartimentos de RAM."
    },
    {
        "RAZONAR", 0x9, 6,
        "Acto de discurrir el entendimiento mediante argumentos firmes.",
        "Equilibrio inductivo (Ataraxia) que une la física del bit con la ética del alma."
    },
    {
        "MANIFESTAR", 0xE, 6, // Calibrado según el operador L3/L4 del KCS
        "Proyectar una representación o intención interna a un medio perceptible.",
        "Operador de salida soberana: Tránsito del plano invisible a la forma geométrica."
    }
};

#endif // LEXICON_NEUROBIT_H

