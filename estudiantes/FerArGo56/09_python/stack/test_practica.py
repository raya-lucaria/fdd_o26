"""Las pruebas de practica.py. Corre: pytest -v --no-header test_practica.py"""

import pytest
from pydantic import ValidationError

from practica import Venta, total_por_tienda, valida

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
    sucia = {**BUENA, "cantidad": "-3"}
    with pytest.raises(ValidationError):
        Venta.model_validate(sucia)


def test_borde_espacios_y_total() -> None:
    filas = [
        {**BUENA, "tienda": "  Centro  ", "cantidad": "2", "precio": "10"},
        {**BUENA, "cantidad": "0"},  # inválida: se descarta
    ]
    buenas = valida(filas)
    assert len(buenas) == 1

    resultado = total_por_tienda(buenas)
    assert resultado["tienda"][0] == "Centro"
    assert resultado["total"][0] == 20.0