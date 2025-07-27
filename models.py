# dreamscape_api/models.py
from typing import Optional # 'Optional' significa que un campo puede tener un valor o ser None (vacío)
from sqlmodel import Field, SQLModel # Importamos Field (para definir campos) y SQLModel (la base para nuestros modelos)

# Base para el modelo de Sueño. Contiene campos comunes para la entrada y salida.
class DreamBase(SQLModel):
    user_id: str # El ID del usuario que envía el sueño (será un string)
    dream_description: str # La descripción del sueño (también un string)
    preferred_output_type: str = Field(default="narrative") # Tipo de contenido deseado (narrativa, ilustración, 3d_scenario).
                                                            # "default='narrative'" significa que si no se especifica, será "narrative".

# Modelo completo para la tabla 'dreams' en la base de datos.
# Hereda de DreamBase para incluir sus campos.
class Dream(DreamBase, table=True): # 'table=True' le dice a SQLModel que este modelo corresponde a una tabla de BD.
    id: Optional[int] = Field(default=None, primary_key=True) # ID único del sueño. 'Optional[int]' porque la DB lo generará.
                                                            # 'primary_key=True' lo marca como clave principal.
    status: str = Field(default="pending") # Estado del procesamiento del sueño (ej., "pending", "processing", "completed", "failed").
    generated_content_url: Optional[str] = None # URL del contenido generado (ej., enlace a la narrativa/imagen). Puede ser nulo al principio.
    generated_content_preview: Optional[str] = None # Pequeño fragmento o descripción del contenido generado.

# Modelo de entrada para la creación de un sueño.
# Hereda solo de DreamBase porque no necesitamos el 'id', 'status', 'url' o 'preview' al crear uno.
class DreamCreate(DreamBase):
    pass # 'pass' es un marcador de posición, significa que no hay campos adicionales aquí.

# Modelo de salida para la lectura de un sueño (lo que la API devolverá).
# Hereda de DreamBase y Dream para incluir todos los campos relevantes para mostrar al usuario.
class DreamRead(DreamBase):
    id: int # Aquí el ID es obligatorio porque estamos leyendo un sueño que ya existe.
    status: str
    generated_content_url: Optional[str] = None
    generated_content_preview: Optional[str] = None