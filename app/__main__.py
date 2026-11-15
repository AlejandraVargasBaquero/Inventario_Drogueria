"""Demostración de HU-05 con los datos del documento de requisitos.

Ejecutar desde la raíz del proyecto con ``python -m app``.
"""

from datetime import date

from app.reglas.modelos import Lote, Medicamento
from app.reglas.pedidos import productos_por_pedir

HOY = date(2026, 10, 24)

MEDICAMENTOS = [
    Medicamento(1, "Acetaminofén 500 mg", 10),
    Medicamento(2, "Amoxicilina 500 mg", 10),
    Medicamento(3, "Ibuprofeno 400 mg", 5),
    Medicamento(4, "Loratadina 10 mg", 10),
]

LOTES = [
    Lote(1, "L-0925", date(2026, 9, 30), 12),  # vencido: no cuenta
    Lote(1, "L-0627", date(2027, 6, 30), 3),
    Lote(2, "AM-11", date(2026, 11, 15), 8),
    Lote(3, "IB-02", date(2027, 3, 1), 2),
    Lote(4, "LO-01", date(2027, 5, 1), 10),  # igual al mínimo: no aparece
]


def main() -> None:
    """Imprime la lista de productos por pedir para la fecha de ejemplo."""
    print(f"Productos por pedir al {HOY:%d/%m/%Y}:")
    for producto in productos_por_pedir(MEDICAMENTOS, LOTES, HOY):
        print(f"- {producto.nombre}: {producto.texto}")


if __name__ == "__main__":
    main()
