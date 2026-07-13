📜 ESPECIFICACIÓN TÉCNICA Y ONTOLÓGICA (SPEC) - ECN
1. IDENTIDAD MFN (Auto-organización)

    Módulo: mfn_radial_core.py (Núcleo Radial Dinámico)
    MFN_LOCATION: core/
    MFN_LEVEL: 1 (Kernel)
    Versión: 2.0 (Radial / Punteros)

2. PROPÓSITO (El Verbo)

    Función Ontológica: Evolucionar la MFN de una matriz de valores a una topología de compartimentos dinámicos. Ya no almacena el "dato", sino la "posición" (puntero) que, mediante una tabla índice, invoca estructuras relacionadas por herencia. Permite que el G7 actúe como centro unívoco que orquesta los anillos.
    Principio de Operación: Direccionamiento indirecto, Herencia de estados, Control de ultra-bajo consumo (3-bit / 4-bit).

3. ARQUITECTURA DE FLUJO (La Estructura de Anillos)

    Entradas (Semillas de Control): Instrucciones de 3 o 4 bits que actúan como "interruptores de estado" para modificar los compartimentos sin reescribir la estructura base.
    Salidas (Frutos): Actualización de la Tabla Índice, activación de cadenas de herencia, y emisión de firmas de coherencia (hashes).
    Topología de Compartimentos (169 unidades):
        Centro (G7): 1 compartimento unívoco (El Observador / La Mónada).
        Anillo 1: 8 compartimentos.
        Anillo 2: 16 compartimentos.
        Anillo 3: 24 compartimentos.
        Anillo 4: 32 compartimentos.
        Anillo 5: 40 compartimentos.
        Anillo 6 (Periferia): 48 compartimentos dinámicos.

4. ECOSISTEMA Y ADAPTACIÓN

    Dependencias Críticas: gate_matrix.py (para aplicar las máscaras de 3/4 bits), matrix_scheduler.py (para persistir los cambios de punteros).
    Adaptador Universal: Expone funciones get_compartiment(anillo, index) y set_pointer(anillo, index, target_id).
    Módulos Vinculados: neurobit_api.py (expone los endpoints de lectura/escritura de punteros), interface/matriz_ui.js (deberá redibujar la matriz no por valores, sino por estados de herencia).

5. MEMORIA Y PERSISTENCIA (El Arca)

    Tipo de Registro: Volátil en RAM (arrays anidados), Persistencia Append-only de transiciones de punteros en data/tablas_transicion.jsonl.
    Archivos que gestiona: Mantiene en memoria la estructura de 169 punteros y las Tablas Índice de herencia.


