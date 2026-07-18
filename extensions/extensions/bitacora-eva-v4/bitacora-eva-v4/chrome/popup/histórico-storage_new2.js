// ANTES (escribe inmediatamente):
// await fetch('http://127.0.0.1:5000/memoria', {method: 'POST', body: ...})

// DESPUÉS (usa dispatcher del backend):
async function syncToMemoria(messages) {
    // Los mensajes ya están en buffer del dispatcher
    // El backend decide cuándo escribir
    await fetch('http://127.0.0.1:5000/dispatch/queue', {
        method: 'POST',
        body: JSON.stringify({
            events: messages.map(msg => ({
                type: 'bitacora_message',
                content: msg,
                source: 'bitacora-eva',
                timestamp: new Date().toISOString()
            }))
        })
    });
    // El dispatcher escribe en batch automáticamente
}