# Tu versión de ventas_ia.py: la misma pregunta, con el stack de la clase.
# Pydantic v2 en la frontera (una clase Venta) y Polars para agregar.
# La prueba de ejemplo de test_practica.py importa Venta de este archivo.
#
# Abre ventas_ia.py al lado: cada pieza de abajo reemplaza una suya.
# La pregunta: total vendido por tienda, sin cantidades inválidas, de mayor
# a menor. Tus totales deben salir iguales a los de `python ventas_ia.py`.

# 1. El contrato: la clase Venta, en la sintaxis de Pydantic v2 (celdas A.4-A.7).

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
    cantidad: int | None
    precio: float

    @field_validator("cantidad")
    @classmethod
    def cantidad_positiva(cls, valor):
        if valor is not None and valor <= 0:
            raise ValueError("La cantidad debe ser positiva")
        return valor

# 2. La frontera: qué filas del CSV entran y cuáles se descartan (A.5, A.9).

RUTA = Path(__file__).parent / "ventas.csv"

def lee_filas(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def valida(filas: list[dict]) -> list[dict]:
    buenas = []

    for fila in filas:
        try:
            venta = Venta.model_validate(fila)
            buenas.append(venta.model_dump())
        except ValidationError:
            pass

    return buenas

# 3. La suma por tienda con Polars, sin for ni .apply (B.1, B.2).

def total_por_tienda(buenas: list[dict]) -> pl.DataFrame:
    df = pl.DataFrame(buenas)

    return (
        df.with_columns(
            (pl.col("cantidad") * pl.col("precio")).alias("total")
        )
        .group_by("tienda")
        .agg(pl.col("total").sum())
        .sort("total", descending=True)
    )

# 4. Un main que imprima el resultado, para compararlo con ventas_ia.py.

if __name__ == "__main__":
    filas = lee_filas(RUTA)
    buenas = valida(filas)

    print(f"{len(buenas)} de {len(filas)} filas válidas")
    print(total_por_tienda(buenas))