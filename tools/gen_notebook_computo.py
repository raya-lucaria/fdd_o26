"""Genera codigo/11_computo/computo.ipynb a partir de tools/notebook_computo/.

La unidad 11 tiene su notebook como fuente propia, no las paginas: un archivo
por tema en tools/notebook_computo/ (`00_arranque.py`, `01_tiempo.py`, ...),
en formato *percent*:

    # %% [markdown]
    # # Titulo
    # Texto en markdown, cada renglon comentado con «# ».

    # %%
    # celda 1.1
    import time
    ...

`# %%` abre una celda de codigo (lo que siga en ese renglon es un rotulo y se
ignora); `# %% [markdown]` (o `[md]`) abre una de texto, cuyos renglones
pierden el «# » inicial. Lo que hay antes del primer `# %%` (un docstring, por
ejemplo) no entra al notebook. Los temas se unen en orden de nombre.

El vinculo con las paginas lo vigila tools/test_computo_curriculum.py: cada
`**Haz (celda k.m):**` de una pagina aparece literal en una celda del notebook
que empieza con `# celda k.m`, y el .ipynb en disco es byte a byte lo que
produce este script. Las celdas usan `await` de nivel superior (el kernel ya
tiene un event loop corriendo); `asyncio.run(...)` truena ahi y no aparece.

Sin dependencias fuera de la libreria estandar. Determinista: mismas fuentes,
mismos bytes. El notebook nunca se edita a mano.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = RAIZ / "tools/notebook_computo"
DESTINO = RAIZ / "codigo/11_computo/computo.ipynb"

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
