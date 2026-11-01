# Tu versión de ventas_ia.py: la misma pregunta, con el stack de la clase.
# Pydantic v2 en la frontera (una clase Venta) y Polars para agregar.
# La prueba de ejemplo de test_practica.py importa Venta de este archivo.

import pathlib
from datetime import date
from pathlib import Path
from typing import Any

import polars as pl
from pydantic import BaseModel, ConfigDict, Field, ValidationError

RUTA = pathlib.Path(__file__).resolve().parent / "ventas.csv"

class Venta(BaseModel):
    model_config = ConfigDict( # otro cambio
        str_strip_whitespace = True # v2 quito el any
    )
    fecha: date
    tienda: str
    producto: str
    cantidad: int | None = Field(default = None, gt = 0)
    # Otra forma de agregar un valor por default y validar con v2
    precio: float = Field(gt = 0)

def lee_filas(ruta: str | Path) -> list[dict[str, Any]]:
    return pl.read_csv(ruta).to_dicts()
#segun gemini, el metodo de polars es cache-friendly, es mas rapido

def valida(filas: list[dict[str,Any]]) -> list[dict[str,Any]]:
    buenas = []
    for fila in filas:
        try:
            buenas.append(Venta(**fila).model_dump()) # .dict() a .model_dump()
        except ValidationError:
            pass
    return buenas

"""
Recomendacion de gemini(comentarios para mi):
- cambiar Venta(**fila) a Venta.model_validate(fila)
Razon:
- ya no se desempaqueta el diccionario para pasar los argumentos por separado.
En la nueva version, pydantic se lo pasa directamente a su motor interno Rust
que los revisa sin pasos intermedios.

def valida(filas: list[dict[str,Any]]) -> list[dict[str,Any]]:
    buenas = []
    for fila in filas:
        try:
            buenas.append(Venta.model_validate(fila).model_dump())
        except ValidationError:
            pass
        return buenas
""" 
def total_por_tienda(buenas:list[dict[str, Any]]) -> pl.DataFrame: # cambio a polars
    return (
    pl.DataFrame(buenas)
    .with_columns((pl.col("cantidad") * pl.col("precio")).alias("total"))
    .group_by("tienda")
    .agg(pl.col("total").sum())
    .sort("total", descending = True)  
    )

if __name__ == "__main__":
    filas = lee_filas(RUTA)
    buenas = valida(filas)
    print(f"{len(buenas)} de {len(filas)} filas válidas")
    print(total_por_tienda(buenas))
