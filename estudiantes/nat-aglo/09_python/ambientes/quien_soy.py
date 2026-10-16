"""Dice qué Python está corriendo y si estás dentro de un ambiente.

Sólo usa la biblioteca estándar: corre igual dentro y fuera de un ambiente,
con rich instalado o sin él. Ésa es la idea: correrlo en cada situación y
comparar.
"""
import os
import shutil
import sys
from importlib import metadata

en_ambiente = sys.prefix != sys.base_prefix

try:
    rich = f"instalado, versión {metadata.version('rich')}"
except metadata.PackageNotFoundError:
    rich = "NO instalado en este Python"

print(f"python que corre  : {sys.executable}")
print(f"versión           : {sys.version.split()[0]}")
print(f"sys.prefix        : {sys.prefix}")
print(f"¿en un ambiente?  : {'sí' if en_ambiente else 'no'}")
print(f"'python' en PATH  : {shutil.which('python') or '(ninguno)'}")
print(f"rich              : {rich}")
