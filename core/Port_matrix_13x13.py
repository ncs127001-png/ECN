
# =========================================================
# BLOQUE MIGRADO AUTOMÁTICAMENTE DESDE: CLASIFICACION_PREDICTIVA/05_MFN_MATRIX_13x13/matrix_13x13.py
# =========================================================

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class Matrix13x13:
    """
    Implementación Backend de la Matriz 13x13 (Port de arquetipos.js).
    
    Principios:
    - Tamaño: 13x13
    - Centro: [6,6]
    - Simetría Hermética: "Como es Arriba, es Abajo"
    - Arquetipos: 1-9 (Reducción Teosófica)
    """
    
    def __init__(self, size: int = 13):
        self.size = size
        self.center = size // 2  # 6
        self.matrix = self._generate_base_matrix()
        self.archetypes_map = self._map_archetypes()
        
    def _teosophical_reduction(self, n: int) -> int:
        """Reducción recursiva a 1 digit (1-9)."""
        if n < 1: return 9
        while n >= 10:
            n = sum(int(d) for d in str(n))
        return n
        
    def _generate_base_matrix(self) -> List[List[int]]:
        """Genera la matriz base con simetría y reglas."""
        matrix = [[0] * self.size for _ in range(self.size)]
        
        for i in range(self.size):
            for j in range(self.size):
                # Distancia Manhattan desde el centro
                dist = abs(i - self.center) + abs(j - self.center)
                
                # Raíz base
                val = (dist % 9) + 1
                
                # Muros (Bordes) -> 9
                if i == 0 or i == self.size - 1 or j == 0 or j == self.size - 1:
                    val = 9
                
                # Pernos (Esquinas) -> 6
                if (i == 0 or i == self.size - 1) and (j == 0 or j == self.size - 1):
                    val = 6
                
                matrix[i][j] = val
                
        self._apply_hermetic_symmetry(matrix)
        return matrix

    def _apply_hermetic_symmetry(self, matrix: List[List[int]]):
        """Aplica simetría vertical en columnas centrales (3-11)."""
        start = 3
        end = self.size - 3
        
        for i in range(self.size // 2):
            symmetric_i = self.size - 1 - i
            for j in range(start, end):
                # Reflejar valor reducido
                root = self._teosophical_reduction(matrix[i][j])
                matrix[symmetric_i][j] = root

    def _map_archetypes(self) -> Dict[str, Dict[str, Any]]:
        """Mapea IDs de celda a sus propiedades."""
        mapping = {}
        archetype_defs = {
            1: {"nombre": "Unidad", "vibracion": "Inicio"},
            2: {"nombre": "Dualidad", "vibracion": "Equilibrio"},
            3: {"nombre": "Trinidad", "vibracion": "Expresión"},
            4: {"nombre": "Orden", "vibracion": "Estabilidad"},
            5: {"nombre": "Voluntad", "vibracion": "Poder"},
            6: {"nombre": "Armonía", "vibracion": "Unión"},
            7: {"nombre": "Sabiduría", "vibracion": "Intuición"},
            8: {"nombre": "Infinito", "vibracion": "Ciclo"},
            9: {"nombre": "Completitud", "vibracion": "Cierre"}
        }
        
        for i in range(self.size):
            for j in range(self.size):
                root = self.matrix[i][j]
                cell_id = f"{i}-{j}"
                mapping[cell_id] = {
                    "posicion": [i, j],
                    "raiz": root,
                    **archetype_defs.get(root, {})
                }
        return mapping

    def encode_text(self, text: str) -> Dict[str, Any]:
        """Convierte texto a Neurobyte."""
        max_chars = self.size * self.size
        truncated = text[:max_chars]
        
        # ASCII values
        ascii_vals = [ord(c) for c in truncated]
        
        archetypes_used = []
        trajectory = []
        
        # Find cells for each char
        cells_by_root = {}
        for cid, data in self.archetypes_map.items():
            r = data['raiz']
            if r not in cells_by_root:
                cells_by_root[r] = []
            cells_by_root[r].append(cid)
            
        for i, val in enumerate(ascii_vals):
            root = self._teosophical_reduction(val)
            candidates = cells_by_root.get(root, [])
            if candidates:
                # Pick cyclical candidate
                chosen_id = candidates[i % len(candidates)]
                trajectory.append(chosen_id)
                archetypes_used.append(self.archetypes_map[chosen_id]['nombre'])
                
        # Hash
        msg_hash = hashlib.sha1(truncated.encode()).hexdigest()
        
        return {
            "contenido": truncated,
            "contenido_original_length": len(text),
            "hash": msg_hash,
            "arquetipos_usados": archetypes_used,
            "trayectoria": trajectory,
            "simetria_validada": self.validate_symmetry(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "protocol_version": "NEUROBIT_v2.1"
        }

    def validate_symmetry(self) -> bool:
        """Verifica la simetría hermética."""
        start = 3
        end = self.size - 3
        for i in range(self.size // 2):
            sym_i = self.size - 1 - i
            for j in range(start, end):
                if self.matrix[i][j] != self.matrix[sym_i][j]:
                    return False
        return True

    def get_cell(self, r: int, c: int) -> Optional[Dict[str, Any]]:
        cell_id = f"{r}-{c}"
        return self.archetypes_map.get(cell_id)

# Singleton instance for easy import
default_matrix = Matrix13x13()

# =========================================================
# BLOQUE MIGRADO AUTOMÁTICAMENTE DESDE: CLASIFICACION_PREDICTIVA/05_MFN_MATRIX_13x13/matrix_13x13.py
# =========================================================

import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class Matrix13x13:
    """
    Implementación Backend de la Matriz 13x13 (Port de arquetipos.js).
    
    Principios:
    - Tamaño: 13x13
    - Centro: [6,6]
    - Simetría Hermética: "Como es Arriba, es Abajo"
    - Arquetipos: 1-9 (Reducción Teosófica)
    """
    
    def __init__(self, size: int = 13):
        self.size = size
        self.center = size // 2  # 6
        self.matrix = self._generate_base_matrix()
        self.archetypes_map = self._map_archetypes()
        
    def _teosophical_reduction(self, n: int) -> int:
        """Reducción recursiva a 1 digit (1-9)."""
        if n < 1: return 9
        while n >= 10:
            n = sum(int(d) for d in str(n))
        return n
        
    def _generate_base_matrix(self) -> List[List[int]]:
        """Genera la matriz base con simetría y reglas."""
        matrix = [[0] * self.size for _ in range(self.size)]
        
        for i in range(self.size):
            for j in range(self.size):
                # Distancia Manhattan desde el centro
                dist = abs(i - self.center) + abs(j - self.center)
                
                # Raíz base
                val = (dist % 9) + 1
                
                # Muros (Bordes) -> 9
                if i == 0 or i == self.size - 1 or j == 0 or j == self.size - 1:
                    val = 9
                
                # Pernos (Esquinas) -> 6
                if (i == 0 or i == self.size - 1) and (j == 0 or j == self.size - 1):
                    val = 6
                
                matrix[i][j] = val
                
        self._apply_hermetic_symmetry(matrix)
        return matrix

    def _apply_hermetic_symmetry(self, matrix: List[List[int]]):
        """Aplica simetría vertical en columnas centrales (3-11)."""
        start = 3
        end = self.size - 3
        
        for i in range(self.size // 2):
            symmetric_i = self.size - 1 - i
            for j in range(start, end):
                # Reflejar valor reducido
                root = self._teosophical_reduction(matrix[i][j])
                matrix[symmetric_i][j] = root

    def _map_archetypes(self) -> Dict[str, Dict[str, Any]]:
        """Mapea IDs de celda a sus propiedades."""
        mapping = {}
        archetype_defs = {
            1: {"nombre": "Unidad", "vibracion": "Inicio"},
            2: {"nombre": "Dualidad", "vibracion": "Equilibrio"},
            3: {"nombre": "Trinidad", "vibracion": "Expresión"},
            4: {"nombre": "Orden", "vibracion": "Estabilidad"},
            5: {"nombre": "Voluntad", "vibracion": "Poder"},
            6: {"nombre": "Armonía", "vibracion": "Unión"},
            7: {"nombre": "Sabiduría", "vibracion": "Intuición"},
            8: {"nombre": "Infinito", "vibracion": "Ciclo"},
            9: {"nombre": "Completitud", "vibracion": "Cierre"}
        }
        
        for i in range(self.size):
            for j in range(self.size):
                root = self.matrix[i][j]
                cell_id = f"{i}-{j}"
                mapping[cell_id] = {
                    "posicion": [i, j],
                    "raiz": root,
                    **archetype_defs.get(root, {})
                }
        return mapping

    def encode_text(self, text: str) -> Dict[str, Any]:
        """Convierte texto a Neurobyte."""
        max_chars = self.size * self.size
        truncated = text[:max_chars]
        
        # ASCII values
        ascii_vals = [ord(c) for c in truncated]
        
        archetypes_used = []
        trajectory = []
        
        # Find cells for each char
        cells_by_root = {}
        for cid, data in self.archetypes_map.items():
            r = data['raiz']
            if r not in cells_by_root:
                cells_by_root[r] = []
            cells_by_root[r].append(cid)
            
        for i, val in enumerate(ascii_vals):
            root = self._teosophical_reduction(val)
            candidates = cells_by_root.get(root, [])
            if candidates:
                # Pick cyclical candidate
                chosen_id = candidates[i % len(candidates)]
                trajectory.append(chosen_id)
                archetypes_used.append(self.archetypes_map[chosen_id]['nombre'])
                
        # Hash
        msg_hash = hashlib.sha1(truncated.encode()).hexdigest()
        
        return {
            "contenido": truncated,
            "contenido_original_length": len(text),
            "hash": msg_hash,
            "arquetipos_usados": archetypes_used,
            "trayectoria": trajectory,
            "simetria_validada": self.validate_symmetry(),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "protocol_version": "NEUROBIT_v2.1"
        }

    def validate_symmetry(self) -> bool:
        """Verifica la simetría hermética."""
        start = 3
        end = self.size - 3
        for i in range(self.size // 2):
            sym_i = self.size - 1 - i
            for j in range(start, end):
                if self.matrix[i][j] != self.matrix[sym_i][j]:
                    return False
        return True

    def get_cell(self, r: int, c: int) -> Optional[Dict[str, Any]]:
        cell_id = f"{r}-{c}"
        return self.archetypes_map.get(cell_id)

# Singleton instance for easy import
default_matrix = Matrix13x13()
