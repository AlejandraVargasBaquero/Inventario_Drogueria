"""Pruebas de validar_minimo (HU-05, escenario 2)."""

import pytest

from app.reglas.existencias import validar_minimo


@pytest.mark.parametrize(
    "minimo, esperado",
    [
        (10, 10),  # partición válida: entero positivo
        (0, 0),  # límite: el cero es válido («no pedir nunca»)
        (1, 1),  # límite: primer entero positivo
        (500, 500),  # entero grande
    ],
)
def test_minimo_valido_se_devuelve(minimo, esperado):
    assert validar_minimo(minimo) == esperado


@pytest.mark.parametrize(
    "minimo",
    [
        -2,  # escenario 2 de HU-05
        -1,  # límite: último entero inválido
        -100,  # negativo grande
    ],
)
def test_minimo_negativo_lanza_error(minimo):
    with pytest.raises(ValueError):
        validar_minimo(minimo)


@pytest.mark.parametrize(
    "minimo",
    [
        "10",  # texto
        2.5,  # decimal
        None,  # vacío
    ],
)
def test_minimo_no_entero_lanza_error(minimo):
    with pytest.raises(ValueError, match="entero"):
        validar_minimo(minimo)


def test_validar_minimo_devuelve_un_entero():
    assert isinstance(validar_minimo(7), int)
