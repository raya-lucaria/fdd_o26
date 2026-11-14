"""Datos sintéticos de ventas y dos ayudas para medir.

Lo usan los tres notebooks y mide.py:

- genera(n): escribe datos/ventas_{n}.csv y datos/ventas_{n}.parquet.
- cronometra(fn): el mejor tiempo de varias corridas.
- tabla(resultados): la tabla de una carrera, con «cuántas veces más lento».
- recomienda_n(): tu RAM y el N que te recomendamos.
"""

import os
import time
from collections.abc import Callable
from datetime import date
from pathlib import Path

import numpy as np
import polars as pl

# datos/ vive junto a este archivo, no donde se corra Python.
CARPETA = Path(__file__).parent / "datos"

TIENDAS = [
    "Centro",
    "Norte",
    "Sur",
    "Oriente",
    "Poniente",
    "Polanco",
    "Coyoacán",
    "Santa Fe",
]
PRODUCTOS = [f"P{i:03d}" for i in range(1, 41)]  # P001 … P040


def _construye(n: int) -> pl.DataFrame:
    """Arma n filas de una vez (vectorizado), siempre las mismas: semilla 0."""
    rng = np.random.default_rng(0)

    # fecha: un día cualquiera de 2025 (0 = 1 de enero, 364 = 31 de diciembre).
    dias = rng.integers(0, 365, size=n)
    tienda = np.array(TIENDAS)[rng.integers(0, len(TIENDAS), size=n)]
    producto = np.array(PRODUCTOS)[rng.integers(0, len(PRODUCTOS), size=n)]
    precio = np.round(rng.uniform(5.0, 500.0, size=n), 2)

    # cantidad: de 1 a 10; ~1 % se vuelve inválida (de -3 a 0) y ~1 % vacía.
    cantidad = rng.integers(1, 11, size=n)
    sorteo = rng.random(n)
    invalida = sorteo < 0.01
    cantidad[invalida] = rng.integers(-3, 1, size=int(invalida.sum()))
    vacia = (sorteo >= 0.01) & (sorteo < 0.02)

    return pl.DataFrame(
        {
            "dia": dias,
            "tienda": tienda,
            "producto": producto,
            "cantidad": cantidad,
            "vacia": vacia,
            "precio": precio,
        }
    ).select(
        (pl.lit(date(2025, 1, 1)) + pl.duration(days=pl.col("dia"))).alias("fecha"),
        pl.col("tienda"),
        pl.col("producto"),
        # Donde «vacia» es verdadero, la cantidad queda nula (null).
        pl.when(pl.col("vacia"))
        .then(None)
        .otherwise(pl.col("cantidad"))
        .cast(pl.Int64)
        .alias("cantidad"),
        pl.col("precio"),
    )


def genera(n: int) -> dict[str, Path]:
    """Escribe datos/ventas_{n}.csv y .parquet si no existen; regresa sus rutas."""
    rutas = {
        "csv": CARPETA / f"ventas_{n}.csv",
        "parquet": CARPETA / f"ventas_{n}.parquet",
    }
    if not all(ruta.exists() for ruta in rutas.values()):
        CARPETA.mkdir(exist_ok=True)
        df = _construye(n)
        df.write_csv(rutas["csv"])
        df.write_parquet(rutas["parquet"])
    for ruta in rutas.values():
        print(f"{ruta}  {n:_} filas  {ruta.stat().st_size / 1e6:.1f} MB")
    return rutas


def cronometra(fn: Callable[[], object], veces: int = 3) -> float:
    """Corre fn `veces` veces y regresa el MEJOR tiempo, en segundos.

    El mejor y no el promedio: las corridas lentas son ruido de la máquina
    (otro programa, la caché fría), no del código.
    """
    tiempos = []
    for _ in range(veces):
        inicio = time.perf_counter()
        fn()
        tiempos.append(time.perf_counter() - inicio)
    return min(tiempos)


def tabla(resultados: dict[str, float], columna: str = "segundos") -> pl.DataFrame:
    """De {opción: valor} a una tabla ordenada de mejor (menor) a peor."""
    df = pl.DataFrame({"opcion": list(resultados), columna: list(resultados.values())})
    return df.sort(columna).with_columns(
        (pl.col(columna) / pl.col(columna).min()).round(1).alias("veces_vs_mejor")
    )


def recomienda_n() -> int:
    """Imprime la RAM de esta máquina y el N recomendado. No cambia tu N."""
    # os.sysconf existe en Linux y macOS (no en Windows nativo).
    ram_gb = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024**3
    if ram_gb <= 8:
        n = 100_000
    else:
        n = 1_000_000
    print(f"Tienes {ram_gb:.0f} GB de RAM → te recomendamos N = {n:_}")
    if ram_gb > 16:
        print("Con más de 16 GB también puedes probar N = 10_000_000.")
    return n
