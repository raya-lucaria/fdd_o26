# Tu versión de ventas_ia.py: la misma pregunta, con el stack de la clase.
# Pydantic v2 en la frontera (una clase Venta) y Polars para agregar.
# La prueba de ejemplo de test_practica.py importa Venta de este archivo.

import csv
import os
from datetime import date

import polars as pl
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ventas.csv")


class Venta(BaseModel):
    fecha: date
    tienda: str
    producto: str
    cantidad: int | None
    precio: float

    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("cantidad")
    @classmethod
    def cantidad_positiva(cls, v):
        if v is not None and v <= 0:
            raise ValueError("la cantidad debe ser positiva")
        return v


def lee_filas(ruta: str) -> list[dict]:
    filas = []
    with open(ruta, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            filas.append(fila)
    return filas


def valida(filas: list[dict]) -> list[dict]:
    buenas = []
    for fila in filas:
        try:
            venta = Venta.model_validate(fila)
            buenas.append(venta.model_dump())
        except ValidationError:
            pass
    return buenas


def total_por_tienda(buenas: list[dict]) -> pl.DataFrame:
    df = pl.DataFrame(buenas)
    df = df.with_columns(
        (pl.col("cantidad") * pl.col("precio")).alias("total")
    )
    return (
        df.group_by("tienda")
        .agg(pl.col("total").sum())
        .sort("total", descending=True)
    )
if __name__ == "__main__":
    filas = lee_filas(RUTA)
    buenas = valida(filas)
    print(f"{len(buenas)} de {len(filas)} filas válidas")
    print(total_por_tienda(buenas))
