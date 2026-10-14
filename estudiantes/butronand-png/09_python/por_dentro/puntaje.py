"""Puntaje de lealtad de un cliente: un cálculo pesado de ejemplo (CPU)."""


def puntaje(cliente: str) -> int:
    total = 0
    for i in range(3_000_000):
        total += (i * len(cliente)) % 7
    return total
