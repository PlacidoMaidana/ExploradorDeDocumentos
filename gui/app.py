import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

from core.scheme_generator import generar_esquema_estructurado, expandir_todo, contraer_todo, expandir_carpeta, contraer_carpeta
from core.content_processor import mostrar_contenido_archivos, mostrar_contenido_raiz
from core.markdown_converter import exportar_a_markdown, exportar_a_txt
from gui.components.menu import crear_menu_contextual
from gui.components.search_replace import crear_ventana_busqueda_reemplazo
from core.palabrasClave import VisorArchivos





class FileExplorerApp(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.root = master  # <- compatibilidad para componentes que usan parent.root
        self.directorio = None
        self.estructura_arbol = []
        self.carpeta_seleccionada = None
        self.archivos_seleccionados = set()  # Usamos set para evitar duplicados
        self.lineas_seleccionadas = {}  # Diccionario para mapear línea -> archivo
        self.tipo_operacion_actual = "esquema"
        
        # pyinstaller --onefile --windowed --icon=File-explorer.ico --name="Explorador" main.py
        # Intentar cargar el icono si existe
        try:
            self.iconbitmap("File-explorer.ico")
        except:
            pass  # Continuar sin icono si no existe
        
        self.configurar_interfaz()
        self.crear_menu_principal()
        
    def crear_menu_principal(self):
        """Crea el menú principal de la aplicación"""
        menubar = tk.Menu(self.master, tearoff=0)
        
        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menu_archivo.add_command(label="📁 Seleccionar Directorio", 
                                command=self.seleccionar_directorio,
                                accelerator="Ctrl+O")
        menu_archivo.add_separator()
        menu_archivo.add_command(label="💾 Exportar a Markdown", 
                                command=self.exportar_markdown)
        menu_archivo.add_command(label="💾 Exportar a TXT", 
                                command=self.exportar_txt)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="🚪 Salir", 
                                command=self.master.quit,
                                accelerator="Ctrl+Q")
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        
        # Menú Editar
        menu_editar = tk.Menu(menubar, tearoff=0)
        menu_editar.add_command(label="🔍 Buscar y Reemplazar", 
                               command=self.abrir_busqueda_reemplazo,
                               accelerator="Ctrl+F")
        menu_editar.add_separator()
        menu_editar.add_command(label="📋 Copiar", 
                               command=self.copiar_seleccion,
                               accelerator="Ctrl+C")
        menu_editar.add_command(label="📄 Seleccionar Todo", 
                               command=self.seleccionar_todo,
                               accelerator="Ctrl+A")
        menu_editar.add_command(label="🧹 Limpiar Selección", 
                               command=self.limpiar_seleccion)
        menubar.add_cascade(label="Editar", menu=menu_editar)
        
        # Menú Ver
        menu_ver = tk.Menu(menubar, tearoff=0)
        menu_ver.add_command(label="📂 Esquema del Directorio", 
                            command=self.mostrar_esquema)
        menu_ver.add_command(label="📄 Contenido Raíz", 
                            command=self.mostrar_contenido_raiz)
        menu_ver.add_command(label="📚 Contenido Completo", 
                            command=self.mostrar_contenido_completo)
        menu_ver.add_command(label="👁️ Ver Archivos Seleccionados", 
                            command=self.ver_contenido_seleccionado)
        menu_ver.add_command(label="??? Ver palabras clave",
                     command=lambda: self.visor.mostrar_palabras_clave() if hasattr(self, "visor") else None)
        
        menu_ver.add_separator()
        menu_ver.add_command(label="🔼 Expandir Todo", 
                            command=self.expandir_todo)
        menu_ver.add_command(label="🔽 Contraer Todo", 
                            command=self.contraer_todo)
        menubar.add_cascade(label="Ver", menu=menu_ver)
        
        self.master.config(menu=menubar)
        self.configurar_atajos_globales()
        
    def configurar_atajos_globales(self):
        """Configura atajos de teclado globales"""
        self.master.bind('<Control-o>', lambda e: self.seleccionar_directorio())
        self.master.bind('<Control-f>', lambda e: self.abrir_busqueda_reemplazo())
        self.master.bind('<Control-q>', lambda e: self.master.quit())
        self.master.bind('<Control-a>', lambda e: self.seleccionar_todo())
        self.master.bind('<Control-c>', lambda e: self.copiar_seleccion())
        
    def seleccionar_directorio(self):
        """Abre diálogo para seleccionar directorio"""
        directorio = filedialog.askdirectory(title="Seleccione el directorio a explorar")
        if not directorio:
            return

        try:
            self.visor = VisorArchivos(directorio, self.text_area)
            self.directorio = directorio
            self.cargar_directorio(directorio)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
    def configurar_interfaz(self):
        """Configura los elementos de la interfaz gráfica"""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra de herramientas superior
        toolbar_superior = ttk.Frame(main_frame)
        toolbar_superior.pack(fill=tk.X, pady=(0, 10))
        
        # Botón para seleccionar directorio
        ttk.Button(toolbar_superior, text="📁 Seleccionar Directorio", 
                  command=self.seleccionar_directorio).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separador
        ttk.Separator(toolbar_superior, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Botón de búsqueda
        ttk.Button(toolbar_superior, text="🔍 Buscar", 
                  command=self.abrir_busqueda_reemplazo).pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón limpiar selección
        ttk.Button(toolbar_superior, text="🧹 Limpiar Selección", 
                  command=self.limpiar_seleccion).pack(side=tk.LEFT, padx=(0, 5))
        
        # Barra de herramientas principal
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # Botones para operaciones específicas
        ttk.Button(toolbar, text="🔼 Expandir Carpeta", command=self.expandir_carpeta_actual).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="🔽 Contraer Carpeta", command=self.contraer_carpeta_actual).pack(side=tk.LEFT, padx=(0, 5))
        
        # Botones para operaciones globales
        ttk.Button(toolbar, text="🔼 Expandir Todo", command=self.expandir_todo).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="🔽 Contraer Todo", command=self.contraer_todo).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separador
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        # Botones para contenido
        ttk.Button(toolbar, text="📄 Contenido Raíz", command=self.mostrar_contenido_raiz).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="📚 Contenido Completo", command=self.mostrar_contenido_completo).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="👁️ Ver Seleccionados", command=self.ver_contenido_seleccionado).pack(side=tk.LEFT, padx=(5, 0))
        btn_claves = ttk.Button(toolbar, text="🔑 Mostrar Palabras Clave",
                        command=lambda: self.visor.mostrar_palabras_clave() if hasattr(self, "visor") else None)
        btn_claves.pack(side=tk.LEFT, padx=(5, 0))
        
        
        
        # Área de texto para mostrar resultados
        frame_texto = ttk.Frame(main_frame)
        frame_texto.pack(fill=tk.BOTH, expand=True)
        
        self.text_area = tk.Text(frame_texto, wrap=tk.WORD, width=80, height=30, undo=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(frame_texto, orient=tk.VERTICAL, command=self.text_area.yview)
        h_scrollbar = ttk.Scrollbar(frame_texto, orient=tk.HORIZONTAL, command=self.text_area.xview)
        self.text_area.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout para el área de texto y scrollbars
        self.text_area.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        frame_texto.grid_rowconfigure(0, weight=1)
        frame_texto.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.text_area.bind("<Double-Button-1>", self.alternar_plegado)
        self.text_area.bind("<Button-1>", self.seleccionar_elemento)
        self.text_area.bind("<Button-3>", self.mostrar_menu_contextual)
        self.text_area.bind("<Control-Button-1>", self.seleccionar_elemento_ctrl)  # Ctrl+clic
        self.text_area.bind("<Control-a>", lambda e: self.seleccionar_todo())
        self.text_area.bind("<Control-c>", lambda e: self.copiar_seleccion())
        
        # Configurar tags para selección
        self.text_area.tag_configure("seleccionado", background="#e6f3ff", foreground="#000000")
        
        # Crear menú contextual
        self.menu_contextual = crear_menu_contextual(self, self.text_area)
        
    def seleccionar_elemento(self, event):
        """Maneja la selección de elementos con clic normal"""
        # Limpiar selección anterior si no se presiona Control
        if not (event.state & 0x4):  # 0x4 es el estado de Control
            self.archivos_seleccionados.clear()
            self.text_area.tag_remove("seleccionado", "1.0", tk.END)
        
        self._procesar_seleccion_elemento(event)
    
    def seleccionar_elemento_ctrl(self, event):
        """Maneja la selección de elementos con Ctrl+clic (selección múltiple)"""
        self._procesar_seleccion_elemento(event)
    
    def _procesar_seleccion_elemento(self, event):
        """Procesa la selección de un elemento individual"""
        index = self.text_area.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0])
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        line_text = self.text_area.get(line_start, line_end)

        if "📁 " in line_text:
            self.carpeta_seleccionada = line_text.split("📁 ", 1)[1].strip()
            # No seleccionamos carpetas, solo archivos
        elif "📄 " in line_text:
            nombre_archivo = line_text.split("📄 ", 1)[1].strip()
            
            # Obtener la ruta completa del archivo
            ruta_completa = self._obtener_ruta_completa_archivo(nombre_archivo)
            
            if ruta_completa:
                if ruta_completa in self.archivos_seleccionados:
                    # Deseleccionar
                    self.archivos_seleccionados.remove(ruta_completa)
                    self.text_area.tag_remove("seleccionado", line_start, line_end)
                else:
                    # Seleccionar
                    self.archivos_seleccionados.add(ruta_completa)
                    self.text_area.tag_add("seleccionado", line_start, line_end)
                
                # Actualizar información de selección
                self.actualizar_info_seleccion()
    
    def _obtener_ruta_completa_archivo(self, nombre_archivo):
        """Obtiene la ruta completa de un archivo buscando en el árbol"""
        def buscar_en_estructura(estructura, nombre, ruta_actual=""):
            for item in estructura:
                ruta_item = os.path.join(ruta_actual, item['nombre']) if ruta_actual else item['nombre']
                if item['es_directorio']:
                    resultado = buscar_en_estructura(item['contenido'], nombre, ruta_item)
                    if resultado:
                        return resultado
                else:
                    if item['nombre'] == nombre:
                        return ruta_item
            return None
        
        return buscar_en_estructura(self.estructura_arbol, nombre_archivo)
    
    def actualizar_info_seleccion(self):
        """Actualiza la información de archivos seleccionados en la barra de estado"""
        if hasattr(self, 'lbl_info_seleccion'):
            total = len(self.archivos_seleccionados)
            self.lbl_info_seleccion.config(text=f"Archivos seleccionados: {total}")
        
    def limpiar_seleccion(self):
        """Limpia toda la selección de archivos"""
        self.archivos_seleccionados.clear()
        self.text_area.tag_remove("seleccionado", "1.0", tk.END)
        self.actualizar_info_seleccion()
        messagebox.showinfo("Información", "Selección limpiada")
    
    def abrir_busqueda_reemplazo(self):
        """Abre la ventana de búsqueda y reemplazo"""
        crear_ventana_busqueda_reemplazo(self.master, self.text_area)
        
    def mostrar_esquema(self):
        """Muestra el esquema del directorio actual"""
        if self.estructura_arbol:
            self.renderizar_esquema(self.estructura_arbol)
            self.tipo_operacion_actual = "esquema"
    
    def expandir_carpeta_actual(self):
        """Expande la carpeta actualmente seleccionada"""
        if not self.carpeta_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una carpeta haciendo clic en ella.")
            return
            
        if expandir_carpeta(self.estructura_arbol, self.carpeta_seleccionada):
            self.renderizar_esquema(self.estructura_arbol)
            self.tipo_operacion_actual = "esquema"
        else:
            messagebox.showwarning("Advertencia", f"No se pudo encontrar la carpeta: {self.carpeta_seleccionada}")
        
    def contraer_carpeta_actual(self):
        """Contrae la carpeta actualmente seleccionada"""
        if not self.carpeta_seleccionada:
            messagebox.showwarning("Advertencia", "Seleccione una carpeta haciendo clic en ella.")
            return
            
        if contraer_carpeta(self.estructura_arbol, self.carpeta_seleccionada):
            self.renderizar_esquema(self.estructura_arbol)
            self.tipo_operacion_actual = "esquema"
        else:
            messagebox.showwarning("Advertencia", f"No se pudo encontrar la carpeta: {self.carpeta_seleccionada}")
        
    def expandir_todo(self):
        """Expande todos los directorios en el árbol"""
        if not self.estructura_arbol:
            messagebox.showwarning("Advertencia", "Primero cargue un directorio.")
            return
        
        expandir_todo(self.estructura_arbol)
        self.renderizar_esquema(self.estructura_arbol)
        self.tipo_operacion_actual = "esquema"
        
    def contraer_todo(self):
        """Contrae todos los directorios en el árbol"""
        if not self.estructura_arbol:
            messagebox.showwarning("Advertencia", "Primero cargue un directorio.")
            return
        
        contraer_todo(self.estructura_arbol)
        self.renderizar_esquema(self.estructura_arbol)
        self.tipo_operacion_actual = "esquema"
        
    def mostrar_contenido_raiz(self):
        """Muestra el contenido de los archivos en la raíz"""
        if not self.directorio:
            messagebox.showwarning("Advertencia", "Primero cargue un directorio.")
            return
            
        contenido = mostrar_contenido_raiz(self.directorio)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, contenido)
        self.tipo_operacion_actual = "contenido_raiz"
        
    def mostrar_contenido_completo(self):
        """Muestra el contenido de todos los archivos válidos"""
        if not self.directorio:
            messagebox.showwarning("Advertencia", "Primero cargue un directorio.")
            return
            
        def actualizar_progreso(actual, total):
            self.master.title(f"Procesando... {actual}/{total}")
            
        contenido = mostrar_contenido_archivos(self.directorio, progress_callback=actualizar_progreso)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, contenido)
        self.master.title("Explorador de Directorios")
        self.tipo_operacion_actual = "contenido_completo"
    
    def alternar_plegado(self, event):
        """Alterna el estado de expansión de directorios con doble clic"""
        index = self.text_area.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0])
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        line_text = self.text_area.get(line_start, line_end)

        if "📁 " in line_text:
            nombre = line_text.split("📁 ", 1)[1].strip()
            es_directorio = True
        elif "📄 " in line_text:
            nombre = line_text.split("📄 ", 1)[1].strip()
            es_directorio = False
        else:
            return

        if not es_directorio:
            return

        self._alternar_en_estructura(self.estructura_arbol, nombre)
        self.renderizar_esquema(self.estructura_arbol)
        self.carpeta_seleccionada = nombre
        
    def _alternar_en_estructura(self, estructura, nombre):
        """Alterna el estado de expansión en la estructura interna"""
        for item in estructura:
            if item['nombre'] == nombre and item['es_directorio']:
                item['expandido'] = not item['expandido']
                return
            if item['es_directorio'] and item['expandido']:
                self._alternar_en_estructura(item['contenido'], nombre)
                
    def renderizar_esquema(self, estructura, nivel=0):
        """Renderiza el esquema completo en el área de texto"""
        self.text_area.delete(1.0, tk.END)
        self._renderizar_nivel(estructura, nivel)
        
    def _renderizar_nivel(self, estructura, nivel):
        """Renderiza recursivamente cada nivel del árbol"""
        for item in estructura:
            prefijo = "  " * nivel
            if item['es_directorio']:
                icono = "📁 "
                if item['expandido']:
                    prefijo += "▼ "
                else:
                    prefijo += "► "
            else:
                icono = "📄 "
                prefijo += "  "
                
            self.text_area.insert(tk.END, prefijo + icono + item['nombre'] + "\n")
            if item['es_directorio'] and item['expandido']:
                self._renderizar_nivel(item['contenido'], nivel + 1)
                
    def ver_contenido_seleccionado(self):
        """Muestra el contenido de archivos seleccionados"""
        if not self.archivos_seleccionados:
            messagebox.showwarning("Advertencia", "No hay archivos seleccionados. Use Ctrl+clic para seleccionar múltiples archivos.")
            return
    
        salida = ''
        archivos_procesados = 0
        archivos_con_error = 0
    
        for ruta_archivo in self.archivos_seleccionados:
            full_path = os.path.join(self.directorio, ruta_archivo)
            if os.path.exists(full_path):
                ext = os.path.splitext(ruta_archivo)[1].lower()
                try:
                    # Para archivos especiales (Word, PowerPoint, PDF)
                    if ext in ['.docx', '.pptx', '.pdf']:
                        from core.content_processor import leer_archivo_especial
                        contenido = leer_archivo_especial(full_path, ext)
                    else:
                        # Para archivos de texto
                        try:
                            with open(full_path, 'r', encoding='utf-8') as f:
                                contenido = f.read()
                        except UnicodeDecodeError:
                            try:
                                with open(full_path, 'r', encoding='latin-1') as f:
                                    contenido = f.read()
                            except Exception as e:
                                contenido = f"[ERROR] No se pudo leer '{ruta_archivo}': {str(e)}"
                    
                    salida += f"\n{'='*80}\n📄 {ruta_archivo}\n{'='*80}\n\n{contenido.strip()}\n\n"
                    archivos_procesados += 1
                    
                except Exception as e:
                    salida += f"\n[ERROR] No se pudo procesar '{ruta_archivo}': {str(e)}\n\n"
                    archivos_con_error += 1
            else:
                salida += f"\n[ERROR] Archivo no encontrado: {ruta_archivo}\n\n"
                archivos_con_error += 1
    
        # Agregar resumen al final
        if archivos_procesados > 0 or archivos_con_error > 0:
            salida += f"\n{'='*80}\n"
            salida += f"📊 RESUMEN: {archivos_procesados} archivos procesados, {archivos_con_error} con errores\n"
            salida += f"{'='*80}\n"
    
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, salida)
        self.tipo_operacion_actual = "contenido_seleccionado"
        
    def mostrar_menu_contextual(self, event):
        """Muestra el menú contextual en la posición del clic"""
        try:
            self.menu_contextual.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contextual.grab_release()
            
    def copiar_seleccion(self):
        """Copia el texto seleccionado al portapapeles"""
        try:
            seleccion = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear()
            self.master.clipboard_append(seleccion)
            messagebox.showinfo("Éxito", "Texto copiado al portapapeles")
        except tk.TclError:
            messagebox.showwarning("Advertencia", "No hay texto seleccionado para copiar")
            
    def seleccionar_todo(self):
        """Selecciona todo el texto del área de salida"""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)

    def exportar_markdown(self):
        """Exporta el contenido como archivo Markdown"""
        contenido = self.text_area.get("1.0", "end-1c").strip()
        
        if not contenido:
            messagebox.showwarning("Sin contenido", "No hay contenido para exportar.")
            return

        ruta_archivo = filedialog.asksaveasfilename(
            title="Guardar como Markdown",
            defaultextension=".md",
            filetypes=[("Archivos Markdown", "*.md"), ("Todos los archivos", "*.*")]
        )
        
        if not ruta_archivo:
            return
            
        try:
            with open(ruta_archivo, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)
            messagebox.showinfo("Exportación exitosa", f"Archivo guardado en:\n{ruta_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")

    def exportar_txt(self):
        """Exporta el contenido como archivo de texto"""
        contenido = self.text_area.get("1.0", "end-1c").strip()
        
        if not contenido:
            messagebox.showwarning("Sin contenido", "No hay contenido para exportar.")
            return

        ruta_archivo = filedialog.asksaveasfilename(
            title="Guardar como TXT",
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if not ruta_archivo:
            return
            
        try:
            with open(ruta_archivo, "w", encoding="utf-8") as archivo:
                archivo.write(contenido)
            messagebox.showinfo("Exportación exitosa", f"Archivo guardado en:\n{ruta_archivo}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")

    def cargar_directorio(self, ruta):
        """Carga un directorio y genera el esquema"""
        self.directorio = ruta
        self.estructura_arbol = generar_esquema_estructurado(ruta)
        self.renderizar_esquema(self.estructura_arbol)
        self.tipo_operacion_actual = "esquema"
        self.master.title(f"Explorador de Directorios - {ruta}")
        # Limpiar selección al cargar nuevo directorio
        self.limpiar_seleccion()