import os
from datetime import datetime
from tkinter import filedialog, messagebox

class MarkdownConverter:
    def __init__(self, directorio, tipo_operacion, contenido):
        self.directorio = directorio
        self.tipo_operacion = tipo_operacion
        self.contenido = contenido
    
    def convertir(self):
        """Convierte el contenido actual a formato Markdown"""
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nombre_directorio = os.path.basename(self.directorio) if self.directorio else "Directorio"
        
        # Crear encabezado del documento
        markdown = f"""# Exploración de Directorio: {nombre_directorio}

**Fecha de generación:** {fecha_actual}  
**Directorio:** `{self.directorio}`  
**Tipo de exploración:** {self._obtener_nombre_operacion()}

---

"""
        
        if self.tipo_operacion in ["esquema", "esquema_marcado"]:
            # Para esquemas, usar formato de árbol con bloques de código
            markdown += "## Estructura del Directorio\n\n"
            markdown += "```\n"
            markdown += self.contenido
            markdown += "\n```\n"
            
        else:
            # Para contenido de archivos
            markdown += "## Contenido de Archivos\n\n"
            
            # Procesar el contenido línea por línea
            lineas = self.contenido.split('\n')
            i = 0
            while i < len(lineas):
                linea = lineas[i]
                
                # Detectar inicio de archivo (línea con !!!)
                if linea.startswith('!') and len(linea) > 10:  # Línea de separadores
                    # Saltar la línea de separadores
                    i += 1
                    if i < len(lineas):
                        nombre_archivo = lineas[i].strip()
                        if nombre_archivo:  # Solo si hay nombre de archivo
                            markdown += f"### 📄 {nombre_archivo}\n\n"
                            i += 1
                            
                            # Saltar la segunda línea de separadores
                            if i < len(lineas) and lineas[i].startswith('!'):
                                i += 1
                            
                            # Obtener extensión para el resaltado de sintaxis
                            extension = os.path.splitext(nombre_archivo)[1].lower()
                            lenguaje = self._obtener_lenguaje_markdown(extension)
                            
                            # Recopilar contenido del archivo hasta el siguiente separador o error
                            contenido_archivo = []
                            while i < len(lineas):
                                if lineas[i].startswith('!') and len(lineas[i]) > 10:
                                    break
                                if lineas[i].startswith('[ERROR]'):
                                    break
                                contenido_archivo.append(lineas[i])
                                i += 1
                            
                            # Agregar el código con resaltado de sintaxis
                            if contenido_archivo:
                                codigo = '\n'.join(contenido_archivo).strip()
                                if codigo:
                                    markdown += f"```{lenguaje}\n{codigo}\n```\n\n"
                                else:
                                    markdown += "*Archivo vacío*\n\n"
                            continue
                
                # Procesar errores
                if linea.startswith('[ERROR]'):
                    markdown += f"⚠️ **Error:** {linea[7:].strip()}\n\n"
                
                i += 1
        
        return markdown
    
    def _obtener_nombre_operacion(self):
        """Retorna el nombre legible de la operación"""
        nombres = {
            "esquema": "Esquema completo del directorio",
            "contenido_raiz": "Contenido de archivos en directorio raíz",
            "contenido_completo": "Contenido completo de archivos",
            "contenido_seleccionado": "Contenido de archivos seleccionados"
        }
        return nombres.get(self.tipo_operacion, "Exploración personalizada")
    
    def _obtener_lenguaje_markdown(self, extension):
        """Retorna el identificador de lenguaje para resaltado de sintaxis en Markdown"""
        lenguajes = {
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.css': 'css',
            '.php': 'php',
            '.json': 'json',
            '.xml': 'xml',
            '.md': 'markdown',
            '.txt': 'text',
            '.csv': 'csv',
            '.sql': 'sql',
            # Nuevos formatos
            '.docx': 'text',
            '.pptx': 'text', 
            '.pdf': 'text'
        }
        return lenguajes.get(extension, 'text')

    def _markdown_a_texto_plano(self, markdown):
        """Convierte markdown a texto plano simple"""
        # Eliminar encabezados markdown
        texto = markdown.replace('# ', '').replace('## ', '').replace('### ', '')
        # Eliminar formato bold/italic
        texto = texto.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
        # Eliminar bloques de código
        texto = texto.replace('```python', '').replace('```javascript', '').replace('```html', '')
        texto = texto.replace('```css', '').replace('```php', '').replace('```json', '').replace('```', '')
        # Eliminar líneas vacías excesivas
        lineas = texto.split('\n')
        lineas_filtradas = []
        for i, linea in enumerate(lineas):
            if linea.strip() or (i < len(lineas)-1 and lineas[i+1].strip()):
                lineas_filtradas.append(linea)
        
        return '\n'.join(lineas_filtradas)

# Funciones de exportación que utilizan la clase MarkdownConverter
def exportar_a_markdown(contenido, parent_window, directorio, tipo_operacion):
    """Exporta el contenido actual a formato Markdown usando la clase MarkdownConverter"""
    if not contenido.strip():
        messagebox.showwarning("Advertencia", "No hay contenido para exportar.")
        return False
        
    archivo = filedialog.asksaveasfilename(
        parent=parent_window,
        defaultextension=".md",
        filetypes=[("Markdown", "*.md"), ("Todos los archivos", "*.*")]
    )
    if archivo:
        try:
            converter = MarkdownConverter(directorio, tipo_operacion, contenido)
            markdown_content = converter.convertir()
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            messagebox.showinfo("Éxito", f"Contenido exportado a {archivo}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")
            return False
    return False

def exportar_a_txt(contenido, parent_window, directorio, tipo_operacion):
    """Exporta el contenido actual a formato TXT con encabezado"""
    if not contenido.strip():
        messagebox.showwarning("Advertencia", "No hay contenido para exportar.")
        return False
        
    archivo = filedialog.asksaveasfilename(
        parent=parent_window,
        defaultextension=".txt",
        filetypes=[("Texto", "*.txt"), ("Todos los archivos", "*.*")]
    )
    if archivo:
        try:
            # Para TXT, también usar el converter pero con formato simple
            converter = MarkdownConverter(directorio, tipo_operacion, contenido)
            markdown_content = converter.convertir()
            
            # Convertir markdown a texto plano simple
            texto_plano = converter._markdown_a_texto_plano(markdown_content)
            
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(texto_plano)
            messagebox.showinfo("Éxito", f"Contenido exportado a {archivo}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")
            return False
    return False