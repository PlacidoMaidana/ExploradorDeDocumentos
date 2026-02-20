import os
from utils.constants import EXT_VALIDAS

def contar_archivos_validos(ruta):
    """Cuenta el total de archivos válidos para la barra de progreso"""
    count = 0
    for root, _, files in os.walk(ruta):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in EXT_VALIDAS:
                count += 1
    return count

def contar_archivos_marcados(ruta):
    """Cuenta archivos válidos solo en directorios marcados"""
    count = 0
    for root, dirs, files in os.walk(ruta):
        path_parts = os.path.relpath(root, ruta).split(os.sep)
        is_marked_path = any(part.startswith('+') for part in path_parts if part != '.')
        
        if is_marked_path or os.path.basename(root).startswith('+'):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in EXT_VALIDAS:
                    count += 1
            dirs[:] = [d for d in dirs if d.startswith('+')]
        else:
            dirs[:] = [d for d in dirs if d.startswith('+')]
    return count