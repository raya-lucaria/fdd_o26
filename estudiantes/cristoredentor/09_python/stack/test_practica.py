"""Las pruebas de practica.py. Corre: pytest -v --no-header test_practica.py

Trae una prueba de ejemplo; copia su forma para escribir las tuyas.
Mientras practica.py no defina Venta, pytest salta este archivo y lo dice.
"""

import pytest

try:
    from pydantic import ValidationError

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


def test_fila_buena_se_convierte() -> None:
    venta = Venta.model_validate(BUENA)
    assert venta.cantidad == 3
    assert venta.precio == 120.5

#Veamos que pasa si añadimos una fila que no cumple con el model_validate 

MALA = {
    "fecha": "Centro", #Error puesto a propósito
    "tienda": "Centro",
    "producto": "P001",
    "cantidad": "*",
    "precio": "120.50",
}

def test_mala_definicion_venta() -> None:
    with pytest.raises(ValidationError) as exc:
        Venta.model_validate(MALA)
    campos = {error["loc"][0] for error in exc.value.errors()}
    assert campos == {"fecha", "cantidad"}

# Caso borde: la fecha tiene el formato correcto (AAAA-MM-DD) pero el día no
# existe. Un regex de formato la dejaría pasar; date sí sabe que febrero no
# tiene 30 días. Viene de ventas.csv (tienda Poniente).

FECHA_INEXISTENTE = {**BUENA, "fecha": "2025-02-30"}


def test_fecha_inexistente_se_rechaza() -> None:
    with pytest.raises(ValidationError) as exc:
        Venta.model_validate(FECHA_INEXISTENTE)
    campos = {error["loc"][0] for error in exc.value.errors()}
    assert campos == {"fecha"}
