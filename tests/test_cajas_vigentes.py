"""Pruebas de cajas_vigentes (supuestos 1, 2 y 4 de HU-05).

Regla (oráculo): la cantidad vigente de un medicamento es la suma de
``cantidad_actual`` de sus lotes con ``fecha_vencimiento >= hoy``. Un lote que vence
hoy cuenta; los vencidos no cuentan aunque no se hayan dado de baja; sin lotes la
cantidad es 0. Una cantidad no entera o negativa es un error con el número de lote.
Hoy = 24/10/2026, como en el documento de requisitos.
"""

import re
from datetime import date

import pytest

from app.reglas.existencias import cajas_vigentes
from app.reglas.modelos import Lote

HOY = date(2026, 10, 24)
AYER = date(2026, 10, 23)


@pytest.mark.parametrize(
    "lotes, esperado",
    [
        ([], 0),  # partición: sin lotes (supuesto 4)
        ([Lote(1, "L-0627", date(2027, 6, 30), 3)], 3),  # partición: un vigente
        (
            [
                Lote(1, "L-0127", date(2027, 1, 31), 15),
                Lote(1, "L-0627", date(2027, 6, 30), 3),
            ],
            18,
        ),  # partición: varios vigentes, 15 + 3 (ejemplo 2 del README)
        ([Lote(1, "L-0925", date(2026, 9, 30), 12)], 0),  # partición: solo vencido
        (
            [
                Lote(1, "L-0925", date(2026, 9, 30), 12),
                Lote(1, "L-0627", date(2027, 6, 30), 3),
            ],
            3,
        ),  # partición: mezcla, las 12 vencidas no suman (ejemplo 1)
        ([Lote(1, "L-0000", date(2027, 6, 30), 0)], 0),  # partición: lote vigente vacío
        ([Lote(1, "L-1023", AYER, 10)], 0),  # límite: venció ayer, último vencido
        ([Lote(1, "L-1024", HOY, 10)], 10),  # límite: vence hoy, primer vigente
    ],
)
def test_suma_solo_las_cajas_de_lotes_vigentes(lotes, esperado):
    assert cajas_vigentes(1, lotes, HOY) == esperado


def test_no_suma_lotes_de_otro_medicamento():
    lotes = [
        Lote(1, "L-0627", date(2027, 6, 30), 3),
        Lote(2, "AM-11", date(2026, 11, 15), 8),  # amoxicilina, no acetaminofén
    ]

    assert cajas_vigentes(1, lotes, HOY) == 3


def test_no_valida_lotes_de_otro_medicamento():
    """Decisión A-4: solo se validan los lotes que la función suma."""
    lotes = [Lote(2, "AM-99", date(2027, 1, 1), -1)]

    assert cajas_vigentes(1, lotes, HOY) == 0


@pytest.mark.parametrize(
    "cantidad, fecha",
    [
        (-4, date(2027, 1, 1)),  # partición: lote vigente con cantidad negativa
        (-4, date(2026, 9, 30)),  # lote vencido: también es error (decisión A-3)
        # Agregado en el paso 5: con «< -1» en lugar de «< 0» ninguna prueba fallaba.
        (-1, date(2027, 1, 1)),  # límite: último negativo, justo antes del 0
    ],
)
def test_cantidad_negativa_lanza_error_con_el_lote(cantidad, fecha):
    mensaje = "El lote L-0001 tiene una cantidad negativa"

    with pytest.raises(ValueError, match=f"^{re.escape(mensaje)}$"):
        cajas_vigentes(1, [Lote(1, "L-0001", fecha, cantidad)], HOY)


@pytest.mark.parametrize(
    "cantidad",
    [
        2.5,  # decimal
        "5",  # texto
        True,  # booleano
    ],
)
def test_cantidad_no_entera_lanza_error_con_el_lote(cantidad):
    mensaje = "El lote L-0002 tiene una cantidad que no es entera"

    with pytest.raises(ValueError, match=f"^{re.escape(mensaje)}$"):
        cajas_vigentes(1, [Lote(1, "L-0002", date(2027, 1, 1), cantidad)], HOY)
