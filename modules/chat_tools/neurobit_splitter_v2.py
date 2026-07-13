#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEUROBIT_SPLITTER_V2
Herramienta de separación fractal de conversaciones JSON
Schema específico: Plataforma con estructura {"success", "request_id", "data": [...]}
Entorno: Linux + Terminal
Dependencias: Standard Library (json, os, argparse, pathlib, re)
"""

import json
import os
import re
import argparse
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

# ==============================================================================
# CONFIGURACIÓN DE SCHEMA (VALIDADA CON FRAGMENTO PROPORCIONADO)
# ==============================================================================
KEY_IDENTIFICADOR = "id"           # UUID único de cada conversación
KEY_TITULO = "title"               # Título legible para nombre de archivo
RUTA_LISTA_CONVERSACIONES = "data" # Clave que contiene la lista de chats

# ==============================================================================
# UTILIDADES
# ==============================================================================

def sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    Sanitiza un string para uso como nombre de archivo en Linux.
    Elimina caracteres prohibidos y normaliza espacios.
    """
    # Reemplazar caracteres problemáticos
    name = name.replace("/", "_").replace("\\", "_")
    name = name.replace(":", "-").replace("|", "-")
    name = name.replace("<", "(").replace(">", ")")
    name = name.replace('"', "'").replace("*", "_")
    name = name.replace("?", "!")
    
    # Normalizar espacios múltiples
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()
    
    # Truncar si excede longitud máxima
    if len(name) > max_length:
        name = name[:max_length].rsplit(' ', 1)[0]
    
    # Asegurar que no esté vacío
    if not name:
        name = "sin_titulo"
    
    return name

# ==============================================================================
# LÓGICA DE PROCESAMIENTO
# ==============================================================================

