// CONECTOR_INACTIVO: Este módulo está listo pero no se invoca automáticamente. Requiere acción explícita del usuario (ej. escribir >20 chars).
export const Ollama = {
    async analizar(texto) {
        try {
            const response = await fetch('http://localhost:11434/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: 'neurobit-strict:latest',
                    prompt: `Analiza el siguiente texto y devuelve únicamente un JSON con este formato: {"context": "TITULO_CORTO", "tags": "TAG1, TAG2"}. \n\nTexto: ${texto}`,
                    stream: false
                })
            });
            const data = await response.json();
            // Limpiamos la respuesta de Ollama por si incluye markdown
            const cleanResponse = data.response.replace(/```json|```/g, '').trim();
            return JSON.parse(cleanResponse);
        } catch (err) {
            console.error("Ollama Offline o Error de CORS");
            return null;
        }
    }
};