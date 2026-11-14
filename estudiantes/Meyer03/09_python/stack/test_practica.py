"""Las pruebas de practica.py. Corre: pytest -v --no-header test_practica.py

Una fila buena, una fila sucia, casos borde en el límite del contrato, y la
pregunta completa sobre ventas.csv comparada con lo que da ventas_ia.py.
Mientras practica.py no defina Venta, pytest salta este archivo y lo dice.
"""

import pytest
from pydantic import ValidationError

try:
    from practica import RUTA, Venta, lee_filas, total_por_tienda, valida
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
    # La fila de Sur del 2025-01-08 en ventas.csv: el precio dice "abc".
    sucia = {**BUENA, "tienda": "Sur", "precio": "abc"}
    with pytest.raises(ValidationError) as error:
        Venta.model_validate(sucia)
    assert error.value.errors()[0]["loc"] == ("precio",)
    assert error.value.errors()[0]["type"] == "float_parsing"


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        pytest.param("cantidad", "0", id="cantidad-cero"),
        pytest.param("cantidad", "", id="cantidad-vacia"),
        pytest.param("fecha", "2025-02-30", id="fecha-30-de-febrero"),
    ],
)
def test_caso_borde_se_rechaza(campo: str, valor: str) -> None:
    with pytest.raises(ValidationError) as error:
        Venta.model_validate({**BUENA, campo: valor})
    assert error.value.errors()[0]["loc"] == (campo,)


def test_espacios_alrededor_se_quitan() -> None:
    venta = Venta.model_validate({**BUENA, "tienda": "  Centro  "})
    assert venta.tienda == "Centro"


def test_totales_iguales_a_ventas_ia() -> None:
    ventas, descartadas = valida(lee_filas(RUTA))
    totales = total_por_tienda(ventas)
    assert len(ventas) == 16
    assert len(descartadas) == 4
    assert totales["tienda"].to_list()[:3] == ["Santa Fe", "Polanco", "Centro"]
    assert totales["total"].to_list()[0] == pytest.approx(3307.14)
