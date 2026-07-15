import json
from pathlib import Path

class StatePersistence:
    def __init__(self, storage_path=None):
        if storage_path is None:
            base_dir = Path(__file__).parent
            storage_path = base_dir / "data" / "charset_states.json"
        
        self.storage_path = Path(storage_path).resolve()
        self.states = {}
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_states()
        
        print(f"💾 Persistence initialized:")
        print(f"   📂 Path: {self.storage_path}")
        print(f"   📁 Dir exists: {self.storage_path.parent.exists()}")
        print(f"   📄 File exists: {self.storage_path.exists()}")
        
    def _load_states(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.states = json.load(f)
                print(f"✅ Loaded {len(self.states)} states from disk")
            except json.JSONDecodeError:
                print("⚠️  File corrupted, starting fresh")
                self.states = {}
        else:
            print(" Creating new storage file")
            self.states = {}
            
       
    def _persist(self):
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.states, f, indent=2, ensure_ascii=False)
            
            if self.storage_path.exists():
                size = self.storage_path.stat().st_size
                print(f"   ✅ File written ({size} bytes)")
        except Exception as e:
            print(f"   ❌ Error saving: {e}")
    def save_state(self, char_code, matrix_13x13, font_size=None, metadata=None):
        """Guarda el estado de un carácter con metadatos completos"""
        key = str(char_code)
        
        self.states[key] = {
            "char": chr(char_code),
            "code": char_code,
            "matrix": matrix_13x13,
            "font_size": font_size or 13,  # ← NUEVO: font_size usado en el muestreo
            "timestamp": datetime.now().isoformat(),  # ← NUEVO: timestamp legible
            "metadata": metadata or {}
        }
        
        self._persist()
        print(f"💾 Saved '{chr(char_code)}' (Code {char_code}) @ {font_size or 13}px")

    def get_all_states(self):
        return self.states
