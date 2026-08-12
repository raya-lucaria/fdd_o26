"""Guarda: toda imagen de la unidad tiene su fila en CREDITOS.md.

Una imagen sin procedencia declarada es una imagen que no se puede publicar.
"""
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "course/2_pipeline_de_datos/_assets"
CREDITOS = ASSETS / "CREDITOS.md"
EXTENSIONES = {".svg", ".jpg", ".jpeg", ".png"}


def imagenes():
    if not ASSETS.is_dir():
        return []
    return sorted(
        p for p in ASSETS.iterdir()
        if p.is_file() and p.suffix.lower() in EXTENSIONES
    )


def filas():
    """Filas de la tabla de CREDITOS.md, como listas de celdas."""
    out = []
    for linea in CREDITOS.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea.startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip("|").split("|")]
        if not celdas or set(celdas[0]) <= {"-", ":"}:
            continue  # separador de la tabla
        if celdas[0].lower() == "archivo":
            continue  # encabezado
        out.append(celdas)
    return out


def test_creditos_existe():
    assert CREDITOS.is_file(), f"falta {CREDITOS}"


def test_hay_imagenes():
    assert imagenes(), f"no hay imagenes en {ASSETS}"


@pytest.mark.parametrize("imagen", [p.name for p in imagenes()])
def test_cada_imagen_tiene_fila_de_creditos(imagen):
    nombres = {f[0] for f in filas()}
    assert imagen in nombres, (
        f"{imagen} no tiene fila en CREDITOS.md: toda imagen necesita "
        f"descripcion, autor/origen y licencia."
    )


def test_cada_fila_esta_completa():
    for celdas in filas():
        assert len(celdas) >= 4, f"fila incompleta en CREDITOS.md: {celdas}"
        for i, celda in enumerate(celdas[:4]):
            assert celda, f"celda vacia ({i}) en la fila de {celdas[0]}"


def test_ninguna_fila_apunta_a_un_archivo_inexistente():
    presentes = {p.name for p in imagenes()}
    for celdas in filas():
        assert celdas[0] in presentes, (
            f"CREDITOS.md acredita '{celdas[0]}', que ya no esta en _assets/"
        )
