"""Modelos de la capa de reglas de inventario.

Son objetos simples, sin base de datos, para que las reglas se puedan probar solas
(ADR-001). Los campos son los del modelo de datos de la semana 4.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Medicamento:
    id: int
    nombre: str
    stock_minimo: int


@dataclass(frozen=True)
class Lote:
    medicamento_id: int
    numero_lote: str
    fecha_vencimiento: date
    cantidad_actual: int


@dataclass(frozen=True)
class ProductoPorPedir:
    medicamento_id: int
    nombre: str
    vigentes: int
    minimo: int

    @property
    def texto(self) -> str:
        """Texto que ve el dueño, por ejemplo «3 de 10 cajas» (HU-05)."""
        return f"{self.vigentes} de {self.minimo} cajas"
