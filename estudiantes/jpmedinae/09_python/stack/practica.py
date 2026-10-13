import csv
from datetime import date
from pathlib import Path

import polars as pl
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator


class Venta(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    fecha: date
    tienda: str
    producto: str
    cantidad: int
    precio: float

    @field_validator("cantidad")
    @classmethod
    def cantidad_positiva(cls, valor: int) -> int:
        if valor <= 0:
            raise ValueError("La cantidad debe ser positiva")
        return valor

RUTA = Path(__file__).parent / "ventas.csv"


def lee_filas(ruta: Path) -> list[dict[str, str]]:
    with ruta.open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))

def valida(filas: list[dict[str, str]]) -> list[Venta]:
    buenas = []

    for fila in filas:
        try:
            venta = Venta.model_validate(fila)
            buenas.append(venta)
        except ValidationError:
            continue

    return buenas

def total_por_tienda(buenas: list[Venta]) -> pl.DataFrame:
    datos = [venta.model_dump() for venta in buenas]

    df = pl.DataFrame(datos)

    return (
        df.with_columns(
            (pl.col("cantidad") * pl.col("precio")).alias("total")
        )
        .group_by("tienda")
        .agg(pl.col("total").sum())
        .sort("total", descending=True)
    )