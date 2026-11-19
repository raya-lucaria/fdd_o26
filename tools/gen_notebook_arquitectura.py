"""Genera codigo/11_computo/arquitectura.ipynb a partir de tools/notebook_arquitectura/.

Notebook de los bloques 11.2 y 11.3 (sistemas distribuidos, capas de
ejecucion, componer un servidor, como llegan los resultados). Misma mecanica
que tools/gen_notebook_computo.py: un archivo por tema en formato *percent*
(`00_arranque.py`, `09_distribuido.py`, `10_capas.py`, `11_servidor.py`,
`12_resultados.py`), `# %%` abre una celda de codigo y `# %% [markdown]` una de
texto; los temas se unen en orden de nombre. Cada celda de codigo empieza con
un rotulo `# celda N.M`, unico y en orden; las celdas usan `await` de nivel
superior (el kernel ya tiene un event loop). Lo vigila
tools/test_computo_curriculum.py: sin salidas, kernel python3 y el .ipynb en
disco es byte a byte lo que produce este script. Determinista, sin
dependencias fuera de la libreria estandar. El notebook nunca se edita a mano.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = RAIZ / "tools/notebook_arquitectura"
DESTINO = RAIZ / "codigo/11_computo/arquitectura.ipynb"

_SEPARADOR = re.compile(r"^# %%(.*)$")
_MARKDOWN = re.compile(r"^\s*\[(markdown|md)\]")


def temas():
    """Los archivos fuente, en orden de nombre (vacio si aun no existen)."""
    if not FUENTE.is_dir():
        return []
    return sorted(p for p in FUENTE.glob("[0-9][0-9]_*.py") if p.is_file())


def _recorta(lineas):
    """Quita renglones en blanco al principio y al final."""
    while lineas and not lineas[0].strip():
        lineas = lineas[1:]
    while lineas and not lineas[-1].strip():
        lineas = lineas[:-1]
    return lineas


def _descomenta(lineas):
    """Markdown en percent: «# texto» -> «texto», «#» -> renglon vacio."""
    if not all(l.startswith("#") for l in lineas if l.strip()):
        return lineas
    return [l[2:] if l.startswith("# ") else l[1:] for l in lineas]


def celdas_de(texto):
    """[(tipo, fuente)] de un archivo percent; tipo es "code" o "markdown"."""
    celdas, tipo, lineas = [], None, []

    def cierra():
        cuerpo = _recorta(lineas)
        if tipo == "markdown":
            cuerpo = _recorta(_descomenta(cuerpo))
        if tipo and cuerpo:
            celdas.append((tipo, "\n".join(l.rstrip() for l in cuerpo)))

    for linea in texto.splitlines():
        m = _SEPARADOR.match(linea)
        if m:
            cierra()
            tipo = "markdown" if _MARKDOWN.match(m.group(1)) else "code"
            lineas = []
        else:
            lineas.append(linea)
    cierra()
    return celdas


def _fuente(texto):
    lineas = texto.split("\n")
    return [l + "\n" for l in lineas[:-1]] + [lineas[-1]]


def _md(texto):
    return {"cell_type": "markdown", "metadata": {}, "source": _fuente(texto)}


def _codigo(texto):
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": _fuente(texto)}


def notebook():
    celdas = []
    for tema in temas():
        for tipo, texto in celdas_de(tema.read_text(encoding="utf-8")):
            celdas.append(_md(texto) if tipo == "markdown" else _codigo(texto))
    nb = {"cells": celdas, "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 4}
    return json.dumps(nb, ensure_ascii=False, indent=1) + "\n"


if __name__ == "__main__":
    if not temas():
        print(f"aviso: no hay temas en {FUENTE.relative_to(RAIZ)}", file=sys.stderr)
    DESTINO.write_text(notebook(), encoding="utf-8")
    print(f"escrito {DESTINO.relative_to(RAIZ)} ({len(temas())} temas)")
    sys.exit(0)
