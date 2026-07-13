// js/file-search.js
document.addEventListener('DOMContentLoaded', function() {
    // Cargar el estado inicial
    loadInitialState();
    
    // Event listeners
    document.getElementById('searchForm').addEventListener('submit', function(e) {
        e.preventDefault();
        startFileSearch();
    });
    
    document.getElementById('sampleListBtn').addEventListener('click', function() {
        document.getElementById('fileList').value = 'documento.pdf\nimagen.jpg\nreporte.txt\nplanilla.xlsx\npresentacion.pptx';
    });
    
    document.getElementById('defaultSourceBtn').addEventListener('click', function() {
        document.getElementById('sourceDir').value = '/home/' + getCurrentUser() + '/Documentos';
    });
});

function getCurrentUser() {
    // En un entorno real, esto vendría del servidor
    // Por ahora, usamos un método simple para detectar el usuario
    const path = window.location.pathname;
    const match = path.match(/\/home\/([^\/]+)/);
    return match ? match[1] : 'usuario';
}

function loadInitialState() {
    // Establecer valores por defecto
    const currentUser = getCurrentUser();
    document.getElementById('sourceDir').value = '/home/' + currentUser;
    document.getElementById('destFolder').value = 'archivos_recuperados_' + new Date().toISOString().slice(0,10).replace(/-/g, '');
    
    // Verificar conexión con la API
    checkApiStatus();
}

function checkApiStatus() {
    fetch('http://localhost:5000/test')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('apiStatus').innerHTML = `
                    <span class="status-indicator online"></span>
                    <span class="status-text">API Neurobit: Online</span>
                `;
            } else {
                throw new Error('API no responde correctamente');
            }
        })
        .catch(error => {
            document.getElementById('apiStatus').innerHTML = `
                <span class="status-indicator offline"></span>
                <span class="status-text">API Neurobit: Offline - ${error.message}</span>
            `;
            showNotification('La API no está disponible. ¿El servicio neurobit-api está activo?', 'error');
        });
}

function startFileSearch() {
    const fileList = document.getElementById('fileList').value.trim();
    const sourceDir = document.getElementById('sourceDir').value.trim();
    const destFolder = document.getElementById('destFolder').value.trim();
    
    // Validación básica
    if (!fileList) {
        showNotification('Por favor, ingresa una lista de archivos a buscar', 'error');
        return;
    }
    
    if (!sourceDir || !destFolder) {
        showNotification('Por favor, completa todos los campos', 'error');
        return;
    }
    
    // Mostrar cargando
    document.getElementById('searchResult').innerHTML = `
        <div class="loading-container">
            <div class="loading-spinner"></div>
            <p>🔍 Buscando archivos... Esto puede tardar dependiendo de la cantidad de archivos</p>
            <p class="subtext">No cierres esta ventana</p>
        </div>
    `;
    
    // Enviar petición a la API
    fetch('http://localhost:5000/search-files', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            file_list: fileList,
            source_dir: sourceDir,
            dest_folder: destFolder
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Error desconocido');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'started') {
            showResult(data);
            // Iniciar polling para verificar el estado
            startStatusPolling(destFolder);
        } else {
            throw new Error('Respuesta inesperada de la API');
        }
    })
    .catch(error => {
        document.getElementById('searchResult').innerHTML = `
            <div class="error-container">
                <h3>❌ Error en la búsqueda</h3>
                <p>${error.message}</p>
                <p class="tip">💡 <strong>Consejos:</strong></p>
                <ul>
                    <li>Verifica que el directorio de origen exista</li>
                    <li>Asegúrate de que el servicio neurobit-api esté activo (sudo systemctl status neurobit-api)</li>
                    <li>Revisa los permisos de las carpetas</li>
                </ul>
                <button class="btn retry-btn" onclick="startFileSearch()">↻ Reintentar</button>
            </div>
        `;
    });
}

function startStatusPolling(folderName) {
    let attempts = 0;
    const maxAttempts = 60; // 5 minutos (60 intentos * 5 segundos)
    
    const poll = setInterval(() => {
        attempts++;
        
        if (attempts > maxAttempts) {
            clearInterval(poll);
            document.getElementById('searchResult').innerHTML += `
                <div class="warning-container">
                    <p>⚠️ La búsqueda lleva más tiempo del esperado. Puedes verificar el estado manualmente.</p>
                    <button class="btn" onclick="openFolder('${folderName}')">📁 Abrir carpeta de resultados</button>
                </div>
            `;
            return;
        }
        
        // Actualizar interfaz con tiempo transcurrido
        const minutes = Math.floor(attempts / 12);
        const seconds = (attempts % 12) * 5;
        document.getElementById('searchResult').querySelector('.subtext').textContent = 
            `Tiempo transcurrido: ${minutes}m ${seconds}s`;
            
    }, 5000); // Verificar cada 5 segundos
}

function showResult(data) {
    document.getElementById('searchResult').innerHTML = `
        <div class="success-container">
            <h3>✅ ¡Búsqueda iniciada con éxito!</h3>
            <div class="result-details">
                <p><strong>📁 Carpeta de resultados:</strong> ${data.result_folder}</p>
                <p><strong>⏱️ Tiempo estimado:</strong> ${data.estimated_time}</p>
            </div>
            <div class="actions">
                <button class="btn primary-btn" onclick="openFolder('${data.result_folder}')">📁 Abrir carpeta</button>
                <button class="btn secondary-btn" onclick="downloadResults('${data.result_folder}')">📥 Descargar resultados</button>
            </div>
            <div class="status-monitor">
                <p>📊 <strong>Estado en tiempo real:</strong></p>
                <p class="status-text">Procesando... <span id="statusTimer">0s</span></p>
                <div class="progress-bar">
                    <div class="progress" id="progressBar"></div>
                </div>
            </div>
        </div>
    `;
    
    // Iniciar contador de tiempo
    let seconds = 0;
    setInterval(() => {
        seconds++;
        document.getElementById('statusTimer').textContent = `${seconds}s`;
        
        // Simular progreso (en una versión real, esto vendría de la API)
        if (seconds % 10 === 0 && document.getElementById('progressBar')) {
            const progress = Math.min(95, seconds * 2);
            document.getElementById('progressBar').style.width = `${progress}%`;
        }
    }, 1000);
}

function openFolder(path) {
    // En una aplicación de escritorio real, esto abriría la carpeta
    // Por ahora, mostramos una alerta informativa
    alert(`Para abrir la carpeta:\n\n1. Abre tu explorador de archivos\n2. Navega a: ${path}\n\nO copia esta ruta y pégala en la barra de direcciones de tu explorador.`);
    
    // En el futuro, podríamos usar una API nativa como:
    // window.electronAPI.openFolder(path);
}

function downloadResults(path) {
    // Redirigir para descargar
    window.location.href = `/download?path=${encodeURIComponent(path)}`;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${getIconForType(type)}</span>
            <p>${message}</p>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Eliminar después de 5 segundos
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 5000);
}

function getIconForType(type) {
    const icons = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    };
    return icons[type] || 'ℹ️';
}

// Para depuración
window.startFileSearch = startFileSearch;
window.checkApiStatus = checkApiStatus;
