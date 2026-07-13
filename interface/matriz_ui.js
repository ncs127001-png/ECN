/**
 * matriz_ui.js
 * 
 * Interfaz interactiva para la Matriz 13x13 en Estación Central
 * Integración con arquetipos.js
 * 
 * Función: Renderizar la matriz como grid HTML+CSS interactivo
 *          Permitir seleccionar celdas y generar neurobytes
 */

class MatrizUI {
  constructor(contenedor, tamaño = 13) {
    this.contenedor = typeof contenedor === 'string' 
      ? document.querySelector(contenedor) 
      : contenedor;
    this.tamaño = tamaño;
    this.matriz = new MatrizArquetipos(tamaño);
    this.celdaSeleccionada = null;
    this.init();
  }

  /**
   * Inicializar la interfaz
   */
  init() {
    this.crearHTML();
    this.aplicarEstilos();
    this.attachEventListeners();
  }

  /**
   * Crear estructura HTML del grid 13x13
   */
  crearHTML() {
    // Contenedor principal
    const wrapper = document.createElement('div');
    wrapper.className = 'matriz-wrapper';
    wrapper.innerHTML = `
      <div class="matriz-header">
        <h2>🧬 Matriz de Arquetipos 13×13</h2>
        <p class="matriz-desc">Selecciona celdas para generar neurobytes. La simetría hermética se valida automáticamente.</p>
      </div>
      
      <div class="matriz-container">
        <div id="matriz-grid" class="matriz-grid"></div>
      </div>
      
      <div class="matriz-info">
        <div id="celda-info" class="celda-info">
          <p>Haz clic en una celda para ver sus propiedades</p>
        </div>
        <div id="neurobyte-visor" class="neurobyte-visor" style="display: none;">
          <h3>📨 Neurobyte Generado</h3>
          <div id="neurobyte-content"></div>
        </div>
      </div>
      
      <div class="matriz-acciones">
        <button id="btn-validar-simetria" class="btn btn-primary">✓ Validar Simetría</button>
        <button id="btn-generar-neurobyte" class="btn btn-secondary">📬 Generar Neurobyte</button>
        <button id="btn-exportar" class="btn btn-tertiary">💾 Exportar Matriz</button>
      </div>
    `;

    this.contenedor.appendChild(wrapper);
    this.grid = document.getElementById('matriz-grid');
    this.renderizarGrid();
  }

  /**
   * Renderizar el grid 13x13
   */
  renderizarGrid() {
    this.grid.innerHTML = '';
    
    const matrizJSON = this.matriz.obtenerMatrizJSON();
    const arquetipos = matrizJSON.arquetipos;

    for (let i = 0; i < this.tamaño; i++) {
      for (let j = 0; j < this.tamaño; j++) {
        const celda = this.matriz.obtenerCelda(i, j);
        const cellEl = document.createElement('div');
        
        cellEl.className = 'celda';
        cellEl.dataset.fila = i;
        cellEl.dataset.columna = j;
        cellEl.dataset.raiz = celda.raiz;
        cellEl.style.backgroundColor = celda.color;
        cellEl.innerHTML = `<span>${celda.raiz}</span>`;
        
        // Añadir borde especial a celdas importantes
        if ((i === 0 || i === this.tamaño - 1) && (j === 0 || j === this.tamaño - 1)) {
          cellEl.classList.add('esquina'); // Perno de 6
        } else if (i === 0 || i === this.tamaño - 1 || j === 0 || j === this.tamaño - 1) {
          cellEl.classList.add('muro'); // Muro de 9s
        } else if (i === 6 && j === 6) {
          cellEl.classList.add('centro'); // Centro (Voluntad)
        }
        
        cellEl.addEventListener('click', () => this.seleccionarCelda(i, j));
        cellEl.addEventListener('mouseenter', () => this.mostrarInfoCelda(i, j));
        
        this.grid.appendChild(cellEl);
      }
    }
  }

  /**
   * Seleccionar celda y actualizar interfaz
   */
  seleccionarCelda(fila, columna) {
    // Limpiar selección anterior
    document.querySelectorAll('.celda.selected').forEach(c => c.classList.remove('selected'));
    
    // Nueva selección
    const cellEl = this.grid.querySelector(`[data-fila="${fila}"][data-columna="${columna}"]`);
    cellEl.classList.add('selected');
    
    this.celdaSeleccionada = { fila, columna };
    this.mostrarInfoCelda(fila, columna);
  }

  /**
   * Mostrar información de la celda
   */
  mostrarInfoCelda(fila, columna) {
    const celda = this.matriz.obtenerCelda(fila, columna);
    const info = document.getElementById('celda-info');
    
    info.innerHTML = `
      <h3>📍 Celda: [${fila}, ${columna}]</h3>
      <p><strong>Arquetipo:</strong> ${celda.nombre}</p>
      <p><strong>Raíz Numerológica:</strong> ${celda.raiz}</p>
      <p><strong>Vibración:</strong> ${celda.vibración}</p>
      <p><strong>Color:</strong> ${celda.color}</p>
      ${fila === 6 && columna === 6 ? '<p style="color: #f38181;"><strong>✨ CENTRO - VOLUNTAD DEL HOMO VIVO</strong></p>' : ''}
      ${(fila === 0 || fila === 12 || columna === 0 || columna === 12) ? '<p style="color: #FFD3B6;"><strong>🛡️ PROTECCIÓN - PARTE DE LOS MUROS</strong></p>' : ''}
    `;
  }

