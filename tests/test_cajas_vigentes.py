"""Pruebas de cajas_vigentes (supuestos 1, 2 y 4 de HU-05)."""

from datetime import date, timedelta

import pytest

from app.reglas.existencias import cajas_vigentes
from app.reglas.modelos import Lote

HOY = date(2026, 10, 24)
AYER = HOY - timedelta(days=1)
MANANA = HOY + timedelta(days=1)


@pytest.mark.parametrize(
    "lotes, esperado",
    [
        ([], 0),  # sin lotes
        ([Lote(1, "L-0627", date(2027, 6, 30), 3)], 3),  # un lote vigente
        (
            [
                Lote(1, "L-0127", date(2027, 1, 31), 15),
                Lote(1, "L-0627", date(2027, 6, 30), 3),
            ],
            18,
        ),  # dos lotes vigentes se suman
        ([Lote(1, "L-0925", date(2026, 9, 30), 12)], 0),  # solo vencido
        (
            [
                Lote(1, "L-0925", date(2026, 9, 30), 12),
                Lote(1, "L-0627", date(2027, 6, 30), 3),
            ],
            3,
        ),  # mezcla: el vencido no suma
        ([Lote(1, "L-1024", HOY, 10)], 10),  # límite: vence hoy cuenta
        ([Lote(1, "L-1023", AYER, 10)], 0),  # límite: venció ayer no cuenta
        ([Lote(1, "L-1025", MANANA, 10)], 10),  # vence mañana cuenta
    ],
)
def test_cajas_vigentes_segun_vencimiento(lotes, esperado):
    assert cajas_vigentes(1, lotes, HOY) == esperado


def test_cajas_vigentes_es_cero_o_mas():
    lotes = [Lote(1, "L-0925", date(2026, 9, 30), 12)]
    assert cajas_vigentes(1, lotes, HOY) >= 0


def test_ignora_lotes_de_otro_medicamento():
    lotes = [
        Lote(1, "L-0627", date(2027, 6, 30), 3),
        Lote(2, "AM-11", date(2026, 11, 15), 8),
    ]
    assert cajas_vigentes(1, lotes, HOY) == 3


def test_lote_con_cantidad_negativa_lanza_error():
    with pytest.raises(ValueError):
        cajas_vigentes(1, [Lote(1, "L-0001", date(2027, 1, 1), -4)], HOY)


def test_lote_con_cantidad_decimal_lanza_error():
    with pytest.raises(ValueError):
        cajas_vigentes(1, [Lote(1, "L-0002", date(2027, 1, 1), 2.5)], HOY)
