"""Las pruebas de practica.py. Corre: pytest -v --no-header test_practica.py

Trae una prueba de ejemplo; copia su forma para escribir las tuyas.
Mientras practica.py no defina Venta, pytest salta este archivo y lo dice.
"""
import pytest
from pydantic import ValidationError

try:
    from practica import Venta
except ImportError:
    pytest.skip("practica.py todavía no define Venta", allow_module_level=True)

# Una fila buena de ventas.csv, tal como llega del CSV: todo es texto.
BUENA = {
    "fecha": "2025-01-03",
    "tienda": "Centro",
    "producto": "P001",
    "cantidad": "3",
    "precio": "120.50",
}

SUCIA = {

    "fecha": "03-01-2025",
    "tienda": "Centro",
    "producto": "1234",
    "cantidad": "4",
    "precio": "200.50"
}

BORDE = {
    "fecha": "2025-01-03",
    "tienda": "Centro",
    "producto": "P002",
    "cantidad": None,
    "precio": "300.00",

}

def test_fila_buena_se_convierte() -> None:
    venta = Venta.model_validate(BUENA)
    assert venta.cantidad == 3
    assert venta.precio == 120.5

def test_fila_sucia_error() -> None:
    with pytest.raises(ValidationError):
        Venta.model_validate(SUCIA)

def test_cantidad_vacia_es_none() -> None:
    venta = Venta.model_validate(BORDE)
    assert venta.cantidad is None
