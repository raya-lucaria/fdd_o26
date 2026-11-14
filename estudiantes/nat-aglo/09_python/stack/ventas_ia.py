"""Total vendido por tienda, a partir de ventas.csv.

Así lo escribió una IA a la que no se le dijo qué stack usar: eligió lo que
más vio. Corre con las versiones de este proyecto, con avisos de deprecación.
No lo arregles aquí: tu versión va en practica.py.

Corre: python ventas_ia.py
"""

import csv
import os
from datetime import date
from typing import Dict, List, Optional

import pandas as pd
from pydantic import BaseModel, ValidationError, validator

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ventas.csv")


class Venta(BaseModel):
    fecha: date
    tienda: str
    producto: str
    cantidad: Optional[int]
    precio: float

    class Config:
        anystr_strip_whitespace = True

    @validator("cantidad")
    def cantidad_positiva(cls, v):
        if v is not None and v <= 0:
            raise ValueError("la cantidad debe ser positiva")
        return v


def lee_filas(ruta: str) -> List[Dict]:
    filas = []
    with open(ruta, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            filas.append(fila)
    return filas


def valida(filas: List[Dict]) -> List[Dict]:
    buenas = []
    for fila in filas:
        try:
            buenas.append(Venta(**fila).dict())
        except ValidationError:
            pass
    return buenas


def total_por_tienda(buenas: List[Dict]) -> pd.Series:
    df = pd.DataFrame(buenas)
    df["total"] = df.apply(lambda fila: fila["cantidad"] * fila["precio"], axis=1)
    return df.groupby("tienda")["total"].sum().sort_values(ascending=False)


if __name__ == "__main__":
    filas = lee_filas(RUTA)
    buenas = valida(filas)
    print(f"{len(buenas)} de {len(filas)} filas válidas")
    print(total_por_tienda(buenas))
