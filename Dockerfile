# Imagen base
FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de Mesa (por defecto 8521)
EXPOSE 8521

# Comando por defecto
CMD ["python", "scripts/first_mesa.py"]
