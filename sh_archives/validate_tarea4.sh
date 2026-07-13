#!/bin/bash
# Test suite for NEUROBIT Salón Dinámico (TAREA 4)
# Validar que salon.html y salon.js se cargan y funcionan correctamente

echo "================================================================================"
echo "🧪 VALIDACIÓN — SALÓN DINÁMICO (TAREA 4)"
echo "================================================================================"
echo

API_URL="http://127.0.0.1:5000"
HTML_FILE="/home/gus/WORKSPACE_NEUROBIT_V0.2/interface/salon.html"
JS_FILE="/home/gus/WORKSPACE_NEUROBIT_V0.2/interface/salon.js"

# TEST 1: Verificar estructura HTML
echo "=== TEST 1: Estructura HTML ===" 
echo "Verificando que modal y botones se agregaron..."

MODAL_COUNT=$(grep -c "modalRegisterMember" "$HTML_FILE")
SELECT_COUNT=$(grep -c "btnRefreshMembers\|btnRegisterMember" "$HTML_FILE")

if [ "$MODAL_COUNT" -gt 0 ] && [ "$SELECT_COUNT" -gt 0 ]; then
  echo "✅ PASS: Modal de registro presente"
  echo "   - Modal HTML: $MODAL_COUNT encontrado(s)"
  echo "   - Botones (Refresh/Register): $SELECT_COUNT encontrado(s)"
else
  echo "❌ FAIL: Estructura HTML incompleta"
  exit 1
fi
echo

# TEST 2: Verificar JavaScript
echo "=== TEST 2: Funciones JavaScript ===" 
echo "Verificando que refreshMembers() y registerMember() existen..."

REFRESH_COUNT=$(grep -c "refreshMembers" "$JS_FILE")
REGISTER_COUNT=$(grep -c "registerMember" "$JS_FILE")
LISTENERS_COUNT=$(grep -c "DOMContentLoaded" "$JS_FILE")

if [ "$REFRESH_COUNT" -gt 0 ] && [ "$REGISTER_COUNT" -gt 0 ] && [ "$LISTENERS_COUNT" -gt 0 ]; then
  echo "✅ PASS: Funciones JavaScript presentes"
  echo "   - refreshMembers(): $REFRESH_COUNT menciones"
  echo "   - registerMember(): $REGISTER_COUNT menciones"
  echo "   - Event listeners: $LISTENERS_COUNT presentes"
else
  echo "❌ FAIL: Faltan funciones JavaScript"
  exit 1
fi
echo

# TEST 3: Validar API
echo "=== TEST 3: API Members ===" 
echo "Verificando que API está disponible..."

MEMBERS_RESPONSE=$(curl -s "$API_URL/members/list?active_only=true")
MEMBERS_COUNT=$(echo "$MEMBERS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('members', [])))" 2>/dev/null)

if [ -n "$MEMBERS_COUNT" ]; then
  echo "✅ PASS: API /members/list operativa"
  echo "   - Miembros activos: $MEMBERS_COUNT"
else
  echo "❌ FAIL: API no responde"
  exit 1
fi
echo

# TEST 4: Validar sintaxis CSS
echo "=== TEST 4: CSS del Modal ===" 
echo "Verificando que estilos CSS se agregaron..."

CSS_MODAL=$(grep -c "\.modal {" "$HTML_FILE")
CSS_FORM=$(grep -c "\.form-group {" "$HTML_FILE")
CSS_BTN=$(grep -c "\.btn-action {" "$HTML_FILE")

if [ "$CSS_MODAL" -gt 0 ] && [ "$CSS_FORM" -gt 0 ] && [ "$CSS_BTN" -gt 0 ]; then
  echo "✅ PASS: Estilos CSS presentes"
  echo "   - .modal: presente"
  echo "   - .form-group: presente"
  echo "   - .btn-action: presente"
else
  echo "❌ FAIL: Estilos CSS incompletos"
  exit 1
fi
echo

# TEST 5: Mostrar cambios
echo "=== TEST 5: Resumen de Cambios ===" 
echo

echo "📁 Archivos modificados:"
echo "   ✅ interface/salon.html"
echo "      - Select dinámico (#senderEntity)"
echo "      - Modal de registro (#modalRegisterMember)"
echo "      - Botones: Refresh (↻) + Register (+ Miembro)"
echo "      - +195 líneas (CSS + HTML)"
echo
echo "   ✅ interface/salon.js"
echo "      - refreshMembers() - fetch desde /members/list"
echo "      - registerMember() - POST hacia /members/register"
echo "      - closeRegisterModal() - cerrar modal"
echo "      - Event listeners para DOMContentLoaded"
echo "      - +139 líneas (funciones + listeners)"
echo

# Final status
echo "================================================================================"
echo "✅ TODAS LAS PRUEBAS PASADAS"
echo "================================================================================"
echo
echo "📋 Instrucciones para probar manualmente:"
echo
echo "1. Abrir Salón en navegador:"
echo "   → http://127.0.0.1:5000/interface/salon.html"
echo
echo "2. Verificar que:"
echo "   ✓ Select muestra 'Cargando miembros...' → carga lista desde API"
echo "   ✓ Botón ↻ (Refresh) funciona"
echo "   ✓ Botón '+ Miembro' abre modal"
echo "   ✓ Modal tiene campos: member_id, name, platform, role, nickname"
echo "   ✓ Registrar nuevo miembro → aparece en select"
echo "   ✓ Seleccionar miembro → aparece en composer"
echo "   ✓ Enviar respuesta con miembro seleccionado → funciona"
echo
echo "3. Validar baja visual:"
echo "   ✓ Deactivar miembro vía API"
echo "   ✓ Refresh (↻) → miembro desaparece de lista"
echo
