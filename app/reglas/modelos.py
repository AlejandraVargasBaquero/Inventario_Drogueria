"""Modelos de la capa de reglas de inventario.

Son objetos simples, sin base de datos, para que las reglas se puedan probar solas
(ADR-001). Los campos son los del modelo de datos de la semana 4. Son inmutables
(``frozen=True``) para que ninguna regla pueda cambiar los datos que recibe.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Medicamento:
    """Medicamento registrado en la droguería.

    Attributes:
        id: identificador único.
        nombre: nombre con la presentación, por ejemplo «Acetaminofén 500 mg».
        stock_minimo: cajas por debajo de las cuales hay que pedir (0 = no pedir).
    """

    id: int
    nombre: str
    stock_minimo: int


@dataclass(frozen=True)
class Lote:
    """Lote de un medicamento con su fecha de vencimiento.

    Attributes:
        medicamento_id: id del medicamento al que pertenece.
        numero_lote: código impreso en la caja, por ejemplo «L-0627».
        fecha_vencimiento: último día en que el lote se puede vender.
        cantidad_actual: cajas que quedan del lote.
    """

    medicamento_id: int
    numero_lote: str
    fecha_vencimiento: date
    cantidad_actual: int


@dataclass(frozen=True)
class ProductoPorPedir:
    """Fila de la lista de productos por pedir (resultado de HU-05).

    Attributes:
        medicamento_id: id del medicamento.
        nombre: nombre del medicamento.
        vigentes: cajas de lotes no vencidos.
        minimo: mínimo definido por el dueño.
    """

    medicamento_id: int
    nombre: str
    vigentes: int
    minimo: int

    @property
    def texto(self) -> str:
        """Texto que ve el dueño, por ejemplo «3 de 10 cajas» (HU-05)."""
        return f"{self.vigentes} de {self.minimo} cajas"
