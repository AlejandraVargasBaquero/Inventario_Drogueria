"""Tabla de decisión de productos_por_pedir (HU-05)."""

from datetime import date

import pytest

from app.reglas.modelos import Lote, Medicamento
from app.reglas.pedidos import productos_por_pedir

HOY = date(2026, 10, 24)
VIGENTE = date(2027, 6, 30)
VENCIDO = date(2026, 9, 30)


@pytest.mark.parametrize(
    "minimo, lotes, aparece",
    [
        (0, [], False),  # R2: mínimo 0, sin vencidos
        (0, [Lote(1, "L-V", VENCIDO, 5)], False),  # R3: mínimo 0, con vencidos
        (10, [Lote(1, "L-1", VIGENTE, 3)], True),  # R4: bajo el mínimo
        (
            10,
            [Lote(1, "L-1", VIGENTE, 3), Lote(1, "L-V", VENCIDO, 12)],
            True,
        ),  # R5: bajo el mínimo, vencidas no cuentan
        (10, [Lote(1, "L-1", VIGENTE, 18)], False),  # R6: no está bajo el mínimo
        (
            10,
            [Lote(1, "L-1", VIGENTE, 18), Lote(1, "L-V", VENCIDO, 12)],
            False,
        ),  # R7: no está bajo el mínimo, con vencidos
    ],
)
def test_tabla_de_decision(minimo, lotes, aparece):
    medicamento = Medicamento(1, "Acetaminofén 500 mg", minimo)

    resultado = productos_por_pedir([medicamento], lotes, HOY)

    assert (len(resultado) == 1) == aparece


def test_r1_datos_invalidos_lanza_error():
    medicamento = Medicamento(1, "Acetaminofén 500 mg", -2)
    with pytest.raises(ValueError):
        productos_por_pedir([medicamento], [], HOY)


def test_vigentes_igual_al_minimo_no_aparece():
    medicamento = Medicamento(4, "Loratadina 10 mg", 10)
    lotes = [Lote(4, "LO-01", date(2027, 5, 1), 10)]
    assert productos_por_pedir([medicamento], lotes, HOY) == []


def test_resultado_no_es_none():
    medicamento = Medicamento(1, "Acetaminofén 500 mg", 10)
    assert productos_por_pedir([medicamento], [], HOY) is not None
