"""Total vendido por tienda, a partir de ventas.csv.

Corre: python practica.py
"""

import csv
from datetime import date
from pathlib import Path

import polars as pl
from pydantic import BaseModel, ConfigDict, Field, ValidationError

RUTA = Path(__file__).parent / "ventas.csv"


class Venta(BaseModel):
    """Una fila de ventas.csv, validada una vez, en la frontera."""

    model_config = ConfigDict(str_strip_whitespace=True)

    fecha: date
    tienda: str
    producto: str
    cantidad: int = Field(gt=0)
    precio: float = Field(gt=0)


def lee_filas(ruta: Path) -> list[dict[str, str]]:
    """
    Método que lee un archivo csv y devuelve sus filas sin validar.

    :param ruta: Ruta donde se encuentra archivo csv
    :return: Lista con una fila por renglón del csv, sin contar el encabezado

    >>> filas = lee_filas(RUTA)
    >>> len(filas)
    20
    >>> filas[0]["tienda"], filas[0]["cantidad"], filas[0]["precio"]
    ('Centro', '3', '120.50')

    """
    with ruta.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def valida(filas: list[dict[str, str]]) -> list[Venta]:
    """
    Método que convierte cada fila en una un objeto tipo Venta y descarta las inválidas.

    :param filas: Filas crudas
    :return: Lista con las ventas que pasaron la validación, en el orden original

    >>> buena = {"fecha": "2025-01-03", "tienda": "Centro", "producto": "P001",
    ...          "cantidad": "3", "precio": "120.50"}
    >>> sucia = {**buena, "precio": "abc"}
    >>> ventas = valida([buena, sucia])
    >>> len(ventas)
    1
    >>> ventas[0].cantidad, ventas[0].precio
    (3, 120.5)

    """
    buenas = []
    for fila in filas:
        try:
            buenas.append(Venta.model_validate(fila))
        except ValidationError:
            pass  #Si hay una linea sucia no se rompe
    return buenas


def total_por_tienda(buenas: list[Venta]) -> pl.DataFrame:
    """
    Método que suma cantidad * precio por tienda, de mayor a menor.

    :param buenas: Ventas ya validadas, como las devuelve :func:`valida`
    :return: DataFrame con las columnas ``tienda`` y ``total``, una fila por tienda,
        ordenado por ``total`` de forma descendente

    >>> tabla = total_por_tienda(valida(lee_filas(RUTA)))
    >>> tabla.columns
    ['tienda', 'total']
    >>> tabla.row(0)
    ('Santa Fe', 3307.14)

    """
    df = pl.DataFrame([venta.model_dump() for venta in buenas])
    return (
        df.group_by("tienda")
        .agg((pl.col("cantidad") * pl.col("precio")).sum().alias("total"))
        .sort("total", descending=True)
    )


if __name__ == "__main__":
    filas = lee_filas(RUTA)
    buenas = valida(filas)
    print(f"{len(buenas)} de {len(filas)} filas válidas")
    print(total_por_tienda(buenas))
