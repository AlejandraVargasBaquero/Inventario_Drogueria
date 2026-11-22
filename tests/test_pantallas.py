"""Pruebas de la capa web con Flask (frontend).

Cada prueba usa una base SQLite nueva en una carpeta temporal y una fecha fija
(24/10/2026), así que no dependen del día ni del archivo inventario.sqlite3.
"""

from datetime import date

import pytest

from app.datos.repositorio import conectar, listar_lotes, listar_medicamentos
from app.web import create_app

HOY = date(2026, 10, 24)


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


def token(cliente):
    """Abre el inventario para que la sesión tenga el token del formulario."""
    cliente.get("/inventario")
    with cliente.session_transaction() as sesion:
        return sesion["csrf"]


def enviar(cliente, ruta, **datos):
    """Envía un formulario con su token y sigue la redirección."""
    return cliente.post(
        ruta, data={"csrf": token(cliente), **datos}, follow_redirects=True
    )


def medicamentos_guardados(app):
    con = conectar(app.config["RUTA_BD"])
    try:
        return listar_medicamentos(con)
    finally:
        con.close()


def lotes_guardados(app):
    con = conectar(app.config["RUTA_BD"])
    try:
        return listar_lotes(con)
    finally:
        con.close()


def html(respuesta):
    return respuesta.get_data(as_text=True)


# ---------- Pantalla de productos por pedir (HU-05) ----------


def test_sin_medicamentos_dice_que_no_hay_nada_por_pedir(cliente):
    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    assert "No hay productos por pedir" in html(respuesta)
    assert "24/10/2026" in html(respuesta)


def test_escenario_1_acetaminofen_aparece_con_3_de_10_cajas(cliente):
    """HU-05, escenario 1, cargado desde las pantallas de registro."""
    enviar(cliente, "/medicamentos", nombre="Acetaminofén 500 mg", minimo="10")
    enviar(
        cliente,
        "/lotes",
        medicamento_id="1",
        numero_lote="L-0925",
        fecha_vencimiento="2026-09-30",
        cantidad="12",
    )  # vencido: no cuenta
    enviar(
        cliente,
        "/lotes",
        medicamento_id="1",
        numero_lote="L-0627",
        fecha_vencimiento="2027-06-30",
        cantidad="3",
    )

    pagina = html(cliente.get("/"))

    assert "Acetaminofén 500 mg" in pagina
    assert "3 de 10 cajas" in pagina


def test_la_lista_va_de_menor_a_mayor_cantidad_vigente(cliente):
    enviar(cliente, "/medicamentos", nombre="Amoxicilina 500 mg", minimo="10")
    enviar(cliente, "/medicamentos", nombre="Ibuprofeno 400 mg", minimo="5")
    enviar(
        cliente,
        "/lotes",
        medicamento_id="1",
        numero_lote="AM-11",
        fecha_vencimiento="2026-11-15",
        cantidad="8",
    )
    enviar(
        cliente,
        "/lotes",
        medicamento_id="2",
        numero_lote="IB-02",
        fecha_vencimiento="2027-03-01",
        cantidad="2",
    )

    pagina = html(cliente.get("/"))

    assert pagina.index("2 de 5 cajas") < pagina.index("8 de 10 cajas")


# ---------- Registro de medicamentos y mínimo (HU-05, escenario 2) ----------


def test_registrar_medicamento_lo_guarda_y_lo_muestra(cliente, app):
    respuesta = enviar(cliente, "/medicamentos", nombre="Loratadina 10 mg", minimo="5")

    assert "Se registró Loratadina 10 mg" in html(respuesta)
    assert [m.nombre for m in medicamentos_guardados(app)] == ["Loratadina 10 mg"]


def test_escenario_2_minimo_negativo_al_registrar_no_se_guarda(cliente, app):
    respuesta = enviar(
        cliente, "/medicamentos", nombre="Ibuprofeno 400 mg", minimo="-2"
    )

    assert "El mínimo debe ser un número igual o mayor que cero" in html(respuesta)
    assert medicamentos_guardados(app) == []


def test_escenario_2_cambiar_minimo_a_negativo_no_lo_guarda(cliente, app):
    enviar(cliente, "/medicamentos", nombre="Ibuprofeno 400 mg", minimo="5")

    respuesta = enviar(cliente, "/medicamentos/1/minimo", minimo="-2")

    assert "El mínimo debe ser un número igual o mayor que cero" in html(respuesta)
    assert medicamentos_guardados(app)[0].stock_minimo == 5


def test_cambiar_minimo_valido_lo_guarda(cliente, app):
    enviar(cliente, "/medicamentos", nombre="Ibuprofeno 400 mg", minimo="5")

    respuesta = enviar(cliente, "/medicamentos/1/minimo", minimo=" 8 ")

    assert "Se cambió el mínimo de Ibuprofeno 400 mg a 8" in html(respuesta)
    assert medicamentos_guardados(app)[0].stock_minimo == 8


@pytest.mark.parametrize(
    "minimo",
    [
        "",  # campo vacío
        "abc",  # letras
        "2.5",  # decimal
        "10.0",  # decimal con valor entero (ambigüedad A-1)
    ],
)
def test_minimo_que_no_es_entero_muestra_el_mensaje(cliente, app, minimo):
    respuesta = enviar(
        cliente, "/medicamentos", nombre="Omeprazol 20 mg", minimo=minimo
    )

    assert "El mínimo debe ser un número entero de cajas" in html(respuesta)
    assert medicamentos_guardados(app) == []


