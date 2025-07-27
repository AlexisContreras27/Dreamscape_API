# dreamscape_api/Dockerfile

FROM python:3.10-slim-buster

# Configura el directorio de trabajo donde se copiará el contenido de tu proyecto local.
# Aquí es donde Docker esperará encontrar el "contexto" de tu aplicación.
WORKDIR /app

# Copia solo requirements.txt primero para aprovechar el cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido de tu directorio LOCAL actual (dreamscape_api/)
# A una SUB-CARPETA dentro del contenedor llamada 'dreamscape_api'.
# Esto es CRÍTICO para que Python lo reconozca como un paquete.
COPY . /app/dreamscape_api

# Añade /app al PATH de Python para que pueda encontrar el paquete 'dreamscape_api'
ENV PYTHONPATH=/app

EXPOSE 8000

# El comando de inicio ahora apunta al PAQUETE 'dreamscape_api'
# Esto le dice a Uvicorn que cargue la aplicación 'app' del módulo 'main'
# que se encuentra dentro del PAQUETE 'dreamscape_api'.
CMD ["uvicorn", "dreamscape_api.main:app", "--host", "0.0.0.0", "--port", "8000"]