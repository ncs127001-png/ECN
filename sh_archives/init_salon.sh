#!/usr/bin/env bash
# Inicializa estructura mínima del Salón NEUROBIT en local
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "Inicializando NEUROBIT Salon en ${ROOT_DIR}"
mkdir -p "${ROOT_DIR}/core" "${ROOT_DIR}/interface" "${ROOT_DIR}/data" "${ROOT_DIR}/storage/RING_PROCESOS"
echo "Creando memoria append-only (si no existe)"
touch "${ROOT_DIR}/data/memoria_eva.jsonl"
echo "Copiando interfaz mínima"
if [ -f "${ROOT_DIR}/interface/sala_minimal.html" ]; then
  echo "Interfaz ya presente"
else
  echo "Interfaz no encontrada: asegúrate de que interface/sala_minimal.html existe"
fi

echo "Para arrancar la API en background (opcional):"
echo "  python3 neurobit_api.py &"
echo "Luego abre http://127.0.0.1:5000/interface/sala_minimal.html si sirves archivos estáticos o copia el archivo al servidor web local."

echo "Init completo."
