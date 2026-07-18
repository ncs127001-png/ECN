// feedback.js - Sistema de feedback visual minimalista pero efectivo
class FeedbackSystem {
  constructor() {
    this.init();
  }

  init() {
    // Crear contenedor global si no existe
    if (!document.getElementById('neurobit-feedback-container')) {
      const container = document.createElement('div');
      container.id = 'neurobit-feedback-container';
      container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 300px;
        pointer-events: none;
      `;
      document.body.appendChild(container);
    }
  }

  show(message, type = 'info', duration = 2000) {
    const container = document.getElementById('neurobit-feedback-container');
    const feedback = document.createElement('div');
    
    // Definir clases y estilos según tipo
    const styles = {
      success: 'background: linear-gradient(135deg, #00c853 0%, #00897b 100%); border-left: 4px solid #00c853;',
      error: 'background: linear-gradient(135deg, #ff5252 0%, #d32f2f 100%); border-left: 4px solid #ff5252;',
      info: 'background: linear-gradient(135deg, #2196f3 0%, #0288d1 100%); border-left: 4px solid #2196f3;',
      warning: 'background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); border-left: 4px solid #ff9800;'
    };

    feedback.className = `neurobit-feedback ${type}`;
    feedback.style.cssText = `
      ${styles[type]}
      color: white;
      padding: 12px 16px;
      margin-bottom: 8px;
      border-radius: 0 4px 4px 0;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      animation: slideIn 0.3s ease forwards, fadeOut 0.5s ease 1.5s forwards;
      opacity: 0;
      transform: translateX(100%);
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      font-size: 14px;
      line-height: 1.4;
      pointer-events: auto;
      transition: all 0.3s ease;
    `;

    feedback.innerHTML = `
      <div style="display: flex; align-items: center; gap: 8px;">
        <span class="icon" style="font-weight: bold; font-size: 18px;">
          ${type === 'success' ? '✓' : type === 'error' ? '✗' : type === 'warning' ? '!' : '●'}
        </span>
        <span class="message">${message}</span>
      </div>
      <style>
        @keyframes slideIn {
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes fadeOut {
          to { opacity: 0; transform: translateX(100px); }
        }
        .neurobit-feedback:hover {
          transform: translateX(-5px);
          box-shadow: 0 6px 16px rgba(0,0,0,0.25);
        }
      </style>
    `;

    container.appendChild(feedback);

    // Eliminar automáticamente después de la duración
    setTimeout(() => {
      feedback.style.animation = 'fadeOut 0.5s ease forwards';
      setTimeout(() => {
        if (feedback.parentNode) {
          feedback.parentNode.removeChild(feedback);
        }
      }, 500);
    }, duration);

    return feedback;
  }

  // Métodos abreviados para cada tipo
  success(message, duration = 2000) {
    return this.show(message, 'success', duration);
  }

  error(message, duration = 3000) {
    return this.show(message, 'error', duration);
  }

  info(message, duration = 2000) {
    return this.show(message, 'info', duration);
  }

  warning(message, duration = 2500) {
    return this.show(message, 'warning', duration);
  }
}

// Inicializar sistema globalmente
window.NeurobitFeedback = new FeedbackSystem();

// Exportar para uso en módulos
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FeedbackSystem;
}