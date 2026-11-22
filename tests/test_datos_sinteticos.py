"""Pruebas con los datos sintéticos de conftest.py.

Los esperados se calcularon a mano con la regla, lote por lote (registro, sección 4).
"""

import re
from datetime import date

import pytest

from app.reglas.existencias import cajas_vigentes
from app.reglas.modelos import Lote, Medicamento
from app.reglas.pedidos import productos_por_pedir


@pytest.mark.parametrize(
    "medicamento_id, esperado",
    [
        (1, 3),  # Acetaminofén: 12 vencidas no cuentan, quedan 3
        (2, 4),  # Jarabe niños: el lote NIÑ-01 vence hoy y cuenta
        (3, 0),  # Crema D'Rosa: CR-07 venció ayer y CR-08 tiene 0 cajas
        (4, 1),  # nombre vacío: 1 caja
        (5, 0),  # Suero oral: sin lotes
        (6, 7),  # Loratadina: 7 cajas
    ],
)
def test_cajas_vigentes_del_inventario_sintetico(
    inventario_neiva, medicamento_id, esperado
):
    lotes, hoy = inventario_neiva["lotes"], inventario_neiva["hoy"]

    assert cajas_vigentes(medicamento_id, lotes, hoy) == esperado


def test_lista_por_pedir_del_inventario_sintetico(inventario_neiva):
    """Aparecen 3 de 6: el jarabe (4 de 4), el suero (mínimo 0) y la loratadina
    (7 de 5) no. Orden de menor a mayor vigentes: 0, 1, 3."""
    resultado = productos_por_pedir(**inventario_neiva)

    assert [(p.nombre, p.texto) for p in resultado] == [
        ("Crema de caléndula D'Rosa 30 g", "0 de 2 cajas"),
        ("", "1 de 3 cajas"),
        ("Acetaminofén 500 mg", "3 de 10 cajas"),
    ]


def test_mensaje_de_error_conserva_la_enie_del_lote():
    lotes = [Lote(2, "NIÑ-02", date(2027, 1, 1), -1)]
    mensaje = "El lote NIÑ-02 tiene una cantidad negativa"

    with pytest.raises(ValueError, match=f"^{re.escape(mensaje)}$"):
        cajas_vigentes(2, lotes, date(2026, 10, 24))


def test_volumen_de_cinco_mil_lotes(cinco_mil_lotes):
    """RNF-01: hasta 5.000 lotes. 2.500 vencen hoy (cuentan) y 2.500 vencieron ayer."""
    acetaminofen = Medicamento(1, "Acetaminofén 500 mg", 3000)
    hoy = date(2026, 10, 24)

    assert cajas_vigentes(1, cinco_mil_lotes, hoy) == 2500
    resultado = productos_por_pedir([acetaminofen], cinco_mil_lotes, hoy)
    assert [p.texto for p in resultado] == ["2500 de 3000 cajas"]
