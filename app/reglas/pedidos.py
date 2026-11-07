"""HU-05. Productos bajo el mínimo. Ver el contrato en el README."""

from datetime import date

from app.reglas.modelos import Lote, Medicamento, ProductoPorPedir


def productos_por_pedir(
    medicamentos: list[Medicamento],
    lotes: list[Lote],
    hoy: date,
) -> list[ProductoPorPedir]:
    ids = set()
    for m in medicamentos:
        if m.stock_minimo < 0:
            raise ValueError("El mínimo debe ser un número igual o mayor que cero")
        ids.add(m.id)

    v = {}
    for l in lotes:
        if l.cantidad_actual < 0:
            raise ValueError(f"El lote {l.numero_lote} tiene una cantidad negativa")
        if l.medicamento_id not in ids:
            raise ValueError(
                f"El lote {l.numero_lote} es de un medicamento no registrado"
            )
        if l.fecha_vencimiento >= hoy:
            v[l.medicamento_id] = v.get(l.medicamento_id, 0) + l.cantidad_actual

    r = []
    for m in medicamentos:
        if v.get(m.id, 0) < m.stock_minimo:
            r.append(ProductoPorPedir(m.id, m.nombre, v.get(m.id, 0), m.stock_minimo))
    return sorted(r, key=lambda p: p.vigentes)
