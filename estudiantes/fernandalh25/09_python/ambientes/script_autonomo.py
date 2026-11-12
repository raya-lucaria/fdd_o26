# /// script
# requires-python = ">=3.12"
# dependencies = ["rich"]
# ///
"""Un script que declara sus dependencias dentro de sí mismo (PEP 723).

`uv run script_autonomo.py` lee el bloque de arriba, crea un ambiente
temporal con rich y lo corre. No hay pyproject.toml ni .venv en tu carpeta.
"""
import sys

from rich.console import Console
from rich.table import Table

tabla = Table(title="Corrido por uv run, sin proyecto")
tabla.add_column("Qué")
tabla.add_column("Valor")
tabla.add_row("Python", sys.version.split()[0])
tabla.add_row("Ambiente", sys.prefix)
Console().print(tabla)
