"""Total vendido por tienda, a partir de ventas.csv, con el stack de la clase.

Lo mismo que pregunta ventas_ia.py, reescrito:
- Pydantic v2 valida cada fila una vez, en la frontera (la clase Venta).
- Polars agrega con expresiones de columna: ni for ni .apply para sumar.

Corre: uv run python practica.py
"""

import csv
from datetime import date
from pathlib import Path

import polars as pl
from pydantic import BaseModel, ConfigDict, Field, ValidationError

RUTA = Path(__file__).with_name("ventas.csv")

ESQUEMA = {
    "fecha": pl.Date,
    "tienda": pl.String,
    "producto": pl.String,
    "cantidad": pl.Int64,
    "precio": pl.Float64,
}


class Venta(BaseModel):
    """Una fila válida de ventas.csv. Lo que no cumple, no entra."""

    model_config = ConfigDict(str_strip_whitespace=True)

    fecha: date
    tienda: str
    producto: str
    cantidad: int = Field(gt=0)
    precio: float = Field(gt=0)


def lee_validas(ruta: Path) -> tuple[list[Venta], int]:
    """Lee el CSV y valida cada fila. Devuelve las válidas y cuántas filas había."""
    validas: list[Venta] = []
    leidas = 0
    with ruta.open(encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            leidas += 1
            try:
                validas.append(Venta.model_validate(fila))
            except ValidationError:
                continue
    return validas, leidas


def total_por_tienda(ventas: list[Venta]) -> pl.DataFrame:
    """Total (cantidad × precio) por tienda, de mayor a menor."""
    df = pl.DataFrame([v.model_dump() for v in ventas], schema=ESQUEMA)
    return (
        df.group_by("tienda")
        .agg((pl.col("cantidad") * pl.col("precio")).sum().alias("total"))
        .sort("total", descending=True)
    )


def main() -> None:
    validas, leidas = lee_validas(RUTA)
    print(f"{len(validas)} de {leidas} filas válidas")
    print(total_por_tienda(validas))


if __name__ == "__main__":
    main()
