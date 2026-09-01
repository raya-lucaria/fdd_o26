"""Guardas del generador de diagramas de la unidad de Expresiones regulares.

Regenera antes de comparar, igual que test_diagramas.py: correr pytest
certifica que lo comiteado coincide con lo que el generador produce hoy, y no
solo que el archivo existe. Editar un SVG a mano falla aqui.

Las convenciones de la raiz <svg> no son cosmeticas: el sitio incrusta los
diagramas con <img>, y sin width/height propios el navegador los pinta a
~300x150 CSS px en vez de llenar el contenedor de la figura.
"""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
GENERADOR = RAIZ / "tools/gen_regex.py"
ASSETS = RAIZ / "course/6_expresiones_regulares/_assets"
UNIDAD = RAIZ / "course/6_expresiones_regulares"
SKIN = RAIZ / "skins/fdd-eva.yaml"


def _cargar():
    assert GENERADOR.is_file(), (
        "falta tools/gen_regex.py: los diagramas de la unidad deben salir de "
        "un generador determinista, no escribirse a mano"
    )
    spec = importlib.util.spec_from_file_location("gen_regex", GENERADOR)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


@pytest.fixture(scope="module", autouse=True)
def _svgs_frescos():
    subprocess.run([sys.executable, str(GENERADOR)], check=True)


def test_el_catalogo_no_esta_vacio():
    assert _cargar().DIAGRAMAS, "el catalogo DIAGRAMAS esta vacio"


def test_cada_diagrama_declarado_existe_en_disco():
    for nombre in _cargar().DIAGRAMAS:
        assert nombre.startswith("rx-"), (
            f"{nombre}: los ids de objeto numerado de Raya son unicos en TODO "
            "el curso, no por pagina; sin el prefijo 'rx-' pueden chocar con "
            "una figura de otra unidad"
        )
        assert (ASSETS / f"{nombre}.svg").is_file(), f"falta {nombre}.svg"


def test_no_sobran_svg_sin_generador():
    declarados = {f"{n}.svg" for n in _cargar().DIAGRAMAS}
    en_disco = {p.name for p in ASSETS.glob("*.svg")}
    huerfanos = en_disco - declarados
    assert not huerfanos, (
        f"SVG sin entrada en DIAGRAMAS: {sorted(huerfanos)}. El generador es "
        "la unica fuente de verdad de los diagramas de esta unidad."
    )


def test_cada_svg_en_disco_es_lo_que_produce_el_generador():
    modulo = _cargar()
    for nombre, funcion in modulo.DIAGRAMAS.items():
        en_disco = (ASSETS / f"{nombre}.svg").read_text(encoding="utf-8")
        assert en_disco == funcion(), (
            f"{nombre}.svg no coincide con gen_regex.py: no edites el SVG a "
            "mano, cambia la funcion y vuelve a correr el generador"
        )


@pytest.mark.parametrize("atributo", ["width", "height", "viewBox", "role", "aria-label"])
def test_la_raiz_svg_cumple_las_cinco_convenciones(atributo):
    for nombre in _cargar().DIAGRAMAS:
        texto = (ASSETS / f"{nombre}.svg").read_text(encoding="utf-8")
        raiz = re.match(r"<svg\b[^>]*>", texto)
        assert raiz, f"{nombre}.svg: no se encontro la etiqueta <svg>"
        assert f'{atributo}="' in raiz.group(), (
            f"{nombre}.svg: <svg> sin {atributo}"
        )


def test_cada_svg_hornea_su_fondo():
    """Sin rect de fondo, el diagrama se lee mal en tema claro."""
    modulo = _cargar()
    fondo = yaml.safe_load(SKIN.read_text(encoding="utf-8"))["tokens"]["color"]["page"]
    assert modulo.FONDO == fondo, (
        f"gen_regex.FONDO ({modulo.FONDO}) ya no es color.page del skin ({fondo})"
    )
    for nombre in modulo.DIAGRAMAS:
        texto = (ASSETS / f"{nombre}.svg").read_text(encoding="utf-8")
        assert f'fill="{fondo}"' in texto, f"{nombre}.svg no pinta su propio fondo"


