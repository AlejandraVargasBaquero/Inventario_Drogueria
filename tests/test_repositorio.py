"""Pruebas de la capa de datos con SQLite (backend).

Cada prueba usa una base de datos nueva en memoria, así que no dependen unas de otras
ni del archivo inventario.sqlite3. Hoy = 24/10/2026, como en los requisitos.
"""

import re
from datetime import date, datetime

import pytest

from app.datos.repositorio import (
    cambiar_minimo,
    conectar,
    crear_esquema,
    guardar_lote,
    guardar_medicamento,
    listar_lotes,
    listar_medicamentos,
)
from app.reglas.modelos import Lote, Medicamento
from app.reglas.pedidos import productos_por_pedir

HOY = date(2026, 10, 24)


@pytest.fixture
def con():
    conexion = conectar(":memory:")
    crear_esquema(conexion)
    yield conexion
    conexion.close()


def mensaje_exacto(texto):
    return f"^{re.escape(texto)}$"


# ---------- Medicamentos ----------

def test_guarda_y_lee_un_medicamento(con):
    id_nuevo = guardar_medicamento(con, "Acetaminofén 500 mg", 10)

    esperado = [Medicamento(id_nuevo, "Acetaminofén 500 mg", 10)]
    assert listar_medicamentos(con) == esperado


def test_lista_los_medicamentos_en_el_orden_en_que_se_registraron(con):
    guardar_medicamento(con, "Acetaminofén 500 mg", 10)
    guardar_medicamento(con, "Amoxicilina 500 mg", 10)

    nombres = [m.nombre for m in listar_medicamentos(con)]

    assert nombres == ["Acetaminofén 500 mg", "Amoxicilina 500 mg"]


def test_quita_espacios_al_principio_y_al_final_del_nombre(con):
    guardar_medicamento(con, "  Loratadina 10 mg  ", 5)

    assert listar_medicamentos(con)[0].nombre == "Loratadina 10 mg"


@pytest.mark.parametrize("nombre", ["", "   "])  # vacío y solo espacios (A-6)
def test_nombre_vacio_no_se_guarda(con, nombre):
    with pytest.raises(
        ValueError, match=mensaje_exacto("El nombre del medicamento es obligatorio")
    ):
        guardar_medicamento(con, nombre, 5)

    assert listar_medicamentos(con) == []


def test_minimo_negativo_no_se_guarda(con):
    """HU-05, escenario 2: con −2 el sistema no lo guarda y muestra el mensaje."""
    with pytest.raises(
        ValueError,
        match=mensaje_exacto("El mínimo debe ser un número igual o mayor que cero"),
    ):
        guardar_medicamento(con, "Ibuprofeno 400 mg", -2)

    assert listar_medicamentos(con) == []


def test_cambiar_minimo_guarda_el_nuevo_valor(con):
    id_ibuprofeno = guardar_medicamento(con, "Ibuprofeno 400 mg", 5)

    cambiar_minimo(con, id_ibuprofeno, 8)

    assert listar_medicamentos(con)[0].stock_minimo == 8


def test_cambiar_minimo_a_negativo_no_lo_guarda(con):
    """HU-05, escenario 2, al configurar el mínimo de un medicamento que ya existe."""
    id_ibuprofeno = guardar_medicamento(con, "Ibuprofeno 400 mg", 5)

    with pytest.raises(
        ValueError,
        match=mensaje_exacto("El mínimo debe ser un número igual o mayor que cero"),
    ):
        cambiar_minimo(con, id_ibuprofeno, -2)

    assert listar_medicamentos(con)[0].stock_minimo == 5


def test_cambiar_minimo_de_medicamento_que_no_existe_lanza_error(con):
    with pytest.raises(
        ValueError, match=mensaje_exacto("El medicamento con id 99 no existe")
    ):
        cambiar_minimo(con, 99, 3)


# ---------- Lotes ----------

def test_guarda_y_lee_un_lote_con_su_fecha_como_date(con):
    id_med = guardar_medicamento(con, "Acetaminofén 500 mg", 10)

    guardar_lote(con, id_med, "L-0627", date(2027, 6, 30), 3)

    assert listar_lotes(con) == [Lote(id_med, "L-0627", date(2027, 6, 30), 3)]
    assert type(listar_lotes(con)[0].fecha_vencimiento) is date


def test_lote_de_medicamento_que_no_existe_no_se_guarda(con):
    with pytest.raises(
        ValueError, match=mensaje_exacto("El medicamento con id 99 no existe")
    ):
        guardar_lote(con, 99, "L-9999", date(2027, 1, 1), 5)

    assert listar_lotes(con) == []


