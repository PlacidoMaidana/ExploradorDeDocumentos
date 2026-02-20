"""
CONFIGURACIÓN DE GEMINI MODAL
Archivo para configurar fácilmente tu API Key y modelo preferido
"""

# ============================================================================
# CONFIGURACIÓN PRINCIPAL
# ============================================================================

# Tu API Key de Google Gemini
# Obtén una en: https://makersuite.google.com/app/apikey
API_KEY = "AIzaSyDUMffgm3ZRADAxQugX84TUe2rNvyBLhTU"

# ============================================================================
# SELECCIÓN DE MODELO
# ============================================================================

# Modelos disponibles y recomendados:

# ⚡ RÁPIDOS Y EFICIENTES (Recomendados para uso general)
MODELO_FLASH_25 = "gemini-2.5-flash"          # ✅ MEJOR OPCIÓN (default)
MODELO_FLASH_20 = "gemini-2.0-flash"          # Alternativa estable
MODELO_FLASH_LITE = "gemini-2.5-flash-lite"   # Ultra rápido

# 🧠 POTENTES (Para análisis profundos)
MODELO_PRO_25 = "gemini-2.5-pro"              # Más inteligente
MODELO_PRO_LATEST = "gemini-pro-latest"       # Versión estable

# 🆕 EXPERIMENTALES (Última generación)
MODELO_FLASH_3 = "gemini-3-flash-preview"     # Serie 3.0
MODELO_PRO_3 = "gemini-3-pro-preview"         # Serie 3.0 Pro

# ============================================================================
# MODELO ACTIVO
# ============================================================================

# Cambia esta línea para usar un modelo diferente:
MODELO_SELECCIONADO = MODELO_FLASH_25  # 👈 Cambia aquí para probar otros

# Ejemplos de cómo cambiar:
# MODELO_SELECCIONADO = MODELO_PRO_25      # Para más potencia
# MODELO_SELECCIONADO = MODELO_FLASH_3     # Para experimentar con 3.0
# MODELO_SELECCIONADO = MODELO_FLASH_LITE  # Para máxima velocidad

# ============================================================================
# CONFIGURACIÓN AVANZADA
# ============================================================================

# Parámetros de generación (opcional - valores por defecto)
CONFIGURACION_GENERACION = {
    "temperature": 0.7,          # Creatividad (0.0-1.0)
    "top_p": 0.95,              # Diversidad de respuestas
    "top_k": 40,                # Cantidad de opciones
    "max_output_tokens": 2048,  # Longitud máxima de respuesta
}

# ============================================================================
# INFORMACIÓN DE MODELOS
# ============================================================================

INFO_MODELOS = {
    "gemini-2.5-flash": {
        "nombre": "Gemini 2.5 Flash",
        "velocidad": "⚡⚡⚡",
        "potencia": "🧠🧠",
        "descripcion": "Mejor balance velocidad/calidad"
    },
    "gemini-2.5-pro": {
        "nombre": "Gemini 2.5 Pro",
        "velocidad": "⚡⚡",
        "potencia": "🧠🧠🧠",
        "descripcion": "Máxima precisión y análisis profundo"
    },
    "gemini-3-flash-preview": {
        "nombre": "Gemini 3.0 Flash Preview",
        "velocidad": "⚡⚡⚡⚡",
        "potencia": "🧠🧠🧠",
        "descripcion": "Última generación, experimental"
    },
    "gemini-2.5-flash-lite": {
        "nombre": "Gemini 2.5 Flash Lite",
        "velocidad": "⚡⚡⚡⚡⚡",
        "potencia": "🧠",
        "descripcion": "Ultra rápido para consultas simples"
    }
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def obtener_info_modelo(modelo=None):
    """Obtiene información del modelo seleccionado."""
    if modelo is None:
        modelo = MODELO_SELECCIONADO
    
    info = INFO_MODELOS.get(modelo, {
        "nombre": modelo,
        "velocidad": "⚡⚡⚡",
        "potencia": "🧠🧠",
        "descripcion": "Modelo personalizado"
    })
    
    return info

def mostrar_configuracion():
    """Muestra la configuración actual."""
    info = obtener_info_modelo()
    
    print("=" * 60)
    print("⚙️  CONFIGURACIÓN ACTUAL")
    print("=" * 60)
    print(f"\n📋 Modelo seleccionado: {MODELO_SELECCIONADO}")
    print(f"   Nombre: {info['nombre']}")
    print(f"   Velocidad: {info['velocidad']}")
    print(f"   Potencia: {info['potencia']}")
    print(f"   Descripción: {info['descripcion']}")
    print(f"\n🔑 API Key: {'✅ Configurada' if API_KEY and API_KEY != 'TU_API_KEY_AQUI' else '❌ No configurada'}")
    print("\n" + "=" * 60)

# ============================================================================
# EJECUCIÓN DE PRUEBA
# ============================================================================

if __name__ == "__main__":
    mostrar_configuracion()
    
    # Verificar API Key
    if not API_KEY or API_KEY == "TU_API_KEY_AQUI":
        print("\n⚠️  ERROR: Debes configurar tu API Key")
        print("   Edita este archivo y agrega tu API Key en la línea 11\n")
    else:
        print("\n✅ Configuración lista para usar")
        print("\n💡 Para usar esta configuración en tu código:")
        print("   from config_gemini import API_KEY, MODELO_SELECCIONADO")
        print("   genai.configure(api_key=API_KEY)")
        print(f"   model = genai.GenerativeModel(MODELO_SELECCIONADO)\n")