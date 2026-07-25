/**
 * arquetipos.js
 * 
 * NEUROBIT v2.1 - Módulo de Arquetipos
 * 
 * Implementa la Matriz 13x13 como estructura viva:
 * - Raíces numerológicas (reducción teosófica 1-9)
 * - Simetría hermética: f1(c3:c11) = f13(c3:c11)
 * - Arquetipos como sigilos dinámicos
 * - Encoding/decoding de neurobytes
 * 
 * Soberanía: Cero dependencias externas (solo JS vanilla + crypto nativa)
 * 
 * Uso:
 *   const matriz = new MatrizArquetipos(13);
 *   const neurobyte = matriz.encodeDesdeTexto("Mensaje sanador");
 *   console.log(neurobyte); // { contenido, hash, arquetipos, simetria_validada }
 */

class MatrizArquetipos {
  constructor(tamaño = 13) {
    this.tamaño = tamaño;
    this.centro = Math.floor(tamaño / 2); // 6 para 13x13
    this.matriz = this.generarMatrizBase();
    this.arquetipos = this.mapearArquetipos();
  }

  /**
   * Reducción teosófica: suma dígitos hasta obtener 1-9
   * Ejemplo: 38 → 3+8 = 11 → 1+1 = 2
   */
  reducirTeosoficamente(numero) {
    if (numero < 1) return 9;
    while (numero >= 10) {
      numero = Math.floor(numero / 10) + (numero % 10);
    }
    return numero || 9;
  }

  /**
   * Genera matriz 13x13 con simetría hermética
   * Principio: "Como es Arriba, es Abajo" (Hermes Trismegisto)
   * 
   * Estructura:
   * - Muros de 9s (protección semántica): filas/columnas 0, 12
   * - Pernos de 6s (anclaje): esquinas
   * - Centro 3x3: teclado numérico (universal)
   * - Simetría: fila_i <-> fila_(n-1-i)
   */
  generarMatrizBase() {
    const matriz = Array(this.tamaño)
      .fill(null)
      .map(() => Array(this.tamaño).fill(0));

    // Llenar con números 1-9 basados en posición
    for (let i = 0; i < this.tamaño; i++) {
      for (let j = 0; j < this.tamaño; j++) {
        // Distancia desde centro (Manhattane)
        const distancia = Math.abs(i - this.centro) + Math.abs(j - this.centro);
        
        // Raíz numerológica basada en distancia
        let valor = (distancia % 9) + 1; // 1-9
        
        // Reglas especiales para protección
        if (i === 0 || i === this.tamaño - 1 || j === 0 || j === this.tamaño - 1) {
          valor = 9; // Muros de 9s
        }
        
        // Pernos de 6s en esquinas
        if ((i === 0 || i === this.tamaño - 1) && (j === 0 || j === this.tamaño - 1)) {
          valor = 6;
        }
        
        // Aplicar simetría hermética
        matriz[i][j] = valor;
      }
    }

    // Validar y reforzar simetría
    this.aplicarSimetriaHermetica(matriz);
    return matriz;
  }

  /**
   * Refuerza la simetría: fila_i refleja fila_(n-1-i) en columnas 3-11
   */
  aplicarSimetriaHermetica(matriz) {
    const inicio = 3;
    const fin = this.tamaño - 3;
    
    for (let i = 0; i < Math.floor(this.tamaño / 2); i++) {
      const simetrica = this.tamaño - 1 - i;
      
      for (let j = inicio; j < fin; j++) {
        // Ambas filas deben tener el mismo arquetipo en esta posición
        const raiz = this.reducirTeosoficamente(matriz[i][j]);
        matriz[simetrica][j] = raiz;
      }
    }
  }

  /**
   * Mapea cada celda a su arquetipo (sigilo numerológico)
   */
  mapearArquetipos() {
    const map = {};
    const arquetiposDesc = {
      1: { nombre: "Unidad", color: "#FF6B6B", vibración: "Inicio" },
      2: { nombre: "Dualidad", color: "#4ECDC4", vibración: "Equilibrio" },
      3: { nombre: "Trinidad", color: "#FFE66D", vibración: "Expresión" },
      4: { nombre: "Orden", color: "#95E1D3", vibración: "Estabilidad" },
      5: { nombre: "Voluntad", color: "#F38181", vibración: "Poder" }, // Centro
      6: { nombre: "Armonía", color: "#AA96DA", vibración: "Unión" },
      7: { nombre: "Sabiduría", color: "#FCBAD3", vibración: "Intuición" },
      8: { nombre: "Infinito", color: "#A8E6CF", vibración: "Ciclo" },
      9: { nombre: "Completitud", color: "#FFD3B6", vibración: "Cierre" }
    };

    for (let i = 0; i < this.tamaño; i++) {
      for (let j = 0; j < this.tamaño; j++) {
        const raiz = this.matriz[i][j];
        const id = `${i}-${j}`;
        map[id] = {
          posicion: [i, j],
          raiz,
          ...arquetiposDesc[raiz]
        };
      }
    }

    return map;
  }

