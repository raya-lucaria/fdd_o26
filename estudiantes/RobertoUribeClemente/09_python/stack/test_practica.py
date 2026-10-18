"""Las pruebas de practica.py. Corre: pytest -v --no-header test_practica.py

Trae una prueba de ejemplo; copia su forma para escribir las tuyas.
Mientras practica.py no defina Venta, pytest salta este archivo y lo dice.
"""

import pytest
from pydantic import ValidationError

try:
    from practica import Venta, total_por_tienda
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


def test_fila_buena_se_convierte() -> None:
    venta = Venta.model_validate(BUENA)
    assert venta.cantidad == 3
    assert venta.precio == 120.5


def test_fila_sucia_se_rechaza() -> None:
    sucia = {**BUENA, "precio": "abc"}
    with pytest.raises(ValidationError):
        Venta.model_validate(sucia)


def test_sin_ventas_da_tabla_vacia() -> None:
    resultado = total_por_tienda([])
    assert resultado.height == 0
    assert resultado.columns == ["tienda", "total"]