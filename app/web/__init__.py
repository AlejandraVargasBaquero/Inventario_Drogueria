"""Capa de interfaz web con Flask (ADR-001).

Ejecutar desde la raíz del proyecto con ``python -m flask --app app.web run``.
Las pantallas solo leen el formulario, llaman a la capa de datos y a las reglas, y
muestran el resultado: ninguna regla de negocio vive aquí.
"""

import os
import secrets
from pathlib import Path

from flask import Flask, g

from app.datos.repositorio import conectar, crear_esquema


def create_app(config: dict | None = None) -> Flask:
    """Crea la aplicación.

    Args:
        config: valores que reemplazan la configuración (lo usan las pruebas):
            ``SECRET_KEY``, ``RUTA_BD`` y ``HOY`` (fecha fija; si es None se usa
            la fecha del día).
    """
    _cargar_env(Path.cwd() / ".env")
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        RUTA_BD=os.environ.get("RUTA_BD", "inventario.sqlite3"),
        HOY=None,
    )
    if config:
        app.config.update(config)

    from app.web.rutas import bp

    app.register_blueprint(bp)
    app.teardown_appcontext(_cerrar_bd)
    with app.app_context():
        crear_esquema(obtener_bd())
    return app


def obtener_bd():
    """Una conexión por petición, guardada en ``g`` y cerrada al terminar."""
    from flask import current_app

    if "bd" not in g:
        g.bd = conectar(current_app.config["RUTA_BD"])
    return g.bd


def _cerrar_bd(_error=None) -> None:
    bd = g.pop("bd", None)
    if bd is not None:
        bd.close()


def _cargar_env(ruta: Path) -> None:
    """Lee ``.env`` (CLAVE=valor por línea) sin pisar variables que ya existan.

    Se hace con la librería estándar para no agregar python-dotenv.
    """
    if not ruta.is_file():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip())