def test_todo_texto_lleva_fill_explicito():
    for nombre in _cargar().DIAGRAMAS:
        texto = (ASSETS / f"{nombre}.svg").read_text(encoding="utf-8")
        for etiqueta in re.findall(r"<text\b[^>]*>", texto):
            assert 'fill="' in etiqueta, (
                f"{nombre}.svg: <text> sin fill hereda el color del tema y "
                f"puede volverse ilegible -> {etiqueta}"
            )


def test_cada_svg_tiene_aria_label_descriptiva():
    """La etiqueta accesible debe describir el diagrama, no nombrarlo."""
    for nombre in _cargar().DIAGRAMAS:
        texto = (ASSETS / f"{nombre}.svg").read_text(encoding="utf-8")
        etiqueta = re.search(r'aria-label="([^"]*)"', texto).group(1)
        assert len(etiqueta) >= 80, (
            f"{nombre}.svg: aria-label demasiado corta ({len(etiqueta)} "
            "caracteres) para describir el diagrama a quien no lo ve"
        )


def test_los_colores_del_generador_salen_del_skin():
    modulo = _cargar()
    tokens = yaml.safe_load(SKIN.read_text(encoding="utf-8"))["tokens"]
    paleta = set(tokens["color"].values()) | set(tokens["graph"].values())
    usados = {
        modulo.FONDO, modulo.PANEL, modulo.TEXTO, modulo.SUAVE, modulo.LINEA,
        modulo.ACENTO, modulo.TINTE, modulo.AMBAR, modulo.CIAN,
        modulo.VIOLETA, modulo.ROJO,
    }
    fuera = usados - paleta
    assert not fuera, (
        f"colores que no estan en skins/fdd-eva.yaml: {sorted(fuera)}"
    )


def test_cada_svg_esta_referenciado_por_alguna_pagina():
    """Un diagrama que nadie incrusta es peso muerto en el repositorio."""
    paginas = "".join(
        p.read_text(encoding="utf-8") for p in sorted(UNIDAD.glob("*.md"))
    )
    for nombre in _cargar().DIAGRAMAS:
        assert f"{nombre}.svg" in paginas, (
            f"{nombre}.svg no aparece en ninguna pagina de la unidad"
        )


def test_ningun_texto_se_sale_del_lienzo():
    """Una etiqueta fuera del viewBox se recorta en el navegador."""
    modulo = _cargar()
    for nombre in modulo.DIAGRAMAS:
        texto = (ASSETS / f"{nombre}.svg").read_text(encoding="utf-8")
        raiz = re.match(r"<svg\b[^>]*>", texto).group()
        ancho = int(re.search(r'width="(\d+)"', raiz).group(1))
        alto = int(re.search(r'height="(\d+)"', raiz).group(1))
        for etiqueta in re.findall(r"<text\b[^>]*>", texto):
            x = float(re.search(r'\sx="([-\d.]+)"', etiqueta).group(1))
            y = float(re.search(r'\sy="([-\d.]+)"', etiqueta).group(1))
            assert 0 <= x <= ancho and 0 <= y <= alto, (
                f"{nombre}.svg: texto en ({x}, {y}) fuera del lienzo "
                f"{ancho}x{alto}"
            )


def test_el_generador_rechaza_un_nombre_desconocido():
    resultado = subprocess.run(
        [sys.executable, str(GENERADOR), "rx-no-existe"],
        capture_output=True, text=True,
    )
    assert resultado.returncode != 0
    assert "desconocido" in resultado.stderr


def test_los_textos_van_escapados():
    """Comillas y ampersands en una etiqueta romperian el XML."""
    modulo = _cargar()
    assert modulo.texto(0, 0, 'a & b "c"').count("&amp;") == 1
    assert escape("<") in modulo.teclado(0, 0, "<a>")
