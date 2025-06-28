# Usar una imagen base oficial de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar el archivo de requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación (excluyendo archivos sensibles via .dockerignore)
COPY . .

# Exponer el puerto en el que la app se ejecuta
EXPOSE 8080

# Comando para correr la aplicación usando uvicorn
# Primero probamos con la app minimal, luego con la app completa
CMD ["sh", "-c", "python simple_startup.py"]