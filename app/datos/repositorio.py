"""Repositorio SQLite de medicamentos y lotes (capa de datos del ADR-001).

Reglas de esta capa:

- Todas las consultas usan parámetros ``?``; nunca se arma SQL con texto del usuario
  (pendiente de inyección de la semana 6).
- Antes de guardar se aplican las mismas reglas de ``app.reglas``: si un dato es
  inválido no se guarda nada (HU-05, escenario 2).
- Las fechas se guardan como texto ISO (AAAA-MM-DD) y se devuelven como ``date``
  (pendiente de fechas de la semana 6).
- Solo usa ``sqlite3`` de la librería estándar.
"""

import sqlite3
from datetime import date, datetime

from app.reglas.existencias import validar_cantidad, validar_minimo
from app.reglas.modelos import Lote, Medicamento

MENSAJE_NOMBRE_OBLIGATORIO = "El nombre del medicamento es obligatorio"
MENSAJE_LOTE_OBLIGATORIO = "El número de lote es obligatorio"
MENSAJE_MEDICAMENTO_NO_EXISTE = "El medicamento con id {id} no existe"
MENSAJE_LOTE_REPETIDO = "El lote {lote} ya está registrado para ese medicamento"
MENSAJE_FECHA_INVALIDA = "La fecha de vencimiento debe ser una fecha (día, mes y año)"
MENSAJE_NUMERO_MUY_GRANDE = "El número es demasiado grande para guardarlo"
MENSAJE_LOTE_NO_EXISTE = "El lote {lote} no existe para ese medicamento"

# Un INTEGER de SQLite ocupa 8 bytes con signo (D-01).
MAYOR_ENTERO_SQLITE = 2**63 - 1

ESQUEMA = """
CREATE TABLE IF NOT EXISTS medicamento (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    stock_minimo INTEGER NOT NULL CHECK (stock_minimo >= 0)
);

CREATE TABLE IF NOT EXISTS lote (
    id INTEGER PRIMARY KEY,
    medicamento_id INTEGER NOT NULL REFERENCES medicamento (id),
    numero_lote TEXT NOT NULL,
    fecha_vencimiento TEXT NOT NULL,
    cantidad_actual INTEGER NOT NULL CHECK (cantidad_actual >= 0),
    UNIQUE (medicamento_id, numero_lote)
);
"""


def conectar(ruta: str) -> sqlite3.Connection:
    """Abre la base de datos con las llaves foráneas activadas.

    Args:
        ruta: archivo de la base (por ejemplo ``inventario.sqlite3``) o
            ``":memory:"`` para las pruebas.
    """
    con = sqlite3.connect(ruta)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def crear_esquema(con: sqlite3.Connection) -> None:
    """Crea las tablas si no existen. No borra datos que ya estén guardados."""
    con.executescript(ESQUEMA)


def guardar_medicamento(con: sqlite3.Connection, nombre: str, stock_minimo: int) -> int:
    """Registra un medicamento y devuelve su id.

    Raises:
        ValueError: si el nombre está vacío o el mínimo no es un entero >= 0. En
            ese caso no se guarda nada.
    """
    nombre_limpio = _texto_obligatorio(nombre, MENSAJE_NOMBRE_OBLIGATORIO)
    validar_minimo(stock_minimo)
    _exigir_rango(stock_minimo)
    with con:
        cursor = con.execute(
            "INSERT INTO medicamento (nombre, stock_minimo) VALUES (?, ?)",
            (nombre_limpio, stock_minimo),
        )
    return cursor.lastrowid


def cambiar_minimo(
    con: sqlite3.Connection, medicamento_id: int, nuevo_minimo: int
) -> None:
    """Cambia el mínimo de un medicamento (HU-05, escenario 2).

    Raises:
        ValueError: si el mínimo no es válido (no se guarda) o el medicamento no
            existe.
    """
    validar_minimo(nuevo_minimo)
    _exigir_rango(nuevo_minimo)
    _exigir_medicamento(con, medicamento_id)
    with con:
        con.execute(
            "UPDATE medicamento SET stock_minimo = ? WHERE id = ?",
            (nuevo_minimo, medicamento_id),
        )


def guardar_lote(
    con: sqlite3.Connection,
    medicamento_id: int,
    numero_lote: str,
    fecha_vencimiento: date,
    cantidad: int,
) -> None:
    """Registra un lote de un medicamento que ya existe.

    Raises:
        ValueError: si el número de lote está vacío, la fecha no es ``date``, la
            cantidad no es un entero >= 0, el medicamento no existe o el lote ya
            está registrado para ese medicamento. En esos casos no se guarda nada.
    """
    numero_limpio = _texto_obligatorio(numero_lote, MENSAJE_LOTE_OBLIGATORIO)
    if not _es_fecha(fecha_vencimiento):
        raise ValueError(MENSAJE_FECHA_INVALIDA)
    validar_cantidad(Lote(medicamento_id, numero_limpio, fecha_vencimiento, cantidad))
    _exigir_rango(cantidad)
    _exigir_medicamento(con, medicamento_id)
    fila = (medicamento_id, numero_limpio, fecha_vencimiento.isoformat(), cantidad)
    try:
        with con:
            con.execute(
                "INSERT INTO lote (medicamento_id, numero_lote, fecha_vencimiento,"
                " cantidad_actual) VALUES (?, ?, ?, ?)",
                fila,
            )
    except sqlite3.IntegrityError as error:
        raise ValueError(MENSAJE_LOTE_REPETIDO.format(lote=numero_limpio)) from error


