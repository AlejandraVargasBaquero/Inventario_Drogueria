"""Pruebas de editar la cantidad de un lote y de eliminar lotes y medicamentos.

Capa de datos con una base en memoria y capa web con el cliente de pruebas de
Flask. Hoy = 24/10/2026, como en los requisitos.
"""

import re
from datetime import date

import pytest

from app.datos.repositorio import (
    cambiar_cantidad_lote,
    conectar,
    crear_esquema,
    eliminar_lote,
    eliminar_medicamento,
    guardar_lote,
    guardar_medicamento,
    listar_lotes,
    listar_medicamentos,
)
from app.web import create_app

HOY = date(2026, 10, 24)


def exacto(texto):
    return f"^{re.escape(texto)}$"


@pytest.fixture
def con():
    conexion = conectar(":memory:")
    crear_esquema(conexion)
    yield conexion
    conexion.close()


@pytest.fixture
def acetaminofen(con):
    """Acetaminofén con un lote vencido (L-0925) y uno vigente (L-0627)."""
    medicamento_id = guardar_medicamento(con, "Acetaminofén 500 mg", 10)
    guardar_lote(con, medicamento_id, "L-0925", date(2026, 9, 30), 12)
    guardar_lote(con, medicamento_id, "L-0627", date(2027, 6, 30), 3)
    return medicamento_id


def cajas_por_lote(con):
    return {lote.numero_lote: lote.cantidad_actual for lote in listar_lotes(con)}


# ---------- Cambiar la cantidad de un lote ----------


def test_cambiar_cantidad_guarda_el_nuevo_valor(con, acetaminofen):
    cambiar_cantidad_lote(con, acetaminofen, "L-0627", 1)

    assert cajas_por_lote(con) == {"L-0925": 12, "L-0627": 1}


def test_cambiar_cantidad_a_cero_es_valido(con, acetaminofen):
    """Límite: 0 cajas es el último valor válido (el lote se agotó)."""
    cambiar_cantidad_lote(con, acetaminofen, "L-0627", 0)

    assert cajas_por_lote(con)["L-0627"] == 0


@pytest.mark.parametrize(
    "cantidad, mensaje",
    [
        (-1, "El lote L-0627 tiene una cantidad negativa"),  # límite inválido
        ("3", "El lote L-0627 tiene una cantidad que no es entera"),
        (True, "El lote L-0627 tiene una cantidad que no es entera"),
        (None, "El lote L-0627 tiene una cantidad que no es entera"),
        (10**20, "El número es demasiado grande para guardarlo"),  # D-01
    ],
)
def test_cambiar_cantidad_invalida_no_la_guarda(con, acetaminofen, cantidad, mensaje):
    with pytest.raises(ValueError, match=exacto(mensaje)):
        cambiar_cantidad_lote(con, acetaminofen, "L-0627", cantidad)

    assert cajas_por_lote(con)["L-0627"] == 3


def test_cambiar_cantidad_de_lote_que_no_existe_lanza_error(con, acetaminofen):
    with pytest.raises(
        ValueError, match=exacto("El lote L-9999 no existe para ese medicamento")
    ):
        cambiar_cantidad_lote(con, acetaminofen, "L-9999", 5)


# ---------- Eliminar un lote ----------


def test_eliminar_lote_borra_solo_ese_lote(con, acetaminofen):
    eliminar_lote(con, acetaminofen, "L-0925")

    assert cajas_por_lote(con) == {"L-0627": 3}
    assert len(listar_medicamentos(con)) == 1


def test_el_mismo_numero_en_otro_medicamento_no_se_borra(con, acetaminofen):
    otro = guardar_medicamento(con, "Ibuprofeno 400 mg", 5)
    guardar_lote(con, otro, "L-0627", date(2027, 3, 1), 2)

    eliminar_lote(con, otro, "L-0627")

    assert [(lote.medicamento_id, lote.numero_lote) for lote in listar_lotes(con)] == [
        (acetaminofen, "L-0925"),
        (acetaminofen, "L-0627"),
    ]


def test_eliminar_lote_que_no_existe_lanza_error(con, acetaminofen):
    with pytest.raises(
        ValueError, match=exacto("El lote L-9999 no existe para ese medicamento")
    ):
        eliminar_lote(con, acetaminofen, "L-9999")

    assert len(listar_lotes(con)) == 2


# ---------- Eliminar un medicamento ----------


def test_eliminar_medicamento_borra_tambien_sus_lotes(con, acetaminofen):
    otro = guardar_medicamento(con, "Ibuprofeno 400 mg", 5)
    guardar_lote(con, otro, "IB-02", date(2027, 3, 1), 2)

    eliminados = eliminar_medicamento(con, acetaminofen)

    assert eliminados == 2
    assert [m.nombre for m in listar_medicamentos(con)] == ["Ibuprofeno 400 mg"]
    assert cajas_por_lote(con) == {"IB-02": 2}


