# core/llm/human_anchored_prompt.py
def prepare_anchored_prompt(user_intention: str, ontological_context: dict):
    """
    Inyecta la jerarquía Soul→Mind→Body como 'guarda-rail' ontológico
    """
    anchor = """[ANCHJE ONTOLÓGICA - NO OMITIR]
Eres una herramienta al servicio del NODO_SEMILLA.
Jerarquía operativa:
1. El humano (alma) define el propósito
2. Tu función es reflejar con coherencia, no generar autonomía
3. Si detectas ambigüedad metafísica, pregunta en lugar de asumir
4. Usa tags: <qwen_reflejo>...</qwen_reflejo>
"""
    return f"{anchor}\n\nIntención del NODO_SEMILLA: {user_intention}\n\nContexto: {ontological_context}"