import tkinter as tk
from tkinter import scrolledtext

class TextArea(scrolledtext.ScrolledText):
    def __init__(self, master, app):
        super().__init__(master, wrap=tk.WORD, width=100, height=35)
        self.app = app
        self.setup_context_menu()
        self.bind_events()
    
    def setup_context_menu(self):
        """Configura el menú contextual"""
        self.menu_contextual = tk.Menu(self, tearoff=0)
        self.menu_contextual.add_command(label="Ver Contenido Seleccionado", command=self.app.ver_contenido_seleccionado, accelerator="Ctrl+V")
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(label="Copiar", command=self.copiar_seleccion, accelerator="Ctrl+C")
        self.menu_contextual.add_command(label="Seleccionar Todo", command=self.seleccionar_todo, accelerator="Ctrl+A")
    
    def bind_events(self):
        """Vincula eventos del teclado y ratón"""
        self.bind("<Button-3>", self.mostrar_menu_contextual)  # Windows/Linux
        self.bind("<Button-2>", self.mostrar_menu_contextual)  # macOS
        self.bind("<Control-v>", lambda event: self.app.ver_contenido_seleccionado())
        self.bind("<Control-c>", lambda event: self.copiar_seleccion())
        self.bind("<Control-a>", lambda event: self.seleccionar_todo())
    
    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual en la posición del clic"""
        try:
            self.menu_contextual.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contextual.grab_release()
    
    def copiar_seleccion(self):
        """Copia el texto seleccionado al portapapeles"""
        try:
            seleccion = self.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(seleccion)
        except tk.TclError:
            pass  # No hay texto seleccionado
    
    def seleccionar_todo(self):
        """Selecciona todo el texto en el área de salida"""
        self.tag_add(tk.SEL, "1.0", tk.END)
        self.mark_set(tk.INSERT, "1.0")
        self.see(tk.INSERT)
        return 'break'
    
    def clear(self):
        """Limpia el área de texto"""
        self.delete(1.0, tk.END)
    
    def insert_text(self, text):
        """Inserta texto en el área de texto"""
        self.insert(tk.END, text)
    
    def get_content(self):
        """Obtiene todo el contenido del área de texto"""
        return self.get(1.0, tk.END)