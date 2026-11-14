"""Total vendido por tienda, a partir de ventas.csv.

La misma pregunta que ventas_ia.py, con el stack de la clase:
Pydantic v2 valida en la frontera y Polars agrega.

Corre: python practica.py
"""

import csv
from datetime import date
from pathlib import Path

import polars as pl
from pydantic import BaseModel, ConfigDict, Field, ValidationError

RUTA = Path(__file__).parent / "ventas.csv"


class Venta(BaseModel):
    """Una fila de ventas.csv: Pydantic convierte el texto o explica por qué no."""

    model_config = ConfigDict(str_strip_whitespace=True)

    fecha: date
    tienda: str
    producto: str
    cantidad: int = Field(gt=0) #Mayor que 0
    precio: float


def lee_filas(ruta: Path) -> list[dict[str, str]]:
    """Lee el CSV tal cual: cada fila es un dict de textos."""
    with open(ruta, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def valida(filas: list[dict[str, str]]) -> list[Venta]:
    """La frontera: se queda con las filas que cumplen el contrato."""
    buenas: list[Venta] = []
    for fila in filas:
        try:
            buenas.append(Venta.model_validate(fila))
        except ValidationError:
            pass
    return buenas


def total_por_tienda(buenas: list[Venta]) -> pl.DataFrame:
    """Total vendido (cantidad * precio) por tienda, de mayor a menor."""
    df = pl.DataFrame(
        {
            "tienda": [v.tienda for v in buenas],
            "cantidad": [v.cantidad for v in buenas],
            "precio": [v.precio for v in buenas],
        },
        schema={"tienda": pl.String, "cantidad": pl.Int64, "precio": pl.Float64},
    )
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