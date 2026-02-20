import tkinter as tk
from gui.components.gemini_assistant import abrir_modal_gemini

def crear_menu_contextual(parent, text_widget):
    """Crea y retorna un menú contextual con todas las funcionalidades"""
    menu = tk.Menu(parent.root, tearoff=0)
    
    # Comandos básicos
    menu.add_command(label="📋 Copiar", command=parent.copiar_seleccion)
    # Opción con chispa (La más moderna)
    menu.add_command(label="✨ Procesar con Gemini", command=lambda: abrir_modal_gemini(parent.root, text_widget))
    menu.add_command(label="📄 Seleccionar Todo", command=parent.seleccionar_todo)
    menu.add_command(label="🧹 Limpiar Selección", command=parent.limpiar_seleccion)
    menu.add_separator()
    
    # Navegación del árbol
    menu.add_command(label="🔼 Expandir Carpeta", command=parent.expandir_carpeta_actual)
    menu.add_command(label="🔽 Contraer Carpeta", command=parent.contraer_carpeta_actual)
    menu.add_separator()
    
    # Operaciones globales
    menu.add_command(label="🔼 Expandir Todo", command=parent.expandir_todo)
    menu.add_command(label="🔽 Contraer Todo", command=parent.contraer_todo)
    menu.add_separator()
    
    # Contenido de archivos
    menu.add_command(label="👁️ Ver Archivos Seleccionados", command=parent.ver_contenido_seleccionado)
    menu.add_separator()
    
    # Exportación
    menu.add_command(label="💾 Exportar a Markdown", command=parent.exportar_a_markdown)
    menu.add_command(label="💾 Exportar a TXT", command=parent.exportar_a_txt)
    
    return menu