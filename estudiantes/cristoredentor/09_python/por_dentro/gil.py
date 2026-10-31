"""Lab de la página «El GIL»: ¿cuándo ayudan los hilos?

Corre:  uv run gil.py
Sin GIL (en casa):  uv run --no-project --python 3.14t gil.py
"""
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

N = 200_000 if "--rapido" in sys.argv else 10_000_000  # sumas por trabajo
TRABAJOS = 4


def calcula(n):
    """Trabajo de CPU: suma en un ciclo de Python puro."""
    total = 0
    for i in range(n):
        total += i
    return total


def espera(_):
    """Trabajo que espera: como pedirle algo a una API."""
    time.sleep(0.05 if "--rapido" in sys.argv else 1)


def mide(etiqueta, Pool, trabajo, args):
    inicio = time.perf_counter()
    with Pool(max_workers=TRABAJOS) as pool:
        list(pool.map(trabajo, args))
    print(f"{etiqueta:<24} {time.perf_counter() - inicio:5.2f} s")


if __name__ == "__main__":
    gil = sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else True
    print(f"Python {sys.version.split()[0]} · GIL {'activo' if gil else 'apagado'}")
    inicio = time.perf_counter()
    for _ in range(TRABAJOS):
        calcula(N)
    print(f"{'calcula, uno tras otro':<24} {time.perf_counter() - inicio:5.2f} s")
    mide("calcula, 4 hilos", ThreadPoolExecutor, calcula, [N] * TRABAJOS)
    mide("calcula, 4 procesos", ProcessPoolExecutor, calcula, [N] * TRABAJOS)
    mide("espera, 4 hilos", ThreadPoolExecutor, espera, range(TRABAJOS))