def test_nombre_vacio_muestra_el_mensaje(cliente, app):
    respuesta = enviar(cliente, "/medicamentos", nombre="   ", minimo="5")

    assert "El nombre del medicamento es obligatorio" in html(respuesta)
    assert medicamentos_guardados(app) == []


# ---------- Registro de lotes ----------


def test_registrar_lote_lo_guarda_y_lo_muestra_en_el_inventario(cliente, app):
    enviar(cliente, "/medicamentos", nombre="Acetaminofén 500 mg", minimo="10")

    respuesta = enviar(
        cliente,
        "/lotes",
        medicamento_id="1",
        numero_lote="L-0627",
        fecha_vencimiento="2027-06-30",
        cantidad="3",
    )

    assert "Se registró el lote L-0627" in html(respuesta)
    assert lotes_guardados(app)[0].fecha_vencimiento == date(2027, 6, 30)
    assert "30/06/2027" in html(cliente.get("/inventario"))


def test_el_inventario_marca_los_lotes_vencidos_y_el_que_vence_hoy(cliente):
    enviar(cliente, "/medicamentos", nombre="Acetaminofén 500 mg", minimo="10")
    enviar(
        cliente,
        "/lotes",
        medicamento_id="1",
        numero_lote="L-0925",
        fecha_vencimiento="2026-09-30",
        cantidad="12",
    )
    enviar(
        cliente,
        "/lotes",
        medicamento_id="1",
        numero_lote="L-1024",
        fecha_vencimiento="2026-10-24",
        cantidad="4",
    )

    pagina = html(cliente.get("/inventario"))

    fila_vencida = pagina[pagina.index("L-0925") : pagina.index("L-1024")]
    fila_de_hoy = pagina[pagina.index("L-1024") :]
    assert "Vencido" in fila_vencida
    assert "Vigente" in fila_de_hoy.split("</tr>")[0]


@pytest.mark.parametrize(
    "campos, mensaje",
    [
        (
            {"fecha_vencimiento": "", "cantidad": "3"},
            "La fecha de vencimiento debe ser una fecha (día, mes y año)",
        ),
        (
            {"fecha_vencimiento": "2027-02-30", "cantidad": "3"},  # no existe
            "La fecha de vencimiento debe ser una fecha (día, mes y año)",
        ),
        (
            {"fecha_vencimiento": "2027-01-01", "cantidad": "-1"},
            "El lote L-0001 tiene una cantidad negativa",
        ),
        (
            {"fecha_vencimiento": "2027-01-01", "cantidad": "tres"},
            "El lote L-0001 tiene una cantidad que no es entera",
        ),
    ],
)
def test_lote_invalido_no_se_guarda_y_muestra_el_mensaje(cliente, app, campos, mensaje):
    enviar(cliente, "/medicamentos", nombre="Acetaminofén 500 mg", minimo="10")

    respuesta = enviar(
        cliente, "/lotes", medicamento_id="1", numero_lote="L-0001", **campos
    )

    assert mensaje in html(respuesta)
    assert lotes_guardados(app) == []


@pytest.mark.parametrize(
    "medicamento_id, mensaje",
    [
        ("99", "El medicamento con id 99 no existe"),
        ("", "Elige un medicamento"),
        ("abc", "Elige un medicamento"),
    ],
)
def test_lote_sin_medicamento_valido_no_se_guarda(
    cliente, app, medicamento_id, mensaje
):
    respuesta = enviar(
        cliente,
        "/lotes",
        medicamento_id=medicamento_id,
        numero_lote="L-0001",
        fecha_vencimiento="2027-01-01",
        cantidad="3",
    )

    assert mensaje in html(respuesta)
    assert lotes_guardados(app) == []


# ---------- Seguridad ----------


def test_nombre_con_html_se_muestra_escapado(cliente):
    """XSS (pendiente de la semana 6): Jinja2 escapa el nombre; no se usa |safe."""
    enviar(cliente, "/medicamentos", nombre="<script>alert(1)</script>", minimo="5")

    for ruta in ["/", "/inventario"]:
        pagina = html(cliente.get(ruta))
        assert "<script>alert(1)</script>" not in pagina
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in pagina


@pytest.mark.parametrize(
    "ruta, datos",
    [
        ("/medicamentos", {"nombre": "Loratadina 10 mg", "minimo": "5"}),
        ("/medicamentos/1/minimo", {"minimo": "0"}),
    ],
)
def test_formulario_sin_token_se_rechaza(cliente, app, ruta, datos):
    """Un formulario enviado desde otra página no trae el token de la sesión."""
    if ruta != "/medicamentos":
        enviar(cliente, "/medicamentos", nombre="Ibuprofeno 400 mg", minimo="5")

    respuesta = cliente.post(ruta, data=datos)

    assert respuesta.status_code == 400
    minimos = [m.stock_minimo for m in medicamentos_guardados(app)]
    assert minimos in ([], [5])


def test_formulario_con_token_equivocado_se_rechaza(cliente, app):
    token(cliente)

    respuesta = cliente.post(
        "/medicamentos", data={"csrf": "otro", "nombre": "Loratadina", "minimo": "5"}
    )

    assert respuesta.status_code == 400
    assert medicamentos_guardados(app) == []
