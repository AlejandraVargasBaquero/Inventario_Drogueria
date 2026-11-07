"""HU-05. Productos bajo el mínimo. Ver el contrato en el README."""

from datetime import date

from app.reglas.modelos import Lote, Medicamento, ProductoPorPedir


def productos_por_pedir(
    medicamentos: list[Medicamento],
    lotes: list[Lote],
    hoy: date,
) -> list[ProductoPorPedir]:
    raise NotImplementedError("HU-05 todavía no está implementada")
