"""Mide UNA opción en un proceso nuevo: tiempo y memoria del proceso (RSS).

Uso:  python mide.py <escenario> <n>
Imprime una línea separada por tabuladores:
    escenario  segundos  rss_base_mb  rss_pico_mb  delta_mb

Por qué un proceso nuevo por opción:
- tracemalloc sólo ve la memoria que pide Python; Polars y DuckDB reservan
  la suya en Rust y C++. El RSS es lo que el sistema le dio al proceso entero.
- El pico de RSS sólo sube: en un proceso compartido, la segunda opción
  heredaría el pico de la primera.
- El import cuesta: el reloj arranca DESPUÉS del import, y rss_base_mb es la
  memoria con la librería ya cargada; delta_mb es lo que sumó la consulta.
"""

import os
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

try:
    import resource  # existe en Linux y macOS, no en Windows nativo
except ImportError:
    sys.exit("mide.py necesita el módulo resource: usa Linux, macOS o WSL.")

AQUI = Path(__file__).parent
ESCENARIOS = [
    "pandas", "polars", "polars-lazy", "duckdb", "polars-1-hilo",
    "lista", "generador", "scan",
]  # fmt: skip


def rss_pico_mb() -> float:
    """El RSS más alto que ha tenido este proceso, en MB."""
    # En Linux, ru_maxrss de un proceso lanzado desde el notebook arrastra el
    # pico del kernel que lo lanzó; VmHWM es el pico de este proceso nada más.
    estado = Path("/proc/self/status")
    if estado.exists():
        for linea in estado.read_text().splitlines():
            if linea.startswith("VmHWM:"):
                return int(linea.split()[1]) / 1024
    pico = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux lo reporta en KB; macOS, en bytes.
    return pico / 1024**2 if sys.platform == "darwin" else pico / 1024


# La pregunta de B: total vendido (cantidad * precio) por tienda, sólo filas
# con cantidad > 0 (los nulos quedan fuera), de mayor a menor.


def con_pandas(csv: Path) -> None:
    import pandas as pd

    inicio = time.perf_counter()
    df = pd.read_csv(csv)
    df = df[df["cantidad"] > 0]  # NaN > 0 es False: los vacíos se van
    total = df["cantidad"] * df["precio"]
    total.groupby(df["tienda"]).sum().sort_values(ascending=False)
    termina(inicio)


def con_polars(csv: Path, lazy: bool) -> None:
    import polars as pl

    inicio = time.perf_counter()
    # Eager lee todo el archivo; lazy (scan_csv) arma un plan y lo optimiza.
    df = pl.scan_csv(csv) if lazy else pl.read_csv(csv)
    consulta = (
        df.filter(pl.col("cantidad") > 0)  # null > 0 es null: el filtro lo descarta
        .group_by("tienda")
        .agg((pl.col("cantidad") * pl.col("precio")).sum().alias("total"))
        .sort("total", descending=True)
    )
    if isinstance(consulta, pl.LazyFrame):
        consulta.collect()
    termina(inicio)


def con_duckdb(csv: Path) -> None:
    import duckdb

    inicio = time.perf_counter()
    duckdb.sql(f"""
        SELECT tienda, SUM(cantidad * precio) AS total
        FROM read_csv('{csv}')
        WHERE cantidad > 0
        GROUP BY tienda
        ORDER BY total DESC
    """).fetchall()
    termina(inicio)


def con_lista(csv: Path) -> None:
    """Suma la columna precio leyendo TODO el archivo a una lista primero."""
    inicio = time.perf_counter()
    with open(csv, encoding="utf-8") as f:
        lineas = f.readlines()[1:]  # todas en memoria a la vez; sin encabezado
    sum(float(linea.rsplit(",", 1)[1]) for linea in lineas)
    termina(inicio)


def precios(csv: Path) -> Iterator[float]:
    """Generador: entrega un precio a la vez; nunca guarda el archivo entero."""
    with open(csv, encoding="utf-8") as f:
        next(f)  # salta el encabezado
        for linea in f:
            yield float(linea.rsplit(",", 1)[1])


def con_generador(csv: Path) -> None:
    inicio = time.perf_counter()
    sum(precios(csv))
    termina(inicio)


def con_scan(csv: Path) -> None:
    import polars as pl

    inicio = time.perf_counter()
    pl.scan_csv(csv).select(pl.col("precio").sum()).collect()
    termina(inicio)


def termina(inicio: float) -> None:
    """Para el reloj e imprime la línea de resultados."""
    segundos = time.perf_counter() - inicio
    pico = rss_pico_mb()
    print(f"{ESCENARIO}\t{segundos:.3f}\t{BASE:.1f}\t{pico:.1f}\t{pico - BASE:.1f}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ESCENARIOS:
        uso = "Uso: python mide.py <escenario> <n>"
        sys.exit(f"{uso}\nEscenarios: {', '.join(ESCENARIOS)}")
    ESCENARIO, n = sys.argv[1], int(sys.argv[2])
    csv = AQUI / "datos" / f"ventas_{n}.csv"

    # Si faltan los datos, se generan en OTRO proceso: así ni el tiempo ni la
    # memoria de generarlos se cuelan en la medición.
    if not csv.exists():
        codigo = f"import datos; datos.genera({n})"
        subprocess.run(
            [sys.executable, "-c", codigo], cwd=AQUI, check=True, stdout=sys.stderr
        )

    if ESCENARIO == "polars-1-hilo":
        # Tiene que ir ANTES de importar polars: Polars lo lee al cargarse.
        os.environ["POLARS_MAX_THREADS"] = "1"

    # Importa la librería del escenario ANTES de medir la base.
    if ESCENARIO == "pandas":
        import pandas  # noqa: F401
    elif ESCENARIO == "duckdb":
        import duckdb  # noqa: F401
    elif ESCENARIO in ("polars", "polars-lazy", "polars-1-hilo", "scan"):
        import polars  # noqa: F401
    BASE = rss_pico_mb()

    if ESCENARIO == "pandas":
        con_pandas(csv)
    elif ESCENARIO in ("polars", "polars-1-hilo"):
        con_polars(csv, lazy=False)
    elif ESCENARIO == "polars-lazy":
        con_polars(csv, lazy=True)
    elif ESCENARIO == "duckdb":
        con_duckdb(csv)
    elif ESCENARIO == "lista":
        con_lista(csv)
    elif ESCENARIO == "generador":
        con_generador(csv)
    else:
        con_scan(csv)
