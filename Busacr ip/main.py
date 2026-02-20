import os
import re
import tkinter as tk
from tkinter import filedialog, scrolledtext

# Expresión regular para detectar IPs válidas
regex_ip = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"

def seleccionar_directorio():
    ruta = filedialog.askdirectory()
    if ruta:
        entrada_directorio.delete(0, tk.END)
        entrada_directorio.insert(0, ruta)

def escanear_ips():
    ruta = entrada_directorio.get()
    if not ruta:
        mostrar_resultado("⚠️ Seleccioná un directorio primero.\n")
        return

    mostrar_resultado(f"🔍 Escaneando archivos en: {ruta}\n\n")

    for carpeta_actual, _, archivos in os.walk(ruta):
        for archivo in archivos:
            if archivo.endswith(".txt"):
                ruta_completa = os.path.join(carpeta_actual, archivo)
                try:
                    with open(ruta_completa, "r", encoding="utf-8", errors="ignore") as f:
                        for num_linea, linea in enumerate(f, start=1):
                            if "ip:" in linea.lower():
                                ips_encontradas = re.findall(regex_ip, linea)
                                if ips_encontradas:
                                    mostrar_resultado(f"[{archivo}] Línea {num_linea}: {linea.strip()}\n")
                except Exception as e:
                    mostrar_resultado(f"❌ Error al leer {ruta_completa}: {e}\n")

def mostrar_resultado(texto):
    salida_texto.insert(tk.END, texto)
    salida_texto.see(tk.END)

# Crear ventana principal
ventana = tk.Tk()
ventana.title("Escaneo de IPs en archivos TXT")
ventana.geometry("800x500")

# Selector de directorio
frame_superior = tk.Frame(ventana)
frame_superior.pack(pady=10)

tk.Label(frame_superior, text="Directorio raíz:").pack(side=tk.LEFT)
entrada_directorio = tk.Entry(frame_superior, width=60)
entrada_directorio.pack(side=tk.LEFT, padx=5)
tk.Button(frame_superior, text="Seleccionar...", command=seleccionar_directorio).pack(side=tk.LEFT)

# Botón de procesamiento
tk.Button(ventana, text="🔍 Comenzar escaneo", command=escanear_ips, bg="#4CAF50", fg="white").pack(pady=10)

# Área de resultados
salida_texto = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, width=100, height=20)
salida_texto.pack(padx=10, pady=10)

ventana.mainloop()