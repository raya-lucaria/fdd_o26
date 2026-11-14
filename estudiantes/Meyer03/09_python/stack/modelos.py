"""El contrato de una venta, y tres errores plantados para las herramientas.

- Venta: una fila de ventas.csv validada por Pydantic.
- total: la misma función de la celda A.2; la llamada de abajo le pasa
  textos en vez de números. Python no la revisa; mypy sí, sin correrla.
- Plantados para ruff: un import que nadie usa (F401) y un `== None` (E711).
"""

import json
from datetime import date

from pydantic import BaseModel, Field


class Venta(BaseModel):
    """Una fila de ventas. Pydantic convierte "12.50" → 12.5 o explica por qué no."""

    fecha: date
    tienda: str
    producto: str
    cantidad: int = Field(gt=0)  # gt = greater than: estrictamente mayor que 0
    precio: float = Field(gt=0)


def total(precios: list[float]) -> float:
    """Suma los precios. La anotación dice list[float]; Python no la revisa."""
    return sum(precios)


def sin_tienda(venta: dict[str, str | None]) -> bool:
    """¿La fila llegó sin tienda?"""
    return venta.get("tienda") == None


if __name__ == "__main__":
    # Textos, no números: mypy lo marca sin correr; Python truena adentro de sum.
    print(total(["12.5", "3"]))
