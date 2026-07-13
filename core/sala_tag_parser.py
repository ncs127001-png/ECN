# core/sala_tag_parser.py (nuevo módulo)
def parse_tags(message_content: str) -> dict:
    """
    Extrae tags como <claude_tecnico>, <tarea>, <acta>
    Retorna: {"rol": str, "tipo": str, "contenido": str, "tareas_detectadas": list}
    """
    # Regex para tags NEUROBIT_FUNDAMENT_PROTOCOL
    # Detección de patrones: "[tarea]", "[acta]", "[consigna]"
    pass

# Integración en neurobit_api.py → POST /salon/send
# Cada mensaje parseado → tareas agregadas a data/tareas_pendientes.jsonl