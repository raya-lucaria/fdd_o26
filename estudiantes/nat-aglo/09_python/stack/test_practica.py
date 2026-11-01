"""Las pruebas de practica.py. Corre: pytest -v --no-header test_practica.py

Trae una prueba de ejemplo; copia su forma para escribir las tuyas.
Mientras practica.py no defina Venta, pytest salta este archivo y lo dice.
"""
from pydantic import ValidationError
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
<<<<<<< Updated upstream
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
=======
    "fecha": "2025-01-03",
    "tienda": "Centro",
    "producto": "P002",
    "cantidad": "",
    "precio": "122.00" 
>>>>>>> Stashed changes
}

BORDE = {
    "fecha": "2025-01-03",
    "tienda": "Centro",
    "producto": "P003",
    "cantidad": "0",
    "precio": "118.50"
}
def test_fila_buena_se_convierte() -> None:
    venta = Venta.model_validate(BUENA)
    assert venta.cantidad == 3
    assert venta.precio == 120.5

<<<<<<< Updated upstream
def test_fecha_invalida_se_rechaza() -> None:
    with pytest.raises(ValidationError, match="fecha"):
        Venta.model_validate(SUCIA)

def test_cantidad_vacia_es_none() -> None:
    venta = Venta.model_validate(BORDE)
    assert venta.cantidad is None
=======
def test_fila_sucia_error() -> None:
  with pytest.raises(ValidationError, match="cantidad"):
    Venta.model_validate(SUCIA)

def test_fila_borde_cantidad_cero_se_rechaza() -> None:
  with pytest.raises(ValidationError, match="greater_than"):
    Venta.model_validate(BORDE)
>>>>>>> Stashed changes