def cambiar_cantidad_lote(
    con: sqlite3.Connection, medicamento_id: int, numero_lote: str, nueva_cantidad: int
) -> None:
    """Cambia las cajas de un lote (por ejemplo, después de vender o contar).

    Raises:
        ValueError: si la cantidad no es un entero >= 0 o el lote no existe para
            ese medicamento. En esos casos no se guarda nada.
    """
    validar_cantidad(Lote(medicamento_id, numero_lote, date.min, nueva_cantidad))
    _exigir_rango(nueva_cantidad)
    _exigir_lote(con, medicamento_id, numero_lote)
    with con:
        con.execute(
            "UPDATE lote SET cantidad_actual = ?"
            " WHERE medicamento_id = ? AND numero_lote = ?",
            (nueva_cantidad, medicamento_id, numero_lote),
        )


def eliminar_lote(
    con: sqlite3.Connection, medicamento_id: int, numero_lote: str
) -> None:
    """Elimina un lote de un medicamento.

    Raises:
        ValueError: si el lote no existe para ese medicamento.
    """
    _exigir_lote(con, medicamento_id, numero_lote)
    with con:
        con.execute(
            "DELETE FROM lote WHERE medicamento_id = ? AND numero_lote = ?",
            (medicamento_id, numero_lote),
        )


def eliminar_medicamento(con: sqlite3.Connection, medicamento_id: int) -> int:
    """Elimina un medicamento y todos sus lotes en una sola transacción.

    Returns:
        Cuántos lotes se eliminaron con él.

    Raises:
        ValueError: si el medicamento no existe. No se borra nada.
    """
    _exigir_medicamento(con, medicamento_id)
    with con:
        lotes = con.execute(
            "DELETE FROM lote WHERE medicamento_id = ?", (medicamento_id,)
        ).rowcount
        con.execute("DELETE FROM medicamento WHERE id = ?", (medicamento_id,))
    return lotes


def listar_medicamentos(con: sqlite3.Connection) -> list[Medicamento]:
    """Devuelve los medicamentos en el orden en que se registraron."""
    filas = con.execute(
        "SELECT id, nombre, stock_minimo FROM medicamento ORDER BY id"
    ).fetchall()
    return [Medicamento(*fila) for fila in filas]


def listar_lotes(con: sqlite3.Connection) -> list[Lote]:
    """Devuelve todos los lotes, con la fecha de vencimiento convertida a ``date``."""
    filas = con.execute(
        "SELECT medicamento_id, numero_lote, fecha_vencimiento, cantidad_actual"
        " FROM lote ORDER BY id"
    ).fetchall()
    return [
        Lote(medicamento_id, numero, date.fromisoformat(fecha), cantidad)
        for medicamento_id, numero, fecha, cantidad in filas
    ]


def _texto_obligatorio(valor: object, mensaje: str) -> str:
    """Devuelve el texto sin espacios a los lados o lanza ValueError si está vacío."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(mensaje)
    return valor.strip()


def _es_fecha(valor: object) -> bool:
    """``datetime`` es subclase de ``date``, así que se excluye aparte."""
    return isinstance(valor, date) and not isinstance(valor, datetime)


def _exigir_rango(numero: int) -> None:
    """D-01: un entero que no cabe en SQLite lanzaba OverflowError (error 500)."""
    if abs(numero) > MAYOR_ENTERO_SQLITE:
        raise ValueError(MENSAJE_NUMERO_MUY_GRANDE)


def _exigir_medicamento(con: sqlite3.Connection, medicamento_id: int) -> None:
    _exigir_rango(medicamento_id)
    fila = con.execute(
        "SELECT 1 FROM medicamento WHERE id = ?", (medicamento_id,)
    ).fetchone()
    if fila is None:
        raise ValueError(MENSAJE_MEDICAMENTO_NO_EXISTE.format(id=medicamento_id))


def _exigir_lote(
    con: sqlite3.Connection, medicamento_id: int, numero_lote: str
) -> None:
    _exigir_rango(medicamento_id)
    fila = con.execute(
        "SELECT 1 FROM lote WHERE medicamento_id = ? AND numero_lote = ?",
        (medicamento_id, numero_lote),
    ).fetchone()
    if fila is None:
        raise ValueError(MENSAJE_LOTE_NO_EXISTE.format(lote=numero_lote))
