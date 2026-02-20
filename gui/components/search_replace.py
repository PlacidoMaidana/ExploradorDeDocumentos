import tkinter as tk
from tkinter import ttk, messagebox
import re

class VentanaBusquedaReemplazo:
    def __init__(self, parent, text_widget):
        self.parent = parent
        self.text_widget = text_widget
        self.ventana = None
        self.current_index = 0
        self.matches = []
        
    def abrir_ventana(self):
        if self.ventana and self.ventana.winfo_exists():
            self.ventana.lift()
            return
            
        self.ventana = tk.Toplevel(self.parent)
        self.ventana.title("🔍 Buscar y Reemplazar")
        self.ventana.geometry("500x400")
        self.ventana.resizable(True, True)
        self.ventana.configure(bg='#f0f0f0')
        self.ventana.transient(self.parent)
        
        # Centrar ventana
        self.ventana.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        self.crear_interfaz()
        self.configurar_atajos()
        
    def crear_interfaz(self):
        # Frame principal
        main_frame = ttk.Frame(self.ventana, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Búsqueda
        ttk.Label(main_frame, text="Buscar:").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_buscar = ttk.Entry(main_frame, width=40)
        self.entry_buscar.grid(row=0, column=1, columnspan=2, sticky='ew', padx=(5, 0), pady=5)
        self.entry_buscar.focus()
        
        # Reemplazo
        ttk.Label(main_frame, text="Reemplazar con:").grid(row=1, column=0, sticky='w', pady=5)
        self.entry_reemplazar = ttk.Entry(main_frame, width=40)
        self.entry_reemplazar.grid(row=1, column=1, columnspan=2, sticky='ew', padx=(5, 0), pady=5)
        
        # Opciones
        frame_opciones = ttk.LabelFrame(main_frame, text="Opciones", padding="5")
        frame_opciones.grid(row=2, column=0, columnspan=3, sticky='ew', pady=10)
        
        self.case_sensitive = tk.BooleanVar()
        self.whole_word = tk.BooleanVar()
        self.regex_mode = tk.BooleanVar()
        
        ttk.Checkbutton(frame_opciones, text="Coincidir mayúsculas/minúsculas", 
                       variable=self.case_sensitive).pack(anchor='w')
        ttk.Checkbutton(frame_opciones, text="Palabra completa", 
                       variable=self.whole_word).pack(anchor='w')
        ttk.Checkbutton(frame_opciones, text="Expresión regular", 
                       variable=self.regex_mode).pack(anchor='w')
        
        # Botones
        frame_botones = ttk.Frame(main_frame)
        frame_botones.grid(row=3, column=0, columnspan=3, pady=10)
        
        ttk.Button(frame_botones, text="🔍 Buscar Siguiente", 
                  command=self.buscar_siguiente).pack(side='left', padx=2)
        ttk.Button(frame_botones, text="🔄 Buscar Anterior", 
                  command=self.buscar_anterior).pack(side='left', padx=2)
        ttk.Button(frame_botones, text="✏️ Reemplazar", 
                  command=self.reemplazar_uno).pack(side='left', padx=2)
        ttk.Button(frame_botones, text="🔄 Reemplazar Todos", 
                  command=self.reemplazar_todos).pack(side='left', padx=2)
        ttk.Button(frame_botones, text="❌ Cerrar", 
                  command=self.cerrar_ventana).pack(side='right', padx=2)
        
        # Información
        self.lbl_info = ttk.Label(main_frame, text="Ingresa texto para buscar")
        self.lbl_info.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Configurar pesos de columnas
        main_frame.columnconfigure(1, weight=1)
        
        # Bind eventos
        self.entry_buscar.bind('<KeyRelease>', self.actualizar_busqueda)
        
    def configurar_atajos(self):
        self.ventana.bind('<Control-f>', lambda e: self.entry_buscar.focus())
        self.ventana.bind('<Control-r>', lambda e: self.entry_reemplazar.focus())
        self.ventana.bind('<F3>', lambda e: self.buscar_siguiente())
        self.ventana.bind('<Shift-F3>', lambda e: self.buscar_anterior())
        self.ventana.bind('<Escape>', lambda e: self.cerrar_ventana())
        
    def actualizar_busqueda(self, event=None):
        texto_buscar = self.entry_buscar.get().strip()
        if not texto_buscar:
            self.lbl_info.config(text="Ingresa texto para buscar")
            self.matches = []
            return
            
        try:
            self.encontrar_coincidencias()
            total = len(self.matches)
            
            if total > 0:
                self.lbl_info.config(text=f"Encontradas: {total} coincidencias")
                self.current_index = 0
                self.resaltar_coincidencia(0)
            else:
                self.lbl_info.config(text="No se encontraron coincidencias")
                
        except re.error as e:
            self.lbl_info.config(text=f"Error en expresión regular: {str(e)}")
            
    def encontrar_coincidencias(self):
        texto_buscar = self.entry_buscar.get()
        contenido = self.text_widget.get("1.0", "end-1c")
        self.matches = []
        
        if self.regex_mode.get():
            # Modo expresión regular
            flags = 0 if self.case_sensitive.get() else re.IGNORECASE
            try:
                pattern = re.compile(texto_buscar, flags)
                for match in pattern.finditer(contenido):
                    self.matches.append((f"1.0+{match.start()}c", f"1.0+{match.end()}c"))
            except re.error:
                raise
        else:
            # Modo texto normal
            if self.whole_word.get():
                pattern = r'\b' + re.escape(texto_buscar) + r'\b'
            else:
                pattern = re.escape(texto_buscar)
                
            flags = 0 if self.case_sensitive.get() else re.IGNORECASE
            for match in re.finditer(pattern, contenido, flags):
                self.matches.append((f"1.0+{match.start()}c", f"1.0+{match.end()}c"))
    
    def resaltar_coincidencia(self, index):
        if not self.matches:
            return
            
        # Limpiar resaltados anteriores
        self.text_widget.tag_remove("resaltado", "1.0", "end")
        self.text_widget.tag_remove("seleccionado", "1.0", "end")
        
        # Resaltar todas las coincidencias
        for start, end in self.matches:
            self.text_widget.tag_add("resaltado", start, end)
        
        # Resaltar la coincidencia actual
        start, end = self.matches[index]
        self.text_widget.tag_add("seleccionado", start, end)
        
        # Configurar estilos
        self.text_widget.tag_config("resaltado", background='#fff3cd')
        self.text_widget.tag_config("seleccionado", background='#3498db', foreground='white')
        
        # Mover el cursor a la coincidencia actual
        self.text_widget.mark_set("insert", start)
        self.text_widget.see(start)
        
        # Actualizar información
        self.lbl_info.config(text=f"Coincidencia {index + 1} de {len(self.matches)}")
    
    def buscar_siguiente(self):
        if not self.matches:
            self.actualizar_busqueda()
            return
            
        self.current_index = (self.current_index + 1) % len(self.matches)
        self.resaltar_coincidencia(self.current_index)
    
    def buscar_anterior(self):
        if not self.matches:
            self.actualizar_busqueda()
            return
            
        self.current_index = (self.current_index - 1) % len(self.matches)
        self.resaltar_coincidencia(self.current_index)
    
    def reemplazar_uno(self):
        if not self.matches or self.current_index >= len(self.matches):
            messagebox.showinfo("Información", "No hay coincidencias para reemplazar")
            return
            
        texto_reemplazar = self.entry_reemplazar.get()
        start, end = self.matches[self.current_index]
        
        # Reemplazar el texto
        self.text_widget.delete(start, end)
        self.text_widget.insert(start, texto_reemplazar)
        
        # Actualizar la lista de coincidencias
        self.actualizar_busqueda()
        
    def reemplazar_todos(self):
        if not self.matches:
            messagebox.showinfo("Información", "No hay coincidencias para reemplazar")
            return
            
        texto_reemplazar = self.entry_reemplazar.get()
        total_reemplazos = 0
        
        # Reemplazar desde el final hacia el principio para mantener las posiciones
        for start, end in reversed(self.matches):
            self.text_widget.delete(start, end)
            self.text_widget.insert(start, texto_reemplazar)
            total_reemplazos += 1
        
        messagebox.showinfo("Éxito", f"Se reemplazaron {total_reemplazos} coincidencias")
        self.actualizar_busqueda()
    
    def cerrar_ventana(self):
        # Limpiar resaltados
        if self.text_widget:
            self.text_widget.tag_remove("resaltado", "1.0", "end")
            self.text_widget.tag_remove("seleccionado", "1.0", "end")
        
        if self.ventana:
            self.ventana.destroy()

# Función para abrir la ventana desde otros módulos
def crear_ventana_busqueda_reemplazo(parent, text_widget):
    ventana = VentanaBusquedaReemplazo(parent, text_widget)
    ventana.abrir_ventana()
    return ventana