
import csv
from datetime import date
from pathlib import Path

import polars as pl
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

RUTA = Path(__file__).resolve().parent / "ventas.csv"


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
            raise ValueError("la cantidad debe ser positiva")
        return valor


def lee_filas(ruta: str | Path) -> list[dict[str, str]]:
    with open(ruta, encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def valida(filas: list[dict[str, str]]) -> list[Venta]:
    buenas: list[Venta] = []

    for fila in filas:
        try:
            venta = Venta.model_validate(fila)
            buenas.append(venta)
        except ValidationError:
            continue

    return buenas


def total_por_tienda(ventas: list[Venta]) -> pl.DataFrame:
    if not ventas:
        return pl.DataFrame(
            schema={"tienda": pl.String, "total": pl.Float64}
        )

    datos = pl.DataFrame(
        [venta.model_dump() for venta in ventas]
    )

    return (
        datos
        .with_columns(
            (pl.col("cantidad") * pl.col("precio")).alias("total")
        )
        .group_by("tienda")
        .agg(pl.col("total").sum())
        .sort("total", descending=True)
    )


def main() -> None:
    filas = lee_filas(RUTA)
    buenas = valida(filas)

    print(f"{len(buenas)} de {len(filas)} filas válidas")
    print(total_por_tienda(buenas))


if __name__ == "__main__":
    main()

