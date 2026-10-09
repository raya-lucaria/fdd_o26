"""El trabajo que usan las celdas de la página «El GIL».

Vive en un archivo y no en una celda porque un proceso nuevo vuelve a
importar el código de la función, y una celda no está en ningún archivo.
"""
import time


def calcula(segundos):
    """Suma en Python puro durante `segundos` y regresa cuántas sumas hizo."""
    fin = time.perf_counter() + segundos
    sumas = 0
    while time.perf_counter() < fin:
        for _ in range(10_000):
            sumas += 1
    return sumas


def espera(segundos):
    """Espera `segundos` sin calcular nada: como pedirle algo a una API."""
    time.sleep(segundos)
    return segundos
