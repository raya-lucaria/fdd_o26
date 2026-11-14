"""Las pruebas de practica.py. Corre: pytest -v --no-header test_practica.py

Trae una prueba de ejemplo; copia su forma para escribir las tuyas.
Mientras practica.py no defina Venta, pytest salta este archivo y lo dice.
"""

import pytest

try:
    from practica import Venta
except ImportError:
    pytest.skip(
        "practica.py todavía no define Venta",
        allow_module_level=True
    )


# CASO 1: Fila buena
# Comprueba que Pydantic convierte los textos del CSV.

BUENA = {
    "fecha": "2025-01-03",
    "tienda": "Centro",
    "producto": "P001",
    "cantidad": "3",
    "precio": "120.50",
}


def test_fila_buena_se_convierte():
    venta = Venta.model_validate(BUENA)

    assert venta.cantidad == 3
    assert venta.precio == 120.5


# CASO 2: Fila sucia
# Una venta con cantidad negativa debe rechazarse.

SUCIA = {
    "fecha": "2025-01-03",
    "tienda": "Centro",
    "producto": "P002",
    "cantidad": "-5",
    "precio": "120.50",
}


def test_fila_sucia_se_rechaza():
    with pytest.raises(ValueError):
        Venta.model_validate(SUCIA)


# CASO 3: Caso borde
# Una cantidad de cero tampoco representa
# una venta válida.

BORDE = {
    "fecha": "2025-01-03",
    "tienda": "Norte",
    "producto": "P003",
    "cantidad": "0",
    "precio": "50.00",
}


def test_cantidad_cero_se_rechaza():
    with pytest.raises(ValueError):
        Venta.model_validate(BORDE)

