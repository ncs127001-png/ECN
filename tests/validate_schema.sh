#!/bin/bash
# validate_schema.sh

FILE=$1

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  VALIDACIÓN DE SCHEMA - QWEN_CHAT_IMPORT                 ║"
echo "╚══════════════════════════════════════════════════════════╝"

# Verificar campos requeridos
REQUIRED_FIELDS=(
    "id"
    "user_id"
    "title"
    "messages"
    "chat"
    "chat.history.messages"
    "chat.currentId"
    "chat.currentResponseIds"
    "created_at"
    "updated_at"
    "share_id"
    "archived"
    "pinned"
    "folder_id"
    "project_id"
)

echo -e "\n📋 Campos requeridos:"
for field in "${REQUIRED_FIELDS[@]}"; do
    if jq -e ".$field" "$FILE" > /dev/null 2>&1 || jq -e ".[0].$field" "$FILE" > /dev/null 2>&1; then
        echo "  ✅ $field"
    else
        echo "  ❌ $field (FALTANTE)"
    fi
done

echo -e "\n📊 Estadísticas:"
echo "  Tamaño: $(du -h "$FILE" | cut -f1)"
echo "  Mensajes: $(jq '.[0].messages | length' "$FILE" 2>/dev/null || echo "N/A")"