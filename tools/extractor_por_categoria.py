#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extractor_por_categoria.py
Extrae mensajes clasificados desde el historial numerado
y genera archivos separados por categoría.

Autor: NODO_SEMILLA NEUROBIT
Versión: 1.0
"""

import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class ExtractorPorCategoria:
    """Extrae mensajes clasificados y genera archivos por categoría."""
    
    def __init__(self, archivo_clasificacion: str, archivo_numerado: str, carpeta_salida: str = None):
        self.archivo_clasificacion = Path(archivo_clasificacion)
        self.archivo_numerado = Path(archivo_numerado)
        self.carpeta_salida = Path(carpeta_salida) if carpeta_salida else Path("./mensajes_extraidos")
        
        self.categorias = {
            'TECNICO': [],
            'ONTOLOGICO': [],
            'COORDINACION': [],
            'INTERRUPCION': [],
            'HISTORIA': [],
            'REALIZADO': []
        }
        
        self.mensajes_numerados = {}
        
    def leer_clasificacion(self) -> dict:
        """Lee el archivo de clasificación y extrae número → categoría."""
        if not self.archivo_clasificacion.exists():
            raise FileNotFoundError(f"Archivo de clasificación no encontrado: {self.archivo_clasificacion}")
        
        clasificacion = {}
        patron = re.compile(r'^MENSAJE\s+(\d+):\s+\[([A-Z_]+)\]', re.MULTILINE)
        
        with open(self.archivo_clasificacion, 'r', encoding='utf-8') as f:
            contenido = f.read()
            matches = patron.findall(contenido)
            
            for numero, categoria in matches:
                clasificacion[int(numero)] = categoria
        
        print(f"📋 Clasificaciones leídas: {len(clasificacion)} mensajes")
        return clasificacion
    
    def leer_mensajes_numerados(self) -> dict:
        """Lee el archivo numerado y extrae cada mensaje completo."""
        if not self.archivo_numerado.exists():
            raise FileNotFoundError(f"Archivo numerado no encontrado: {self.archivo_numerado}")
        
        with open(self.archivo_numerado, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Patrón para identificar inicio de cada mensaje
        patron_mensaje = re.compile(
            r'═{70}\nMENSAJE N°:\s*(\d+)\n.*?═{70}\n(.*?)\n─{70}\nFIN MENSAJE',
            re.DOTALL
        )
        
        mensajes = {}
        for match in patron_mensaje.finditer(contenido):
            numero = int(match.group(1))
            contenido_mensaje = match.group(2).strip()
            mensajes[numero] = contenido_mensaje
        
        print(f"📦 Mensajes numerados leídos: {len(mensajes)} mensajes")
        return mensajes
    
    def clasificar_mensajes(self, clasificacion: dict, mensajes: dict):
        """Clasifica cada mensaje en su categoría correspondiente."""
        for numero, categoria in clasificacion.items():
            if numero in mensajes and categoria in self.categorias:
                self.categorias[categoria].append({
                    'numero': numero,
                    'contenido': mensajes[numero]
                })
        
        print(f"📊 Mensajes clasificados por categoría:")
        for cat, lista in self.categorias.items():
            print(f"  {cat}: {len(lista)} mensajes")
    
    def generar_archivos(self):
        """Genera archivos de texto separados por categoría."""
        self.carpeta_salida.mkdir(parents=True, exist_ok=True)
        
        archivos_generados = []
        
        for categoria, mensajes in self.categorias.items():
            if mensajes:  # Solo generar archivo si hay mensajes
                nombre_archivo = f"mensajes_{categoria.lower()}.txt"
                ruta_archivo = self.carpeta_salida / nombre_archivo
                
                with open(ruta_archivo, 'w', encoding='utf-8') as f:
                    # Encabezado
                    f.write("=" * 70 + "\n")
                    f.write(f"NEUROBIT — MENSAJES {categoria}\n")
                    f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Total mensajes: {len(mensajes)}\n")
                    f.write("=" * 70 + "\n\n")
                    
                    # Mensajes
                    for msg in sorted(mensajes, key=lambda x: x['numero']):
                        f.write("─" * 70 + "\n")
                        f.write(f"MENSAJE {msg['numero']:03d}\n")
                        f.write("─" * 70 + "\n\n")
                        f.write(msg['contenido'])
                        f.write("\n\n")
                
                archivos_generados.append(ruta_archivo)
                print(f"  ✅ {nombre_archivo} ({len(mensajes)} mensajes)")
        
        return archivos_generados
    
    def generar_resumen(self, archivos_generados: list):
        """Genera un archivo de resumen ejecutivo."""
        ruta_resumen = self.carpeta_salida / "RESUMEN_EXTRACTION.txt"
        
        with open(ruta_resumen, 'w', encoding='utf-8') as f:
            f.write("╔══════════════════════════════════════════════════════════════╗\n")
            f.write("║  RESUMEN EJECUTIVO — EXTRACCIÓN DE MENSAJES NEUROBIT        ║\n")
            f.write("╠══════════════════════════════════════════════════════════════╣\n")
            f.write(f"║  Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                    ║\n")
            f.write(f"║  Archivo origen: {self.archivo_numerado.name}                     ║\n")
            f.write(f"║  Clasificación: {self.archivo_clasificacion.name}                          ║\n")
            f.write("╠══════════════════════════════════════════════════════════════╣\n")
            f.write("║  MENSAJES POR CATEGORÍA:                                    ║\n")
            f.write("╠══════════════════════════════════════════════════════════════╣\n")
            
            total = 0
            for cat, lista in self.categorias.items():
                f.write(f"║  {cat:15} : {len(lista):3} mensajes                          ║\n")
                total += len(lista)
            
            f.write("╠══════════════════════════════════════════════════════════════╣\n")
            f.write(f"║  TOTAL GENERAL     : {total:3} mensajes                          ║\n")
            f.write("╠══════════════════════════════════════════════════════════════╣\n")
            f.write("║  ARCHIVOS GENERADOS:                                        ║\n")
            f.write("╠══════════════════════════════════════════════════════════════╣\n")
            
            for archivo in archivos_generados:
                f.write(f"║  • {archivo.name:54} ║\n")
            
            f.write("╚══════════════════════════════════════════════════════════════╝\n")
        
        print(f"\n📄 Resumen generado: {ruta_resumen.name}")
        return ruta_resumen
    
    def procesar(self):
        """Ejecuta el proceso completo de extracción."""
        print("=" * 70)
        print("🔄 FASE 3: EXTRACCIÓN AUTOMÁTICA POR CATEGORÍA")
        print("=" * 70)
        print()
        
        print("1️⃣ Leyendo clasificación...")
        clasificacion = self.leer_clasificacion()
        
        print("2️⃣ Leyendo mensajes numerados...")
        mensajes = self.leer_mensajes_numerados()
        
        print("3️⃣ Clasificando mensajes...")
        self.clasificar_mensajes(clasificacion, mensajes)
        
        print("4️⃣ Generando archivos por categoría...")
        archivos = self.generar_archivos()
        
        print("5️⃣ Generando resumen ejecutivo...")
        self.generar_resumen(archivos)
        
        print()
        print("=" * 70)
        print("✅ EXTRACCIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print(f"📁 Carpeta de salida: {self.carpeta_salida.absolute()}")
        print(f"📊 Total archivos generados: {len(archivos) + 1} (incluye resumen)")
        print()


def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python3 extractor_por_categoria.py <clasificacion.txt> <numerado.txt> [carpeta_salida]")
        print("Ejemplo:")
        print("  python3 extractor_por_categoria.py clasificacion_mensajes.txt chat-numerado.txt mensajes_extraidos")
        sys.exit(1)
    
    archivo_clasificacion = sys.argv[1]
    archivo_numerado = sys.argv[2]
    carpeta_salida = sys.argv[3] if len(sys.argv) > 3 else None
    
    extractor = ExtractorPorCategoria(archivo_clasificacion, archivo_numerado, carpeta_salida)
    extractor.procesar()


if __name__ == "__main__":
    main()
