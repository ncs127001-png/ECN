#!/bin/bash
# neurobit_audit.sh - Auditoría del corpus separado

cd conversaciones_separadas/

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  NEUROBIT_CORPUS_AUDIT - 2026-03-13                      ║"
echo "╚══════════════════════════════════════════════════════════╝"

# 1. Top 10 conversaciones por cantidad de mensajes
echo -e "\n📈 TOP 10 CONVERSACIONES (por mensajes):"
for f in *.json; do
    if [ "$f" != "MANIFEST_NEUROBIT.json" ]; then
        count=$(jq '.chat.history.messages | length' "$f" 2>/dev/null || echo 0)
        echo "$count|$f"
    fi
done | sort -t'|' -k1 -nr | head -10 | while IFS='|' read -r count file; do
    printf "  %3d msgs → %s\n" "$count" "$file"
done

# 2. Conversaciones pequeñas (≤5 mensajes) - posibles candidatos para fusión
echo -e "\n📉 CONVERSACIONES PEQUEÑAS (≤5 mensajes):"
for f in *.json; do
    if [ "$f" != "MANIFEST_NEUROBIT.json" ]; then
        count=$(jq '.chat.history.messages | length' "$f" 2>/dev/null || echo 0)
        if [ "$count" -le 5 ]; then
            echo "  $count msgs → $f"
        fi
    fi
done

# 3. Tamaño total del corpus
echo -e "\n💾 TAMAÑO TOTAL DEL CORPUS:"
du -sh . | awk '{print "  " $1 " total en conversaciones_separadas/"}'

# 4. Fecha más reciente de modificación
echo -e "\n📅 ÚLTIMA MODIFICACIÓN:"
ls -lt *.json | head -1 | awk '{print "  " $6, $7, $8, "→", $9}'

echo -e "\n✅ Auditoría completada."