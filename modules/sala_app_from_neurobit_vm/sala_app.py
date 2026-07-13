from flask import Flask, render_template_string, request, jsonify
import datetime
import json
import os

app = Flask(__name__)

# Directorio para mensajes
os.makedirs('inbox', exist_ok=True)
os.makedirs('outbox', exist_ok=True)
os.makedirs('logs', exist_ok=True)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>🧠 Salón de Reuniones NEUROBIT</title>
  <style>
    body { font-family: 'Courier New', monospace; background: #0f0f0f; color: #00ff00; padding: 20px; margin: 0; }
    .terminal { background: #000; padding: 15px; border: 1px solid #00ff00; margin: 10px 0; height: 60vh; overflow-y: auto; font-size: 14px; }
    .status { color: #00ff00; font-weight: bold; padding: 5px; border-bottom: 1px solid #00ff00; margin-bottom: 10px; }
    .input-area { margin-top: 15px; }
    input { background: #000; color: #00ff00; border: 1px solid #00ff00; padding: 8px; width: 80%; font-family: inherit; font-size: 14px; }
    button { background: #006400; color: white; border: none; padding: 8px 15px; cursor: pointer; font-family: inherit; }
    button:hover { background: #00ff00; color: #000; }
    .message { margin: 5px 0; padding: 2px 5px; }
    .tron { color: #00ff00; }
    .simon { color: #3498db; }
  </style>
</head>
<body>
  <h1>🧠 Salón de Reuniones NEUROBIT v0.1</h1>
  <div class="status">🟢 Sistema en modo LOCALHOST - Listo para TRON</div>
  
  <div class="terminal" id="terminal">
    <div class="message"><span class="simon">[SIMON]</span> Salón de Reuniones iniciado</div>
    <div class="message"><span class="simon">[SIMON]</span> Agentes disponibles: TRON, SIMON, EVA, LLAMA_LOCAL</div>
    <div class="message"><span class="simon">[SIMON]</span> Protocolo: TS-Horarios v1.0 (Búsqueda fractal activa)</div>
  </div>
  
  <div class="input-area">
    <input type="text" id="messageInput" placeholder="Mensaje para el Salón..." autofocus>
    <button onclick="sendMessage()">Enviar</button>
  </div>

  <script>
    function sendMessage() {
      const input = document.getElementById('messageInput');
      const message = input.value.trim();
      if (!message) return;
      
      // Mostrar en terminal
      addToTerminal(`[TRON] ${message}`);
      
      // Enviar al servidor
      fetch('/send_message', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: message})
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'received') {
          addToTerminal(`[SIMON] ✓ Mensaje validado y procesado`);
        }
      });
      
      input.value = '';
    }
    
    function addToTerminal(text) {
      const terminal = document.getElementById('terminal');
      const now = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});
      terminal.innerHTML += `<div class="message">${now} ${text}</div>`;
      terminal.scrollTop = terminal.scrollHeight;
    }
    
    // Permitir enviar con Enter
    document.getElementById('messageInput').addEventListener('keypress', function(e) {
      if (e.key === 'Enter') sendMessage();
    });
    
    // Conexión automática
    setTimeout(() => {
      addToTerminal(`[SYSTEM] Conexión establecida con SIMON (VSCode)`);
    }, 1000);
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    message = data.get('message', '')
    
    # Guardar mensaje en inbox
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"inbox/msg_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write(f"TIMESTAMP: {datetime.datetime.utcnow().isoformat()}Z\n")
        f.write(f"ORIGEN: TRON\n")
        f.write(f"CONTENIDO: {message}\n")
    
    # Log simple
    with open('logs/system.log', 'a') as f:
        f.write(f"[{datetime.datetime.now().isoformat()}] TRON: {message}\n")
    
    return jsonify({"status": "received", "file": filename})

if __name__ == '__main__':
    print("🧠 NEUROBIT SALÓN - Accede en http://localhost:5000")
    print("🛑 Para detener: Ctrl+C")
    app.run(host='0.0.0.0', port=5000, debug=True)
