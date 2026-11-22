"""Reglas de existencias que usan HU-05 y las siguientes historias.

Semana 7: se sacaron de ``pedidos.py`` para poder probarlas por separado. Las
reglas son las del contrato de HU-05 en el README (supuestos 1, 2 y 4, escenario 2
y las validaciones de la semana 6). No cambian el comportamiento de
``productos_por_pedir``.
"""

from datetime import date

from app.reglas.modelos import Lote

MENSAJE_MINIMO_INVALIDO = "El mínimo debe ser un número igual o mayor que cero"
MENSAJE_MINIMO_NO_ENTERO = "El mínimo debe ser un número entero de cajas"
MENSAJE_CANTIDAD_NO_ENTERA = "El lote {lote} tiene una cantidad que no es entera"
MENSAJE_CANTIDAD_NEGATIVA = "El lote {lote} tiene una cantidad negativa"


def es_entero(valor: object) -> bool:
    """Indica si ``valor`` es un entero de verdad.

    ``bool`` es subclase de ``int`` en Python, así que True y False se excluyen.
    """
    return isinstance(valor, int) and not isinstance(valor, bool)


def validar_minimo(minimo: object) -> int:
    """Valida el mínimo de cajas que define el dueño (HU-05, escenario 2).

    Regla: el mínimo es un número entero de cajas igual o mayor que cero. El 0
    significa «no pedir nunca».

    Args:
        minimo: el valor que se quiere guardar como mínimo.

    Returns:
        El mismo mínimo, cuando es válido.

    Raises:
        ValueError: «El mínimo debe ser un número entero de cajas» si no es un
            entero (texto, decimal, booleano o None), o «El mínimo debe ser un
            número igual o mayor que cero» si es negativo.
    """
    if not es_entero(minimo):
        raise ValueError(MENSAJE_MINIMO_NO_ENTERO)
    if minimo < 0:
        raise ValueError(MENSAJE_MINIMO_INVALIDO)
    return minimo


def validar_cantidad(lote: Lote) -> None:
    """Comprueba que la cantidad del lote sea un entero mayor o igual que cero.

    Raises:
        ValueError: si la cantidad no es entera o es negativa. El mensaje dice el
            número de lote.
    """
    if not es_entero(lote.cantidad_actual):
        raise ValueError(MENSAJE_CANTIDAD_NO_ENTERA.format(lote=lote.numero_lote))
    if lote.cantidad_actual < 0:
        raise ValueError(MENSAJE_CANTIDAD_NEGATIVA.format(lote=lote.numero_lote))


def es_vigente(lote: Lote, hoy: date) -> bool:
    """Un lote es vigente si ``fecha_vencimiento >= hoy`` (el que vence hoy cuenta)."""
    return lote.fecha_vencimiento >= hoy


def cajas_vigentes(medicamento_id: int, lotes: list[Lote], hoy: date) -> int:
    """Suma las cajas vigentes de un medicamento (supuestos 1, 2 y 4 de HU-05).

    Regla: la cantidad vigente es la suma de ``cantidad_actual`` de los lotes del
    medicamento con ``fecha_vencimiento >= hoy``. Los vencidos no cuentan aunque
    no se hayan dado de baja. Sin lotes, la cantidad es 0.

    Args:
        medicamento_id: id del medicamento.
        lotes: lotes de cualquier medicamento; solo se leen los de este.
        hoy: fecha contra la que se decide qué lote está vencido.

    Returns:
        Las cajas vigentes (entero >= 0).

    Raises:
        ValueError: si un lote de este medicamento, vigente o vencido, tiene una
            cantidad no entera o negativa.
    """
    total = 0
    for lote in lotes:
        if lote.medicamento_id != medicamento_id:
            continue
        validar_cantidad(lote)
        if es_vigente(lote, hoy):
            total += lote.cantidad_actual
    return total
