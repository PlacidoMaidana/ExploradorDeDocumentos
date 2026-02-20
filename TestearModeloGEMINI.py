"""
Script para verificar qué modelos de Gemini están disponibles con tu API Key
"""

import google.generativeai as genai

# Coloca tu API Key aquí
API_KEY = "AIzaSyDUMffgm3ZRADAxQugX84TUe2rNvyBLhTU"

def verificar_modelos():
    """Verifica y muestra los modelos disponibles."""
    
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE MODELOS GEMINI DISPONIBLES")
    print("=" * 60)
    
    try:
        # Configurar API
        genai.configure(api_key=API_KEY)
        print("\n✅ API Key configurada correctamente\n")
        
        # Listar modelos disponibles
        print("📋 Modelos disponibles:")
        print("-" * 60)
        
        modelos_generacion = []
        
        for model in genai.list_models():
            # Filtrar solo modelos que soportan generateContent
            if 'generateContent' in model.supported_generation_methods:
                modelos_generacion.append(model.name)
                print(f"✓ {model.name}")
                print(f"  Métodos: {', '.join(model.supported_generation_methods)}")
                print()
        
        if not modelos_generacion:
            print("❌ No se encontraron modelos disponibles")
            print("   Verifica que tu API Key sea válida")
            return
        
        print("=" * 60)
        print("\n🎯 MODELOS RECOMENDADOS PARA USAR:\n")
        
        # Buscar modelos comunes
        recomendados = {
            'gemini-pro': 'Modelo estándar, bueno para la mayoría de tareas',
            'gemini-1.5-pro': 'Modelo avanzado con ventana de contexto grande',
            'gemini-1.5-flash': 'Modelo rápido y eficiente',
            'gemini-2.0-flash-exp': 'Modelo experimental más reciente'
        }
        
        for nombre_modelo, descripcion in recomendados.items():
            # Buscar coincidencias en los modelos disponibles
            encontrado = [m for m in modelos_generacion if nombre_modelo in m.lower()]
            if encontrado:
                print(f"✅ {encontrado[0]}")
                print(f"   {descripcion}\n")
        
        print("=" * 60)
        print("\n💡 PRUEBA DE CONEXIÓN:")
        print("-" * 60)
        
        # Intentar una generación de prueba con el primer modelo disponible
        if modelos_generacion:
            modelo_prueba = modelos_generacion[0]
            print(f"\nProbando con: {modelo_prueba}")
            
            # Extraer solo el nombre del modelo (sin el prefijo "models/")
            nombre_corto = modelo_prueba.replace("models/", "")
            
            model = genai.GenerativeModel(nombre_corto)
            response = model.generate_content("Di hola")
            
            print(f"\n✅ PRUEBA EXITOSA!")
            print(f"Respuesta: {response.text[:100]}...")
            print(f"\n🎉 Tu API Key funciona correctamente!")
            print(f"🔧 Usa este modelo en tu código: '{nombre_corto}'")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        print("Posibles causas:")
        print("1. API Key incorrecta o inválida")
        print("2. No tienes acceso a la API de Gemini")
        print("3. Problema de conexión a internet")
        print("\nSolución:")
        print("- Verifica tu API Key en: https://makersuite.google.com/app/apikey")
        print("- Genera una nueva API Key si es necesario")
        print("- Asegúrate de tener conexión a internet")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    if API_KEY == "TU_API_KEY_AQUI":
        print("\n⚠️  ERROR: Debes configurar tu API Key primero")
        print("Edita este archivo y reemplaza 'TU_API_KEY_AQUI' con tu API Key real\n")
    else:
        verificar_modelos()