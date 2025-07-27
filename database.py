# dreamscape_api/database.py
from sqlmodel import create_engine, SQLModel, Session # create_engine para la conexión, Session para interactuar
import os # Para leer variables de entorno (como la URL de la base de datos)

# Cargar la URL de la base de datos desde una variable de entorno.
# Si la variable de entorno 'DATABASE_URL' no existe, usa un archivo SQLite local 'database.db'.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# Crear el "motor" de la base de datos.
# Este motor gestiona la conexión a la base de datos.
# 'echo=True' es útil para depuración, ya que muestra las consultas SQL que se ejecutan.
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """
    Crea las tablas de la base de datos basadas en los modelos definidos en SQLModel.
    Esto solo crea tablas si no existen.
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    """
    Función de dependencia para FastAPI que proporciona una sesión de base de datos.
    Una "sesión" es como un canal de comunicación para realizar operaciones (leer, escribir) en la DB.
    'yield' permite que la sesión se use y luego se cierre automáticamente.
    """
    with Session(engine) as session: # Abre una sesión
        yield session # La cede al endpoint de FastAPI