"""HU-05. Productos bajo el mínimo. Ver el contrato en el README."""

from datetime import date

from app.reglas.existencias import es_vigente, validar_cantidad, validar_minimo
from app.reglas.modelos import Lote, Medicamento, ProductoPorPedir

MENSAJE_ID_REPETIDO = "El medicamento con id {id} está repetido"
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
        validar_minimo(medicamento.stock_minimo)


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
        validar_cantidad(lote)
        if lote.medicamento_id not in ids_registrados:
            raise ValueError(
                MENSAJE_LOTE_SIN_MEDICAMENTO.format(lote=lote.numero_lote)
            )
        if es_vigente(lote, hoy):
            vigentes[lote.medicamento_id] = (
                vigentes.get(lote.medicamento_id, 0) + lote.cantidad_actual
            )
    return vigentes
