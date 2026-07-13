// Not_SPQ-Late.c - Compilación óptima con control de estados
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>
#include <ctype.h>
#include <time.h>
#include "config_tandem.h"

struct termios original;

void modo_raw() {
    struct termios raw;
    tcgetattr(STDIN_FILENO, &original);
    raw = original;
    raw.c_lflag &= ~(ECHO | ICANON);
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw);
}

void modo_normal() {
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &original);
}

// Devuelve la descripción según el número semilla
const char* mapear_meta(int semilla) {
    if (semilla == 11) return MAESTROS[0];
    if (semilla == 22) return MAESTROS[1];
    if (semilla == 33) return MAESTROS[2];
    if (semilla >= 1 && semilla <= 9) return ARQUETIPOS[semilla];
    return "Evolucion";
}

// ALGORITMO CON DOBLE BUFFER (Búfer de cálculo vs Búfer de validación)
void procesar_reduccion_teosofica(long numero, char *salida, int *semilla_out) {
    char buf_calculo[MAX_BUFFER];
    char buf_validacion[MAX_BUFFER];
    char temp[MAX_BUFFER];

    // Inicialización del Doble Búfer
    snprintf(buf_calculo, sizeof(buf_calculo), "%ld", numero);
    snprintf(salida, MAX_TRAZA, "%ld", numero);

    while (1) {
        int len = strlen(buf_calculo);

        // Copiar el estado actual al búfer de validación para control
        strncpy(buf_validacion, buf_calculo, sizeof(buf_validacion));

        // CONDICIÓN DE DETENCIÓN INMEDIATA (Semillas y Maestros de corte)
        if (len == 1 || strcmp(buf_validacion, "11") == 0 || 
            strcmp(buf_validacion, "22") == 0 || strcmp(buf_validacion, "33") == 0) {
            *semilla_out = atoi(buf_validacion);
            break; 
        }

        // Desglose aritmético iterativo (Evita recursividad)
        long suma_paso = 0;
        snprintf(temp, sizeof(temp), " [");
        for (int i = 0; i < len; i++) {
            int digito = buf_validacion[i] - '0';
            suma_paso += digito;
            
            char dig_str[16];
            snprintf(dig_str, sizeof(dig_str), (i < len - 1) ? "%d+" : "%d]", digito);
            strncat(temp, dig_str, sizeof(temp) - strlen(temp) - 1);
        }
        strncat(salida, temp, MAX_TRAZA - strlen(salida) - 1);

        // Actualizar el búfer de cálculo con la nueva cifra intermedia
        snprintf(buf_calculo, sizeof(buf_calculo), "%ld", suma_paso);
        
        // Determinar prefijo seguro R o S inspeccionando el siguiente paso
        long sig_len = strlen(buf_calculo);
        if (sig_len == 1 || suma_paso == 11 || suma_paso == 22 || suma_paso == 33) {
            snprintf(temp, sizeof(temp), " > S%ld", suma_paso);
        } else {
            snprintf(temp, sizeof(temp), " > R%ld", suma_paso);
        }
        strncat(salida, temp, MAX_TRAZA - strlen(salida) - 1);
    }
}

void escribir_registro_auditoria(long orig, int sem, const char *traza) {
    FILE *f = fopen(LOG_FILE_PATH, "a");
    if (!f) return;
    
    time_t t = time(NULL);
    struct tm *tm_info = localtime(&t);
    char ts[24];
    strftime(ts, sizeof(ts), "%Y-%m-%d %H:%M:%S", tm_info);

    fprintf(f, "[%s] Entrada: %ld | Semilla: %d | Arquetipo: %s\n", ts, orig, sem, mapear_meta(sem));
    fprintf(f, " Traza: %s\n\n", traza);
    fclose(f);
}

int main() {
    char texto_consola[MAX_TRAZA] = {0};
    int indice_pos = 0;

    printf("╔═══════════════════════════════════════════════════════╗\n");
    printf("║                    Not_SPQ-Late.sh                    ║\n");
    printf("║           Reductor Teosofico Neurobitronico           ║\n");
    printf("╚═══════════════════════════════════════════════════════╝\n");
    printf("Escribe numeros y presiona [SHIFT]+[F7] para expandir: \n\n");

    modo_raw();

    while (1) {
        char c = getchar();
        if (c == 3) break; // Ctrl+C descarte voluntario

        if (c == 27) { // Inicializar captura de secuencia ansi de función
            char seq[16] = {0};
            int s_idx = 0;
            
            while (s_idx < 14) {
                struct termios topo;
                tcgetattr(STDIN_FILENO, &topo);
                topo.c_cc[VMIN] = 0; topo.c_cc[VTIME] = 1;
                tcsetattr(STDIN_FILENO, TCSAFLUSH, &topo);
                char n = getchar();
                tcsetattr(STDIN_FILENO, TCSAFLUSH, &original);
                modo_raw();
                if (n == EOF || n == '\0' || n == 27 || n == '~') {
                    if (n == '~') seq[s_idx++] = n;
                    break;
                }
                seq[s_idx++] = n;
            }

            // Detección de macro Shift+F7 o eventos de interrupción HID
            if (strstr(seq, "18;2~") != NULL || strstr(seq, "18;") != NULL || seq[0] == '[') {
                int i = indice_pos - 1;
                char caching_num[MAX_BUFFER] = {0};
                int c_pos = 0;

                while (i >= 0 && isdigit((unsigned char)texto_consola[i])) {
                    caching_num[c_pos++] = texto_consola[i];
                    i--;
                }

                if (c_pos > 0) {
                    char num_reversado[MAX_BUFFER] = {0};
                    for (int j = 0; j < c_pos; j++) {
                        num_reversado[j] = caching_num[c_pos - 1 - j];
                    }

                    long numero_original = atol(num_reversado);
                    char string_expansion[MAX_TRAZA] = {0};
                    int semilla_final = 0;

                    // Procesamiento modular
                    procesar_reduccion_teosofica(numero_original, string_expansion, &semilla_final);

                    // Reemplazo visual inmediato
                    for (int j = 0; j < c_pos; j++) printf("\b \b");

                    printf("%s [%s]\n", string_expansion, mapear_meta(semilla_final));
                    fflush(stdout);

                    escribir_registro_auditoria(numero_original, semilla_final, string_expansion);
                    
                    // AUTO-CIERRE REQUERIDO: Rompe el bucle de escucha principal al procesar
                    break; 
                }
            }
            continue;
        }

        if (c == 127 || c == 8) {
            if (indice_pos > 0) {
                indice_pos--;
                texto_consola[indice_pos] = '\0';
                printf("\b \b");
                fflush(stdout);
            }
            continue;
        }

        if (c >= 32 && c <= 126) {
            if (indice_pos < MAX_TRAZA - 1) {
                texto_consola[indice_pos++] = c;
                putchar(c);
                fflush(stdout);
            }
        }
    }

    modo_normal();
    printf("\n[LOG] Expansion procesada con exito. Sesion guardada en %s\n", LOG_FILE_PATH);
    return 0;
}