def test_lote_repetido_del_mismo_medicamento_no_se_guarda(con):
    id_med = guardar_medicamento(con, "Acetaminofén 500 mg", 10)
    guardar_lote(con, id_med, "L-0627", date(2027, 6, 30), 3)

    with pytest.raises(
        ValueError,
        match=mensaje_exacto("El lote L-0627 ya está registrado para ese medicamento"),
    ):
        guardar_lote(con, id_med, "L-0627", date(2027, 6, 30), 7)

    assert len(listar_lotes(con)) == 1


@pytest.mark.parametrize(
    "cantidad, mensaje",
    [
        (-1, "El lote L-0001 tiene una cantidad negativa"),  # límite
        (2.5, "El lote L-0001 tiene una cantidad que no es entera"),
        ("5", "El lote L-0001 tiene una cantidad que no es entera"),
    ],
)
def test_lote_con_cantidad_invalida_no_se_guarda(con, cantidad, mensaje):
    id_med = guardar_medicamento(con, "Acetaminofén 500 mg", 10)

    with pytest.raises(ValueError, match=mensaje_exacto(mensaje)):
        guardar_lote(con, id_med, "L-0001", date(2027, 1, 1), cantidad)

    assert listar_lotes(con) == []


@pytest.mark.parametrize(
    "fecha",
    [
        datetime(2027, 1, 1, 8, 30),  # pendiente de la semana 6: datetime no es date
        "2027-01-01",  # texto
        None,
    ],
)
def test_lote_con_fecha_que_no_es_date_no_se_guarda(con, fecha):
    id_med = guardar_medicamento(con, "Acetaminofén 500 mg", 10)

    mensaje = "La fecha de vencimiento debe ser una fecha (día, mes y año)"

    with pytest.raises(ValueError, match=mensaje_exacto(mensaje)):
        guardar_lote(con, id_med, "L-0001", fecha, 3)


def test_numero_de_lote_vacio_no_se_guarda(con):
    id_med = guardar_medicamento(con, "Acetaminofén 500 mg", 10)

    with pytest.raises(
        ValueError, match=mensaje_exacto("El número de lote es obligatorio")
    ):
        guardar_lote(con, id_med, "  ", date(2027, 1, 1), 3)


# ---------- Seguridad: inyección SQL (pendiente de la semana 6) ----------

@pytest.mark.parametrize(
    "nombre",
    [
        "' OR 1=1 --",
        "Jarabe'); DROP TABLE medicamento; --",
    ],
)
def test_nombre_con_sql_se_guarda_como_texto_y_no_se_ejecuta(con, nombre):
    guardar_medicamento(con, "Acetaminofén 500 mg", 10)

    guardar_medicamento(con, nombre, 1)

    nombres = [m.nombre for m in listar_medicamentos(con)]
    assert nombres == ["Acetaminofén 500 mg", nombre]


# ---------- De la base de datos a la regla de HU-05 ----------

def test_productos_por_pedir_con_los_datos_leidos_de_la_base(con):
    """Los mismos datos de python -m app, pero guardados y leídos de SQLite."""
    acetaminofen = guardar_medicamento(con, "Acetaminofén 500 mg", 10)
    amoxicilina = guardar_medicamento(con, "Amoxicilina 500 mg", 10)
    ibuprofeno = guardar_medicamento(con, "Ibuprofeno 400 mg", 5)
    loratadina = guardar_medicamento(con, "Loratadina 10 mg", 10)
    guardar_lote(con, acetaminofen, "L-0925", date(2026, 9, 30), 12)  # vencido
    guardar_lote(con, acetaminofen, "L-0627", date(2027, 6, 30), 3)
    guardar_lote(con, amoxicilina, "AM-11", date(2026, 11, 15), 8)
    guardar_lote(con, ibuprofeno, "IB-02", date(2027, 3, 1), 2)
    guardar_lote(con, loratadina, "LO-01", date(2027, 5, 1), 10)

    resultado = productos_por_pedir(listar_medicamentos(con), listar_lotes(con), HOY)

    assert [(p.nombre, p.texto) for p in resultado] == [
        ("Ibuprofeno 400 mg", "2 de 5 cajas"),
        ("Acetaminofén 500 mg", "3 de 10 cajas"),
        ("Amoxicilina 500 mg", "8 de 10 cajas"),
    ]


def test_los_datos_quedan_guardados_en_el_archivo(tmp_path):
    ruta = tmp_path / "inventario.sqlite3"
    primera = conectar(str(ruta))
    crear_esquema(primera)
    guardar_medicamento(primera, "Suero oral sabor a guanábana", 6)
    primera.close()

    segunda = conectar(str(ruta))
    crear_esquema(segunda)  # no borra lo que ya había

    assert [m.nombre for m in listar_medicamentos(segunda)] == [
        "Suero oral sabor a guanábana"
    ]
    segunda.close()
