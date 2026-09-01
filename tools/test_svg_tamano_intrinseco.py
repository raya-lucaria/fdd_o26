"""Guarda: todo SVG del curso declara su tamano en la raiz.

El sitio incrusta los diagramas con `<img src="...svg">`. Un SVG que solo trae
`viewBox` no tiene tamano intrinseco, asi que el navegador lo pinta al tamano
por omision de un elemento reemplazado —300x150 CSS px, y menos todavia si el
diagrama es vertical, porque la relacion de aspecto lo encoge dentro de esa
caja—. El resultado es una miniatura ilegible de ~70 px al lado de texto de
tamano normal.

Esto ya paso: 26 de los diagramas del curso se publicaron asi, incluidos los
catorce conceptuales de Arquitectura y los dos de Terminal y Bash. La regla
`img { max-width: 100%; height: auto }` del skin no lo evita: encoge lo que es
demasiado grande, no agranda lo que no tiene tamano.
"""
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SVGS = sorted(RAIZ.glob("course/**/_assets/*.svg"))
IDS = [str(p.relative_to(RAIZ / "course")) for p in SVGS]


def raiz_svg(ruta: Path) -> str:
    encontrada = re.search(r"<svg\b[^>]*>", ruta.read_text(encoding="utf-8"))
    assert encontrada, f"{ruta.name}: no se encontro la etiqueta <svg>"
    return encontrada.group()


def test_hay_svgs_que_vigilar():
    assert SVGS, "no se encontro ningun SVG bajo course/**/_assets/"


@pytest.mark.parametrize("svg", SVGS, ids=IDS)
def test_la_raiz_declara_width_y_height(svg):
    etiqueta = raiz_svg(svg)
    for atributo in ("width", "height"):
        assert re.search(rf'\b{atributo}="[\d.]+"', etiqueta), (
            f"{svg.name}: <svg> sin {atributo} propio. Sin tamano intrinseco "
            "el navegador lo pinta a ~300x150 px o menos, no al ancho de su "
            "columna. Copia la medida del viewBox."
        )


@pytest.mark.parametrize("svg", SVGS, ids=IDS)
def test_el_tamano_declarado_conserva_la_proporcion_del_viewBox(svg):
    """Lo que deforma un diagrama es la proporcion, no la escala.

    Un width/height que multiplica el viewBox por una constante es legitimo y
    se usa a proposito: `latencia-throughput.svg` y `roofline-lite.svg` estan
    al doble para que un lienzo pequeno se publique legible. Lo que si rompe el
    dibujo es que la razon de aspecto declarada no sea la del viewBox.
    """
    etiqueta = raiz_svg(svg)
    caja = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', etiqueta)
    assert caja, f"{svg.name}: <svg> sin viewBox de origen 0 0"
    vb = float(caja.group(1)) / float(caja.group(2))
    ancho = float(re.search(r'\bwidth="([\d.]+)"', etiqueta).group(1))
    alto = float(re.search(r'\bheight="([\d.]+)"', etiqueta).group(1))
    assert abs(ancho / alto - vb) < 0.01, (
        f"{svg.name}: la raiz declara {ancho}x{alto} (razon {ancho / alto:.3f}) "
        f"y el viewBox tiene razon {vb:.3f}; el diagrama se publicaria deformado"
    )
