"""
VENTANA MODAL CON GEMINI PARA REALIZAR CONSULTAS SOBRE UN EDITOR
Versión mejorada con historial de conversación y manejo robusto de errores

NOTA IMPORTANTE: La librería google.generativeai está deprecada.
Se recomienda migrar a google.genai en el futuro.
Para suprimir la advertencia temporalmente, puedes usar:
    import warnings
    warnings.filterwarnings("ignore", category=FutureWarning)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import warnings
import json
import os
import requests

# Suprimir advertencia de deprecación temporalmente
warnings.filterwarnings("ignore", category=FutureWarning)

import google.generativeai as genai
import threading

# Configura tu API Key aquí o pásala como argumento
# genai.configure(api_key="TU_API_KEY_AQUI")
DEEPSEEK_API_KEY = "sk-db61c6c518f340da87c9c059641254ac"


class PromptManager:
    """Gestor de prompts persistente en JSON."""
    def __init__(self, filepath="prompts.json"):
        self.filepath = filepath
        self.prompts = self.load_prompts()

    def load_prompts(self):
        default_prompt = {
            "title": "Organizar Archivos (Default)",
            "content": (
                "Quiero que tomes este listado de archivos y los organices en grupos temáticos coherentes.\n"
                "Las reglas son:\n"
                "- No debes modificar los nombres de los archivos.\n"
                "- Cada grupo debe comenzar con una línea que tenga el prefijo 📁 seguido del nombre descriptivo del grupo.\n"
                "- Cada archivo dentro del grupo debe estar en una línea con el prefijo 📄 seguido del nombre original del archivo.\n"
                "- No uses otros símbolos ni cambies el formato, solo 📁 para grupos y 📄 para archivos.\n"
                "- El resultado debe ser un listado limpio y ordenado, listo para que mi sistema de selección lo interprete."
            )
        }
        
        if not os.path.exists(self.filepath):
            return [default_prompt]
            
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not data: return [default_prompt]
                return data
        except:
            return [default_prompt]

    def save_prompts(self):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.prompts, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando prompts: {e}")

    def add_or_update_prompt(self, title, content, original_title=None):
        if original_title:
            for p in self.prompts:
                if p['title'] == original_title:
                    p['title'] = title
                    p['content'] = content
                    self.save_prompts()
                    return
        
        for p in self.prompts:
            if p['title'] == title:
                p['content'] = content
                self.save_prompts()
                return
        
        self.prompts.append({"title": title, "content": content})
        self.save_prompts()

    def delete_prompt(self, title):
        self.prompts = [p for p in self.prompts if p['title'] != title]
        self.save_prompts()

    def get_prompt(self, title):
        for p in self.prompts:
            if p['title'] == title:
                return p
        return None


class VentanaGestionPrompts:
    """Ventana ABM para gestionar prompts."""
    def __init__(self, parent, prompt_manager, callback_update):
        self.window = tk.Toplevel(parent)
        self.window.title("Gestión de Prompts")
        self.window.geometry("700x500")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.manager = prompt_manager
        self.callback_update = callback_update
        self.current_selection = None
        
        self.crear_interfaz()
        
    def crear_interfaz(self):
        paned = tk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        frame_left = tk.Frame(paned)
        self.listbox = tk.Listbox(frame_left)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        
        btn_frame_left = tk.Frame(frame_left)
        btn_frame_left.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame_left, text="Nuevo", command=self.nuevo_prompt).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(btn_frame_left, text="Eliminar", command=self.eliminar_prompt).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        paned.add(frame_left, width=200)
        
        frame_right = tk.Frame(paned)
        tk.Label(frame_right, text="Título:").pack(anchor="w")
        self.entry_title = tk.Entry(frame_right)
        self.entry_title.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(frame_right, text="Contenido del Prompt:").pack(anchor="w")
        self.text_content = scrolledtext.ScrolledText(frame_right, height=10)
        self.text_content.pack(fill=tk.BOTH, expand=True)
        
        tk.Button(frame_right, text="Guardar Cambios", command=self.guardar_prompt, bg="#28A745", fg="white").pack(fill=tk.X, pady=5)
        
        paned.add(frame_right)
        self.cargar_lista()
        
    def cargar_lista(self):
        self.listbox.delete(0, tk.END)
        for p in self.manager.prompts:
            self.listbox.insert(tk.END, p['title'])
            
    def on_select(self, event):
        if not self.listbox.curselection(): return
        index = self.listbox.curselection()[0]
        title = self.listbox.get(index)
        self.current_selection = title
        
        prompt = self.manager.get_prompt(title)
        if prompt:
            self.entry_title.delete(0, tk.END)
            self.entry_title.insert(0, prompt['title'])
            self.text_content.delete("1.0", tk.END)
            self.text_content.insert("1.0", prompt['content'])
            
    def nuevo_prompt(self):
        self.current_selection = None
        self.listbox.selection_clear(0, tk.END)
        self.entry_title.delete(0, tk.END)
        self.text_content.delete("1.0", tk.END)
        self.entry_title.focus_set()
        
    def guardar_prompt(self):
        title = self.entry_title.get().strip()
        content = self.text_content.get("1.0", tk.END).strip()
        
        if not title:
            messagebox.showwarning("Error", "El título es obligatorio")
            return
            
        self.manager.add_or_update_prompt(title, content, self.current_selection)
        self.cargar_lista()
        self.callback_update()
        messagebox.showinfo("Éxito", "Prompt guardado")
        
    def eliminar_prompt(self):
        if not self.current_selection: return
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{self.current_selection}'?"):
            self.manager.delete_prompt(self.current_selection)
            self.nuevo_prompt()
            self.cargar_lista()
            self.callback_update()


class VentanaGeminiModal:
    """
    Ventana modal para interactuar con Gemini Pro manteniendo el contexto
    del texto seleccionado y permitiendo múltiples consultas.
    """
    
    def __init__(self, parent, text_editor, api_key=None):
        """
        Inicializa la ventana modal de Gemini.
        
        :param parent: Ventana padre (tk.Tk o tk.Toplevel)
        :param text_editor: Widget de texto del editor principal
        :param api_key: API Key de Google Gemini (opcional si ya está configurada)
        """
        self.parent = parent
        self.text_editor = text_editor
        self.historial_conversacion = []
        self.prompt_manager = PromptManager()
        self.chat_session = None
        
        # Configurar API si se proporciona la key
        if api_key:
            genai.configure(api_key=api_key)
        
        # Obtener texto seleccionado
        try:
            self.texto_contexto = text_editor.get(tk.SEL_FIRST, tk.SEL_LAST)
            # Crear marcas para rastrear la selección original (útil para la función "Aplicar")
            self.text_editor.mark_set("gemini_sel_start", tk.SEL_FIRST)
            self.text_editor.mark_set("gemini_sel_end", tk.SEL_LAST)
        except tk.TclError:
            messagebox.showwarning(
                "Atención", 
                "Por favor, selecciona el texto en el editor antes de abrir Gemini."
            )
            return
        
        # Crear la ventana modal
        self.crear_ventana_modal()
        
    def crear_ventana_modal(self):
        """Crea y configura la interfaz de la ventana modal."""
        self.modal = tk.Toplevel(self.parent)
        self.modal.title("Asistente Gemini AI - Consultas Contextuales")
        self.modal.geometry("800x700")
        self.modal.transient(self.parent)
        self.modal.grab_set()
        
        # Configurar cierre de ventana
        self.modal.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        
        # Frame principal con padding
        main_frame = tk.Frame(self.modal, padx=20, pady=15)
        main_frame.pack(fill="both", expand=True)
        
        # --- Sección: Contexto ---
        self.crear_seccion_contexto(main_frame)
        
        # --- Sección: Historial de conversación ---
        self.crear_seccion_historial(main_frame)
        
        # --- Sección: Prompt de entrada ---
        self.crear_seccion_prompt(main_frame)
        
        # --- Sección: Botones de acción ---
        self.crear_seccion_botones(main_frame)
        
        # --- Barra de progreso ---
        self.progreso = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progreso.pack(fill="x", pady=5)
        
        # Configurar atajos de teclado
        self.configurar_atajos()
        
    def crear_seccion_contexto(self, parent):
        """Crea la sección que muestra el contexto seleccionado."""
        frame_contexto = tk.LabelFrame(
            parent, 
            text="📄 Contexto Seleccionado", 
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        frame_contexto.pack(fill="x", pady=(0, 10))
        
        self.text_contexto_display = scrolledtext.ScrolledText(
            frame_contexto,
            height=4,
            wrap="word",
            bg="#f0f0f0",
            font=("Consolas", 9),
            state="disabled"
        )
        self.text_contexto_display.pack(fill="both", expand=True)
        
        # Mostrar contexto
        self.text_contexto_display.config(state="normal")
        self.text_contexto_display.insert("1.0", self.texto_contexto)
        self.text_contexto_display.config(state="disabled")
        
    def crear_seccion_historial(self, parent):
        """Crea la sección del historial de conversación."""
        frame_historial = tk.LabelFrame(
            parent,
            text="💬 Conversación",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        frame_historial.pack(fill="both", expand=True, pady=(0, 10))
        
        self.text_historial = scrolledtext.ScrolledText(
            frame_historial,
            height=15,
            wrap="word",
            bg="#ffffff",
            font=("Arial", 10),
            state="disabled"
        )
        self.text_historial.pack(fill="both", expand=True)
        
        # Configurar tags para diferentes tipos de mensajes
        self.text_historial.tag_config("usuario", foreground="#0066cc", font=("Arial", 10, "bold"))
        self.text_historial.tag_config("gemini", foreground="#009900")
        self.text_historial.tag_config("separador", foreground="#888888")
        
    def crear_seccion_prompt(self, parent):
        """Crea la sección de entrada de prompt con soporte para archivos adjuntos."""
        frame_prompt = tk.LabelFrame(
            parent,
            text="✍️ Configuración de la IA",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        frame_prompt.pack(fill="x", pady=(0, 10))
        
        # --- Selector de Prompts ---
        frame_selector = tk.Frame(frame_prompt)
        frame_selector.pack(fill="x", pady=(0, 5))
        
        tk.Label(frame_selector, text="📋 Plantilla:").pack(side="left")
        
        self.combo_prompts = ttk.Combobox(frame_selector, state="readonly")
        self.combo_prompts.pack(side="left", fill="x", expand=True, padx=5)
        self.combo_prompts.bind("<<ComboboxSelected>>", self.cargar_prompt_seleccionado)
        
        # Selector de Modelo
        tk.Label(frame_selector, text="🧠 Modelo:").pack(side="left", padx=(10, 0))
        self.combo_modelo = ttk.Combobox(frame_selector, state="readonly", width=18)
        self.combo_modelo['values'] = ["Gemini 2.5 Flash", "Gemini 2.5 Pro", "Gemini 2.0 Flash", "DeepSeek Chat (V3)", "DeepSeek Reasoner (R1)"]
        self.combo_modelo.current(0)
        self.combo_modelo.pack(side="left", padx=5)
        
        tk.Button(frame_selector, text="⚙️ Gestionar", command=self.abrir_gestion_prompts, 
                 font=("Arial", 8), bg="#e2e6ea").pack(side="left")
    
        # Contenedor horizontal para separar el texto de los botones de acción
        content_frame = tk.Frame(frame_prompt)
        content_frame.pack(fill="both", expand=True)
    
        # Área de texto con barras de desplazamiento (ScrolledText)
        # Aumentamos la altura para que las reglas del prompt sean legibles
        self.entry_prompt = scrolledtext.ScrolledText(
            content_frame,
            height=8, 
            wrap="word",
            font=("Arial", 11),
            bg="#f8f9fa"
        )
        self.entry_prompt.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
        # Nuevo: Panel lateral para acciones como adjuntar archivos
        frame_acciones = tk.Frame(content_frame)
        frame_acciones.pack(side="right", fill="y")
    
        # Botón para adjuntar archivo
        btn_adjuntar = tk.Button(
            frame_acciones, 
            text="📎 Adjuntar\nArchivo", 
            command=lambda: self.incorporar_archivo_al_prompt(), # Reutiliza tu lógica de carga
            bg="#e9ecef",
            font=("Arial", 9),
            width=10,
            pady=5
        )
        btn_adjuntar.pack(side="top", pady=2)
    
        # Cargar prompts en el combo y seleccionar el primero si existe
        self.actualizar_combo_prompts()
        if self.prompt_manager.prompts:
            self.combo_prompts.current(0)
            self.cargar_prompt_seleccionado()
            
        self.entry_prompt.focus_set()
        
    def actualizar_combo_prompts(self):
        """Actualiza la lista del combobox con los prompts disponibles."""
        titles = [p['title'] for p in self.prompt_manager.prompts]
        self.combo_prompts['values'] = titles
        
    def cargar_prompt_seleccionado(self, event=None):
        """Carga el contenido del prompt seleccionado en el área de texto."""
        title = self.combo_prompts.get()
        prompt = self.prompt_manager.get_prompt(title)
        if prompt:
            self.entry_prompt.delete("1.0", tk.END)
            self.entry_prompt.insert("1.0", prompt['content'])
            
    def abrir_gestion_prompts(self):
        """Abre la ventana de gestión de prompts."""
        VentanaGestionPrompts(self.modal, self.prompt_manager, self.actualizar_combo_prompts)
    
    def incorporar_archivo_al_prompt(self):
        """Función auxiliar para leer un archivo y pegarlo al final del prompt actual."""
        from tkinter import filedialog
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo para contexto",
            filetypes=[("Archivos de texto", "*.txt *.md *.py *.js *.csv"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            try:
                with open(archivo, "r", encoding="utf-8") as f:
                    contenido = f.read()
                # Añadimos un separador visual para que la IA distinga el prompt del archivo
                self.entry_prompt.insert(tk.END, f"\n\n--- CONTENIDO DEL ARCHIVO ({archivo}) ---\n{contenido}")
                print(f"Archivo {archivo} adjuntado al prompt.")
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
        
    def crear_seccion_botones(self, parent):
        """Crea los botones de acción."""
        frame_btns = tk.Frame(parent)
        frame_btns.pack(fill="x", pady=(0, 10))
        
        # Botón Consultar
        self.btn_consultar = tk.Button(
            frame_btns,
            text="🤖 Consultar Gemini",
            command=self.realizar_consulta,
            bg="#28A745",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            width=18,
            height=2
        )
        self.btn_consultar.pack(side="left", padx=5)
        
        # Botón Limpiar historial
        tk.Button(
            frame_btns,
            text="🗑️ Limpiar Chat",
            command=self.limpiar_historial,
            bg="#FFC107",
            fg="black",
            font=("Arial", 10),
            cursor="hand2",
            width=15,
            height=2
        ).pack(side="left", padx=5)
        
        # Botón Insertar en editor
        tk.Button(
            frame_btns,
            text="📋 Insertar",
            command=self.insertar_en_editor,
            bg="#007BFF",
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            width=12,
            height=2
        ).pack(side="left", padx=5)

        # Botón Aplicar (Reemplazar)
        tk.Button(
            frame_btns,
            text="📝 Aplicar al Texto",
            command=self.aplicar_cambios_texto,
            bg="#fd7e14",
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            width=15,
            height=2
        ).pack(side="left", padx=5)
        
        # Botón Exportar Historial
        tk.Button(
            frame_btns,
            text="💾 Exportar Chat",
            command=self.exportar_historial,
            bg="#17a2b8",
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            width=15,
            height=2
        ).pack(side="left", padx=5)
        
        # Botón Cerrar
        tk.Button(
            frame_btns,
            text="❌ Cerrar",
            command=self.cerrar_ventana,
            bg="#DC3545",
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            width=12,
            height=2
        ).pack(side="right", padx=5)
        
    def configurar_atajos(self):
        """Configura atajos de teclado."""
        # Ctrl+Enter para enviar consulta
        self.entry_prompt.bind("<Control-Return>", lambda e: self.realizar_consulta())
        
    def agregar_mensaje_historial(self, tipo, mensaje):
        """
        Agrega un mensaje al historial visual.
        
        :param tipo: 'usuario' o 'gemini'
        :param mensaje: Texto del mensaje
        """
        self.text_historial.config(state="normal")
        
        if tipo == "usuario":
            self.text_historial.insert(tk.END, "👤 Tú: ", "usuario")
            self.text_historial.insert(tk.END, f"{mensaje}\n\n")
        elif tipo == "gemini":
            self.text_historial.insert(tk.END, "🤖 Gemini: ", "gemini")
            self.text_historial.insert(tk.END, f"{mensaje}\n")
            self.text_historial.insert(tk.END, "-" * 80 + "\n\n", "separador")
        
        self.text_historial.config(state="disabled")
        self.text_historial.see(tk.END)
        
    def realizar_consulta(self):
        """Realiza la consulta a Gemini en un hilo separado."""
        prompt_user = self.entry_prompt.get("1.0", tk.END).strip()
        
        if not prompt_user:
            messagebox.showwarning("Atención", "Por favor, escribe una pregunta.")
            return
        
        # Deshabilitar botón y mostrar progreso
        self.btn_consultar.config(state="disabled")
        self.progreso.start()
        
        # Agregar pregunta al historial
        self.agregar_mensaje_historial("usuario", prompt_user)
        
        # Limpiar entrada
        self.entry_prompt.delete("1.0", tk.END)
        
        modelo_elegido = self.combo_modelo.get()
        
        # Ejecutar consulta en hilo separado
        thread = threading.Thread(
            target=self._thread_consulta_ai,
            args=(prompt_user, modelo_elegido),
            daemon=True
        )
        thread.start()
        
    def _thread_consulta_ai(self, prompt_user, modelo_elegido):
        """
        Ejecuta la consulta a la IA seleccionada en un hilo separado.
        
        :param prompt_user: Pregunta del usuario
        :param modelo_elegido: Nombre del modelo seleccionado
        """
        try:
            if "DeepSeek" in modelo_elegido:
                self._consulta_deepseek(prompt_user, modelo_elegido)
            else:
                self._consulta_gemini(prompt_user, modelo_elegido)
            
        except Exception as e:
            error_msg = f"Error al consultar IA:\n\n{str(e)}\n\nVerifica tu API Key y conexión a internet."
            self.modal.after(0, lambda: messagebox.showerror("Error de API", error_msg))
            
        finally:
            self.modal.after(0, self._finalizar_consulta)
            
    def _consulta_gemini(self, prompt_user, modelo_elegido):
        """Lógica específica para Google Gemini."""
        # Usamos una sesión persistente para no re-enviar el contexto manualmente
        if self.chat_session is None:
            # Mapeo del nombre en el Combo Box al ID técnico del modelo
            model_id = "gemini-2.5-flash" # Default (el más rápido y estable según tu test)
            
            if "2.5 Pro" in modelo_elegido:
                model_id = "gemini-2.5-pro"
            elif "2.0 Flash" in modelo_elegido:
                model_id = "gemini-2.0-flash"
            elif "2.5 Flash" in modelo_elegido:
                model_id = "gemini-2.5-flash"
                
            model = genai.GenerativeModel(model_id)
            self.chat_session = model.start_chat(history=[])
            
            # Configurar el contexto inicial una sola vez
            contexto_inicial = f"CONTEXTO DEL DOCUMENTO:\n{self.texto_contexto}\n\n---\nA partir de ahora, responde las preguntas del usuario basándote en este contexto."
            self.chat_session.send_message(contexto_inicial)
        
        response = self.chat_session.send_message(prompt_user)
        
        self.historial_conversacion.append({
            "usuario": prompt_user,
            "gemini": response.text
        })
        self.modal.after(0, lambda: self._mostrar_respuesta(response.text))

    def _consulta_deepseek(self, prompt_user, modelo_elegido):
        """Lógica específica para DeepSeek API."""
        if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "TU_DEEPSEEK_KEY":
            raise Exception("Configura la DEEPSEEK_API_KEY en el archivo gemini_assistant.py")
            
        model_id = "deepseek-reasoner" if "Reasoner" in modelo_elegido else "deepseek-chat"
        url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        messages = [{"role": "system", "content": "Eres un asistente experto en programación y análisis de texto."}]
        
        if not self.historial_conversacion:
            first_content = f"CONTEXTO:\n{self.texto_contexto}\n\nPREGUNTA:\n{prompt_user}"
            messages.append({"role": "user", "content": first_content})
        else:
            # Reconstruir historial para mantener contexto en API stateless
            first_entry = self.historial_conversacion[0]
            first_msg = f"CONTEXTO:\n{self.texto_contexto}\n\nPREGUNTA:\n{first_entry['usuario']}"
            messages.append({"role": "user", "content": first_msg})
            messages.append({"role": "assistant", "content": first_entry['gemini']})
            
            for entry in self.historial_conversacion[1:]:
                messages.append({"role": "user", "content": entry['usuario']})
                messages.append({"role": "assistant", "content": entry['gemini']})
                
            messages.append({"role": "user", "content": prompt_user})
            
        data = {"model": model_id, "messages": messages, "stream": False}
        
        response = requests.post(url, json=data, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result_text = response.json()['choices'][0]['message']['content']
            self.historial_conversacion.append({"usuario": prompt_user, "gemini": result_text})
            self.modal.after(0, lambda: self._mostrar_respuesta(result_text))
        else:
            try:
                error_json = response.json()
                error_msg = error_json.get('error', {}).get('message', response.text)
            except:
                error_msg = response.text

            if response.status_code == 402:
                raise Exception(f"Saldo Agotado (Error 402): {error_msg}\n\nLa API de DeepSeek requiere créditos válidos. Por favor recarga tu cuenta en deepseek.com o cambia al modelo 'Gemini' que tiene capa gratuita.")
            else:
                raise Exception(f"DeepSeek Error {response.status_code}: {error_msg}")
            
    def _mostrar_respuesta(self, respuesta):
        """Muestra la respuesta de Gemini en el historial."""
        self.agregar_mensaje_historial("gemini", respuesta)
        
    def _finalizar_consulta(self):
        """Finaliza la consulta y restaura la UI."""
        self.progreso.stop()
        self.btn_consultar.config(state="normal")
        self.entry_prompt.focus_set()
        
    def limpiar_historial(self):
        """Limpia el historial de conversación."""
        if messagebox.askyesno("Confirmar", "¿Deseas limpiar todo el historial de conversación?"):
            self.historial_conversacion.clear()
            self.chat_session = None
            self.text_historial.config(state="normal")
            self.text_historial.delete("1.0", tk.END)
            self.text_historial.config(state="disabled")
            
    def insertar_en_editor(self):
        """Inserta la última respuesta de Gemini en el editor principal."""
        if not self.historial_conversacion:
            messagebox.showwarning("Atención", "No hay respuestas para insertar.")
            return
        
        ultima_respuesta = self.historial_conversacion[-1]["gemini"]
        
        # Formatear como bloque PROMPT
        bloque_formateado = f"\n```PROMPT\n{ultima_respuesta}\n```\n"
        
        # Insertar en el editor principal
        self.text_editor.insert(tk.INSERT, bloque_formateado)
        
        messagebox.showinfo("Éxito", "Respuesta insertada en el editor.")
        
    def aplicar_cambios_texto(self):
        """Reemplaza el texto seleccionado original con la última respuesta de la IA."""
        if not self.historial_conversacion:
            messagebox.showwarning("Atención", "No hay respuestas para aplicar.")
            return
            
        ultima_respuesta = self.historial_conversacion[-1]["gemini"]
        
        if messagebox.askyesno("Confirmar Cambios", "Se reemplazará el texto seleccionado original con la respuesta de la IA.\n\n¿Estás seguro?"):
            try:
                # Usar las marcas para localizar la selección original
                start = self.text_editor.index("gemini_sel_start")
                end = self.text_editor.index("gemini_sel_end")
                
                self.text_editor.delete(start, end)
                self.text_editor.insert(start, ultima_respuesta)
                
                messagebox.showinfo("Éxito", "Texto actualizado correctamente.")
                self.cerrar_ventana()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo aplicar el cambio: {e}")

    def exportar_historial(self):
        """Exporta el historial de la conversación actual a un archivo JSON o TXT."""
        if not self.historial_conversacion:
            messagebox.showinfo("Info", "No hay historial para exportar.")
            return
            
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("Text Files", "*.txt")],
            title="Guardar Historial de Chat"
        )
        
        if not filename:
            return
            
        try:
            if filename.endswith('.json'):
                # Exportar estructura completa incluyendo el contexto inicial
                data = {
                    "contexto_inicial": self.texto_contexto,
                    "conversacion": self.historial_conversacion
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            else:
                # Exportar texto plano legible
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"--- CONTEXTO INICIAL ---\n{self.texto_contexto}\n\n")
                    for entry in self.historial_conversacion:
                        f.write(f"USUARIO: {entry['usuario']}\n")
                        f.write(f"IA: {entry['gemini']}\n")
                        f.write("-" * 40 + "\n")
            
            messagebox.showinfo("Éxito", f"Historial guardado en {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el historial: {e}")

    def cerrar_ventana(self):
        """Cierra la ventana modal."""
        # Limpiar marcas
        try:
            self.text_editor.mark_unset("gemini_sel_start")
            self.text_editor.mark_unset("gemini_sel_end")
        except:
            pass
            
        if self.historial_conversacion:
            if messagebox.askyesno("Confirmar", "¿Deseas cerrar la ventana? Se perderá el historial."):
                self.modal.destroy()
        else:
            self.modal.destroy()


# Función de conveniencia para mantener compatibilidad con código anterior
def abrir_modal_gemini(parent, text_editor, api_key=None):
    """
    Abre una ventana modal para interactuar con Gemini Pro.
    
    :param parent: La ventana o frame padre
    :param text_editor: El widget de texto del editor
    :param api_key: API Key de Google Gemini (opcional)
    """
    api_key="AIzaSyDUMffgm3ZRADAxQugX84TUe2rNvyBLhTU"
    VentanaGeminiModal(parent, text_editor, api_key)
