// 🧠 NEUROBIT PLATFORM ADAPTER v1.0
// Adaptador específico para esta plataforma de chat
// No requiere extensiones de navegador - opera en el contexto actual

class NeurobitPlatformAdapter {
    constructor() {
        this.isFocused = false;
        this.currentFragment = null;
        this.charDelay = 50; // ms entre caracteres
        this.tabDelay = 300; // ms después de TAB
        this.enterDelay = 200; // ms antes de ENTER
        this.platformDetected = this.detectPlatform();
    }
    
    detectPlatform() {
        // Detectar esta plataforma específica
        const isThisPlatform = document.querySelector('[contenteditable="true"]') !== null &&
                              document.querySelector('button:last-child') !== null;
        
        return {
            detected: isThisPlatform,
            name: isThisPlatform ? "CURRENT_CHAT_PLATFORM" : "UNKNOWN",
            elements: {
                input: '[contenteditable="true"]',
                sendButton: 'button:last-child'
            }
        };
    }
    
    async sendFragment(fragmentContent, options = {}) {
        if (!this.platformDetected.detected) {
            console.error("❌ Plataforma no compatible detectada");
            return false;
        }
        
        try {
            this.currentFragment = fragmentContent;
            console.log(`🧠 Iniciando envío de fragmento: ${fragmentContent.substring(0, 50)}...`);
            
            // 1. Asegurar foco en el área de texto
            await this.focusInputField();
            
            // 2. Escribir contenido letra por letra
            await this.typeTextWithDelay(fragmentContent);
            
            // 3. Simular pulsaciones de TAB para llegar al botón de envío
            await this.pressTabSequence(options.tabCount || 2);
            
            // 4. Esperar y enviar
            await this.pressEnter();
            
            console.log("✅ Fragmento enviado exitosamente");
            return true;
            
        } catch (error) {
            console.error(`❌ Error durante el envío: ${error.message}`);
            return false;
        }
    }
    
    async focusInputField() {
        return new Promise((resolve) => {
            const input = document.querySelector(this.platformDetected.elements.input);
            if (!input) throw new Error("Elemento de entrada no encontrado");
            
            // Forzar foco
            input.focus();
            input.click();
            
            // Verificar foco real
            setTimeout(() => {
                if (document.activeElement === input) {
                    console.log("✅ Foco establecido en área de texto");
                    resolve();
                } else {
                    console.warn("⚠️ Foco no establecido - reintentando");
                    input.focus();
                    resolve();
                }
            }, 100);
        });
    }
    
    async typeTextWithDelay(text) {
        return new Promise((resolve) => {
            const input = document.querySelector(this.platformDetected.elements.input);
            if (!input) throw new Error("Elemento de entrada no encontrado");
            
            // Limpiar contenido existente
            input.innerHTML = '';
            
            let index = 0;
            const typeNextChar = () => {
                if (index < text.length) {
                    const char = text.charAt(index);
                    input.innerHTML += char;
                    index++;
                    
                    // Simular eventos para que la plataforma detecte el cambio
                    this.simulateInputEvents(input);
                    
                    setTimeout(typeNextChar, this.charDelay);
                } else {
                    console.log(`✅ Texto completo escrito (${text.length} caracteres)`);
                    resolve();
                }
            };
            
            typeNextChar();
        });
    }
    
    simulateInputEvents(element) {
        // Simular eventos necesarios para que la plataforma detecte el cambio
        const events = ['input', 'change', 'keydown', 'keyup'];
        events.forEach(eventName => {
            const event = new Event(eventName, { bubbles: true });
            element.dispatchEvent(event);
        });
    }
    
    async pressTabSequence(count = 2) {
        return new Promise((resolve) => {
            console.log(`⏩ Simulando ${count} pulsaciones de TAB`);
            
            let current = 0;
            const pressTab = () => {
                if (current < count) {
                    this.simulateKeyPress(9); // Código TAB
                    current++;
                    setTimeout(pressTab, this.tabDelay);
                } else {
                    console.log("✅ Secuencia de TAB completada");
                    resolve();
                }
            };
            
            pressTab();
        });
    }
    
    async pressEnter() {
        return new Promise((resolve) => {
            console.log("📤 Enviando mensaje...");
            setTimeout(() => {
                this.simulateKeyPress(13); // Código ENTER
                console.log("✅ Mensaje enviado");
                resolve();
            }, this.enterDelay);
        });
    }
    
    simulateKeyPress(keyCode) {
        // Simular evento de tecla presionada
        const keydownEvent = new KeyboardEvent('keydown', {
            keyCode: keyCode,
            which: keyCode,
            bubbles: true,
            cancelable: true
        });
        
        const keyupEvent = new KeyboardEvent('keyup', {
            keyCode: keyCode,
            which: keyCode,
            bubbles: true,
            cancelable: true
        });
        
        document.dispatchEvent(keydownEvent);
        document.dispatchEvent(keyupEvent);
        
        // Intentar también en el elemento activo
        if (document.activeElement) {
            document.activeElement.dispatchEvent(keydownEvent);
            document.activeElement.dispatchEvent(keyupEvent);
        }
    }
}

// ✅ Inicializar adaptador
const neurobitAdapter = new NeurobitPlatformAdapter();

// 🧪 Función de prueba para esta plataforma
async function testFragmentSend() {
    if (!neurobitAdapter.platformDetected.detected) {
        alert("❌ Esta plataforma no es compatible con el adaptador NEUROBIT");
        return;
    }
    
    const fragmentContent = `[FRAGMENT: prueba_01]\n¡Hola desde NEUROBIT! Esto es una prueba de envío automático de fragmentos en esta plataforma específica.`;
    
    console.log("🚀 Iniciando prueba de envío NEUROBIT...");
    const result = await neurobitAdapter.sendFragment(fragmentContent, { tabCount: 2 });
    
    if (result) {
        console.log("🎉 Prueba exitosa - el fragmento fue enviado");
    } else {
        console.error("💥 Prueba fallida - revisar consola para detalles");
    }
}

// 💡 Instrucciones de uso:
console.log(`
🧠 NEUROBIT PLATFORM ADAPTER CARGADO

Instrucciones:
1. Abre la consola de desarrollador (F12)
2. Ejecuta: testFragmentSend()
3. Observa el envío automático del fragmento

Características:
✅ Detección automática de plataforma
✅ Escritura letra por letra con delay controlado
✅ Secuencia de TAB para llegar al botón de envío
✅ Simulación de eventos de teclado completos
✅ Retroalimentación en consola en tiempo real

Soberanía operativa: 100% - sin dependencias externas
`);

// 🚀 Auto-inicializar si estamos en el contexto correcto
if (neurobitAdapter.platformDetected.detected) {
    console.log("✅ NEUROBIT ADAPTER ACTIVADO PARA ESTA PLATAFORMA");
} else {
    console.warn("⚠️ Plataforma no reconocida - el adaptador está inactivo");
}