"""Las pruebas de practica.py. Corre: pytest -v --no-header test_practica.py

Trae una prueba de ejemplo; copia su forma para escribir las tuyas.
Mientras practica.py no defina Venta, pytest salta este archivo y lo dice.
"""

import pytest
from pydantic import ValidationError

from practica import Venta

BUENA = {
    "fecha": "2025-01-03",
    "tienda": "Centro",
    "producto": "P001",
    "cantidad": "3",
    "precio": "120.50",
}


def test_fila_buena_se_convierte() -> None:
    venta = Venta.model_validate(BUENA)
    assert venta.cantidad == 3
    assert venta.precio == 120.5


def test_fila_sucia_cantidad_invalida() -> None:
    fila = {
        "fecha": "2025-01-03",
        "tienda": "Centro",
        "producto": "P001",
        "cantidad": "abc",
        "precio": "120.50",
    }

    with pytest.raises(ValidationError):
        Venta.model_validate(fila)


def test_cantidad_cero_se_rechaza() -> None:
    fila = {
        "fecha": "2025-01-03",
        "tienda": "Centro",
        "producto": "P001",
        "cantidad": "0",
        "precio": "120.50",
    }

    with pytest.raises(ValidationError):
        Venta.model_validate(fila)