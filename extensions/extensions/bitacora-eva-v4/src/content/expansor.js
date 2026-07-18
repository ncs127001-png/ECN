// ARCHIVO: expansor.js
// -------------------------------------
// Módulo para expansión de historial y scroll infinito

/**
 * Clase para manejar la expansión del historial de ChatGPT
 */
class HistoryExpander {
  constructor() {
    this.isExpanding = false;
    this.maxScrollAttempts = 10;
    this.scrollDelay = 1000;
  }

  /**
   * Busca botones de "Mostrar más" o "Load more"
   * @returns {Element[]} Array de botones encontrados
   */
  findLoadMoreButtons() {
    const selectors = [
      'button[aria-label*="Mostrar más"]',
      'button[aria-label*="Show more"]',
      'button[aria-label*="Load more"]',
      'button[aria-label*="Cargar más"]',
      'button:contains("Mostrar más")',
      'button:contains("Show more")',
      'button:contains("Load more")',
      'button:contains("Cargar más")',
      '[data-testid*="load-more"]',
      '[data-testid*="show-more"]'
    ];

    const buttons = [];
    selectors.forEach(selector => {
      try {
        const elements = document.querySelectorAll(selector);
        elements.forEach(el => {
          if (el.offsetParent !== null && !buttons.includes(el)) {
            buttons.push(el);
          }
        });
      } catch (e) {
        // Ignorar selectores inválidos
      }
    });

    return buttons;
  }

  /**
   * Busca indicadores de scroll infinito
   * @returns {Element[]} Array de elementos de scroll infinito
   */
  findInfiniteScrollElements() {
    const selectors = [
      '[data-testid*="infinite"]',
      '[data-testid*="scroll"]',
      '.infinite-scroll',
      '.load-more',
      '.show-more'
    ];

    const elements = [];
    selectors.forEach(selector => {
      try {
        const found = document.querySelectorAll(selector);
        found.forEach(el => {
          if (el.offsetParent !== null && !elements.includes(el)) {
            elements.push(el);
          }
        });
      } catch (e) {
        // Ignorar selectores inválidos
      }
    });

    return elements;
  }

  /**
   * Hace scroll hasta el final de la página
   * @returns {Promise<void>}
   */
  async scrollToBottom() {
    return new Promise((resolve) => {
      const scrollHeight = document.documentElement.scrollHeight;
      window.scrollTo(0, scrollHeight);
      
      // Esperar un poco para que se cargue contenido dinámico
      setTimeout(() => {
        resolve();
      }, 500);
    });
  }

  /**
   * Expande el historial haciendo scroll y clickeando botones
   * @returns {Promise<boolean>} true si se expandió exitosamente
   */
  async expandHistory() {
    if (this.isExpanding) {
      console.log('[EVA Expander] Ya se está expandiendo el historial');
      return false;
    }

    this.isExpanding = true;
    console.log('[EVA Expander] Iniciando expansión del historial');

    try {
      let expanded = false;
      let attempts = 0;

      while (attempts < this.maxScrollAttempts) {
        attempts++;
        console.log(`[EVA Expander] Intento ${attempts}/${this.maxScrollAttempts}`);

        // Buscar botones de "Mostrar más"
        const loadMoreButtons = this.findLoadMoreButtons();
        if (loadMoreButtons.length > 0) {
          console.log(`[EVA Expander] Encontrados ${loadMoreButtons.length} botones de "Mostrar más"`);
          
          for (const button of loadMoreButtons) {
            try {
              button.click();
              console.log('[EVA Expander] Click en botón "Mostrar más"');
              expanded = true;
              
              // Esperar a que se cargue el contenido
              await new Promise(resolve => setTimeout(resolve, this.scrollDelay));
            } catch (e) {
              console.warn('[EVA Expander] Error al hacer click en botón:', e);
            }
          }
        }

        // Hacer scroll hacia abajo
        await this.scrollToBottom();

        // Verificar si hay más contenido para cargar
        const newButtons = this.findLoadMoreButtons();
        if (newButtons.length === 0) {
          console.log('[EVA Expander] No hay más botones de "Mostrar más"');
          break;
        }

        // Esperar antes del siguiente intento
        await new Promise(resolve => setTimeout(resolve, this.scrollDelay));
      }

      console.log(`[EVA Expander] Expansión completada. Intentos: ${attempts}`);
      return expanded;

    } catch (error) {
      console.error('[EVA Expander] Error durante la expansión:', error);
      return false;
    } finally {
      this.isExpanding = false;
    }
  }

  /**
   * Verifica si hay más contenido disponible para cargar
   * @returns {boolean} true si hay más contenido
   */
  hasMoreContent() {
    const buttons = this.findLoadMoreButtons();
    const scrollElements = this.findInfiniteScrollElements();
    
    return buttons.length > 0 || scrollElements.length > 0;
  }

  /**
   * Obtiene información del estado actual del historial
   * @returns {Object} Información del estado
   */
  getHistoryInfo() {
    const buttons = this.findLoadMoreButtons();
    const scrollElements = this.findInfiniteScrollElements();
    const scrollHeight = document.documentElement.scrollHeight;
    const clientHeight = document.documentElement.clientHeight;
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

    return {
      hasLoadMoreButtons: buttons.length > 0,
      hasInfiniteScroll: scrollElements.length > 0,
      isAtBottom: (scrollTop + clientHeight) >= (scrollHeight - 100),
      scrollHeight,
      clientHeight,
      scrollTop,
      isExpanding: this.isExpanding
    };
  }
}

// Crear instancia global
const historyExpander = new HistoryExpander();

// Escuchar mensajes para expandir historial
window.addEventListener("message", async (event) => {
  if (event.data.type === "EVA_EXPAND_HISTORY") {
    console.log('[EVA Expander] Recibido mensaje para expandir historial');
    
    try {
      const expanded = await historyExpander.expandHistory();
      
      // Enviar respuesta
      window.postMessage({
        type: "EVA_HISTORY_EXPANDED",
        success: expanded,
        info: historyExpander.getHistoryInfo()
      }, "*");
      
    } catch (error) {
      console.error('[EVA Expander] Error al expandir historial:', error);
      
      window.postMessage({
        type: "EVA_HISTORY_EXPANDED",
        success: false,
        error: error.message
      }, "*");
    }
  }
});

// Exportar para uso en otros módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    HistoryExpander,
    historyExpander
  };
}
