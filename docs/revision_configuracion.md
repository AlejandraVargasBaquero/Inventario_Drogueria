# Revisión del pipeline y del Dockerfile

Proyecto: Sistema de inventario de la Droguería San Rafael
Estudiante: Alejandra Vargas Baquero
Fecha: 2026-11-27

## 1. Cómo se generaron

**Herramienta de IA:** Claude (chat con acceso al repositorio).
**Prompt:** ver la [entrada 19 de la bitácora](../bitacora_ia.md#entrada-19). Lo pedí con el contexto del proyecto (ADR-001, `requirements.txt`, rama `main`, Python 3.10 a 3.13) y la lista de revisión de la semana 9. No usé un prompt simple como en la práctica de clase.

## 2. Hallazgos

Revisé los dos archivos con la lista de la semana 9 (pipeline: eventos, permisos, secretos, versiones, dependencias y fallos; Dockerfile: imagen base, secretos, usuario, `.dockerignore`, versiones y modo desarrollo). Los errores de la práctica de clase (Tienda La Esquina) sirvieron de lista de chequeo.

| Archivo y línea | Problema | Riesgo | Corrección |
|---|---|---|---|
| requirements.txt | Tenía `pytest` y `ruff` junto a Flask | La imagen instalaría herramientas de desarrollo que no usa: más grande y con más paquetes que auditar | `requirements.txt` solo con Flask; `requirements-dev.txt` con pytest, pytest-cov y ruff (commit `8896e0f`) |
| (faltaba) .dockerignore | No existía | `COPY` podría meter `.env`, `inventario.sqlite3` o `.git` en la imagen | Se creó `.dockerignore`. Además el Dockerfile copia solo `requirements.txt` y `app/` (commit `db7bc1f`) |
| Dockerfile:7 y 21 | La base SQLite quedaría dentro del contenedor | Al borrar el contenedor se pierden el inventario y los lotes | `RUTA_BD=/datos/inventario.sqlite3` y `VOLUME ["/datos"]` |
| Dockerfile:28 | Usa el servidor de desarrollo de Flask (`flask run`) | No es un servidor de producción | **Aceptado con justificación:** ADR-001 dice aplicación local de un solo usuario. Sin `--debug` ni `--reload`. Queda en Pendientes cambiarlo a gunicorn si se publica |
| ci.yml:19 | Las versiones de Python deben ir entre comillas | Sin comillas, YAML lee `3.10` como el número 3.1 (error de la práctica de clase) | `["3.10", "3.13"]` |
| ci.yml:34 | La cobertura no hacía fallar el pipeline | La cobertura podría bajar sin que nadie lo note | `--cov-fail-under=90`, solo sobre `app.reglas` y `app.datos` (la lógica del negocio) |

Revisé también lo que en la práctica estaba mal y aquí está bien: `permissions: contents: read` (no `write-all`), no hay claves en el YAML ni en la imagen (la `SECRET_KEY` se pasa con `-e` al ejecutar), la imagen es `python:3.13-slim` y no `latest`, corre con el usuario `drogueria` (no root) y ningún paso tiene `continue-on-error`.

## 3. Lo que encontraron las herramientas

| Herramienta | Avisos | ¿Coinciden con mis hallazgos? | ¿Qué no encontró? |
|---|---|---|---|
| actionlint | [COMPLETAR después de ejecutarlo] | | |
| hadolint | [COMPLETAR después de ejecutarlo] | | |

Comandos: `pip install actionlint-py hadolint-py`, luego `actionlint .github/workflows/ci.yml` y `hadolint Dockerfile`.

## 4. Verificación

- [ ] El pipeline corregido se ejecutó en GitHub y salió en verde: [enlace a la ejecución]
- [ ] Hice fallar una prueba a propósito y el pipeline salió en rojo.
- [ ] La imagen se construye en el pipeline (job `imagen`, que también hace un `curl` a la pantalla «Por pedir»).
- [x] No hay claves en `ci.yml`, en el `Dockerfile` ni en el historial de Git.
- [x] En local: `python -m pytest`: 122 passed; `ruff check --select E,F,B,S .`: All checks passed!; el YAML se lee sin errores.
