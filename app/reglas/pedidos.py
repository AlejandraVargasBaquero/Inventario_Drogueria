"""HU-05. Productos bajo el mínimo. Ver el contrato en el README."""

from datetime import date

from app.reglas.modelos import Lote, Medicamento, ProductoPorPedir

MENSAJE_MINIMO_INVALIDO = "El mínimo debe ser un número igual o mayor que cero"
MENSAJE_MINIMO_NO_ENTERO = "El mínimo debe ser un número entero de cajas"
MENSAJE_ID_REPETIDO = "El medicamento con id {id} está repetido"
MENSAJE_CANTIDAD_NO_ENTERA = "El lote {lote} tiene una cantidad que no es entera"
MENSAJE_CANTIDAD_NEGATIVA = "El lote {lote} tiene una cantidad negativa"
MENSAJE_LOTE_SIN_MEDICAMENTO = "El lote {lote} es de un medicamento no registrado"


def productos_por_pedir(
    medicamentos: list[Medicamento],
    lotes: list[Lote],
    hoy: date,
) -> list[ProductoPorPedir]:
    """Devuelve los medicamentos con menos cajas vigentes que su mínimo (HU-05).

    Un lote es vigente si ``fecha_vencimiento >= hoy``; los vencidos no cuentan
    aunque no se hayan dado de baja. «Por debajo» es menor estricto: con 10 de 10
    el medicamento no aparece. Un mínimo de 0 significa «no pedir nunca».

    Args:
        medicamentos: medicamentos registrados, cada uno con id único y un
            ``stock_minimo`` entero mayor o igual que cero.
        lotes: lotes de esos medicamentos, con ``cantidad_actual`` entera mayor o
            igual que cero.
        hoy: fecha contra la que se decide qué lote está vencido.

    Returns:
        Una lista nueva de ``ProductoPorPedir`` ordenada de menor a mayor cantidad
        vigente; con empate se conserva el orden de ``medicamentos``. Las listas
        recibidas no se modifican.

    Raises:
        ValueError: si un mínimo no es entero o es negativo, si hay dos
            medicamentos con el mismo id, o si un lote tiene una cantidad no
            entera o negativa o es de un medicamento que no está en la lista.
    """
    _validar_medicamentos(medicamentos)
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


def _es_entero(valor: object) -> bool:
    """Indica si ``valor`` es un entero de verdad.

    ``bool`` es subclase de ``int`` en Python, así que True y False se excluyen.
    """
    return isinstance(valor, int) and not isinstance(valor, bool)


def _validar_medicamentos(medicamentos: list[Medicamento]) -> None:
    """Comprueba que los ids no se repitan y que cada mínimo sea un entero >= 0.

    Raises:
        ValueError: con el primer problema encontrado.
    """
    ids_vistos: set[int] = set()
    for medicamento in medicamentos:
        if medicamento.id in ids_vistos:
            raise ValueError(MENSAJE_ID_REPETIDO.format(id=medicamento.id))
        ids_vistos.add(medicamento.id)
        if not _es_entero(medicamento.stock_minimo):
            raise ValueError(MENSAJE_MINIMO_NO_ENTERO)
        if medicamento.stock_minimo < 0:
            raise ValueError(MENSAJE_MINIMO_INVALIDO)


def _cajas_vigentes_por_medicamento(
    lotes: list[Lote], ids_registrados: set[int], hoy: date
) -> dict[int, int]:
    """Valida cada lote y suma las cajas vigentes de cada medicamento en una pasada.

    Args:
        lotes: lotes por revisar.
        ids_registrados: ids de los medicamentos recibidos.
        hoy: un lote que vence hoy todavía cuenta como vigente.

    Returns:
        Diccionario ``{medicamento_id: cajas vigentes}``. Un medicamento sin lotes
        vigentes no aparece en él.

    Raises:
        ValueError: si un lote tiene una cantidad no entera o negativa, o es de un
            medicamento que no está registrado.
    """
    vigentes: dict[int, int] = {}
    for lote in lotes:
        if not _es_entero(lote.cantidad_actual):
            raise ValueError(MENSAJE_CANTIDAD_NO_ENTERA.format(lote=lote.numero_lote))
        if lote.cantidad_actual < 0:
            raise ValueError(MENSAJE_CANTIDAD_NEGATIVA.format(lote=lote.numero_lote))
        if lote.medicamento_id not in ids_registrados:
            raise ValueError(
                MENSAJE_LOTE_SIN_MEDICAMENTO.format(lote=lote.numero_lote)
            )
        if lote.fecha_vencimiento >= hoy:
            vigentes[lote.medicamento_id] = (
                vigentes.get(lote.medicamento_id, 0) + lote.cantidad_actual
            )
    return vigentes
