#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
numerador_mensajes.py
Numera secuencialmente los mensajes de una conversación
y genera separadores claros para clasificación posterior.

Autor: NODO_SEMILLA NEUROBIT
Versión: 1.0
"""

import re
from pathlib import Path
from datetime import datetime

class NumeradorMensajes:
    """Numera y separa mensajes de conversación para clasificación."""
    
    def __init__(self, archivo_entrada: str, archivo_salida: str = None):
        self.archivo_entrada = Path(archivo_entrada)
        self.archivo_salida = Path(archivo_salida) if archivo_salida else None
        
        if not self.archivo_salida:
            base_name = self.archivo_entrada.stem
            self.archivo_salida = self.archivo_entrada.parent / f"{base_name}_NUMERADO.txt"
        
        self.contador_mensajes = 0
        self.mensajes = []
    
    def leer_conversacion(self) -> str:
        """Lee el archivo de conversación completo."""
        if not self.archivo_entrada.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {self.archivo_entrada}")
        
        with open(self.archivo_entrada, 'r', encoding='utf-8') as f:
            return f.read()
    
    def identificar_mensajes(self, contenido: str) -> list:
        """
        Identifica y separa los mensajes individuales.
        Detecta patrones como:
        - ### USER / ### ASSISTANT
        - [NÚMERO DE MENSAJE]
        - Líneas en blanco como separadores
        """
        mensajes = []
        
        # Patrones a detectar
        patron_user = re.compile(r'^### USER\s*$', re.MULTILINE)
        patron_assistant = re.compile(r'^### ASSISTANT\s*$', re.MULTILINE)
        patron_numero = re.compile(r'\[NÚMERO DE MENSAJE[:\s]*(\d+)', re.IGNORECASE)
        
        # Dividir por líneas para análisis
        lineas = contenido.split('\n')
        
        mensaje_actual = []
        en_mensaje = False
        
        for i, linea in enumerate(lineas):
            # Detectar inicio de mensaje
            if patron_user.match(linea) or patron_assistant.match(linea) or patron_numero.search(linea):
                # Guardar mensaje anterior si existe
                if mensaje_actual and en_mensaje:
                    mensajes.append('\n'.join(mensaje_actual))
                
                # Iniciar nuevo mensaje
                mensaje_actual = [linea]
                en_mensaje = True
            elif en_mensaje:
                mensaje_actual.append(linea)
        
        # Agregar último mensaje
        if mensaje_actual:
            mensajes.append('\n'.join(mensaje_actual))
        
        return mensajes
    
    def agregar_numeracion_y_separadores(self, mensajes: list) -> str:
        """
        Agrega numeración secuencial y separadores claros.
        Formato:
        
        ════════════════════════════════════════════════════════════
        MENSAJE N°: 001
        TIPO: [POR_CLASIFICAR]
        FECHA: [AUTODETECTAR_SI_EXITE]
        ════════════════════════════════════════════════════════════
        
        [CONTENIDO DEL MENSAJE]
        
        ────────────────────────────────────────────────────────────
        FIN MENSAJE 001
        ════════════════════════════════════════════════════════════
        """
        
        output_lines = []
        output_lines.append("=" * 70)
        output_lines.append("HISTORIAL DE CONVERSACIÓN NUMERADO")
        output_lines.append(f"Archivo original: {self.archivo_entrada.name}")
        output_lines.append(f"Fecha de procesamiento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append(f"Total de mensajes detectados: {len(mensajes)}")
        output_lines.append("=" * 70)
        output_lines.append("")
        output_lines.append("INSTRUCCIONES DE CLASIFICACIÓN:")
        output_lines.append("1. Revisar cada mensaje numerado")
        output_lines.append("2. Marcar tipo: [TECNICO], [ONTOLOGICO], [INTERRUPCION],")
        output_lines.append("                [HISTORIA], [REALIZADO], [COORDINACION]")
        output_lines.append("3. Guardar como: clasificacion_mensajes.txt")
        output_lines.append("")
        
        for i, mensaje in enumerate(mensajes, 1):
            # Separador de inicio
            output_lines.append("=" * 70)
            output_lines.append(f"MENSAJE N°: {i:03d}")
            output_lines.append(f"TIPO: [POR_CLASIFICAR]")
            
            # Intentar detectar fecha si existe en el mensaje
            fecha_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})', mensaje)
            if fecha_match:
                output_lines.append(f"FECHA: {fecha_match.group(1)}")
            else:
                output_lines.append("FECHA: [NO_DETECTADA]")
            
            output_lines.append("=" * 70)
            output_lines.append("")
            
            # Contenido del mensaje
            output_lines.append(mensaje)
            output_lines.append("")
            
            # Separador de fin
            output_lines.append("─" * 70)
            output_lines.append(f"FIN MENSAJE {i:03d}")
            output_lines.append("=" * 70)
            output_lines.append("")
        
        return '\n'.join(output_lines)
    
    def procesar(self) -> Path:
        """Ejecuta el proceso completo de numeración."""
        print(f"📖 Leyendo conversación: {self.archivo_entrada}")
        contenido = self.leer_conversacion()
        print(f"  Tamaño: {len(contenido):,} caracteres")
        
        print("🔍 Identificando mensajes...")
        mensajes = self.identificar_mensajes(contenido)
        print(f"  Mensajes detectados: {len(mensajes)}")
        
        print("🔢 Agregando numeración y separadores...")
        output = self.agregar_numeracion_y_separadores(mensajes)
        
        print(f"💾 Guardando en: {self.archivo_salida}")
        with open(self.archivo_salida, 'w', encoding='utf-8') as f:
            f.write(output)
        
        print(f"✅ Procesamiento completado!")
        print(f"📋 Resumen:")
        print(f"  Archivo de salida: {self.archivo_salida.absolute()}")
        print(f"  Total mensajes: {len(mensajes)}")
        print(f"  Próximo paso: Clasificar manualmente en clasificacion_mensajes.txt")
        
        return self.archivo_salida


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python3 numerador_mensajes.py <archivo_conversacion.txt> [archivo_salida.txt]")
        print("Ejemplo:")
        print("  python3 numerador_mensajes.py 'chat-Informe para EVA LÚMENA-2.txt'")
        sys.exit(1)
    
    archivo_entrada = sys.argv[1]
    archivo_salida = sys.argv[2] if len(sys.argv) > 2 else None
    
    numerador = NumeradorMensajes(archivo_entrada, archivo_salida)
    numerador.procesar()


if __name__ == "__main__":
    main()