def test_eliminar_medicamento_sin_lotes(con):
    medicamento_id = guardar_medicamento(con, "Loratadina 10 mg", 10)

    assert eliminar_medicamento(con, medicamento_id) == 0
    assert listar_medicamentos(con) == []


def test_eliminar_medicamento_que_no_existe_lanza_error(con, acetaminofen):
    with pytest.raises(ValueError, match=exacto("El medicamento con id 99 no existe")):
        eliminar_medicamento(con, 99)

    assert len(listar_medicamentos(con)) == 1
    assert len(listar_lotes(con)) == 2


# ---------- Pantallas ----------


@pytest.fixture
def app(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "clave-solo-para-pruebas",
            "RUTA_BD": str(tmp_path / "prueba.sqlite3"),
            "HOY": HOY,
        }
    )


@pytest.fixture
def cliente(app):
    return app.test_client()


def enviar(cliente, ruta, **datos):
    cliente.get("/inventario")
    with cliente.session_transaction() as sesion:
        token = sesion["csrf"]
    respuesta = cliente.post(ruta, data={"csrf": token, **datos}, follow_redirects=True)
    return respuesta.get_data(as_text=True)


def guardado(app):
    con = conectar(app.config["RUTA_BD"])
    try:
        return listar_medicamentos(con), listar_lotes(con)
    finally:
        con.close()


@pytest.fixture
def con_datos(cliente):
    enviar(cliente, "/medicamentos", nombre="Acetaminofén 500 mg", minimo="10")
    for numero, fecha, cajas in [
        ("L-0925", "2026-09-30", "12"),
        ("L-0627", "2027-06-30", "3"),
    ]:
        enviar(
            cliente,
            "/lotes",
            medicamento_id="1",
            numero_lote=numero,
            fecha_vencimiento=fecha,
            cantidad=cajas,
        )
    return cliente


def test_pantalla_cambiar_cantidad_actualiza_por_pedir(con_datos, app):
    pagina = enviar(
        con_datos,
        "/lotes/cantidad",
        medicamento_id="1",
        numero_lote="L-0627",
        cantidad="12",
    )

    assert "Se cambió la cantidad del lote L-0627 a 12" in pagina
    assert {lote.numero_lote: lote.cantidad_actual for lote in guardado(app)[1]} == {
        "L-0925": 12,
        "L-0627": 12,
    }
    assert "Acetaminofén 500 mg" not in con_datos.get("/").get_data(as_text=True)


def test_pantalla_cantidad_negativa_muestra_el_mensaje(con_datos, app):
    pagina = enviar(
        con_datos,
        "/lotes/cantidad",
        medicamento_id="1",
        numero_lote="L-0627",
        cantidad="-1",
    )

    assert "El lote L-0627 tiene una cantidad negativa" in pagina
    assert [lote.cantidad_actual for lote in guardado(app)[1]] == [12, 3]


def test_pantalla_eliminar_lote(con_datos, app):
    pagina = enviar(
        con_datos, "/lotes/eliminar", medicamento_id="1", numero_lote="L-0925"
    )

    assert "Se eliminó el lote L-0925" in pagina
    assert [lote.numero_lote for lote in guardado(app)[1]] == ["L-0627"]


def test_pantalla_eliminar_medicamento_y_sus_lotes(con_datos, app):
    pagina = enviar(con_datos, "/medicamentos/1/eliminar")

    assert "Se eliminó Acetaminofén 500 mg y sus 2 lotes" in pagina
    assert guardado(app) == ([], [])


def test_pantalla_eliminar_medicamento_que_no_existe(con_datos, app):
    pagina = enviar(con_datos, "/medicamentos/99/eliminar")

    assert "El medicamento con id 99 no existe" in pagina
    assert len(guardado(app)[0]) == 1


@pytest.mark.parametrize(
    "ruta, datos",
    [
        ("/medicamentos/1/eliminar", {}),
        ("/lotes/eliminar", {"medicamento_id": "1", "numero_lote": "L-0925"}),
        (
            "/lotes/cantidad",
            {"medicamento_id": "1", "numero_lote": "L-0627", "cantidad": "0"},
        ),
    ],
)
def test_eliminar_o_editar_sin_token_se_rechaza(con_datos, app, ruta, datos):
    """Abuso (CSRF): sin el token del formulario no se borra ni se cambia nada."""
    respuesta = con_datos.post(ruta, data=datos)

    assert respuesta.status_code == 400
    medicamentos, lotes = guardado(app)
    assert len(medicamentos) == 1
    assert [lote.cantidad_actual for lote in lotes] == [12, 3]


def test_el_inventario_muestra_los_botones_de_eliminar_y_editar(con_datos):
    pagina = con_datos.get("/inventario").get_data(as_text=True)

    assert 'action="/medicamentos/1/eliminar"' in pagina
    assert 'action="/lotes/eliminar"' in pagina
    assert 'action="/lotes/cantidad"' in pagina
