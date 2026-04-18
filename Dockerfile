# Usamos una imagen de Python ligera
FROM python:3.10-slim

# Instalamos dependencias del sistema necesarias para Flet
RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    libgstvga \
    libgstreamer1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos los archivos de requisitos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el contenido del proyecto
COPY . .

# Exponemos el puerto que usará Flet
EXPOSE 8080

# Comando para ejecutar la aplicación. 
# IMPORTANTE: El nombre del archivo debe coincidir con el tuyo
CMD ["python", "aplicación.py"]