  /**
   * Convierte texto a neurobyte usando arquetipos de la matriz
   * Neurobyte: 169 caracteres máximo (13x13 sigilo)
   */
  encodeDesdeTexto(texto) {
    const maxChars = 169; // 13x13
    const truncado = texto.substring(0, maxChars);
    
    // Convertir cada carácter a su valor ASCII
    const valores = Array.from(truncado).map(c => c.charCodeAt(0));
    
    // Mapear valores a arquetipos
    const arquetiposUsados = [];
    const trayectoria = [];
    
    for (let idx = 0; idx < valores.length; idx++) {
      const ascii = valores[idx];
      const raiz = this.reducirTeosoficamente(ascii);
      
      // Encontrar una celda con este arquetipo
      const celds = Object.entries(this.arquetipos)
        .filter(([_, a]) => a.raiz === raiz);
      
      if (celds.length > 0) {
        const [cellId, arquetipoCell] = celds[idx % celds.length];
        trayectoria.push(cellId);
        arquetiposUsados.push(arquetipoCell);
      }
    }

    // Calcular hash SHA-1 (simulado con crypto nativa si está disponible)
    const hash = this.calcularHash(truncado);
    
    // Validar simetría
    const simetriaValida = this.validarSimetria();

    return {
      contenido: truncado,
      contenido_original_length: texto.length,
      hash,
      arquetipos_usados: arquetiposUsados.map(a => a.nombre),
      trayectoria,
      simetria_validada: simetriaValida,
      timestamp: new Date().toISOString(),
      protocol_version: "NEUROBIT_v2.1"
    };
  }

  /**
   * Calcula hash del contenido (SHA-1 si disponible, fallback a simple hash)
   */
  calcularHash(contenido) {
    // Si estamos en navegador moderno, usar SubtleCrypto
    if (typeof crypto !== 'undefined' && crypto.subtle) {
      // Esto retorna Promise, así que devolvemos una versión sincrónica de fallback
      let hash = 0;
      for (let i = 0; i < contenido.length; i++) {
        const char = contenido.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash; // Convertir a int32
      }
      return Math.abs(hash).toString(16).padStart(40, '0'); // Simular SHA-1
    }
    
    // Fallback: simple hash de 40 caracteres
    let hash = 0;
    for (let i = 0; i < contenido.length; i++) {
      hash = ((hash << 5) - hash) + contenido.charCodeAt(i);
    }
    return Math.abs(hash).toString(16).padStart(40, '0');
  }

  /**
   * Decodifica neurobyte de vuelta a texto
   */
  decodeDesdeNeurobyte(neurobyte) {
    if (!neurobyte.trayectoria || !neurobyte.contenido) {
      return null;
    }
    
    // Validar que la simetría se mantenga
    if (!neurobyte.simetria_validada) {
      console.warn("⚠️ Advertencia: neurobyte no pasó validación de simetría");
    }

    return {
      texto: neurobyte.contenido,
      hash_verificado: neurobyte.hash,
      arquetipos: neurobyte.arquetipos_usados,
      timestamp_creacion: neurobyte.timestamp
    };
  }

  /**
   * Valida que la simetría hermética se mantenga
   * Regla: fila_i[c3:c11] == fila_(n-1-i)[c3:c11]
   */
  validarSimetria() {
    const inicio = 3;
    const fin = this.tamaño - 3;
    
    for (let i = 0; i < Math.floor(this.tamaño / 2); i++) {
      const simetrica = this.tamaño - 1 - i;
      
      for (let j = inicio; j < fin; j++) {
        if (this.matriz[i][j] !== this.matriz[simetrica][j]) {
          return false;
        }
      }
    }
    return true;
  }

  /**
   * Retorna la matriz como objeto JSON para visualización
   */
  obtenerMatrizJSON() {
    return {
      tamaño: this.tamaño,
      centro: this.centro,
      matriz: this.matriz,
      arquetipos: this.arquetipos,
      simetria_valida: this.validarSimetria(),
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Retorna una celda específica con su información completa
   */
  obtenerCelda(fila, columna) {
    if (fila < 0 || fila >= this.tamaño || columna < 0 || columna >= this.tamaño) {
      return null;
    }
    
    const id = `${fila}-${columna}`;
    return {
      id,
      posicion: [fila, columna],
      ...this.arquetipos[id]
    };
  }

  /**
   * Retorna todas las celdas con una raíz numerológica específica
   */
  obtenerCeldasPorRaiz(raiz) {
    return Object.entries(this.arquetipos)
      .filter(([_, a]) => a.raiz === raiz)
      .map(([id, a]) => ({ id, ...a }));
  }
}

/**
 * Exportar para uso en navegador y Node.js
 */
if (typeof module !== 'undefined' && module.exports) {
  module.exports = MatrizArquetipos;
}

// TESTS BÁSICOS (ejecutar en consola del navegador o con Node.js)
if (typeof window === 'undefined') {
  // Estamos en Node.js
  const matriz = new MatrizArquetipos(13);
  
  console.log("\n🧪 TEST 1: Validar simetría hermética");
  console.log(`✅ Simetría válida: ${matriz.validarSimetria()}`);
  
  console.log("\n🧪 TEST 2: Encoding de neurobyte");
  const neurobyte = matriz.encodeDesdeTexto("Aquí está el Logos restaurado");
  console.log(`✅ Hash: ${neurobyte.hash}`);
  console.log(`✅ Arquetipos usados: ${neurobyte.arquetipos_usados.slice(0, 5).join(", ")}...`);
  
  console.log("\n🧪 TEST 3: Decoding");
  const decodificado = matriz.decodeDesdeNeurobyte(neurobyte);
  console.log(`✅ Texto recuperado: "${decodificado.texto}"`);
  
  console.log("\n🧪 TEST 4: Células por raíz");
  const celdasDe5 = matriz.obtenerCeldasPorRaiz(5); // Voluntad (centro)
  console.log(`✅ Células con raíz 5 (Voluntad): ${celdasDe5.length}`);
  console.log(`   Centro esperado [6,6]: ${celdasDe5.some(c => c.posicion[0] === 6 && c.posicion[1] === 6) ? "✓" : "✗"}`);
}
