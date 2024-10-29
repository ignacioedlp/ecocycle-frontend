# Usa una imagen base oficial de Python
FROM python:3.11-alpine

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos requeridos para instalar las dependencias
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido del directorio actual al contenedor
COPY . .

# Expone el puerto en el que correrá Flask
EXPOSE 5000

# Comando para correr la aplicación
CMD ["python", "app.py"]