  /**
   * Aplicar estilos CSS
   */
  aplicarEstilos() {
    const style = document.createElement('style');
    style.textContent = `
      .matriz-wrapper {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 24px;
        margin: 20px 0;
      }

      .matriz-header {
        margin-bottom: 20px;
        text-align: center;
      }

      .matriz-header h2 {
        font-size: 22px;
        margin-bottom: 8px;
        color: #3a6df0;
      }

      .matriz-desc {
        color: #9aa4b2;
        font-size: 14px;
      }

      .matriz-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
        overflow-x: auto;
        padding: 10px;
      }

      .matriz-grid {
        display: grid;
        grid-template-columns: repeat(13, minmax(40px, 1fr));
        gap: 2px;
        background: rgba(0, 0, 0, 0.3);
        padding: 8px;
        border-radius: 8px;
      }

      .celda {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: bold;
        font-size: 12px;
        color: #0b0f14;
        user-select: none;
      }

      .celda:hover {
        transform: scale(1.1);
        box-shadow: 0 0 8px rgba(255, 255, 255, 0.3);
      }

      .celda.selected {
        border: 2px solid #fff;
        box-shadow: 0 0 12px rgba(255, 255, 255, 0.5);
        transform: scale(1.15);
      }

      .celda.centro {
        border: 2px solid #000;
        box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.5);
      }

      .celda.muro {
        border: 1px dashed rgba(255, 255, 255, 0.3);
      }

      .celda.esquina {
        border: 2px solid #000;
      }

      .matriz-info {
        background: rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 16px;
        margin: 20px 0;
        min-height: 120px;
      }

      .celda-info, .neurobyte-visor {
        color: #eef2f7;
      }

      .celda-info h3, .neurobyte-visor h3 {
        color: #3a6df0;
        margin-bottom: 8px;
        font-size: 14px;
      }

      .celda-info p, .neurobyte-visor p {
        font-size: 13px;
        margin: 4px 0;
        color: #9aa4b2;
      }

      .neurobyte-content {
        background: rgba(255, 255, 255, 0.05);
        border-left: 3px solid #3a6df0;
        padding: 12px;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
        word-break: break-all;
        margin-top: 8px;
      }

      .matriz-acciones {
        display: flex;
        gap: 12px;
        justify-content: center;
        margin-top: 20px;
        flex-wrap: wrap;
      }

      .btn {
        padding: 10px 20px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.3s ease;
      }

      .btn-primary {
        background: #3a6df0;
        color: #fff;
      }

      .btn-primary:hover {
        background: #2452c0;
        transform: translateY(-2px);
      }

      .btn-secondary {
        background: #22c55e;
        color: #fff;
      }

      .btn-secondary:hover {
        background: #16a34a;
        transform: translateY(-2px);
      }

      .btn-tertiary {
        background: rgba(255, 255, 255, 0.1);
        color: #eef2f7;
        border: 1px solid rgba(255, 255, 255, 0.2);
      }

      .btn-tertiary:hover {
        background: rgba(255, 255, 255, 0.15);
      }

      @media (max-width: 768px) {
        .matriz-grid {
          grid-template-columns: repeat(13, minmax(30px, 1fr));
        }

        .celda {
          width: 30px;
          height: 30px;
          font-size: 10px;
        }

        .matriz-acciones {
          gap: 8px;
        }

        .btn {
          padding: 8px 16px;
          font-size: 12px;
        }
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * Attach event listeners a botones
   */
  attachEventListeners() {
    document.getElementById('btn-validar-simetria').addEventListener('click', () => {
      this.validarSimetria();
    });

    document.getElementById('btn-generar-neurobyte').addEventListener('click', () => {
      this.generarNeurobyte();
    });

    document.getElementById('btn-exportar').addEventListener('click', () => {
      this.exportarMatriz();
    });
  }

  /**
   * Validar simetría hermética
   */
  validarSimetria() {
    const valida = this.matriz.validarSimetria();
    const mensaje = valida 
      ? "✅ Simetría hermética VÁLIDA - 'Como es Arriba, es Abajo'" 
      : "❌ Simetría NO válida - estructura corrupta";
    
    alert(mensaje);
    console.log(`Simetría: ${valida}`);
  }

  /**
   * Generar neurobyte desde la celda seleccionada
   */
  generarNeurobyte() {
    if (!this.celdaSeleccionada) {
      alert("Selecciona una celda primero");
      return;
    }

    const celda = this.matriz.obtenerCelda(
      this.celdaSeleccionada.fila,
      this.celdaSeleccionada.columna
    );

    // Generar un neurobyte desde el texto del arquetipo
    const texto = `${celda.nombre} - ${celda.vibración} [${this.celdaSeleccionada.fila},${this.celdaSeleccionada.columna}]`;
    const neurobyte = this.matriz.encodeDesdeTexto(texto);

    // Mostrar en la interfaz
    const visor = document.getElementById('neurobyte-visor');
    const content = document.getElementById('neurobyte-content');
    
    visor.style.display = 'block';
    content.innerHTML = `
      <div class="neurobyte-content">
        <p><strong>Contenido:</strong> ${neurobyte.contenido}</p>
        <p><strong>Hash:</strong> ${neurobyte.hash}</p>
        <p><strong>Arquetipos:</strong> ${neurobyte.arquetipos_usados.slice(0, 5).join(', ')}...</p>
        <p><strong>Simetría Validada:</strong> ${neurobyte.simetria_validada ? '✓' : '✗'}</p>
        <p><strong>Timestamp:</strong> ${neurobyte.timestamp}</p>
      </div>
    `;

    console.log("Neurobyte generado:", neurobyte);
  }

  /**
   * Exportar matriz completa como JSON
   */
  exportarMatriz() {
    const matrizJSON = this.matriz.obtenerMatrizJSON();
    const json = JSON.stringify(matrizJSON, null, 2);
    
    // Crear blob y descargar
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `matriz_13x13_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    console.log("Matriz exportada:", matrizJSON);
  }
}

// Exportar para uso
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MatrizUI;
}
