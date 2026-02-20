import tkinter as tk
from tkinter import scrolledtext

class HelpModal:
    def __init__(self, master):
        self.master = master
    
    def mostrar_ayuda_esquema(self):
        """Muestra una ventana de ayuda explicando el formato de esquema aceptado"""
        ayuda_ventana = tk.Toplevel(self.master)
        ayuda_ventana.title("Formato de Esquema Aceptado")
        ayuda_ventana.geometry("700x500")
        ayuda_ventana.grab_set()

        # Frame principal
        frame = tk.Frame(ayuda_ventana)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Título
        tk.Label(frame, text="📌 Cómo Formatear el Esquema de Directorios", font=("Arial", 14, "bold")).pack(pady=(0, 10))

        # Área de texto con scroll
        text_area = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=80, height=25, font=("Consolas", 10))
        text_area.pack(fill=tk.BOTH, expand=True)

        # Contenido de la ayuda
        contenido_ayuda = """
    Tu aplicación puede crear una estructura de carpetas y archivos a partir de un texto pegado en el área principal.
    
    📌 REGLA DE ORO:
    Para que un elemento sea reconocido como DIRECTORIO, su nombre debe TERMINAR con una barra "/".
    
    Si no termina con "/", se creará como un ARCHIVO (vacío).
    
    ---
    
    ✅ EJEMPLO DE ESQUEMA VÁLIDO:
    
    ├── proyecto/
    │   ├── src/
    │   │   ├── main.py
    │   │   └── utils.py
    │   ├── tests/
    │   │   └── test_main.py
    │   ├── README.md
    │   └── .gitignore
    ├── docs/
    │   └── guia_usuario.md
    └── requirements.txt
    
    ---
    
    🔍 ¿CÓMO PEGARLO?
    1. Copia un esquema como el de arriba (de tu IA, de un archivo .md, etc.).
    2. Pégalo en el área de texto principal de la aplicación.
    3. Haz clic en "Crear Estructura desde Esquema".
    4. Selecciona la carpeta destino.
    5. ¡Listo! La estructura se creará automáticamente.
    
    ---
    
    💡 CONSEJO:
    Si tu esquema NO tiene barras "/" al final de los directorios, puedes:
    - Editarlo manualmente en el área de texto ANTES de hacer clic en el botón.
    - Añadir "/" al final de cada nombre de carpeta.
    
    Ejemplo: Cambia "src" por "src/".
    """

        # Insertar el contenido
        text_area.insert(tk.END, contenido_ayuda)
        text_area.config(state=tk.DISABLED)

        # Botón para cerrar
        tk.Button(frame, text="Cerrar", command=ayuda_ventana.destroy, bg="#FF6B6B", fg="white").pack(pady=10)