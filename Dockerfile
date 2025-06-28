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
# Cloud Run setea la variable de entorno PORT, usamos $PORT o 8080 como fallback
# Agregamos --log-level info para mejor debugging
CMD ["sh", "-c", "uvicorn app.app:app --host 0.0.0.0 --port ${PORT:-8080} --log-level info"]