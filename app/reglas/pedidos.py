"""HU-05. Productos bajo el mínimo. Ver el contrato en el README."""

from datetime import date

from app.reglas.modelos import Lote, Medicamento, ProductoPorPedir

MENSAJE_MINIMO_INVALIDO = "El mínimo debe ser un número igual o mayor que cero"


def productos_por_pedir(
    medicamentos: list[Medicamento],
    lotes: list[Lote],
    hoy: date,
) -> list[ProductoPorPedir]:
    """Devuelve los medicamentos con menos cajas vigentes que su mínimo.

    La lista sale ordenada de menor a mayor cantidad vigente y no se modifican
    las listas recibidas.
    """
    _validar_minimos(medicamentos)
    vigentes_por_medicamento = _cajas_vigentes_por_medicamento(
        lotes, {medicamento.id for medicamento in medicamentos}, hoy
    )

    por_pedir = []
    for medicamento in medicamentos:
        vigentes = vigentes_por_medicamento.get(medicamento.id, 0)
        if vigentes < medicamento.stock_minimo:
            por_pedir.append(
                ProductoPorPedir(
                    medicamento_id=medicamento.id,
                    nombre=medicamento.nombre,
                    vigentes=vigentes,
                    minimo=medicamento.stock_minimo,
                )
            )
    return sorted(por_pedir, key=lambda producto: producto.vigentes)


def _validar_minimos(medicamentos: list[Medicamento]) -> None:
    for medicamento in medicamentos:
        if medicamento.stock_minimo < 0:
            raise ValueError(MENSAJE_MINIMO_INVALIDO)


def _cajas_vigentes_por_medicamento(
    lotes: list[Lote], ids_registrados: set[int], hoy: date
) -> dict[int, int]:
    """Suma las cajas de los lotes que no han vencido (un lote que vence hoy cuenta)."""
    vigentes: dict[int, int] = {}
    for lote in lotes:
        if lote.cantidad_actual < 0:
            raise ValueError(f"El lote {lote.numero_lote} tiene una cantidad negativa")
        if lote.medicamento_id not in ids_registrados:
            raise ValueError(
                f"El lote {lote.numero_lote} es de un medicamento no registrado"
            )
        if lote.fecha_vencimiento >= hoy:
            vigentes[lote.medicamento_id] = (
                vigentes.get(lote.medicamento_id, 0) + lote.cantidad_actual
            )
    return vigentes
