#!/bin/bash
# fix_fragmentador.sh - Script de corrección automática

ARCHIVO="tools/fragmentador_conversacion.py"

# Verificar existencia
if [ ! -f "$ARCHIVO" ]; then
    echo "❌ ERROR: Archivo no encontrado: $ARCHIVO"
    exit 1
fi

echo "🔧 Corrigiendo $ARCHIVO..."

# Corrección 1: self patron_user → self.patron_user (línea ~46)
sed -i 's/self patron_user/self.patron_user/g' "$ARCHIVO"

# Corrección 2: self patron_assistant → self.patron_assistant (línea ~47)
sed -i 's/self patron_assistant/self.patron_assistant/g' "$ARCHIVO"

# Corrección 3: fragto_actual → fragmento_actual (todas las ocurrencias)
sed -i 's/fragto_actual/fragmento_actual/g' "$ARCHIVO"

# Verificar correcciones
echo "✅ Correcciones aplicadas"

# Validar sintaxis
python3 -m py_compile "$ARCHIVO" 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Sintaxis validada - Archivo listo para uso"
else
    echo "❌ ERROR: Persisten errores de sintaxis"
    exit 1
fi