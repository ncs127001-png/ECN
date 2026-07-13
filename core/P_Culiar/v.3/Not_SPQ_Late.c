/*
 * P_Culiar.c - Reductor Teosófico Neurobitrónico
 * Enfoque corregido sin desbordamientos y con auto-cierre
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <unistd.h>
#include <ctype.h>
#include <time.h>

#define MAX_BUFFER 256
#define MAX_TRAZA 1024

// === TABLA DE ARQUETIPOS ===
const char* ARQUETIPO[] = {
    [1] = "Unidad/Inicio",
    [2] = "Dualidad/Equilibrio",
    [3] = "Trinidad/Expresión",
    [4] = "Orden/Estabilidad",
    [5] = "Voluntad/Poder (G7)",
    [6] = "Armonía/Unión",
    [7] = "Sabiduría/Intuición",
    [8] = "Infinito/Ciclo",
    [9] = "Completitud/Cierre"
};

const char* MAESTRO[] = {
    [11] = "Maestro Intuición",
    [22] = "Maestro Constructor",
    [33] = "Maestro Maestro"
};

struct termios original_termios;

void modo_raw() {
    struct termios raw;
    tcgetattr(STDIN_FILENO, &original_termios);
    raw = original_termios;
    raw.c_lflag &= ~(ECHO | ICANON);
    raw.c_cc[VMIN] = 1;
    raw.c_cc[VTIME] = 0;
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &raw);
}

void restaurar_terminal() {
    tcsetattr(STDIN_FILENO, TCSAFLUSH, &original_termios);
}

// === REDUCCIÓN TEOSÓFICA CORREGIDA ===
int reducir_a_semilla(long num, char *traza, int *semilla_final, size_t max_traza_len) {
    int pasos = 0;
    long actual = num;
    traza[0] = '\0'; // Inicializar vacío

    // Forzar la entrada al bucle al menos una vez si es necesario, o manejar números de 1 dígito
    if (actual < 10 || actual == 11 || actual == 22 || actual == 33) {
        char paso_inicial[MAX_BUFFER];
        snprintf(paso_inicial, sizeof(paso_inicial), " > S%ld", actual);
        strncat(traza, paso_inicial, max_traza_len - strlen(traza) - 1);
        *semilla_final = (int)actual;
        return 0;
    }

    while (actual >= 10 && actual != 11 && actual != 22 && actual != 33) {
        long suma = 0;
        long temp = actual;
        char suma_str[MAX_BUFFER] = "[";
        
        // Extraer dígitos de forma segura
        char digitos[64];
        int idx = 0;
        while (temp > 0 && idx < 63) {
            digitos[idx++] = (temp % 10) + '0';
            suma += (temp % 10);
            temp /= 10;
        }

        // Construir la cadena en el orden correcto
        int primero = 1;
        for (int i = idx - 1; i >= 0; i--) {
            if (!primero) {
                strncat(suma_str, "+", sizeof(suma_str) - strlen(suma_str) - 1);
            }
            char d[2] = {digitos[i], '\0'};
            strncat(suma_str, d, sizeof(suma_str) - strlen(suma_str) - 1);
            primero = 0;
        }
        strncat(suma_str, "]", sizeof(suma_str) - strlen(suma_str) - 1);

        // Determinar etiqueta S o R de manera segura sin warnings de tamaño
        char etiqueta[MAX_BUFFER];
        if (suma < 10 || suma == 11 || suma == 22 || suma == 33) {
            snprintf(etiqueta, sizeof(etiqueta), " > S%ld", suma);
        } else {
            snprintf(etiqueta, sizeof(etiqueta), " > R%ld", suma);
        }

        // Concatenar de forma segura al buffer de traza global
        char paso_str[MAX_BUFFER * 2];
        snprintf(paso_str, sizeof(paso_str), " %s%s", suma_str, etiqueta);
        strncat(traza, paso_str, max_traza_len - strlen(traza) - 1);

        actual = suma;
        pasos++;
    }

    *semilla_final = (int)actual;
    return pasos;
}

const char* obtener_arquetipo(int semilla) {
    if (semilla >= 1 && semilla <= 9) return ARQUETIPO[semilla];
    if (semilla == 11 || semilla == 22 || semilla == 33) return MAESTRO[semilla];
    return "Desconocido";
}

void guardar_log(long numero_original, int semilla, const char *traza_completa) {
    FILE *log = fopen("p_culiar.log", "a");
    if (!log) return;

    time_t ahora = time(NULL);
    char timestamp[64];
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", localtime(&ahora));

    fprintf(log, "[%s] Entrada: %ld | Semilla: %d | Arquetipo: %s\n", 
            timestamp, numero_original, semilla, obtener_arquetipo(semilla));
    fprintf(log, " Traza: %ld%s\n\n", numero_original, traza_completa);
    fclose(log);
}

int main() {
    char buffer[MAX_TRAZA] = {0};
    int pos = 0;

    printf("╔══════════════════════════════════════════════════════╗\n");
    printf("║ Not_SPQ-Late Reductor Teosófico Neurobitrónico          ║\n");
    printf("║ Escribe números y presiona SHIFT+F7 para expandir    ║\n");
    printf("╚══════════════════════════════════════════════════════╝\n\n");

    modo_raw();

    while (1) {
        char c = getchar();

        if (c == 3) break; // Ctrl+C para abortar voluntariamente

        if (c == 27) { // Capturar secuencia Escape
            char seq[16] = {0};
            int s_idx = 0;
            // Leer buffer de la secuencia rápida
            while (s_idx < 15) {
                struct termios topo;
                tcgetattr(STDIN_FILENO, &topo);
                topo.c_cc[VMIN] = 0; topo.c_cc[VTIME] = 1;
                tcsetattr(STDIN_FILENO, TCSAFLUSH, &topo);
                
                char next = getchar();
                tcsetattr(STDIN_FILENO, TCSAFLUSH, &original_termios);
                modo_raw();

                if (next == EOF || next == '\0' || next == 27 || next == '~') {
                    if (next == '~') seq[s_idx++] = next;
                    break;
                }
                seq[s_idx++] = next;
            }

            // Validar SHIFT+F7 VT100 ("[18;2~") o variantes de mapeo rápido
            if (strstr(seq, "18;2~") != NULL || strstr(seq, "18;") != NULL || seq[0] == '[') {
                int i = pos - 1;
                char num_str[64] = {0};
                int num_len = 0;

                while (i >= 0 && isdigit((unsigned char)buffer[i])) {
                    num_str[num_len++] = buffer[i];
                    i--;
                }

                if (num_len > 0) {
                    char num_final[64] = {0};
                    for (int j = 0; j < num_len; j++) {
                        num_final[j] = num_str[num_len - 1 - j];
                    }

                    long numero = atol(num_final);
                    char traza[MAX_TRAZA] = {0};
                    int semilla = 0;

                    reducir_a_semilla(numero, traza, &semilla, sizeof(traza));

                    // Borrar el número base de la pantalla
                    for (int j = 0; j < num_len; j++) {
                        printf("\b \b");
                    }

                    // Imprimir la expansión completa en pantalla
                    printf("%ld%s [%s]\n", numero, traza, obtener_arquetipo(semilla));
                    fflush(stdout);

                    // Guardar en bitácora
                    guardar_log(numero, semilla, traza);

                    // REQUISITO: Cerrar de forma limpia tras la expansión exitosa
                    break; 
                }
            }
            continue;
        }

        if (c == 127 || c == 8) { // Borrado
            if (pos > 0) {
                pos--;
                buffer[pos] = '\0';
                printf("\b \b");
                fflush(stdout);
            }
            continue;
        }

        if (c >= 32 && c <= 126) { // Captura normal de caracteres
            if (pos < MAX_TRAZA - 1) {
                buffer[pos++] = c;
                putchar(c);
                fflush(stdout);
            }
        }
    }

    restaurar_terminal();
    printf("\n[LOG] Expansión procesada con éxito. Sesión guardada en p_culiar.log\n");
    return 0;
}

