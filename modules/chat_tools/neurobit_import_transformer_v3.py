#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NEUROBIT_IMPORT_TRANSFORMER_V3 - CORREGIDO
Transforma conversaciones separadas al formato de importación Qwen Chat
Schema validado por comparación forense y prueba de importación exitosa

Fecha corrección: 2026-03-14
NODO: oxo-nuxun-80-08-unxnu-oxo
Estado: ✅ PRODUCCIÓN
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

class ImportTransformerV3:
    def __init__(self, input_file: str = None):
        """
        Inicializa el transformer.
        Si input_file es None o vacío, NO carga datos (para modo batch).
        """
        self.input_file = Path(input_file) if input_file else None
        self.data = None
        if self.input_file and self.input_file.exists() and self.input_file.is_file():
            self.load()
    
    def load(self) -> None:
        """Carga el archivo JSON en memoria."""
        if not self.input_file or not self.input_file.exists():
            raise FileNotFoundError(f"El archivo {self.input_file} no existe.")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def extract_conversation_object(self) -> Dict:
        """Extrae el objeto conversación desde cualquier estructura."""
        if self.data is None:
            return {}
        if isinstance(self.data, list):
            return self.data[0] if self.data else {}
        elif isinstance(self.data, dict):
            return self.data
        return {}
    
    def ensure_messages_array(self, conv: Dict) -> List:
        """Asegura que 'messages' sea array plano."""
        if 'messages' in conv and isinstance(conv['messages'], list):
            return conv['messages']
        if 'chat' in conv and 'history' in conv['chat']:
            messages_dict = conv['chat']['history'].get('messages', {})
            if isinstance(messages_dict, dict):
                return list(messages_dict.values())
            elif isinstance(messages_dict, list):
                return messages_dict
        return []
    
    def ensure_chat_structure(self, conv: Dict) -> Dict:
        """Asegura que la estructura 'chat' exista con todos sus campos."""
        if 'chat' not in conv:
            conv['chat'] = {
                "history": {"messages": {}},
                "currentId": None,
                "currentResponseIds": []
            }
        else:
            if 'history' not in conv['chat']:
                conv['chat']['history'] = {"messages": {}}
            if 'messages' not in conv['chat']['history']:
                conv['chat']['history']['messages'] = {}
            if 'currentId' not in conv['chat']:
                conv['chat']['currentId'] = None
            if 'currentResponseIds' not in conv['chat']:
                conv['chat']['currentResponseIds'] = []
        return conv
    
    def ensure_required_fields(self, conv: Dict) -> Dict:
        """Asegura TODOS los campos requeridos observados en exportación nativa."""
        required_fields = {
            "id": conv.get("id"),
            "user_id": conv.get("user_id"),
            "title": conv.get("title", "Sin título"),
            "created_at": conv.get("created_at", int(datetime.now().timestamp())),
            "updated_at": conv.get("updated_at", int(datetime.now().timestamp())),
            "share_id": conv.get("share_id", None),
            "archived": conv.get("archived", False),
            "pinned": conv.get("pinned", False),
            "folder_id": conv.get("folder_id", None),
            "project_id": conv.get("project_id", None),
            "chat_type": conv.get("chat_type", "t2t"),
            "models": conv.get("models", None),
            "meta": conv.get("meta", {}),
            "currentResponseIds": conv.get("currentResponseIds", []),
            "currentId": conv.get("currentId", None)
        }
        for key, value in required_fields.items():
            if key not in conv:
                conv[key] = value
        return conv
    
    def transform(self) -> Dict:
        """Transformación mínima: preservar todo, solo asegurar formato correcto."""
        conv = self.extract_conversation_object()
        messages_array = self.ensure_messages_array(conv)
        conv['messages'] = messages_array
        conv = self.ensure_chat_structure(conv)
        conv = self.ensure_required_fields(conv)
        
        if messages_array:
            for msg in reversed(messages_array):
                if msg.get('role') == 'assistant':
                    conv['currentId'] = msg.get('id')
                    conv['currentResponseIds'] = [msg.get('id')]
                    conv['chat']['currentId'] = msg.get('id')
                    conv['chat']['currentResponseIds'] = [msg.get('id')]
                    break
        
        messages_dict = {}
        for msg in messages_array:
            msg_id = msg.get('id')
            if msg_id:
                messages_dict[msg_id] = msg
        conv['chat']['history']['messages'] = messages_dict
        return conv
    
    def export(self, output_file: str) -> bool:
        """Exporta al formato nativo exacto."""
        transformed = self.transform()
        output = [transformed]
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"[V3] Exportado: {output_file}")
        print(f"     Tamaño: {Path(output_file).stat().st_size / 1024:.2f} KB")
        return True
    
    def transform_batch(self, input_dir: str, output_dir: str) -> Dict[str, bool]:
        """Transforma múltiples archivos."""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {}
        json_files = [f for f in input_path.glob("*.json") if f.name != "MANIFEST_NEUROBIT.json"]
        
        print(f"[V3] Transformando {len(json_files)} archivos...")
        
        for src_file in json_files:
            # Crear nueva instancia para cada archivo
            transformer = ImportTransformerV3(str(src_file))
            dst_file = output_path / f"IMPORT_{src_file.name}"
            results[src_file.name] = transformer.export(str(dst_file))
        
        success_count = sum(1 for v in results.values() if v)
        print(f"[ÉXITO] {success_count}/{len(results)} archivos transformados")
        return results


# ==============================================================================
# CLI
# ==============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NEUROBIT_IMPORT_TRANSFORMER_V3")
    parser.add_argument("action", choices=["single", "batch"], help="single o batch")
    parser.add_argument("input", help="Archivo (single) o Directorio (batch)")
    parser.add_argument("output", help="Archivo (single) o Directorio (batch)")
    
    args = parser.parse_args()
    
    if args.action == "single":
        transformer = ImportTransformerV3(args.input)
        transformer.export(args.output)
    elif args.action == "batch":
        # NO crear instancia vacía - llamar directamente al método de clase
        transformer = ImportTransformerV3()  # Sin argumentos
        transformer.transform_batch(args.input, args.output)
