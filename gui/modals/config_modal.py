import tkinter as tk
import json

class ConfigModal:
    def __init__(self, master, app):
        self.master = master
        self.app = app
        self.modal = None
    
    def abrir(self):
        """Abre el modal de configuración"""
        self.modal = tk.Toplevel(self.master)
        self.modal.title("Configuración de Esquema")
        self.modal.grab_set()
        self.modal.geometry("500x400")

        # INCLUIR
        tk.Label(self.modal, text="Directorios a INCLUIR (uno por línea):").pack()
        self.incluir_text = tk.Text(self.modal, height=6, width=50)
        self.incluir_text.insert(tk.END, "# ejemplo\nsrc\napp\nassets\nhooks\nconstants\ncomponents")
        self.incluir_text.pack()

        # EXCLUIR
        tk.Label(self.modal, text="Directorios a EXCLUIR (uno por línea):").pack()
        self.excluir_text = tk.Text(self.modal, height=6, width=50)
        self.excluir_text.insert(tk.END, "# ejemplo\nnode_modules\n.git")
        self.excluir_text.pack()

        # Botón Aceptar
        tk.Button(self.modal, text="Aceptar", command=self.aceptar).pack(pady=10)
    
    def aceptar(self):
        """Procesa la configuración y cierra el modal"""
        incluir = [
            line.strip() for line in self.incluir_text.get("1.0", tk.END).splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        excluir = [
            line.strip() for line in self.excluir_text.get("1.0", tk.END).splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        
        self.app.config_esquema = {
            "incluir": incluir,
            "excluir": excluir
        }
        
        # Guardar en JSON
        with open("config_directorios.json", "w", encoding="utf-8") as f:
            json.dump(self.app.config_esquema, f, indent=2)

        self.modal.destroy()
        self.app.ver_esquema()  # Actualizar esquema automáticamente