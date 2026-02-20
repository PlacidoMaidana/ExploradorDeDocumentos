import tkinter as tk
from gui.app import FileExplorerApp

def main():
    root = tk.Tk()
    root.title("Explorador de Directorios Avanzado")
    root.iconbitmap("File-explorer.ico")
    root.geometry("1000x700")
    
    # Crear la aplicación
    app = FileExplorerApp(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()
    
     # pyinstaller --onefile --windowed --icon=File-explorer.ico --name="Explorador" main.py