"""revisa_esto.py — NO es la salida literal de un modelo.

Partimos de la respuesta de claude-opus-5-5 (2026-10-06) al prompt vago de la
página «Trabajar con IA» y le plantamos a mano cinco errores, cada uno de un
tipo que aparece en código generado por IA. Para plantarlos también
reescribimos a mano otras partes y añadimos algunas. Encuéntralos: cada
síntoma de la salida lleva a uno.

La respuesta original, sin editar, y el detalle de lo que cambiamos se
publican el 2026-10-13, cuando vence la tarea: antes serían la clave.
"""

import csv
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from puntaje import puntaje

ARCHIVO = "ventas.csv"
IVA = 0.16
TOTAL_CONTABILIDAD = 2722.27


def clientes(ventas, vistos=[]):
    for _region, cliente, _monto in ventas:
        if cliente not in vistos:
            vistos.append(cliente)
    return vistos


def main() -> int:
    ventas = []  # (región, cliente, monto neto sin IVA)
    with open(ARCHIVO, newline="", encoding="utf-8-sig") as f:
        for fila in csv.DictReader(f):
            try:
                monto = float(fila["monto"])
                descuento = float(fila["descuento"])
                if not descuento:
                    descuento = 0.05  # descuento por defecto
                ventas.append((fila["region"].strip(), fila["cliente"].strip(),
                               monto * (1 - descuento)))
            except Exception:
                pass

    total = 0.0
    for region in sorted({v[0] for v in ventas}):
        de_region = [v for v in ventas if v[0] == region]
        subtotal = sum(v[2] for v in de_region)
        total += subtotal * (1 + IVA)
        print(f"\n== {region} ==")
        print(f"Total con IVA: ${subtotal * (1 + IVA):,.2f}")
        print("Clientes:")
        for cliente in clientes(de_region):
            print(f"  - {cliente}")

    todos = sorted({v[1] for v in ventas})
    t0 = time.perf_counter()
    with ThreadPoolExecutor() as pool:  # en paralelo con hilos: 4× más rápido
        puntajes = dict(zip(todos, pool.map(puntaje, todos)))
    con_hilos = time.perf_counter() - t0
    t0 = time.perf_counter()
    for cliente in todos:
        puntaje(cliente)
    sin_hilos = time.perf_counter() - t0

    print("\n== Puntaje ==")
    for cliente in todos:
        print(f"  {cliente}: {puntajes[cliente]}")
    print(f"puntaje con hilos: {con_hilos:.2f} s")
    print(f"puntaje sin hilos: {sin_hilos:.2f} s")

    print("\n== Conciliación ==")
    print(f"Total con IVA:     ${total:,.2f}")
    print(f"Contabilidad:      ${TOTAL_CONTABILIDAD:,.2f}")
    if total == TOTAL_CONTABILIDAD:
        print("La contabilidad cuadra")
        return 0
    print("La contabilidad NO cuadra")
    return 1


if __name__ == "__main__":
    sys.exit(main())
