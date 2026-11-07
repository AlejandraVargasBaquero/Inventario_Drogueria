"""Pruebas de HU-05: productos bajo el mínimo.

Los datos son los del documento de requisitos (semana 3): hoy es 24/10/2026 y el
acetaminofén de 500 mg tiene los lotes L-0925 (vencido), L-0127 y L-0627.
"""

from datetime import date

import pytest

from app.reglas.modelos import Lote, Medicamento
from app.reglas.pedidos import productos_por_pedir

HOY = date(2026, 10, 24)

ACETAMINOFEN = Medicamento(id=1, nombre="Acetaminofén 500 mg", stock_minimo=10)
L_0925_VENCIDO = Lote(1, "L-0925", date(2026, 9, 30), 12)
L_0127 = Lote(1, "L-0127", date(2027, 1, 31), 15)
L_0627 = Lote(1, "L-0627", date(2027, 6, 30), 3)


# ---------- Casos normales ----------

def test_acetaminofen_con_3_vigentes_de_10_aparece_por_pedir():
    """HU-05, escenario 1: las 12 cajas vencidas del L-0925 no cuentan."""
    resultado = productos_por_pedir([ACETAMINOFEN], [L_0925_VENCIDO, L_0627], HOY)

    assert len(resultado) == 1
    assert resultado[0].nombre == "Acetaminofén 500 mg"
    assert resultado[0].vigentes == 3
    assert resultado[0].texto == "3 de 10 cajas"


def test_suma_los_lotes_vigentes_y_no_aparece_si_supera_el_minimo():
    """L-0127 (15) + L-0627 (3) = 18 vigentes, por encima del mínimo de 10."""
    resultado = productos_por_pedir(
        [ACETAMINOFEN], [L_0925_VENCIDO, L_0127, L_0627], HOY
    )

    assert resultado == []


def test_resultado_ordenado_de_menor_a_mayor_cantidad_vigente():
    amoxicilina = Medicamento(2, "Amoxicilina 500 mg", 10)
    ibuprofeno = Medicamento(3, "Ibuprofeno 400 mg", 5)
    lotes = [
        Lote(2, "AM-11", date(2026, 11, 15), 8),
        Lote(3, "IB-02", date(2027, 3, 1), 2),
    ]

    resultado = productos_por_pedir([amoxicilina, ibuprofeno], lotes, HOY)

    assert [p.nombre for p in resultado] == ["Ibuprofeno 400 mg", "Amoxicilina 500 mg"]
    assert [p.texto for p in resultado] == ["2 de 5 cajas", "8 de 10 cajas"]


# ---------- Casos límite ----------

def test_vigentes_iguales_al_minimo_no_aparece():
    loratadina = Medicamento(4, "Loratadina 10 mg", 10)
    lotes = [Lote(4, "LO-01", date(2027, 5, 1), 10)]

    assert productos_por_pedir([loratadina], lotes, HOY) == []


def test_lote_que_vence_hoy_todavia_cuenta_como_vigente():
    lotes = [Lote(1, "L-1024", HOY, 10)]

    assert productos_por_pedir([ACETAMINOFEN], lotes, HOY) == []


def test_medicamento_con_todos_los_lotes_vencidos_aparece_con_cero():
    resultado = productos_por_pedir([ACETAMINOFEN], [L_0925_VENCIDO], HOY)

    assert resultado[0].texto == "0 de 10 cajas"


def test_medicamento_sin_lotes_aparece_con_cero():
    resultado = productos_por_pedir([ACETAMINOFEN], [], HOY)

    assert resultado[0].vigentes == 0


def test_minimo_cero_nunca_aparece_aunque_no_haya_cajas():
    jeringas = Medicamento(5, "Jeringa 5 ml", 0)

    assert productos_por_pedir([jeringas], [], HOY) == []


def test_sin_medicamentos_devuelve_lista_vacia():
    assert productos_por_pedir([], [], HOY) == []


def test_con_empate_conserva_el_orden_de_llegada():
    primero = Medicamento(6, "Suero oral", 5)
    segundo = Medicamento(7, "Gasa estéril", 5)

    resultado = productos_por_pedir([primero, segundo], [], HOY)

    assert [p.nombre for p in resultado] == ["Suero oral", "Gasa estéril"]


def test_no_modifica_las_listas_recibidas():
    medicamentos = [ACETAMINOFEN]
    lotes = [L_0627, L_0925_VENCIDO]

    productos_por_pedir(medicamentos, lotes, HOY)

    assert medicamentos == [ACETAMINOFEN]
    assert lotes == [L_0627, L_0925_VENCIDO]


# ---------- Casos de error ----------

def test_minimo_negativo_lanza_error_con_el_mensaje_de_la_historia():
    """HU-05, escenario 2: mínimo de −2 para el ibuprofeno."""
    ibuprofeno = Medicamento(3, "Ibuprofeno 400 mg", -2)

    with pytest.raises(
        ValueError, match="El mínimo debe ser un número igual o mayor que cero"
    ):
        productos_por_pedir([ibuprofeno], [], HOY)


def test_lote_con_cantidad_negativa_lanza_error():
    lote_malo = Lote(1, "L-0001", date(2027, 1, 1), -4)

    with pytest.raises(ValueError, match="L-0001"):
        productos_por_pedir([ACETAMINOFEN], [lote_malo], HOY)


def test_lote_de_medicamento_no_registrado_lanza_error():
    lote_huerfano = Lote(99, "L-9999", date(2027, 1, 1), 5)

    with pytest.raises(ValueError, match="no registrado"):
        productos_por_pedir([ACETAMINOFEN], [lote_huerfano], HOY)
