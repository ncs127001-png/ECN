// === INTEGRACIÓN SISTEMA DE FEEDBACK ===
// Agregar este bloque al inicio de popup.js después de las dependencias

// Importar sistema de feedback (si usas módulos)
// import { FeedbackSystem } from './src/feedback.js';

// O inicializar directamente si no usas módulos
let feedbackSystem = null;

function initFeedbackSystem() {
  // Verificar si ya está inicializado globalmente
  if (window.NeurobitFeedback) {
    feedbackSystem = window.NeurobitFeedback;
    console.log('✅ Sistema de feedback inicializado (global)');
  } 
  // Si no, crear nueva instancia
  else if (typeof FeedbackSystem !== 'undefined') {
    feedbackSystem = new FeedbackSystem();
    console.log('✅ Sistema de feedback inicializado (nueva instancia)');
  } 
  // Si no existe la clase, cargar dinámicamente
  else {
    loadFeedbackModule();
  }
  
  // Configurar eventos de feedback para botones principales
  setupFeedbackEvents();
}

function loadFeedbackModule() {
  console.log('🔄 Cargando módulo de feedback dinámicamente...');
  
  const script = document.createElement('script');
  script.src = chrome.runtime.getURL('src/feedback.js');
  script.onload = () => {
    feedbackSystem = new window.FeedbackSystem();
    console.log('✅ Módulo de feedback cargado dinámicamente');
    setupFeedbackEvents();
  };
  script.onerror = (e) => {
    console.error('❌ Error al cargar módulo de feedback:', e);
  };
  document.head.appendChild(script);
  
  // Cargar estilos
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = chrome.runtime.getURL('src/css/feedback.css');
  document.head.appendChild(link);
}

function setupFeedbackEvents() {
  if (!feedbackSystem) {
    console.warn('⚠️ Sistema de feedback no disponible para eventos');
    return;
  }
  
  console.log('🎯 Configurando eventos de feedback...');
  
  // Botón de copiar
  const copyBtn = document.getElementById('copy-btn');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      feedbackSystem.success('✓ Copiado al Arca actual', 2000);
    });
    console.log('✅ Evento feedback: copy-btn');
  }
  
  // Botón de guardar
  const saveBtn = document.getElementById('save-btn');
  if (saveBtn) {
    saveBtn.addEventListener('click', () => {
      feedbackSystem.info('💾 Guardando cambios...', 1500);
      setTimeout(() => {
        feedbackSystem.success('✓ Cambios guardados', 2000);
      }, 300);
    });
    console.log('✅ Evento feedback: save-btn');
  }
  
  // Botón de exportar
  const exportBtn = document.getElementById('export-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      feedbackSystem.info('📤 Preparando exportación...', 1500);
      setTimeout(() => {
        feedbackSystem.success('✓ Datos exportados', 2000);
      }, 400);
    });
    console.log('✅ Evento feedback: export-btn');
  }
  
  // Botón de importar
  const importBtn = document.getElementById('import-btn');
  if (importBtn) {
    importBtn.addEventListener('click', () => {
      feedbackSystem.warning('📁 Selecciona archivo a importar', 2500);
    });
    console.log('✅ Evento feedback: import-btn');
  }
  
  // Formulario de mensaje
  const messageForm = document.getElementById('message-form');
  if (messageForm) {
    messageForm.addEventListener('submit', (e) => {
      e.preventDefault();
      feedbackSystem.info('💬 Procesando mensaje...', 1200);
    });
    console.log('✅ Evento feedback: message-form');
  }
  
  console.log('🎉 Todos los eventos de feedback configurados');
}

// Inicializar sistema cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 Inicializando sistema de feedback Neurobit...');
  initFeedbackSystem();
  
  // Feedback de inicio del popup
  setTimeout(() => {
    if (feedbackSystem) {
      feedbackSystem.info('🧠 Neurobit listo', 1500);
    }
  }, 300);
});

// Función de utilidad para mostrar feedback desde cualquier parte
function showFeedback(message, type = 'info', duration = 2000) {
  if (feedbackSystem) {
    feedbackSystem.show(message, type, duration);
  } else {
    console.log(`[${type.toUpperCase()}] ${message}`);
  }
}

// Exportar para uso global
window.showFeedback = showFeedback;
window.initFeedbackSystem = initFeedbackSystem;

// === FIN INTEGRACIÓN SISTEMA DE FEEDBACK ===