"""Total vendido por tienda, a partir de ventas.csv, con el stack de la clase.

La misma pregunta que ventas_ia.py: total vendido por tienda, sin cantidades
inválidas, de mayor a menor. Pydantic v2 valida una vez, en la frontera (la
clase Venta); adentro se confía, y Polars agrega con expresiones.

Corre: python practica.py
"""

import csv
from datetime import date
from pathlib import Path

import polars as pl
from pydantic import BaseModel, ConfigDict, Field, ValidationError

RUTA = Path(__file__).parent / "ventas.csv"

# Los tipos de la tabla los fija el contrato, no los adivina el motor.
ESQUEMA: dict[str, pl.DataType] = {
    "fecha": pl.Date(),
    "tienda": pl.String(),
    "producto": pl.String(),
    "cantidad": pl.Int64(),
    "precio": pl.Float64(),
}


# 1. El contrato, con la sintaxis de Pydantic v2.
class Venta(BaseModel):
    """Una fila válida de ventas.csv."""

    model_config = ConfigDict(str_strip_whitespace=True)

    fecha: date
    tienda: str
    producto: str
    cantidad: int = Field(gt=0)  # vacía, cero o negativa: no entra
    precio: float = Field(gt=0)


def lee_filas(ruta: Path) -> list[dict[str, str]]:
    """Lee el CSV tal cual llega: cada fila es un dict de textos."""
    with ruta.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# 2. La frontera: el contrato decide qué fila entra; ninguna se tira en silencio.
def valida(filas: list[dict[str, str]]) -> tuple[list[Venta], list[str]]:
    """Regresa las ventas válidas y, por cada fila descartada, por qué."""
    ventas: list[Venta] = []
    descartadas: list[str] = []
    for linea, fila in enumerate(filas, start=2):  # la línea 1 es el encabezado
        try:
            ventas.append(Venta.model_validate(fila))
        except ValidationError as error:
            motivos = ", ".join(
                f"{e['loc'][0]} ({e['type']})" for e in error.errors()
            )
            descartadas.append(f"línea {linea}: {motivos}")
    return ventas, descartadas


# 3. La suma por tienda con Polars: una expresión sobre columnas, sin .apply.
def total_por_tienda(ventas: list[Venta]) -> pl.DataFrame:
    """Total vendido (cantidad * precio) por tienda, de mayor a menor."""
    tabla = pl.DataFrame([v.model_dump() for v in ventas], schema=ESQUEMA)
    return (
        tabla.group_by("tienda")
        .agg((pl.col("cantidad") * pl.col("precio")).sum().alias("total"))
        .sort("total", descending=True)
    )


# 4. El main, para comparar con `python ventas_ia.py`.
if __name__ == "__main__":
    filas = lee_filas(RUTA)
    ventas, descartadas = valida(filas)
    print(f"{len(ventas)} de {len(filas)} filas válidas")
    for motivo in descartadas:
        print(f"  descartada · {motivo}")
    print(total_por_tienda(ventas))
