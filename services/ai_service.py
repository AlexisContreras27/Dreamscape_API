# dreamscape_api/services/ai_service.py

import os
import google.generativeai as genai
import asyncio # Necesitamos esto para ejecutar la llamada síncrona a Gemini en un hilo separado

# --- Configuración de Gemini (asegúrate de que GEMINI_API_KEY esté en el entorno) ---
def get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no está configurada en las variables de entorno.")
    genai.configure(api_key=api_key)
    # Puedes elegir 'gemini-pro' para texto
    return genai.GenerativeModel('gemini-1.5-flash')

# --- Función que main.py espera para "analizar" (puede ser simple o una simulación) ---
async def analyze_dream_description(dream_description: str):
    """
    Función que simula un análisis de la descripción del sueño.
    Por ahora, no usa IA para el análisis profundo, solo devuelve un mensaje.
    Podrías expandir esto con Gemini si necesitas un análisis más complejo.
    """
    print(f"DEBUG (AI Service): Analizando descripción del sueño: '{dream_description}'")
    # Este es el resultado que main.py espera para 'analysis_result'
    return {"summary": f"Análisis básico: El sueño trata sobre {dream_description[:50]}..."}

# --- Función que main.py espera para "generar contenido" con Gemini ---
async def generate_content_from_dream(dream_description: str, preferred_output_type: str):
    """
    Genera contenido creativo (historia, poema, etc.) utilizando Google Gemini.
    """
    try:
        model = get_gemini_model() # Obtiene el modelo de Gemini
        
        # Construye el prompt para Gemini. ¡Sé lo más específico posible!
        prompt = f"""
        Basado en la siguiente descripción de un sueño, genera un contenido creativo.
        El formato o tipo de salida preferido es: {preferred_output_type}.

        Descripción del Sueño:
        "{dream_description}"

        Por favor, genera el contenido y asegúrate de que sea coherente con la descripción y el tipo solicitado.
        """

        print(f"DEBUG (AI Service): Enviando prompt a Gemini para generar {preferred_output_type} para '{dream_description[:50]}...'")

        # Realiza la llamada asíncrona a la API de Gemini
        # asyncio.to_thread permite llamar a funciones síncronas (como model.generate_content)
        # desde una función asíncrona sin bloquear el bucle de eventos.
        response = await asyncio.to_thread(model.generate_content, prompt)
        
        # Extrae el texto generado de la respuesta de Gemini
        generated_text = response.text
        print(f"DEBUG (AI Service): Contenido generado por Gemini (primeras 100 chars): {generated_text[:100]}...")

        return {
            "preview": generated_text, # Esto mapea a 'generated_content_preview' en main.py
            "url": None # Por ahora, Gemini solo devuelve texto, no una URL de contenido.
        }

    except ValueError as e:
        # Error si la clave API no está configurada
        print(f"ERROR (AI Service): Configuración de API de Gemini faltante: {e}")
        return {
            "preview": f"Error de configuración de IA: {e}. Contenido no generado.",
            "url": None
        }
    except Exception as e:
        # Cualquier otro error durante la llamada a Gemini
        print(f"ERROR (AI Service): Fallo en la llamada a la API de Gemini: {e}")
        return {
            "preview": f"Error al generar contenido con IA: {e}. Por favor, revise los logs del servidor.",
            "url": None
        }