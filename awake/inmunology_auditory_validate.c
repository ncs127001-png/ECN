#include "fuente_neurobit.h"
#include "lexicon_neurobit.h"
#include <string.h>

/**
 * Filtro de Coherencia Ortolingüística
 * @param palabra Cadena de texto recibida desde el canal a 300 baudios
 * @return Estado de validación (1 = LOGOS_VALIDO, 0 = DISTORSION_DETECTADA)
 */
uint8_t auditar_lexico_sincero(const char* palabra) {
    for (int i = 0; i < MAX_DEFINICIONES; i++) {
        if (strcasecmp(palabra, CodiceSoberano[i].vocablo) == 0) {
            // Principio SINCERO: Verificar que tenga dirección y peso real
            if (CodiceSoberano[i].neuronibble == 0x00 || CodiceSoberano[i].mod9_checksum == 0) {
                return 0; // Rechazo por vacío ontológico o distorsión
            }
            
            // Si el sintagma coincide plenamente con el Códice In-Memory, es aceptado
            return 1; 
        }
    }
    return 0; // Si no pertenece al todo definido, se disuelve el token
}

