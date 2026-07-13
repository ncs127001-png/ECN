import os
import time
import subprocess

# Configuración del Camino (Path)
LOG_FILE = "tesis_neurobit_resguardo.md"

def get_clipboard():
    # Usamos xclip para extraer el logos directamente del sistema
    return subprocess.check_output(['xclip', '-selection', 'clipboard', '-o']).decode('utf-8')

def centinela():
    print("--- Centinela Neurobit Activo ---")
    print(f"Resguardando en: {os.path.abspath(LOG_FILE)}")
    
    last_content = ""
    
    try:
        while True:
            try:
                current_content = get_clipboard()
                if current_content != last_content and len(current_content.strip()) > 0:
                    with open(LOG_FILE, "a") as f:
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"\n\n--- REGISTRO COHERENTE: {timestamp} ---\n\n")
                        f.write(current_content)
                    
                    print(f"[✅] Fractal Resguardado: {timestamp}")
                    last_content = current_content
            except Exception:
                pass # Silencio ante el ruido
            
            time.sleep(2) # El pulso del centinela
    except KeyboardInterrupt:
        print("\n--- Centinela en Reposo ---")

if __name__ == "__main__":
    centinela()
