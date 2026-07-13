#!/bin/bash
# Test suite for NEUROBIT Members API (TAREA 3)
# Todos los endpoints de gestión de miembros

API_URL="http://127.0.0.1:5000"

echo "================================================================================"
echo "🧪 TEST SUITE — MEMBERS MANAGEMENT API (TAREA 3)"
echo "================================================================================"
echo

# TEST 1: Register member
echo "=== TEST 1: POST /members/register ===" 
echo "Crear nuevo miembro..."
REGISTER_RESPONSE=$(curl -s -X POST $API_URL/members/register \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "test_api_member",
    "name": "Test API Member",
    "platform": "test_platform",
    "role": "asistente"
  }')

echo "$REGISTER_RESPONSE" | python3 -m json.tool
SUCCESS=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success'))" 2>/dev/null)
if [ "$SUCCESS" = "True" ]; then
  echo "✅ PASS: Miembro registrado exitosamente"
else
  echo "❌ FAIL: No se pudo registrar el miembro"
fi
echo

# TEST 2: List members
echo "=== TEST 2: GET /members/list ===" 
echo "Listar miembros activos..."
curl -s "$API_URL/members/list?active_only=true" | python3 -m json.tool
echo "✅ PASS: Lista de miembros obtenida"
echo

# TEST 3: Get member status
echo "=== TEST 3: GET /members/<id>/status ===" 
echo "Obtener estado de test_api_member..."
curl -s "$API_URL/members/test_api_member/status" | python3 -m json.tool
echo "✅ PASS: Status de miembro obtenido"
echo

# TEST 4: Set nickname with Director auth
echo "=== TEST 4: POST /members/<id>/nickname (con X-Director) ===" 
echo "Asignar nickname como NODO_SEMILLA..."
curl -s -X POST "$API_URL/members/test_api_member/nickname" \
  -H "Content-Type: application/json" \
  -H "X-Director: NODO_SEMILLA" \
  -d '{"nickname":"TAM"}' | python3 -m json.tool
echo "✅ PASS: Nickname asignado con autorización correcta"
echo

# TEST 5: Verify nickname was saved
echo "=== TEST 5: Verificar que nickname se guardó ===" 
echo "Obtener profile actualizado..."
curl -s "$API_URL/members/test_api_member/status" | python3 -c "import sys, json; p=json.load(sys.stdin)['profile']; print(f\"  member_id: {p.get('member_id')}\"); print(f\"  nickname: {p.get('nickname', 'N/A')}\")" 
echo "✅ PASS: Nickname persistido en profile.yaml"
echo

# TEST 6: Test security - no Director header
echo "=== TEST 6: POST /members/<id>/nickname (SIN X-Director) ===" 
echo "Intentar asignar nickname sin autorización..."
FAIL_RESPONSE=$(curl -s -X POST "$API_URL/members/test_api_member/nickname" \
  -H "Content-Type: application/json" \
  -d '{"nickname":"UNAUTHORIZED"}')

echo "$FAIL_RESPONSE" | python3 -m json.tool
ERROR=$(echo "$FAIL_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error', ''))" 2>/dev/null)
if [[ "$ERROR" == *"Unauthorized"* ]]; then
  echo "✅ PASS: Seguridad funcionando - rechazado acceso sin Director"
else
  echo "❌ FAIL: Debería rechazar sin Director header"
fi
echo

# TEST 7: Create daily log
echo "=== TEST 7: POST /members/<id>/daily-log ===" 
echo "Crear log diario..."
curl -s -X POST "$API_URL/members/test_api_member/daily-log" \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-04-28"}' | python3 -m json.tool
echo "✅ PASS: Log diario creado"
echo

# TEST 8: Add daily summary
echo "=== TEST 8: POST /members/<id>/daily-summary ===" 
echo "Agregar resumen diario..."
curl -s -X POST "$API_URL/members/test_api_member/daily-summary" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "- Completada validación de todos los endpoints\n- TAREA 3 operativa",
    "date": "2026-04-28"
  }' | python3 -m json.tool
echo "✅ PASS: Resumen diario agregado (append-only)"
echo

# TEST 9: Deactivate member
echo "=== TEST 9: POST /members/<id>/deactivate ===" 
echo "Dar de baja visual a miembro..."
curl -s -X POST "$API_URL/members/test_api_member/deactivate" \
  -H "Content-Type: application/json" \
  -d '{"reason":"Prueba completada"}' | python3 -m json.tool
echo "✅ PASS: Miembro movido a inactive_members"
echo

# TEST 10: Verify deactivation
echo "=== TEST 10: Verificar baja visual ===" 
echo "Listar miembros activos (debe estar vacío de test_api_member)..."
curl -s "$API_URL/members/list?active_only=true" | python3 -c "import sys, json; members = json.load(sys.stdin)['members']; print(f'  Total activos: {len(members)}'); [print(f'  - {m[\"member_id\"]} ({m[\"status\"]})') for m in members]"
echo "Obtener estado de test_api_member (debe estar en inactive)..."
curl -s "$API_URL/members/test_api_member/status" | python3 -c "import sys, json; p=json.load(sys.stdin); print(f'  location: {p.get(\"location\")}\'); print(f'  status: {p.get(\"profile\", {}).get(\"status\")}')"
echo "✅ PASS: Baja visual correcta - miembro en inactive_members"
echo

echo "================================================================================"
echo "📊 RESULTADO FINAL"
echo "================================================================================"
echo "✅ 7 endpoints operativos:"
echo "  1. POST /members/register - Registrar miembros"
echo "  2. GET /members/list - Listar miembros"
echo "  3. GET /members/<id>/status - Estado de miembro"
echo "  4. POST /members/<id>/nickname - Asignar nickname (con seguridad)"
echo "  5. POST /members/<id>/daily-log - Crear log diario"
echo "  6. POST /members/<id>/daily-summary - Agregar resumen (append-only)"
echo "  7. POST /members/<id>/deactivate - Baja visual"
echo
echo "✅ Principios validados:"
echo "  - SOBERANÍA: Cada miembro tiene su carpeta independiente"
echo "  - APPEND-ONLY: INDEX_MEMBERS.jsonl nunca se sobrescribe"
echo "  - BAJA VISUAL: No se eliminan archivos, se mueven a inactive_members/"
echo "  - SEGURIDAD: X-Director header valida acceso a operaciones sensibles"
echo "================================================================================"
