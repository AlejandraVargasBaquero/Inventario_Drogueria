"""Tabla de decisión de productos_por_pedir (HU-05).

Condiciones: (A) datos válidos, (B) mínimo mayor que 0, (C) cajas vigentes menores
que el mínimo, (D) el medicamento tiene cajas vencidas. Acción: aparece por pedir,
con cuántas cajas, o ValueError. La tabla completa está en registro_pruebas.md.
Hoy = 24/10/2026.
"""

import re
from datetime import date

import pytest

from app.reglas.modelos import Lote, Medicamento
from app.reglas.pedidos import productos_por_pedir

HOY = date(2026, 10, 24)
VIGENTE = date(2027, 6, 30)
VENCIDO = date(2026, 9, 30)


@pytest.mark.parametrize(
    "minimo, lotes, esperado",
    [
        (0, [], []),  # R2: A sí, B no, D no -> no aparece
        (0, [Lote(1, "L-V", VENCIDO, 5)], []),  # R3: A sí, B no, D sí -> no aparece
        (10, [Lote(1, "L-1", VIGENTE, 3)], ["3 de 10 cajas"]),  # R4: B sí, C sí, D no
        (
            10,
            [Lote(1, "L-1", VIGENTE, 3), Lote(1, "L-V", VENCIDO, 12)],
            ["3 de 10 cajas"],
        ),  # R5: B sí, C sí, D sí -> las 12 vencidas no cuentan (3 + 12 = 15 sacaría
        # al medicamento de la lista)
        (10, [Lote(1, "L-1", VIGENTE, 18)], []),  # R6: B sí, C no, D no
        (
            10,
            [Lote(1, "L-1", VIGENTE, 18), Lote(1, "L-V", VENCIDO, 12)],
            [],
        ),  # R7: B sí, C no, D sí
        # Límites de la condición C (vigentes contra mínimo 10):
        (10, [Lote(1, "L-1", VIGENTE, 9)], ["9 de 10 cajas"]),  # 9: último que aparece
        (10, [Lote(1, "L-1", VIGENTE, 10)], []),  # 10: primero que no (supuesto 3)
        # Límite de la condición B (mínimo 1 contra mínimo 0, sin cajas):
        (1, [], ["0 de 1 cajas"]),  # mínimo 1: primero que sí pide
    ],
)
def test_tabla_de_decision(minimo, lotes, esperado):
    medicamento = Medicamento(1, "Acetaminofén 500 mg", minimo)

    resultado = productos_por_pedir([medicamento], lotes, HOY)

    assert [producto.texto for producto in resultado] == esperado


def test_r1_datos_invalidos_lanza_error_aunque_haya_que_pedir():
    """R1: si A es no, el resto no importa; no se devuelve una lista parcial."""
    bajo_el_minimo = Medicamento(1, "Acetaminofén 500 mg", 10)
    invalido = Medicamento(3, "Ibuprofeno 400 mg", -2)
    mensaje = "El mínimo debe ser un número igual o mayor que cero"

    with pytest.raises(ValueError, match=f"^{re.escape(mensaje)}$"):
        productos_por_pedir([bajo_el_minimo, invalido], [], HOY)
