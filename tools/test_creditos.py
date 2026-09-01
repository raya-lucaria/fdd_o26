"""Guarda: toda imagen de cualquier unidad tiene su fila en CREDITOS.md.

Una imagen sin procedencia declarada es una imagen que no se puede publicar.

Estas guardas nacieron escritas contra la unica unidad que tenia imagenes
propias (Pipeline de Datos). Al aparecer mas unidades con sus propios _assets/,
esa ruta dejo de ser una constante y paso a ser un descubrimiento: cualquier
`course/**/_assets/` con imagenes queda cubierto automaticamente, para que
agregar una unidad no requiera editar este archivo.
"""
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
CURSO = RAIZ / "course"
EXTENSIONES = {".svg", ".jpg", ".jpeg", ".png", ".webp"}


def directorios_de_assets():
    """Todo _assets/ del curso que contenga al menos una imagen."""
    return sorted(
        d for d in CURSO.rglob("_assets")
        if d.is_dir() and any(p.suffix.lower() in EXTENSIONES for p in d.iterdir())
    )


def imagenes(assets):
    return sorted(
        p for p in assets.iterdir()
        if p.is_file() and p.suffix.lower() in EXTENSIONES
    )


def _tabla(assets):
    """(encabezado, filas de datos) de la tabla de CREDITOS.md."""
    encabezado, out = [], []
    creditos = assets / "CREDITOS.md"
    if not creditos.is_file():
        return encabezado, out
    for linea in creditos.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea.startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip("|").split("|")]
        if not celdas or set(celdas[0]) <= {"-", ":"}:
            continue  # separador de la tabla
        if celdas[0].lower() == "archivo":
            encabezado = celdas  # cada unidad declara sus propias columnas
            continue
        out.append(celdas)
    return encabezado, out


def filas(assets):
    """Filas de datos de la tabla de CREDITOS.md, como listas de celdas."""
    return _tabla(assets)[1]


def ident(assets):
    return str(assets.relative_to(RAIZ))


ASSETS = directorios_de_assets()
IDS = [ident(a) for a in ASSETS]


def test_hay_unidades_con_imagenes():
    assert ASSETS, f"no se encontro ningun _assets/ con imagenes bajo {CURSO}"


@pytest.mark.parametrize("assets", ASSETS, ids=IDS)
def test_creditos_existe(assets):
    assert (assets / "CREDITOS.md").is_file(), f"falta {assets}/CREDITOS.md"


@pytest.mark.parametrize("assets", ASSETS, ids=IDS)
def test_cada_imagen_tiene_fila_de_creditos(assets):
    nombres = {f[0] for f in filas(assets)}
    for imagen in imagenes(assets):
        assert imagen.name in nombres, (
            f"{ident(assets)}/{imagen.name} no tiene fila en CREDITOS.md: "
            f"toda imagen necesita descripcion, autor/origen y licencia."
        )


@pytest.mark.parametrize("assets", ASSETS, ids=IDS)
def test_la_tabla_declara_sus_columnas(assets):
    """Sin encabezado no hay contra que comparar las filas."""
    encabezado, _ = _tabla(assets)
    assert len(encabezado) >= 3, (
        f"{ident(assets)}/CREDITOS.md: la tabla necesita al menos las columnas "
        f"de archivo, descripcion y procedencia; encontre {encabezado}"
    )
    columnas = " ".join(encabezado).lower()
    for necesaria in ("archivo", "licencia"):
        assert necesaria in columnas, (
            f"{ident(assets)}/CREDITOS.md: falta la columna de {necesaria} "
            f"en el encabezado {encabezado}"
        )


@pytest.mark.parametrize("assets", ASSETS, ids=IDS)
def test_cada_fila_esta_completa(assets):
    """Completa quiere decir completa segun el encabezado de esa misma tabla.

    Cada unidad elige cuantas columnas usa —hay tablas de tres y de cinco—, asi
    que la guarda compara contra el encabezado del propio archivo en vez de
    imponer el formato de una unidad a las demas.
    """
    encabezado, datos = _tabla(assets)
    for celdas in datos:
        assert len(celdas) == len(encabezado), (
            f"{ident(assets)}/CREDITOS.md: la fila de {celdas[0]} tiene "
            f"{len(celdas)} celdas y el encabezado declara {len(encabezado)}"
        )
        for i, celda in enumerate(celdas):
            assert celda, (
                f"celda vacia ({encabezado[i]}) en la fila de {celdas[0]} "
                f"de {ident(assets)}/CREDITOS.md"
            )


@pytest.mark.parametrize("assets", ASSETS, ids=IDS)
def test_ninguna_fila_apunta_a_un_archivo_inexistente(assets):
    presentes = {p.name for p in imagenes(assets)}
    for celdas in filas(assets):
        assert celdas[0] in presentes, (
            f"{ident(assets)}/CREDITOS.md acredita '{celdas[0]}', "
            "que ya no esta en ese _assets/"
        )
