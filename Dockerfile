# 1. Imagen base: Usamos Python 3.10 versión ligera (slim)
FROM python:3.10-slim

# 2. Directorio de trabajo: Donde vivirá la app dentro de Docker
WORKDIR /app

# 3. Copiamos el archivo de librerías para instalarlas
COPY requirements.txt .

# 4. Instalamos las dependencias (Flask, influxdb-client, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos todo el contenido de tu carpeta actual al contenedor
COPY . .

# 6. Informamos que la app usa el puerto 5000
EXPOSE 5000

# 7. Comando para arrancar. IMPORTANTE: Usamos run.py que es tu archivo principal
CMD ["python", "run.py"]