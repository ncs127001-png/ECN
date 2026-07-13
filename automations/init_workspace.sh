#!/bin/bash
set -e

# NEUROBIT Workspace Initializer
# Ejecutar desde la raíz del proyecto: ./automations/init_workspace.sh

PROJECT_ROOT=$(pwd)
DATA_DIR="$PROJECT_ROOT/data"
CONFIG_DIR="$PROJECT_ROOT/config"

echo "🚀 Iniciando configuración del workspace NEUROBIT..."

# Crear directorios esenciales
mkdir -p "$DATA_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$PROJECT_ROOT/core"
mkdir -p "$PROJECT_ROOT/connectors"
mkdir -p "$PROJECT_ROOT/automations"
mkdir -p "$PROJECT_ROOT/tests/unit"
mkdir -p "$PROJECT_ROOT/.vscode"

# Inicializar memoria persistente
if [ ! -f "$DATA_DIR/memoria_eva.jsonl" ]; then
  echo "📦 Creando memoria_eva.jsonl..."
  touch "$DATA_DIR/memoria_eva.jsonl"
  chmod 600 "$DATA_DIR/memoria_eva.jsonl"
fi

# Configuración base
if [ ! -f "$CONFIG_DIR/neurobit_config.json" ]; then
  echo "⚙️ Generando configuración base..."
  cat > "$CONFIG_DIR/neurobit_config.json" <<EOF
{
  "version": "2.1",
  "environment": "development",
  "ollama": {
    "endpoint": "http://localhost:11434/api/generate",
    "model": "neurobit-strict:latest",
    "timeout": 30000
  },
  "persistence": {
    "arca_path": "./data/memoria_eva.jsonl",
    "journal_path": "./data/writing.record"
  },
  "nodes": ["HOMO_VIVO", "NEUROBIT_D", "ESTACION_CENTRAL", "S0PHI", "QW3N4"]
}
EOF
fi

# Validar dependencias
echo "🔍 Verificando dependencias del sistema..."
if ! command -v ollama &> /dev/null; then
  echo "⚠️  Ollama no está instalado. Se requiere para el funcionamiento completo."
  echo "   Instrucciones: https://ollama.com/download/linux"
else
  echo "✅ Ollama disponible"
fi

if ! command -v python3 &> /dev/null; then
  echo "⚠️  Python3 no encontrado. Se requiere para scripts de automatización."
else
  echo "✅ Python3 disponible"
fi

echo "✅ Workspace NEUROBIT inicializado correctamente"
echo "💡 Siguiente paso: Configurar tu modelo local con 'ollama pull neurobit-strict:latest'"