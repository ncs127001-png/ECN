#!/usr/bin/env python3
import os
import hashlib
import subprocess
from datetime import datetime

def procesar_numero(n):
    if n == 9: return 0, True  # El 9 es el Dragón que muta.
    return (n - 1), False

def obtener_hexagrama(fila, columna):
    return chr(19904 + (fila * 8) + columna)

def extraer_secuencia_raiz():
    secuencia = []
    # Busca dinámicamente en el directorio de persistencia de la v0.2
    for i in range(1, 6):
        filepath = f"cosecha_pi/Cosecha_PI_muestra_{i}.txt"
        if not os.path.exists(filepath): 
            filepath = f"data/Cosecha_PI_muestra_{i}.txt" # Fallback a ruta unificada
        if not os.path.exists(filepath): continue
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    val = int(line.strip().split('|')[-1].strip().split('.')[1])
                    secuencia.append(val)
                except: continue
    return secuencia

def transmutar_y_empaquetar(secuencia):
    lines_output = []
    buffer_visual = []
    
    # Reconstrucción de la matriz de hexagramas
    for i in range(0, len(secuencia) - 1, 2):
        fila, mut_a = procesar_numero(secuencia[i])
        col, mut_b = procesar_numero(secuencia[i+1])
        hexagrama = obtener_hexagrama(fila, col)
        hexagrama += "⚡" if (mut_a or mut_b) else " "
        buffer_visual.append(hexagrama)
        if len(buffer_visual) >= 40:
            lines_output.append(" ".join(buffer_visual))
            buffer_visual = []
    if buffer_visual: 
        lines_output.append(" ".join(buffer_visual))
        
    cuerpo_comandos = "\n".join(lines_output)
    
    # 1. Calcular SHA256 exacto del cuerpo (Aduana de Seguridad del Daemon)
    hash_coherencia = hashlib.sha256(cuerpo_comandos.encode('utf-8')).hexdigest()
    timestamp_soberano = datetime.now().isoformat()
    
    # 2. Construcción del Contenedor Canónico VM Bridge
    paquete_puente = f"""[VM_ASSIGN:EVA]
[VM_ID:vm_eva_001]
[TIMESTAMP:{timestamp_soberano}]
[HASH:{hash_coherencia}]
[VERSION:v1.0]
[VM_END]
echo "📥 [R.E.D. NEUROBIT] Inyectando Cosecha de Hexagramas Transmutados..."
cat << 'EOF'
{cuerpo_comandos}
EOF
echo "🕊️ Secuencia procesada en Localhost."
"""
    return paquete_puente

def inyectar_al_clipboard(contenido):
    """Bypass isTrusted utilizando xclip sobre el clipboard del sistema operativo"""
    try:
        process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
        process.communicate(input=contenido.encode('utf-8'))
        print("✅ [BRIDGE] Paquete de Estado copiado al clipboard del sistema.")
        print("⚡ El daemon 'vm_bridge_daemon' procesará la inyección en tmux:eva:0 de inmediato.")
    except FileNotFoundError:
        print("❌ Error: 'xclip' no está instalado en tu Linux Mint. Ejecuta: sudo apt install xclip")

if __name__ == "__main__":
    secuencia = extraer_secuencia_raiz()
    if secuencia:
        paquete = transmutar_y_empaquetar(secuencia)
        # Mostrar adelanto por consola del paquete formateado
        print("--- PAQUETE ESTRUCTURADO GENERADO ---")
        print("\n".join(paquete.split("\n")[:8])) # Primeras líneas de control
        print("-------------------------------------")
        inyectar_al_clipboard(paquete)
    else:
        print("⚠️ No se encontraron archivos de 'Cosecha_PI' válidos en las rutas locales.")

