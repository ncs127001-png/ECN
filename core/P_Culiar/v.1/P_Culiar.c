#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>
#include <ctype.h>

// Configura la terminal para leer carácter por carácter inmediatamente
void modo_raw(struct termios *original) {
    struct termios raw;
    tcgetattr(STDIN_FILENO, original);
    raw = *original;
    raw.c_lflag &= ~(ECHO | ICANON); // Desactiva el eco y el buffer de línea
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw);
}

// Función que calcula la reducción paso a paso
void reducir_numero(long numero, char *resultado_final) {
    char buffer_actual[256];
    char temp[256];
    
    // Inicializar el resultado con el número original
    sprintf(resultado_final, "%ld", numero);
    sprintf(buffer_actual, "%ld", numero);

    // Bucle de reducción
    while (1) {
        int len = strlen(buffer_actual);
        
        // CONDICIÓN DE SALIDA: Si es de 1 cifra, o es un número maestro (11, 22, 33)
        if (len == 1 || strcmp(buffer_actual, "11") == 0 || 
            strcmp(buffer_actual, "22") == 0 || strcmp(buffer_actual, "33") == 0) {
            break;
        }

        // 1. Construir la cadena de la suma individual: [1+6+9]
        int suma = 0;
        sprintf(temp, " [");
        for (int i = 0; i < len; i++) {
            int digito = buffer_actual[i] - '0';
            suma += digito;
            
            char dig_str[8];
            if (i < len - 1) {
                sprintf(dig_str, "%d+", digito);
            } else {
                sprintf(dig_str, "%d]", digito);
            }
            strcat(temp, dig_str);
        }
        strcat(resultado_final, temp);

        // 2. Preparar el siguiente número (la suma resultante)
        sprintf(buffer_actual, "%d", suma);
        len = strlen(buffer_actual);

        // 3. Determinar si el nuevo número es Semilla (S) o una Reducción intermedia (R)
        if (len == 1 || strcmp(buffer_actual, "11") == 0 || 
            strcmp(buffer_actual, "22") == 0 || strcmp(buffer_actual, "33") == 0) {
            sprintf(temp, " > S%s", buffer_actual); // Llegamos a la semilla
        } else {
            sprintf(temp, " > R%s", buffer_actual); // Es una reducción intermedia
        }
        strcat(resultado_final, temp);
    }
}


// Restaura la terminal a su estado normal
void modo_normal(struct termios *original) {
    tcsetattr(STDIN_FILENO, TCSAFLUSH, original);
}

int main() {
    struct termios original;
    modo_raw(&original);

    char entrada[1024] = {0};
    int pos = 0;
    char c;

    printf("Módulo activo. Escribe texto y presiona Shift+F7 (o F7 según terminal) para expandir:\n");

    while (1) {
        c = getchar();

        // Detectar secuencias de escape (Teclas especiales como F7)
        // Nota: SHIFT+F7 usualmente envía la secuencia: ESC [ 1 8 ; 2 ~ o similar
        if (c == 27) { 
            char seq[8] = {0};
            int s_pos = 0;
            
            // Leer el resto de la secuencia de escape
            while (s_pos < 7) {
                // Pequeño truco de lectura no bloqueante para la secuencia
                struct termios topo;
                tcgetattr(STDIN_FILENO, &topo);
                topo.c_cc[VMIN] = 0; topo.c_cc[VTIME] = 1;
                tcsetattr(STDIN_FILENO, TCSAFLUSH, &topo);
                
                char next = getchar();
                
                tcsetattr(STDIN_FILENO, TCSAFLUSH, &original);
                modo_raw(&original); // Re-armar raw
                
                if (next == EOF || next == '\0' || next == 27) break;
                seq[s_pos++] = next;
            }

            // Validación de la tecla de expansión (Ejemplo genérico de F7/Shift+F7 en VT100: "[18~" o "[18;2~")
            if (strstr(seq, "18~") != NULL || strstr(seq, "18;") != NULL || seq[1] == 'Q') { 
                
                // --- INICIO DEL ALGORITMO DE EXPANSIÓN (Tu Pseudocódigo) ---
                int i = pos - 1;
                char cache_num[256] = {0};
                int cache_pos = 0;

                // Capturar dígitos hacia atrás hasta encontrar un espacio o inicio
                while (i >= 0 && isdigit(entrada[i])) {
                    cache_num[cache_pos++] = entrada[i];
                    i--;
                }

                if (cache_pos > 0) {
                    // Voltear la caché porque se leyó al revés
                    char num_final[256] = {0};
                    for (int j = 0; j < cache_pos; j++) {
                        num_final[j] = cache_num[cache_pos - 1 - j];
                    }

                    // Lógica de expansión automática (Ejemplo: duplicar el valor o procesarlo)
                    long valor = atol(num_final);
                    long resultado_expandido = valor * 2; // Aquí va tu lógica matemática/individual

                    // Borrar el número visualmente en la terminal (Simular Backspaces)
                    for (int j = 0; j < cache_pos; j++) {
                        printf("\b \b"); 
                    }

                    // Imprimir el resultado de la expansión automática en la terminal
                    printf("[EXPANDIDO:%ld]", resultado_expandido);
                    fflush(stdout);

                    // Actualizar el buffer interno de texto
                    pos -= cache_pos;
                    pos += sprintf(&entrada[pos], "[EXPANDIDO:%ld]", resultado_expandido);
                }
                continue; 
            }
        }

        // Salida limpia con Ctrl+C (ASCII 3)
        if (c == 3) {
            break;
        }

        // Manejo normal de caracteres de texto
        if (c >= 32 && c <= 126) {
            entrada[pos++] = c;
            putchar(c); // Hacer eco manual del carácter
            fflush(stdout);
        } else if (c == 127 || c == 8) { // Backspace
            if (pos > 0) {
                pos--;
                entrada[pos] = '\0';
                printf("\b \b");
                fflush(stdout);
            }
        }
    }

    modo_normal(&original);
    return 0;
}

