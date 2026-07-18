// ARCHIVO: background.js
//------------------------------------------------


chrome.runtime.onInstalled.addListener(() => {
  console.log("Bitácora EVA instalada.");
});
// background.js - gestor simple de bitácora
chrome.runtime.onInstalled.addListener(() => {
  console.log('[EVA background] installed');
});

// escucha mensajes de content.js
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if(msg && msg.type === 'EVA_SAVE_REPLY' && msg.entry){
    chrome.storage.local.get({ bitacora: [] }, (res) => {
      const arr = res.bitacora || [];
      arr.push(msg.entry);
      chrome.storage.local.set({ bitacora: arr }, () => {
        console.log('[EVA background] entry saved. total=', arr.length);
        sendResponse({ ok: true, total: arr.length });
      });
    });
    // keep message channel open for async response
    return true;
  }
});
