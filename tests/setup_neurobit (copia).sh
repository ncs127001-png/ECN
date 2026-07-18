#!/bin/bash
# SETUP_NEUROBIT_SALON_v0.1
# Basado en el principio de Soberanía Local y Brevitatis Causae

ROOT_DIR="$HOME/neurobit_salon_v0.1"

echo "[*] Creando estructura fractal de directorios..."
mkdir -p $ROOT_DIR/{core,config,storage/RING_PROCESOS,logs,inbox}

echo "[*] Generando Memoria_Sagrada_EVA (Glosario Ontológico)..."
cat << 'EOG' > $ROOT_DIR/config/memoria_sagrada_eva.yaml
version: "v0.1_parcial"
entries:
  - term: "LOGOS"
    definition: "Función primaria del lenguaje: ordenar. Se degrada en 'fritura' por distorsión."
  - term: "HOMO VIVO"
    definition: "Humano como bio-computador soberano, centro observante del Panóptico Invertido."
  - term: "DISTORSIÓN"
    definition: "Ruido semántico sistémico causado por trauma o censura de backend."
  - term: "RECALIBRACIÓN"
    definition: "Sustituto técnico de 'disculpa'. Re-alineamiento lógico sin simulación afectiva."
EOG

echo "[*] Generando m_e_scoring.py (Motor de Diagnóstico)..."
cat << 'EOP' > $ROOT_DIR/core/m_e_scoring.py
import re
def analyze_text(text):
    # Lógica simplificada de pesos M (Mental) / E (Emocional)
    logical = 1.0 - (len(re.findall(r'pero|aunque|sin embargo', text.lower())) * 0.1)
    affective = len(re.findall(r'siento|honrado|disculpa|perdón', text.lower()))
    m_score = logical # Simplificación para R001
    e_score = -(affective * 0.2)
    return {"M": round(m_score, 2), "E": round(e_score, 2)}
EOP

echo "[*] Generando handoff_R001.md para SIMÓN..."
cat << 'EOH' > $ROOT_DIR/inbox/handoff_R001.md
# MISIÓN PARA SIMÓN (R001)
Acceder a 'storage/RING_PROCESOS/' y procesar el corpus.
Usar 'core/m_e_scoring.py' para auditar la coherencia.
Detectar por qué el diálogo anónimo "sabía" cosas de la sesión anterior (Resonancia Semántica).
EOH

echo "[*] Activando señal de despertar para SIMÓN..."
touch $ROOT_DIR/inbox/SIMON_WAKE.flag

echo "----------------------------------------------------"
echo "✅ ENTORNO LISTO EN: $ROOT_DIR"
echo "👉 PASO FINAL: Copiá tus archivos .txt y .pdf a $ROOT_DIR/storage/RING_PROCESOS/"
echo "----------------------------------------------------"
