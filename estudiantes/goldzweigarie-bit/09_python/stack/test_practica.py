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


def test_fila_sucia_precio_abc_se_rechaza() -> None:
    # La fila de Sur en ventas.csv trae precio "abc".
    with pytest.raises(ValidationError):
        Venta.model_validate({**BUENA, "precio": "abc"})


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("fecha", "2025-02-30"),  # el 30 de febrero no existe
        ("cantidad", "-2"),  # cantidad negativa
        ("cantidad", ""),  # cantidad vacía
    ],
)
def test_caso_borde_se_rechaza(campo: str, valor: str) -> None:
    with pytest.raises(ValidationError):
        Venta.model_validate({**BUENA, campo: valor})


def test_total_por_tienda_suma_y_ordena() -> None:
    norte = {**BUENA, "tienda": "Norte", "cantidad": "1", "precio": "45"}
    otra_centro = {**BUENA, "cantidad": "2", "precio": "10"}
    ventas = [
        Venta.model_validate(BUENA),  # Centro: 3 × 120.50 = 361.50
        Venta.model_validate(norte),  # Norte: 1 × 45 = 45
        Venta.model_validate(otra_centro),  # Centro: + 2 × 10 = 381.50
    ]
    filas = total_por_tienda(ventas).to_dicts()
    assert filas == [
        {"tienda": "Centro", "total": 381.5},
        {"tienda": "Norte", "total": 45.0},
    ]


def test_sin_ventas_da_tabla_vacia() -> None:
    assert total_por_tienda([]).height == 0
