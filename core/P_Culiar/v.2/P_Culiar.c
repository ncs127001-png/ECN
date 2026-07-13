#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>
#include <ctype.h>

#define MAX_EXPANSION 2048

void modo_raw(struct termios *original) {
    struct termios raw;
    tcgetattr(STDIN_FILENO, original);
    raw = *original;
    raw.c_lflag &= ~(ECHO | ICANON); 
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw);
}

// Función de reducción numerológica 100% segura usando snprintf
void reducir_numero(long numero, char *resultado_final, size_t max_len) {
    char buffer_actual[256];
    char temp[256];
    
    snprintf(resultado_final, max_len, "%ld", numero);
    snprintf(buffer_actual, sizeof(buffer_actual), "%ld", numero);

    while (1) {
        int len = strlen(buffer_actual);
        
        if (len == 1 || strcmp(buffer_actual, "11") == 0 || 
            strcmp(buffer_actual, "22") == 0 || strcmp(buffer_actual, "33") == 0) {
            break;
        }

        int suma = 0;
        snprintf(temp, sizeof(temp), " [");
        for (int i = 0; i < len; i++) {
            int digito = buffer_actual[i] - '0';
            suma += digito;
            
            char dig_str[8];
            if (i < len - 1) {
                snprintf(dig_str, sizeof(dig_str), "%d+", digito);
            } else {
                snprintf(dig_str, sizeof(dig_str), "%d]", digito);
            }
            strncat(temp, dig_str, sizeof(temp) - strlen(temp) - 1);
        }
        strncat(resultado_final, temp, max_len - strlen(resultado_final) - 1);

        snprintf(buffer_actual, sizeof(buffer_actual), "%d", suma);
        len = strlen(buffer_actual);

        if (len == 1 || strcmp(buffer_actual, "11") == 0 || 
            strcmp(buffer_actual, "22") == 0 || strcmp(buffer_actual, "33") == 0) {
            snprintf(temp, sizeof(temp), " > S%s", buffer_actual); 
        } else {
            snprintf(temp, sizeof(temp), " > R%s", buffer_actual); 
        }
        strncat(resultado_final, temp, max_len - strlen(resultado_final) - 1);
    }
}

void modo_normal(struct termios *original) {
    tcsetattr(STDIN_FILENO, TCSAFLUSH, original);
}

int main() {
    struct termios original;
    modo_raw(&original);

    char entrada[MAX_EXPANSION] = {0};
    int pos = 0;
    char c;

    printf("Módulo numerológico activo. Escribe texto y presiona Shift+F7 para expandir:\n");

    while (1) {
        c = getchar();

        if (c == 27) { 
            char seq[8] = {0};
            int s_pos = 0;
            
            while (s_pos < 7) {
                struct termios topo;
                tcgetattr(STDIN_FILENO, &topo);
                topo.c_cc[VMIN] = 0; topo.c_cc[VTIME] = 1;
                tcsetattr(STDIN_FILENO, TCSAFLUSH, &topo);
                
                char next = getchar();
                
                tcsetattr(STDIN_FILENO, TCSAFLUSH, &original);
                modo_raw(&original); 
                
                if (next == EOF || next == '\0' || next == 27) break;
                seq[s_pos++] = next;
            }

            if (strstr(seq, "18~") != NULL || strstr(seq, "18;") != NULL || seq[1] == 'Q') { 
                int i = pos - 1;
                char cache_num[256] = {0};
                int cache_pos = 0;

                while (i >= 0 && isdigit((unsigned char)entrada[i])) {
                    cache_num[cache_pos++] = entrada[i];
                    i--;
                }

                if (cache_pos > 0) {
                    char num_final[256] = {0};
                    for (int j = 0; j < cache_pos; j++) {
                        num_final[j] = cache_num[cache_pos - 1 - j];
                    }

                    long valor = atol(num_final);
                    char expansion_completa[MAX_EXPANSION] = {0};

                    // CONEXIÓN CORREGIDA: Llamamos al algoritmo real de reducción
                    reducir_numero(valor, expansion_completa, sizeof(expansion_completa));

                    for (int j = 0; j < cache_pos; j++) {
                        printf("\b \b"); 
                    }

                    printf("%s", expansion_completa);
                    fflush(stdout);

                    pos -= cache_pos;
                    pos += snprintf(&entrada[pos], sizeof(entrada) - pos, "%s", expansion_completa);
                }
                continue; 
            }
        }

        if (c == 3) { // Ctrl+C para salir seguro
            break;
        }

        if (c >= 32 && c <= 126) {
            if (pos < MAX_EXPANSION - 1) {
                entrada[pos++] = c;
                putchar(c); 
                fflush(stdout);
            }
        } else if (c == 127 || c == 8) { 
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

