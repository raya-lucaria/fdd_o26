# Tu versión de ventas_ia.py: la misma pregunta, con el stack de la clase.
# Pydantic v2 en la frontera (una clase Venta) y Polars para agregar.
# La prueba de ejemplo de test_practica.py importa Venta de este archivo.
"""Total vendido por tienda usando Pydantic v2 y Polars.

Las filas del CSV se validan en la frontera con Pydantic.
Después, Polars calcula el total vendido por tienda y lo ordena
de mayor a menor.

Corre:
    python practica.py
"""

import csv
from collections.abc import Iterable, Mapping, Sequence
from datetime import date
from pathlib import Path

import polars as pl
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

RUTA = Path(__file__).with_name("ventas.csv")


class Venta(BaseModel):
    """Una venta válida proveniente del archivo CSV."""

    model_config = ConfigDict(str_strip_whitespace=True)

    fecha: date
    tienda: str
    producto: str
    cantidad: int
    precio: float

    @field_validator("cantidad")
    @classmethod
    def cantidad_positiva(cls, valor: int) -> int:
        """Rechaza cantidades iguales o menores que cero."""
        if valor <= 0:
            raise ValueError("la cantidad debe ser positiva")
        return valor


def lee_filas(ruta: Path) -> list[dict[str, str]]:
    """Lee las filas del CSV sin intentar validarlas todavía."""
    with ruta.open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def valida(filas: Iterable[Mapping[str, str]]) -> list[Venta]:
    """Valida las filas y conserva solamente las ventas correctas."""
    buenas: list[Venta] = []

    for fila in filas:
        try:
            buenas.append(Venta.model_validate(fila))
        except ValidationError:
            continue

    return buenas


def total_por_tienda(ventas: Sequence[Venta]) -> pl.DataFrame:
    """Calcula el total vendido por tienda, de mayor a menor."""
    datos = [
        {
            "tienda": venta.tienda,
            "cantidad": venta.cantidad,
            "precio": venta.precio,
        }
        for venta in ventas
    ]

    if not datos:
        return pl.DataFrame(
            schema={
                "tienda": pl.String,
                "total": pl.Float64,
            }
        )

    return (
        pl.DataFrame(datos)
        .with_columns(
            (pl.col("cantidad") * pl.col("precio")).alias("total")
        )
        .group_by("tienda")
        .agg(pl.col("total").sum())
        .sort("total", descending=True)
    )


def main() -> None:
    """Ejecuta el análisis completo."""
    filas = lee_filas(RUTA)
    buenas = valida(filas)

    print(f"{len(buenas)} de {len(filas)} filas válidas")
    print(total_por_tienda(buenas))


if __name__ == "__main__":
    main()
