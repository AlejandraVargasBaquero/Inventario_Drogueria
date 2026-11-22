"""Datos de prueba sintéticos para la semana 7.

Origen: propuestos con IA (Claude) y revisados a mano; ver registro_pruebas.md,
sección 4, y la bitácora. Son productos de una droguería de barrio ficticia en Neiva.
No hay personas: el proyecto todavía no maneja clientes ni usuarios, así que no hay
nombres ni teléfonos. Ninguna marca es real (D'Rosa es inventada).

Casos difíciles: tildes (Acetaminofén, caléndula, guanábana), ñ (niños, NIÑ-01),
apóstrofo (D'Rosa), nombre vacío, mínimo 0, lote con 0 cajas, lote que vence hoy,
lote que venció ayer, medicamento sin lotes y volumen (5.000 lotes, RNF-01).
"""

from datetime import date, timedelta

import pytest

from app.reglas.modelos import Lote, Medicamento

HOY = date(2026, 10, 24)


@pytest.fixture
def inventario_neiva():
    """Inventario pequeño con los casos difíciles. Hoy = 24/10/2026."""
    medicamentos = [
        Medicamento(1, "Acetaminofén 500 mg", 10),  # tilde
        Medicamento(2, "Jarabe para la tos niños 120 ml", 4),  # ñ
        Medicamento(3, "Crema de caléndula D'Rosa 30 g", 2),  # apóstrofo y tilde
        Medicamento(4, "", 3),  # nombre vacío (ambigüedad A-5)
        Medicamento(5, "Suero oral sabor a guanábana", 0),  # mínimo 0, sin lotes
        Medicamento(6, "Loratadina 10 mg", 5),
    ]
    lotes = [
        Lote(1, "L-0925", date(2026, 9, 30), 12),  # vencido
        Lote(1, "L-0627", date(2027, 6, 30), 3),
        Lote(2, "NIÑ-01", HOY, 4),  # vence hoy y queda igual al mínimo
        Lote(3, "CR-07", HOY - timedelta(days=1), 6),  # venció ayer
        Lote(3, "CR-08", date(2027, 2, 28), 0),  # lote vigente con 0 cajas
        Lote(4, "SN-00", date(2027, 1, 15), 1),
        Lote(6, "LO-11", date(2027, 5, 1), 7),
    ]
    return {"medicamentos": medicamentos, "lotes": lotes, "hoy": HOY}


@pytest.fixture
def cinco_mil_lotes():
    """5.000 lotes de 1 caja del medicamento 1: los pares vencen hoy, los impares
    vencieron ayer. Según la regla, quedan 2.500 cajas vigentes."""
    ayer = HOY - timedelta(days=1)
    return [
        Lote(1, f"L-{i:04d}", HOY if i % 2 == 0 else ayer, 1) for i in range(5000)
    ]
