"""Reporta el ambiente en el que corre este programa.

Córrelo en tu máquina con uv run y dentro del contenedor, y compara.
"""
import os
import platform
import sys
import humanize
from importlib.metadata import distributions
from rich.console import Console
from rich.table import Table


def tamano(carpeta):
    """Bytes que ocupa una carpeta, contando todo lo que hay dentro."""
    total = 0
    for raiz, _, archivos in os.walk(carpeta):
        for a in archivos:
            ruta = os.path.join(raiz, a)
            if not os.path.islink(ruta):
                total += os.path.getsize(ruta)
    return total


def filas_del_ambiente():
    return [
        ("Python", platform.python_version()),
        ("Intérprete", sys.executable),
        ("sys.prefix", sys.prefix),
        ("¿En un ambiente?", "sí" if sys.prefix != sys.base_prefix else "no"),
        ("Sistema", f"{platform.system()} {platform.machine()}"),
    ]


def fila_propia():
    return ("Tamaño del ambiente", humanize.naturalsize(tamano(sys.prefix)))
    # Nota: humanize.naturalsize() devuelve un string como "1.2 MB" o "3.4 GB".
    # tamano es una función definida arriba que calcula el tamaño de una carpeta en bytes.
    # sys.prefix es la carpeta donde está instalado el intérprete de Python que se está usando para correr este programa.

def paquetes():
    return sorted((d.metadata["Name"], d.version) for d in distributions())


def main():
    consola = Console()
    ambiente = Table(title="Mi ambiente")
    ambiente.add_column("Qué")
    ambiente.add_column("Valor", overflow="fold")  # rutas largas completas
    for que, valor in filas_del_ambiente() + [fila_propia()]:
        ambiente.add_row(que, str(valor))
    consola.print(ambiente)

    instalados = Table(title="Paquetes instalados")
    instalados.add_column("Paquete")
    instalados.add_column("Versión")
    for nombre, version in paquetes():
        instalados.add_row(nombre, version)
    consola.print(instalados)


if __name__ == "__main__":
    main()
