# core/llm/coherence_watchdog.py
def detect_degeneration(response: str, window: int = 5):
    """
    Detecta loops semánticos antes de que colapsen el contexto
    """
    # 1. Dividir en frases
    sentences = [s.strip() for s in response.split('.') if s.strip()]
    
    # 2. Calcular diversidad léxica en ventana deslizante
    for i in range(len(sentences) - window):
        window_sentences = sentences[i:i+window]
        unique_words = set(word for s in window_sentences for word in s.lower().split())
        total_words = sum(len(s.split()) for s in window_sentences)
        
        # Si diversidad < 0.3 → alerta de degeneración
        if total_words > 0 and (len(unique_words) / total_words) < 0.3:
            return {"degenerated": True, "at_sentence": i, "diversity": len(unique_words)/total_words}
    
    return {"degenerated": False}