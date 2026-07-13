import os

def dividir_archivo(archivo_entrada, longitud_maxima=20000, nombre_archivo_salida=None):
    """
    Divide un archivo de texto en fragmentos sin cortar palabras o párrafos.
    :param archivo_entrada: Ruta del archivo de entrada.
    :param longitud_maxima: Longitud máxima de cada fragmento en caracteres.
    :param nombre_archivo_salida: Prefijo para los archivos de salida.
    """
    with open(archivo_entrada, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()

    # Dividir el contenido en párrafos
    parrafos = contenido.split('\n\n')
    fragmentos = []
    fragmento_actual = ""

    for parrafo in parrafos:
        if len(fragmento_actual) + len(parrafo) + 2 <= longitud_maxima:
            # Añadir párrafo al fragmento actual
            if fragmento_actual:
                fragmento_actual += "\n\n" + parrafo
            else:
                fragmento_actual = parrafo
        else:
            # Guardar el fragmento actual y empezar uno nuevo
            fragmentos.append(fragmento_actual)
            fragmento_actual = parrafo

    # Añadir el último fragmento si existe
    if fragmento_actual:
        fragmentos.append(fragmento_actual)

    # Guardar los fragmentos en archivos
    for i, fragmento in enumerate(fragmentos):
        nombre_salida = f"{nombre_archivo_salida}_parte_{i+1}.txt" if nombre_archivo_salida else f"parte_{i+1}.txt"
        with open(nombre_salida, 'w', encoding='utf-8') as archivo_salida:
            archivo_salida.write(fragmento)
        print(f"Archivo guardado: {nombre_salida}")

if __name__ == '__main__':
    nombre_archivo = input("Ingrese el nombre del archivo a dividir: ")
    raw = input("Ingrese la longitud máxima de cada fragmento (por defecto 20000): ")
    try:
        longitud_maxima = int(raw) if raw.strip() else 20000
    except ValueError:
        print("Valor inválido para longitud máxima. Usando 20000.")
        longitud_maxima = 20000

    nombre_archivo_salida = input("Ingrese el prefijo para los archivos de salida (deje vacío para usar 'parte_'): ")
    nombre_archivo_salida = nombre_archivo_salida.strip() if nombre_archivo_salida.strip() else None

    dividir_archivo(nombre_archivo, longitud_maxima, nombre_archivo_salida)
