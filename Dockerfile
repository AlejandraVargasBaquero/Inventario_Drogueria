# Imagen de la aplicación web del inventario (ADR-001: Flask + SQLite, uso local).
# Versión de Python fijada y variante slim para una imagen pequeña.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RUTA_BD=/datos/inventario.sqlite3

WORKDIR /app

# Primero solo las dependencias de ejecución (sin pytest ni ruff).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Usuario sin privilegios; la base vive en un volumen aparte.
RUN useradd --create-home --uid 1000 drogueria \
    && mkdir /datos && chown drogueria /datos
USER drogueria
VOLUME ["/datos"]

EXPOSE 5000

# La SECRET_KEY no va en la imagen: se pasa al ejecutar (-e o --env-file).
# Servidor de Flask sin modo debug: la aplicación es local y de un solo usuario
# (ADR-001). Si se publicara en internet habría que cambiarlo por gunicorn.
CMD ["python", "-m", "flask", "--app", "app.web", "run", "--host", "0.0.0.0", "--port", "5000"]
