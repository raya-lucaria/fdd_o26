import pytest
from pydantic import ValidationError

try:
    from practica import Venta, total_por_tienda
except ImportError:
    pytest.skip("practica.py todavía no define Venta", allow_module_level=True)

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


def test_cantidad_cero_se_rechaza() -> None:
    cero = {**BUENA, "cantidad": "0"}
    with pytest.raises(ValidationError):
        Venta.model_validate(cero)


def test_total_por_tienda_suma_y_ordena() -> None:
    centro1 = {**BUENA, "tienda": "Centro", "cantidad": "2", "precio": "10"}
    centro2 = {**BUENA, "tienda": "Centro", "cantidad": "1", "precio": "5"}
    norte = {**BUENA, "tienda": "Norte", "cantidad": "1", "precio": "100"}
    ventas = [
        Venta.model_validate(centro1),
        Venta.model_validate(centro2),
        Venta.model_validate(norte),
    ]
    resultado = total_por_tienda(ventas).to_dicts()
    assert resultado == [
        {"tienda": "Norte", "total": 100.0},
        {"tienda": "Centro", "total": 25.0},
    ]