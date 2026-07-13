// interface/matriz_ui.js - v0.3 SOBERANO
// Propósito: Renderizar la MFN 13x13 y los bloques de espines binarios en el frontend.

class NeurobitCanvasRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.tamCelda = 30; // Píxeles por celda para monitor wide
        this.pivoteG7 = { row: 7, col: 7 }; // Base 1 (SINCERO)
    }

    dibujarMatrizBase(mapaBits169) {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        let idx = 0;
        for (let r = 1; r <= 13; r++) {
            for (let c = 1; c <= 13; c++) {
                let x = (c - 1) * this.tamCelda;
                let y = (r - 1) * this.tamCelda;
                
                // Color por capas de profundidad (Z)
                if (r === this.pivoteG7.row && c === this.pivoteG7.col) {
                    this.ctx.fillStyle = '#ff9900'; // El Centro 5 (Mónada)
                } else if (r === 1 || r === 13 || c === 1 || c === 13) {
                    this.ctx.fillStyle = '#1a0033'; // Anillo Exterior (Perímetro Negro)
                } else {
                    this.ctx.fillStyle = mapaBits169[idx] === 1 ? '#00ff66' : '#222222';
                }
                
                this.ctx.fillRect(x, y, this.tamCelda - 2, this.tamCelda - 2);
                idx++;
            }
        }
        console.log("⚡ [GUI] Grilla radial 13x13 actualizada en pantalla.");
    }
}

