import tkinter as tk
from pathlib import Path

class VisorArchivos:
    def __init__(self, path, text_widget):
        self.path = Path(path)
        self.text = text_widget

    def _mostrar_archivo(self, p):
        rel = p.relative_to(self.path)
        self.text.insert(tk.END, f"\n{'!'*50}\n{rel}\n{'!'*50}\n\n")
        self.text.insert(tk.END, leer_archivo(p))
        self.text.insert(tk.END, "\n")

    def mostrar_palabras_clave(self):
        """Nuevo método: muestra solo nombre de archivo y sus palabras clave"""
        for p in self.path.glob("*.txt"):
            contenido = leer_archivo(p)
            rel = p.relative_to(self.path)

            # Buscar la sección de palabras clave
            inicio = contenido.find("--- Palabras clave ---")
            if inicio != -1:
                # Tomar desde esa línea hasta el salto de línea siguiente
                linea_claves = contenido[inicio:].splitlines()[1].strip()
                self.text.insert(tk.END, f"\n{'='*80}\n📄 {rel}\n{'='*80}\n")
                self.text.insert(tk.END, f"Palabras clave: {linea_claves}\n")

def leer_archivo(ruta):
    try:
        return Path(ruta).read_text(encoding='utf-8')
    except Exception as e:
        return f"[ERROR] {e}"