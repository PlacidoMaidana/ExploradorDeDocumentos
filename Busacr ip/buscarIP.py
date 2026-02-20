import subprocess
import tkinter as tk
from tkinter import simpledialog, scrolledtext
import re

# Diccionario de referencia MAC → oficina
mac_a_oficina = {
    "00-1A-2B-3C-4D-5E": "Oficina Administración",
    "00-1B-2C-3D-4E-5F": "Oficina Técnica",
    # Agregá más según tu red
}


def perfil_de_ip(ip):
    mostrar_resultado(f"📌 Perfil de escaneo para IP: {ip}")
    try:
        resultado = subprocess.check_output(["nmap", "-Pn", "-sV", "-O", ip], stderr=subprocess.DEVNULL, text=True)
        mostrar_resultado(resultado)
    except Exception as e:
        mostrar_resultado(f"❌ Error al ejecutar nmap: {e}")





def mostrar_resultado(texto):
    salida_texto.insert(tk.END, texto + "\n")
    salida_texto.see(tk.END)

def escanear_equipo_por_ip(ip):
    mostrar_resultado(f"🔍 Buscando información para IP: {ip}")

    # Nombre del equipo
    try:
        nombre = subprocess.check_output(["ping", "-a", ip], stderr=subprocess.DEVNULL, text=True)
        mostrar_resultado(f"🖥️ Nombre de equipo:\n{nombre}")
    except:
        mostrar_resultado("❌ No se pudo resolver el nombre del equipo.")

    # Recursos compartidos
    try:
        recursos = subprocess.check_output(["net", "view", f"\\\\{ip}"], stderr=subprocess.DEVNULL, text=True)
        mostrar_resultado(f"📂 Recursos compartidos:\n{recursos}")
    except:
        mostrar_resultado("⚠️ No se detectaron recursos compartidos o el equipo no responde.")

    # Escaneo de puertos con nmap
    try:
        puertos = subprocess.check_output(["nmap", "-Pn", ip], stderr=subprocess.DEVNULL, text=True)
        mostrar_resultado(f"🛡️ Puertos abiertos:\n{puertos}")
    except:
        mostrar_resultado("⚠️ No se pudo ejecutar nmap o no está instalado.")

def mostrar_tabla_arp():
    mostrar_resultado("📡 Tabla ARP local:")
    try:
        salida = subprocess.check_output(["arp", "-a"], stderr=subprocess.DEVNULL, text=True)
        for linea in salida.splitlines():
            partes = re.split(r"\s+", linea.strip())
            if len(partes) >= 3 and re.match(r"\d+\.\d+\.\d+\.\d+", partes[0]):
                ip = partes[0]
                mac = partes[1].upper().replace(":", "-")
                oficina = mac_a_oficina.get(mac, "Ubicación desconocida")
                mostrar_resultado(f"IP: {ip} | MAC: {mac} | Oficina: {oficina}")
    except Exception as e:
        mostrar_resultado(f"❌ Error al obtener tabla ARP: {e}")

def iniciar_busqueda():
    ip = simpledialog.askstring("Buscar IP", "Ingresá la IP que querés ubicar:")
    if ip:
        salida_texto.delete(1.0, tk.END)
        escanear_equipo_por_ip(ip)



def listar_equipos_conectados():
    salida_texto.delete(1.0, tk.END)
    mostrar_resultado("📋 Equipos conectados en la red local:\n")

    try:
        salida = subprocess.check_output(["arp", "-a"], stderr=subprocess.DEVNULL, text=True)
        for linea in salida.splitlines():
            partes = re.split(r"\s+", linea.strip())
            if len(partes) >= 2 and re.match(r"\d+\.\d+\.\d+\.\d+", partes[0]):
                ip = partes[0]
                try:
                    nombre = subprocess.check_output(["ping", "-a", "-n", "1", ip], stderr=subprocess.DEVNULL, text=True)
                    nombre_host = re.search(r"Disparando a ([^\s]+)", nombre)
                    if nombre_host:
                        mostrar_resultado(f"🖥️ {ip} → {nombre_host.group(1)}")
                    else:
                        mostrar_resultado(f"🖥️ {ip} → (sin nombre)")
                except:
                    mostrar_resultado(f"🖥️ {ip} → (no responde)")
    except Exception as e:
        mostrar_resultado(f"❌ Error al obtener lista de equipos: {e}")





# Interfaz
ventana = tk.Tk()
ventana.title("Ubicar equipo por IP en red local")
ventana.geometry("800x600")

tk.Button(ventana, text="🔍 Buscar equipo por IP", command=iniciar_busqueda, bg="#2196F3", fg="white").pack(pady=10)
tk.Button(ventana, text="📡 Mostrar tabla ARP", command=mostrar_tabla_arp, bg="#FF9800", fg="white").pack(pady=5)
tk.Button(ventana, text="📋 Listar equipos conectados", command=listar_equipos_conectados, bg="#4CAF50", fg="white").pack(pady=5)
salida_texto = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, width=100, height=30)
salida_texto.pack(padx=10, pady=10)

ventana.mainloop()