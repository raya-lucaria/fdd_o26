import csv
from datetime import date
from pathlib import Path

import polars as pl
from pydantic import BaseModel, ConfigDict, Field, ValidationError

RUTA = Path(__file__).parent / "ventas.csv"


class Venta(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    fecha: date
    tienda: str
    producto: str
    cantidad: int = Field(gt=0)
    precio: float


def lee_filas(ruta: Path) -> list[dict[str, str]]:
    with open(ruta, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def valida(filas: list[dict[str, str]]) -> tuple[list[Venta], int]:
    buenas: list[Venta] = []
    rechazadas = 0
    for fila in filas:
        try:
            buenas.append(Venta.model_validate(fila))
        except ValidationError:
            rechazadas += 1
    return buenas, rechazadas


def total_por_tienda(ventas: list[Venta]) -> pl.DataFrame:
    tabla = pl.DataFrame(
        {
            "tienda": [v.tienda for v in ventas],
            "cantidad": [v.cantidad for v in ventas],
            "precio": [v.precio for v in ventas],
        }
    )
    tabla = tabla.with_columns((pl.col("cantidad") * pl.col("precio")).alias("total"))
    tabla = tabla.group_by("tienda").agg(pl.col("total").sum())
    return tabla.sort("total", descending=True)


if __name__ == "__main__":
    filas = lee_filas(RUTA)
    buenas, rechazadas = valida(filas)
    print(f"{len(buenas)} de {len(filas)} filas válidas ({rechazadas} rechazadas)")
    print(total_por_tienda(buenas))