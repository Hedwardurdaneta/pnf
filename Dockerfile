# Usamos una imagen de Python ligera
FROM python:3.10-slim

# Instalamos las dependencias esenciales del sistema
RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    libgstreamer1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos e instalamos las librerías de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto de los archivos
COPY . .

# Exponemos el puerto para la web
EXPOSE 8080

# Comando para iniciar la aplicación
# Asegúrate de que el nombre coincida con tu archivo .py
CMD ["python", "aplicación.py"]
