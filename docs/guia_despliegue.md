# Guía de despliegue

La aplicación es local: se instala en el computador de la droguería (ADR-001). Hay dos formas de hacerlo.

## Opción A: Python en el computador

```bash
git clone https://github.com/AlejandraVargasBaquero/Inventario_Drogueria.git
cd Inventario_Drogueria
python -m venv .venv
.venv\Scripts\activate                  # Windows
python -m pip install -r requirements.txt
copy .env.example .env                  # y poner una SECRET_KEY propia
python -m flask --app app.web run
```

Abrir http://127.0.0.1:5000. La base queda en `inventario.sqlite3`, en la misma carpeta.

## Opción B: contenedor Docker

```bash
docker build -t inventario-drogueria .
docker volume create inventario-datos
docker run -d --name inventario -p 127.0.0.1:5000:5000 \
  --env-file .env -v inventario-datos:/datos inventario-drogueria
```

- `-p 127.0.0.1:5000:5000` publica el puerto solo en el mismo computador, no en la red del barrio.
- La base vive en el volumen `inventario-datos`: si se borra el contenedor, los datos se conservan.
- La `SECRET_KEY` sale de `.env` y nunca entra en la imagen.

## Variables de entorno

| Variable | Para qué | Valor por defecto |
|---|---|---|
| `SECRET_KEY` | Firma la sesión y el token de los formularios | Si falta, se genera una aleatoria en cada arranque y las sesiones abiertas se pierden |
| `RUTA_BD` | Archivo de la base SQLite | `inventario.sqlite3` (en Docker: `/datos/inventario.sqlite3`) |

## Antes de entregar una versión

1. El pipeline de GitHub Actions está en verde (ruff, 122 pruebas, cobertura ≥ 90 % en reglas y datos, imagen construida).
2. `pip-audit -r requirements.txt` no muestra vulnerabilidades.
3. Copia de seguridad de la base antes de actualizar (ver [plan de operación](plan_operacion.md)).
