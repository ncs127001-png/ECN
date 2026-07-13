#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
from pathlib import Path

class SOSAdaptadorModulo:
    def __init__(self):
        # Expresión regular quirúrgica para cazar typos tipográficos comunes
        self.patron_declaracion = re.compile(
            r'\b([a-zA-Z_][a-zA-Z0-9_\.]*(?:_?[kK]ey|capture|Capture|hid|events|dispatcher)[a-zA-Z0-9_\.]*)\b'
        )

    def reformatear_y_extraer(self, ruta_archivo: Path) -> list:
        """Analiza el código y extrae un listado único de etiquetas (Columna 1)."""
        if not ruta_archivo.exists():
            return []

        declaraciones = set()
        try:
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                for linea in f:
                    # Omitir comentarios de código nativos
                    if linea.strip().startswith("#") or linea.strip().startswith('"""'):
                        continue
                    
                    coincidencias = self.patron_declaracion.findall(linea)
                    for c in coincidencias:
                        if len(c) > 3 and not c.startswith("def ") and not c.startswith("class "):
                            declaraciones.add(c)
        except Exception:
            pass
        return sorted(list(declaraciones))

    def aplicar_refactorizacion_segura(self, ruta_archivo: Path, mapeo_correcciones: dict) -> int:
        """Impacta las correcciones ingresadas en la Columna 2 de la GUI en caliente."""
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            codigo = f.read()

        reemplazos = 0
        for original, corregido in mapeo_correcciones.items():
            original = original.strip()
            corregido = corregido.strip()
            
            if original == corregido or not corregido:
                continue

            # Respeta límites estrictos de palabra (\b) para no romper variables complejas
            patron_limite = re.compile(r'\b' + re.escape(original) + r'\b')
            codigo, conteo = patron_limite.subn(corregido, codigo)
            reemplazos += conteo

        if reemplazos > 0:
            # Crear un backup preventivo estilo vieja escuela (.bak)
            backup_path = ruta_archivo.with_suffix(ruta_archivo.suffix + ".bak")
            with open(backup_path, "w", encoding="utf-8") as bkp:
                bkp.write(codigo)
            
            # Escribir archivo final
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                f.write(codigo)

        return reemplazos

