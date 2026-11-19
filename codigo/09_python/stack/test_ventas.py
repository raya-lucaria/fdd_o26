"""Tres pruebas del contrato Venta. Corre: pytest test_ventas.py"""

import pytest
from pydantic import ValidationError

from modelos import Venta

# Una fila buena de ventas.csv, tal como llega del CSV: todo es texto.
BUENA = {
    "fecha": "2025-01-03",
    "tienda": "Centro",
    "producto": "P001",
    "cantidad": "3",
    "precio": "120.50",
}


def test_fila_buena_se_convierte() -> None:
    venta = Venta.model_validate(BUENA)
    # Pydantic convirtió los textos a los tipos del contrato.
    assert venta.cantidad == 3
    assert venta.precio == 120.5


def test_precio_abc_se_rechaza() -> None:
    with pytest.raises(ValidationError, match="precio"):
        Venta.model_validate({**BUENA, "precio": "abc"})


def test_precio_negativo_se_rechaza() -> None:
    with pytest.raises(ValidationError, match="greater_than"):
        Venta.model_validate({**BUENA, "precio": "-5"})
