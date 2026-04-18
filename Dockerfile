FROM python:3.10-slim

# Instalamos dependencias del sistema
RUN apt-get update && apt-get install -y \
    libgtk-3-0 \
    libgstreamer1.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos e instalamos librerías
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponemos el puerto
EXPOSE 8080

# Ejecutamos la app. Asegúrate que el nombre sea aplicación.py
CMD ["python", "aplicación.py"]
