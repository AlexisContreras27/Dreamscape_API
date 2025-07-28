# dreamscape_api/main.py
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks # Importamos las clases principales de FastAPI
from sqlmodel import Session, select # Importamos Session para la DB y select para consultas
from typing import List # Para indicar que una función devuelve una lista de algo

from .database import create_db_and_tables, get_session # Importamos las funciones de DB de nuestro archivo database.py
from .models import Dream, DreamCreate, DreamRead # Importamos nuestros modelos de datos
from .services import ai_service # Importa tu servicio de IA
import os
from dotenv import load_dotenv # Para cargar variables de entorno del archivo .env

# Carga las variables de entorno desde el archivo .env
# ¡Esto debe ser lo primero en tu archivo principal para que las variables estén disponibles!
load_dotenv()

# Inicializa la aplicación FastAPI
app = FastAPI(
    title="DreamScape API", # Título para la documentación de Swagger UI
    description="API para generar narrativas y contenido visual/3D basado en descripciones de sueños.",
    version="0.1.0" # Versión de tu API
)

# --- Eventos de inicio y apagado ---
# @app.on_event("startup") es un decorador que ejecuta una función cuando la API se inicia.
@app.on_event("startup")
def on_startup():
    """
    Crea las tablas de la base de datos al iniciar la aplicación.
    Esto asegura que la tabla 'dreams' exista antes de que intentemos usarla.
    """
    create_db_and_tables()
    print("Base de datos y tablas creadas (o ya existentes).")

# --- Funcionalidad en segundo plano para procesar sueños ---
# Esta es una función asíncrona que se ejecutará sin bloquear la respuesta de la API.
async def process_dream_in_background(dream_id: int, db_session: Session):
    """
    Tarea de segundo plano para analizar y generar contenido del sueño.
    """
    print(f"DEBUG: Iniciando procesamiento de sueño ID: {dream_id}")
    # Es crucial abrir una nueva sesión para tareas de segundo plano,
    # ya que la sesión principal se cierra al enviar la respuesta al cliente.
    with Session(db_session.bind) as session: # 'db_session.bind' se refiere al 'engine' de la DB
        dream = session.get(Dream, dream_id) # Obtiene el sueño por su ID
        if not dream:
            print(f"ERROR: Sueño ID {dream_id} no encontrado para procesamiento.")
            return

        try:
            # 1. Análisis de la descripción del sueño usando nuestro servicio de IA simulado
            analysis_result = await ai_service.analyze_dream_description(dream.dream_description)
            print(f"DEBUG: Análisis completado para sueño ID {dream_id}: {analysis_result}")

            # 2. Generación de contenido usando nuestro servicio de IA simulado
            generation_result = await ai_service.generate_content_from_dream(
                dream.dream_description, dream.preferred_output_type
            )
            print(f"DEBUG: Generación completada para sueño ID {dream_id}: {generation_result}")

            # 3. Actualizar el sueño en la base de datos con los resultados y cambiar el estado
            dream.status = "completed"
            dream.generated_content_url = generation_result["url"]
            dream.generated_content_preview = generation_result["preview"]
            session.add(dream) # Agrega el objeto modificado a la sesión
            session.commit() # Guarda los cambios en la base de datos
            session.refresh(dream) # Recarga el objeto para obtener los últimos datos de la DB
            print(f"DEBUG: Sueño ID {dream_id} actualizado a 'completed'.")

        except Exception as e:
            # Si ocurre un error, marcamos el sueño como fallido
            print(f"ERROR: Error procesando sueño ID {dream_id}: {e}")
            dream.status = "failed"
            session.add(dream)
            session.commit()
            session.refresh(dream)

# --- Endpoints de la API ---

# Endpoint para crear un nuevo sueño (POST /dreams/)
@app.post("/dreams/", response_model=DreamRead, status_code=201) # Decorador para definir el endpoint
async def create_dream(
    dream_create: DreamCreate, # FastAPI validará la entrada contra nuestro modelo DreamCreate
    background_tasks: BackgroundTasks, # Inyecta la funcionalidad para ejecutar tareas en segundo plano
    db_session: Session = Depends(get_session) # Inyecta una sesión de DB usando nuestra dependencia
):
    """
    Envía una descripción de sueño para análisis y generación de contenido.
    El procesamiento de IA se realiza en segundo plano, la API responde rápidamente.
    """
    # Crea una instancia de nuestro modelo de DB a partir de los datos de entrada
    db_dream = Dream.model_validate(dream_create)
    db_session.add(db_dream) # Agrega el nuevo sueño a la sesión de la base de datos
    db_session.commit() # Guarda el sueño en la base de datos
    db_session.refresh(db_dream) # Recarga el objeto para obtener el ID generado por la DB

    # Inicia la tarea de procesamiento de IA en segundo plano.
    # Esto permite que la API responda inmediatamente mientras la IA trabaja.
    background_tasks.add_task(process_dream_in_background, db_dream.id, db_session)

    return db_dream # Devuelve el sueño recién creado (con estado 'pending' inicialmente)

# Endpoint para leer un sueño específico por su ID (GET /dreams/{dream_id})
@app.get("/dreams/{dream_id}", response_model=DreamRead)
async def read_dream(dream_id: int, db_session: Session = Depends(get_session)):
    """
    Obtiene los detalles de un sueño específico por su ID.
    """
    dream = db_session.get(Dream, dream_id) # Busca el sueño en la DB por su ID
    if not dream:
        # Si el sueño no se encuentra, devuelve un error 404
        raise HTTPException(status_code=404, detail="Sueño no encontrado")
    return dream # Devuelve el sueño encontrado

# Endpoint para obtener una lista de todos los sueños (GET /dreams/)
@app.get("/dreams/", response_model=List[DreamRead]) # response_model=List[DreamRead] indica que devuelve una lista
async def read_dreams(
    offset: int = 0, # Parámetro de paginación: cuántos registros saltar
    limit: int = 10, # Parámetro de paginación: cuántos registros devolver (por defecto 10)
    db_session: Session = Depends(get_session)
):
    """
    Obtiene una lista de todos los sueños, con opciones de paginación.
    """
    # Ejecuta una consulta para seleccionar sueños, aplicando offset y limit
    dreams = db_session.exec(select(Dream).offset(offset).limit(limit)).all()
    return dreams # Devuelve la lista de sueños

# --- EJEMPLO DE AUTENTICACIÓN (DESCOMENTAR Y ADAPTAR PARA PRODUCCIÓN) ---
# Para la autenticación, usarías algo como:
# from fastapi.security import APIKeyHeader
# api_key_header = APIKeyHeader(name="X-API-Key") # Define que esperamos una clave API en el encabezado 'X-API-Key'

# async def get_api_key(api_key: str = Depends(api_key_header)):
#     """
#     Función de dependencia para validar la clave API.
#     Compara la clave proporcionada con una clave segura cargada desde .env.
#     """
#     if api_key == os.getenv("YOUR_API_KEY"): # Compara con una clave guardada en .env
#         return api_key # Si es válida, retorna la clave
#     raise HTTPException(status_code=403, detail="Clave API inválida") # Si no es válida, devuelve un error 403

# # Y luego lo usarías en tus endpoints para protegerlos:
# # @app.post("/dreams/", response_model=DreamRead, status_code=201, dependencies=[Depends(get_api_key)])
# # ...
# # Esto significa que antes de ejecutar 'create_dream', se ejecutará 'get_api_key'
# # y si falla, la solicitud será rechazada.