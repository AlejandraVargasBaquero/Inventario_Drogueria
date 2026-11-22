"""Conversión del texto de los formularios a los tipos que esperan las reglas.

Ambigüedad A-1 (semana 7): la capa de reglas solo acepta enteros; aquí se convierte
el texto. Si el texto no es un entero se devuelve None para que la regla muestre su
propio mensaje («El mínimo debe ser un número entero de cajas»).
"""

import re
from datetime import date

ENTERO = re.compile(r"-?\d+")
FECHA_ISO = re.compile(r"\d{4}-\d{2}-\d{2}")


def texto_a_entero(texto: str | None) -> int | None:
    """«10» → 10, « -2 » → -2; «», «abc», «2.5» y «10.0» → None."""
    limpio = (texto or "").strip()
    return int(limpio) if ENTERO.fullmatch(limpio) else None


def texto_a_fecha(texto: str | None) -> date | None:
    """«2027-06-30» (lo que envía un campo de tipo date) → date; si no, None."""
    limpio = (texto or "").strip()
    if not FECHA_ISO.fullmatch(limpio):
        return None
    try:
        return date.fromisoformat(limpio)
    except ValueError:  # por ejemplo 2027-02-30
        return None
