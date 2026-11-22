"""Pruebas de validar_minimo (HU-05, escenario 2 y validaciones de la semana 6).

Regla (oráculo): el mínimo es un número entero de cajas igual o mayor que cero; el 0
significa «no pedir nunca». Si no es entero, el mensaje es «El mínimo debe ser un
número entero de cajas». Si es negativo, «El mínimo debe ser un número igual o mayor
que cero». Los mensajes esperados se escriben aquí a mano, copiados de la regla, y
no se importan del código.
"""

import re

import pytest

from app.reglas.existencias import validar_minimo

MENSAJE_NEGATIVO = "El mínimo debe ser un número igual o mayor que cero"
MENSAJE_NO_ENTERO = "El mínimo debe ser un número entero de cajas"


@pytest.mark.parametrize(
    "minimo, esperado",
    [
        (10, 10),  # partición válida: entero positivo (mínimo del acetaminofén)
        (1, 1),  # límite: primer entero positivo
        (0, 0),  # límite: primer valor válido, «no pedir nunca»
    ],
)
def test_minimo_valido_se_devuelve_igual(minimo, esperado):
    assert validar_minimo(minimo) == esperado


@pytest.mark.parametrize(
    "minimo",
    [
        -1,  # límite: último entero inválido, justo antes del 0
        -2,  # partición negativa: valor del escenario 2 de HU-05
    ],
)
def test_minimo_negativo_lanza_error_del_escenario_2(minimo):
    with pytest.raises(ValueError, match=f"^{re.escape(MENSAJE_NEGATIVO)}$"):
        validar_minimo(minimo)


@pytest.mark.parametrize(
    "minimo",
    [
        "10",  # partición texto: así llega el valor desde un formulario
        "-2",  # texto negativo: primero se revisa el tipo (ambigüedad A-2)
        2.5,  # partición decimal
        10.0,  # decimal con valor entero: tampoco es entero (ambigüedad A-1)
        True,  # booleano: bool es subclase de int en Python (semana 6)
        False,  # booleano que vale 0: no debe pasar como «no pedir nunca»
        None,  # campo vacío
    ],
)
def test_minimo_que_no_es_entero_lanza_error(minimo):
    with pytest.raises(ValueError, match=f"^{re.escape(MENSAJE_NO_ENTERO)}$"):
        validar_minimo(minimo)
