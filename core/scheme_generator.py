import os
from utils.constants import EXT_VALIDAS

import os
from utils.constants import EXT_VALIDAS

def generar_esquema_estructurado(ruta, nivel=0):
    """Genera la estructura jerárquica del directorio"""
    estructura = []
    try:
        elementos = sorted(os.listdir(ruta))
        for elemento in elementos:
            ruta_completa = os.path.join(ruta, elemento)
            es_directorio = os.path.isdir(ruta_completa)
            item = {
                'nombre': elemento,
                'es_directorio': es_directorio,
                'expandido': False,  # Por defecto contraído
                'contenido': []
            }
            if es_directorio:
                item['contenido'] = generar_esquema_estructurado(ruta_completa, nivel + 1)
                estructura.append(item)
            else:
                # Mostrar todos los archivos sin filtrar por extensión
                # El filtrado se hace solo al ver el contenido
                estructura.append(item)
    except PermissionError:
        pass
    return estructura

def generar_esquema_directorio(ruta, prefijo='', excluir=None, incluir=None):
    excluir = set(excluir or [])
    incluir = set(incluir or [])
    resultado = ''

    try:
        elementos = sorted(os.listdir(ruta))
    except Exception as e:
        return f"[ERROR] No se pudo acceder a {ruta}: {e}\n"

    for i, elem in enumerate(elementos):
        ruta_completa = os.path.join(ruta, elem)

        if elem in excluir and os.path.isdir(ruta_completa):
            continue

        if incluir and os.path.isdir(ruta_completa) and elem not in incluir:
            continue

        es_ultimo = (i == len(elementos) - 1)
        conector = '└── ' if es_ultimo else '├── '
        resultado += f"{prefijo}{conector}{elem}\n"

        if os.path.isdir(ruta_completa):
            nuevo_prefijo = prefijo + ('    ' if es_ultimo else '│   ')
            resultado += generar_esquema_directorio(ruta_completa, nuevo_prefijo, excluir, incluir)

    return resultado

def generar_esquema_directorio_marcado(ruta, prefijo=''):
    resultado = ''
    elementos = sorted(os.listdir(ruta))
    
    elementos_marcados = [e for e in elementos if os.path.isdir(os.path.join(ruta, e)) and e.startswith('+')]
    
    for i, elem in enumerate(elementos_marcados):
        ruta_completa = os.path.join(ruta, elem)
        es_ultimo = (i == len(elementos_marcados) - 1)
        conector = '└── ' if es_ultimo else '├── '
        resultado += f"{prefijo}{conector}{elem}\n"
        nuevo_prefijo = prefijo + ('    ' if es_ultimo else '│   ')
        resultado += generar_esquema_directorio_marcado(ruta_completa, nuevo_prefijo)
    
    return resultado



def expandir_todo(estructura):
    """Expande recursivamente todos los directorios"""
    for item in estructura:
        if item['es_directorio']:
            item['expandido'] = True
            expandir_todo(item['contenido'])

def contraer_todo(estructura):
    """Contrae recursivamente todos los directorios"""
    for item in estructura:
        if item['es_directorio']:
            item['expandido'] = False
            contraer_todo(item['contenido'])
            
            
def expandir_carpeta(estructura, nombre_carpeta):
    """Expande una carpeta específica por nombre"""
    for item in estructura:
        if item['nombre'] == nombre_carpeta and item['es_directorio']:
            item['expandido'] = True
            return True
        if item['es_directorio'] and item['expandido']:
            if expandir_carpeta(item['contenido'], nombre_carpeta):
                return True
    return False

def contraer_carpeta(estructura, nombre_carpeta):
    """Contrae una carpeta específica por nombre"""
    for item in estructura:
        if item['nombre'] == nombre_carpeta and item['es_directorio']:
            item['expandido'] = False
            return True
        if item['es_directorio'] and item['expandido']:
            if contraer_carpeta(item['contenido'], nombre_carpeta):
                return True
    return False