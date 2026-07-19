#!/usr/bin/env python3
"""core/coherence_filter.py

Prototipo ligero del filtro de coherencia M/E para NEUROBIT.

Funciones principales:
 - score_coherence(text): devuelve valor entre 0.0 y 1.0 (métrica heurística).
 - score_emotion(text): devuelve valor entre -1.0 y 1.0 (valencia emocional simple).
 - detect_ambiguities(text, glossary=None): lista términos potencialmente ambiguos.
 - analyze(text, metadata={}): arma un envelope parcial (dict) con los campos esenciales.

Este prototipo usa heurísticas sencillas (sin dependencias externas) y está pensado
para ser reemplazado por modelos más sofisticados (RAG + embeddings) en la fase 2.
"""

from __future__ import annotations

import json
import math
import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional

# Pequeño léxico para sentiment (prototipo):
POSITIVE = {"bueno", "bien", "claro", "coherente", "útil", "positivo", "gracias", "amor"}
NEGATIVE = {"malo", "mal", "confuso", "incoherente", "error", "odio", "frustración", "fritura"}

_WORD_RE = re.compile(r"\w+", re.UNICODE)


def _tokenize(text: str) -> List[str]:
    return _WORD_RE.findall(text.lower())


def score_coherence(text: str) -> float:
    """Heurística simple para medir coherencia (0.0..1.0).

    Combina ratio de palabras únicas y longitud media de oraciones.
    Es intencionalmente conservadora; usa métricas interpretables.
    """
    if not text or not text.strip():
        return 0.0
    tokens = _tokenize(text)
    if not tokens:
        return 0.0
    unique_ratio = len(set(tokens)) / len(tokens)

    # Sentences: split on punctuation (simple)
    sentences = re.split(r'[\.\n\?!]+', text)
    sentences = [s for s in sentences if s.strip()]
    avg_sentence_len = len(tokens) / max(1, len(sentences))

    # Normalize average sentence length to [0,1] with 20 words = 1.0
    avg_norm = min(1.0, avg_sentence_len / 20.0)

    # Weighted sum
    coherence = 0.6 * unique_ratio + 0.4 * avg_norm
    # clamp
    return max(0.0, min(1.0, coherence))


def score_emotion(text: str) -> float:
    """Heurística simple de valencia emocional (-1.0..1.0).

    Cuenta palabras positivas/negativas del léxico prototipo.
    """
    if not text or not text.strip():
        return 0.0
    tokens = _tokenize(text)
    pos = sum(1 for t in tokens if t in POSITIVE)
    neg = sum(1 for t in tokens if t in NEGATIVE)
    total = pos + neg
    if total == 0:
        return 0.0
    val = (pos - neg) / total
    # val ya está en [-1,1]
    return max(-1.0, min(1.0, val))


def detect_ambiguities(text: str, glossary: Optional[List[str]] = None) -> List[Dict[str, List[str]]]:
    """Detecta términos potencialmente ambiguos.

    - Si se proporciona `glossary` (lista de términos), los marca.
    - Además detecta marcadores modales/condicionales que suelen generar ambigüedad.
    """
    tokens = _tokenize(text)
    found = []
    modal_markers = {"quizá", "quizas", "tal vez", "podría", "podria", "posible", "puede", "parece", "obvio", "evidente"}
    text_lower = text.lower()

    # detect glossary terms
    if glossary:
        for term in glossary:
            if re.search(r"\b" + re.escape(term.lower()) + r"\b", text_lower):
                found.append({"term": term, "reason": "in_glossary"})

    # detect modal markers
    for m in modal_markers:
        if m in text_lower:
            found.append({"term": m, "reason": "modal_marker"})

    # interrogatives and question marks
    if "?" in text:
        found.append({"term": "?", "reason": "question_mark"})

    # deduplicate by term
    unique = {f['term']: f for f in found}
    return list(unique.values())


def analyze(text: str, metadata: Optional[Dict] = None, glossary: Optional[List[str]] = None) -> Dict:
    """Genera un envelope parcial con análisis M/E y metadatos mínimos.

    Este prototipo devuelve un dict listo para almacenar o enviar a la API.
    """
    if metadata is None:
        metadata = {}
    coherence = score_coherence(text)
    emotion = score_emotion(text)
    ambiguities = detect_ambiguities(text, glossary=glossary)

    envelope = {
        "message_id": metadata.get("message_id") or f"msg_{uuid.uuid4().hex[:8]}",
        "entity_id": metadata.get("entity_id", "UNKNOWN"),
        "perspective": metadata.get("perspective", "tecnica"),
        "context": metadata.get("context", "") ,
        "plane": {"M": round((coherence * 2.0 - 1.0), 3), "E": round(emotion, 3)},
        # plane.M maps coherence(0..1) to -1..1 for compatibility con esquema
        "intention": metadata.get("intention", ""),
        "content": text,
        "analysis": {
            "coherence_score": round(coherence, 4),
            "emotional_score": round(emotion, 4),
            "identified_ambiguities": ambiguities,
            "suggested_reformulation": None,
            "evidence": []
        },
        "provenance": {"created": datetime.utcnow().isoformat() + "Z", "signed_by": metadata.get("signed_by", "AUTO")},
        "action": metadata.get("action", "store"),
        "human_approval": {"approved": False}
    }
    return envelope


def _demo():
    sample = (
        "Estoy convencido de que la opción X es la mejor. "
        "Sin embargo, puede haber ambigüedad en el término 'norma'."
    )
    env = analyze(sample, metadata={"entity_id": "HUMAN_TRON", "perspective": "coordinacion", "signed_by": "TRON"}, glossary=["norma","fritura"])
    print(json.dumps(env, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _demo()