class ChatSplitter:
    def __init__(self, input_path: str, output_dir: str):
        self.input_path = Path(input_path)
        self.output_dir = Path(output_dir)
        self.data = None
        self.stats = {"total": 0, "processed": 0, "errors": 0}

    def load_data(self) -> None:
        """Carga el archivo JSON en memoria."""
        if not self.input_path.exists():
            raise FileNotFoundError(f"[ERROR] El archivo {self.input_path} no existe en el filesystem.")
        
        file_size_mb = self.input_path.stat().st_size / (1024 * 1024)
        print(f"[LOG] Cargando estructura desde {self.input_path} ({file_size_mb:.2f} MB)...")
        
        with open(self.input_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        print(f"[LOG] Carga completada. Tipo de dato raíz: {type(self.data).__name__}")

    def normalize_data(self) -> List[Dict[str, Any]]:
        """Normaliza los datos a una lista de conversaciones para iterar."""
        if not isinstance(self.data, dict):
            raise ValueError(f"[ERROR] Se esperaba diccionario en raíz, se obtuvo {type(self.data).__name__}")
        
        if RUTA_LISTA_CONVERSACIONES not in self.data:
            raise ValueError(f"[ERROR] La clave '{RUTA_LISTA_CONVERSACIONES}' no existe en el JSON.")
        
        conversations = self.data[RUTA_LISTA_CONVERSACIONES]
        
        if not isinstance(conversations, list):
            raise ValueError(f"[ERROR] '{RUTA_LISTA_CONVERSACIONES}' debe contener una lista, se obtuvo {type(conversations).__name__}")
        
        return conversations

    def split(self) -> None:
        """Ejecuta la separación de conversaciones."""
        self.load_data()
        conversations = self.normalize_data()
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"[LOG] Directorio de salida preparado: {self.output_dir.absolute()}")
        print(f"[LOG] Total de conversaciones detectadas: {len(conversations)}")
        print("-" * 60)

        self.stats["total"] = len(conversations)
        
        for idx, conversation in enumerate(conversations, 1):
            if not isinstance(conversation, dict):
                self.stats["errors"] += 1
                print(f"[SKIP] Ítem {idx} no es un diccionario válido.")
                continue
            
            # Obtener identificadores
            chat_id = conversation.get(KEY_IDENTIFICADOR, f"unknown_{idx}")
            chat_title = conversation.get(KEY_TITULO, f"Conversación {idx}")
            
            # Construir nombre de archivo legible + ID para unicidad
            safe_title = sanitize_filename(chat_title)
            short_id = str(chat_id)[:8]  # Primeros 8 caracteres del UUID
            output_filename = f"{safe_title}_{short_id}.json"
            output_file = self.output_dir / output_filename
            
            # Escribir archivo individual manteniendo estructura original
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    # Opción A: Guardar solo el objeto conversación (recomendado para importación)
                    json.dump(conversation, f, ensure_ascii=False, indent=2)
                    
                    # Opción B: Si necesita el wrapper {"success", "data": [...]}, descomentar:
                    # wrapper = {"success": True, "request_id": self.data.get("request_id", ""), "data": [conversation]}
                    # json.dump(wrapper, f, ensure_ascii=False, indent=2)
                
                self.stats["processed"] += 1
                
                # Feedback cada 10 conversaciones
                if idx % 10 == 0:
                    print(f"[PROCESO] {idx}/{len(conversations)} - {safe_title[:40]}...")
                    
            except Exception as e:
                self.stats["errors"] += 1
                print(f"[ERROR] Falló escritura de {output_filename}: {e}")

        print("-" * 60)
        print(f"[ÉXITO] Proceso finalizado.")
        print(f"  • Total detectado:  {self.stats['total']}")
        print(f"  • Procesados:       {self.stats['processed']}")
        print(f"  • Errores:          {self.stats['errors']}")
        print(f"  • Salida:           {self.output_dir.absolute()}")

    def generate_manifest(self) -> None:
        """Genera un archivo manifiesto con el mapeo de conversaciones."""
        conversations = self.normalize_data()
        
        manifest = {
            "generated_at": datetime.now().isoformat(),
            "source_file": str(self.input_path.absolute()),
            "output_directory": str(self.output_dir.absolute()),
            "total_conversations": len(conversations),
            "conversations": []
        }
        
        for idx, conv in enumerate(conversations, 1):
            if isinstance(conv, dict):
                chat_id = conv.get(KEY_IDENTIFICADOR, f"unknown_{idx}")
                chat_title = conv.get(KEY_TITULO, f"Conversación {idx}")
                manifest["conversations"].append({
                    "index": idx,
                    "id": chat_id,
                    "title": chat_title,
                    "filename": f"{sanitize_filename(chat_title)}_{str(chat_id)[:8]}.json"
                })
        
        manifest_path = self.output_dir / "MANIFEST_NEUROBIT.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        
        print(f"[LOG] Manifiesto generado: {manifest_path}")

    def merge(self, input_dir: str, output_file: str) -> None:
        """Rutina inversa: Consolida JSONs individuales en uno solo."""
        input_path = Path(input_dir)
        output_path = Path(output_file)
        
        if not input_path.is_dir():
            raise FileNotFoundError(f"[ERROR] El directorio {input_path} no existe.")
        
        merged_data = []
        json_files = sorted(input_path.glob("*.json"))
        json_files = [f for f in json_files if f.name != "MANIFEST_NEUROBIT.json"]  # Excluir manifiesto
        
        print(f"[LOG] Iniciando consolidación de {len(json_files)} archivos...")
        
        for jfile in json_files:
            with open(jfile, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        merged_data.append(data)
                    elif isinstance(data, list):
                        merged_data.extend(data)
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Archivo corrupto saltado: {jfile.name} - {e}")
        
        # Reconstruir estructura original con wrapper
        output_wrapper = {
            "success": True,
            "request_id": f"merge-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "data": merged_data
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_wrapper, f, ensure_ascii=False, indent=2)
            
        print(f"[ÉXITO] Consolidación completada: {output_path} ({len(merged_data)} conversaciones)")

# ==============================================================================
# INTERFAZ DE LÍNEA DE COMANDOS (CLI)
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="NEUROBIT_SPLITTER_V2: Separación y consolidación de conversaciones JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS DE USO:
  Separar conversaciones:
    ./neurobit_splitter_v2.py split exportacion_total.json conversaciones_separadas/
  
  Consolidar conversaciones:
    ./neurobit_splitter_v2.py merge conversaciones_separadas/ importacion_preparada.json
  
  Generar solo manifiesto:
    ./neurobit_splitter_v2.py manifest exportacion_total.json conversaciones_separadas/
        """
    )
    parser.add_argument("action", choices=["split", "merge", "manifest"], 
                        help="Acción: split (separar), merge (unir), manifest (solo índice)")
    parser.add_argument("input", help="Archivo JSON (split/manifest) o Directorio (merge)")
    parser.add_argument("output", help="Directorio (split/manifest) o Archivo JSON (merge)")
    
    args = parser.parse_args()
    
    try:
        tool = ChatSplitter(args.input, args.output)
        
        if args.action == "split":
            tool.split()
            tool.generate_manifest()
        elif args.action == "manifest":
            tool.load_data()
            tool.generate_manifest()
        elif args.action == "merge":
            tool.merge(args.input, args.output)
            
    except Exception as e:
        print(f"[ERROR CRÍTICO] {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())