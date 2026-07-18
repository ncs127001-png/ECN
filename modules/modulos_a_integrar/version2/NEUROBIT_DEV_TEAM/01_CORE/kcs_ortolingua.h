#ifndef KCS_ORTOLINGUA_H
#define KCS_ORTOLINGUA_H

#include <stdint.h>

typedef enum {
    ROOT_DECIR       = 0x04, 
    ROOT_MANIFESTAR  = 0x05, 
    ROOT_ENTE        = 0x06, 
    ROOT_VICIAR      = 0x00  
} FractalRoot;

typedef enum {
    M_LITERAL    = 0, 
    M_SIMBOLICO  = 1, 
    M_TECNICO    = 2, 
    M_ONTOLOGICO = 7  
} ReadingMode;

typedef struct {
    uint8_t root   : 4;  
    uint8_t mode   : 3;  
    uint8_t state  : 1;  
} OrtoToken;

uint8_t encode_verbo(FractalRoot r, ReadingMode m, uint8_t is_manifest) {
    OrtoToken token;
    token.root = r;
    token.mode = m;
    token.state = is_manifest;
    
    if (token.root == 0x00) return 0x00; 
    
    return *(uint8_t*)&token; 
}

#endif // KCS_ORTOLINGUA_H
