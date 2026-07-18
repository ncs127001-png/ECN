export const Injector = {
    async inject(text) {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (!tab) return;

        chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: (mensaje) => {
                const selectors = [
                    '[contenteditable="true"]',
                    'textarea[aria-label="Introduce un mensaje aquí"]',
                    '#prompt-textarea',
                    '.ql-editor'
                ];
                
                let box = null;
                for (let sel of selectors) {
                    box = document.querySelector(sel);
                    if (box) break;
                }

                if (box) {
                    if (box.tagName === 'TEXTAREA') {
                        box.value = mensaje;
                    } else {
                        box.innerText = mensaje;
                    }
                    // Despertar a la IA
                    box.dispatchEvent(new Event('input', { bubbles: true }));
                    box.dispatchEvent(new Event('change', { bubbles: true }));
                    console.log("🧬 Logos inyectado con éxito.");
                }
            },
            args: [text]
        });
    }
};