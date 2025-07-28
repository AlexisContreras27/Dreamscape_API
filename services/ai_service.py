# services/ai_service.py

import os
import google.generativeai as genai
import asyncio # Necesitas esto si tu función de IA va a ser async

# Configura Gemini con tu clave API
# Esta configuración se hace una vez al inicio del programa.
# Es importante que GEMINI_API_KEY esté disponible en el entorno.
# Esto puede hacerse mejor en un archivo de configuración o al inicio de la app.

# Una mejor práctica sería inicializar el modelo una vez y pasarlo
# o usar un singleton, pero para empezar, esta es una forma simple.

def get_gemini_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY no está configurada en las variables de entorno.")
    genai.configure(api_key=api_key)
    # Elige el modelo apropiado. 'gemini-pro' es un buen punto de partida para texto.
    return genai.GenerativeModel('gemini-pro')

async def generate_dream_content_with_gemini(dream_description: str, preferred_output_type: str):
    """
    Genera contenido con Google Gemini basado en la descripción del sueño
    y el tipo de salida preferido.
    """
    try:
        model = get_gemini_model() # Obtiene o inicializa el modelo Gemini

        # Construye el prompt para Gemini
        # Sé lo más específico posible con el prompt para mejores resultados
        prompt = f"""
        Basado en la siguiente descripción de un sueño, genera un contenido creativo
        con el formato o tipo de salida solicitado.

        Descripción del Sueño:
        {dream_description}

        Tipo de Salida Preferido: {preferred_output_type}
        """

        # Realiza la llamada asíncrona a la API de Gemini
        # Usamos await porque generate_content puede ser una operación que toma tiempo
        response = await asyncio.to_thread(model.generate_content, prompt) # Para hacer síncrona la llamada dentro de una función async
        # O si el método de Gemini es directamente async:
        # response = await model.generate_content_async(prompt)

        # Extrae el texto generado de la respuesta
        generated_text = response.text

        return {
            "generated_content_preview": generated_text,
            "generated_content_url": None # Gemini no genera URLs de contenido directamente, tendrías que subirlo a un bucket S3/GCS. Por ahora, dejarlo en None.
        }
    except ValueError as e:
        # Si la clave API no está configurada
        return {
            "generated_content_preview": f"Error de configuración: {e}. No se pudo generar el contenido.",
            "generated_content_url": None
        }
    except Exception as e:
        # Captura otros errores (ej., problemas con la API de Gemini)
        return {
            "generated_content_preview": f"Error al generar contenido con IA: {e}",
            "generated_content_url": None
        }

# Asegúrate de que tu main.py o tus routers llamen a esta función
# en lugar de la versión placeholder.
# Por ejemplo, en tu endpoint POST /dreams/
# from dreamscape_api.services.ai_service import generate_dream_content_with_gemini
# ...
# dream.generated_content_preview = (await generate_dream_content_with_gemini(
#    dream.dream_description, dream.preferred_output_type
# ))["generated_content_preview"]