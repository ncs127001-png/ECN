import tkinter as tk

class TextNavigator:
    def __init__(self, root, extractor, mapper, editor, persistence):
        self.root = root
        self.root.title("Neurobit Text Navigator")
        self.root.geometry("800x100")
        
        label = tk.Label(root, text="📝 Text Navigator - En desarrollo", 
                        font=("Consolas", 14), fg="#00ffcc", bg="#111111")
        label.pack(pady=30)
        
        btn = tk.Button(root, text="Volver", command=root.destroy,
                       bg="#004444", fg="#00ffcc", font=("Consolas", 12))
        btn.pack(pady=10)
