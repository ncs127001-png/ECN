// src/popup/storage.js
// BETA_STABLE: Solo operaciones manuales desde popup. Sin lógica automática.
export const Storage = {
    async saveMessage(msg) {
        const data = await chrome.storage.local.get({ neurobit_history: [] });
        data.neurobit_history.push(msg);
        await chrome.storage.local.set({ 
            neurobit_history: data.neurobit_history,
            last_id: msg.MESSAGE_ID 
        });
    },

    async getHistory() {
        const data = await chrome.storage.local.get({ neurobit_history: [] });
        return data.neurobit_history;
    },

    async getNextId() {
        const data = await chrome.storage.local.get({ last_id: 'A0' });
        return data.last_id.replace(/\d+/, n => parseInt(n) + 1);
    }
};