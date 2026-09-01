"""Guardas del generador de diagramas de la unidad de Git y GitHub.

Regenera antes de comparar: correr pytest certifica que lo comiteado coincide
con lo que el generador produce hoy. Editar un SVG a mano falla aqui.

Las convenciones de tamano de la raiz <svg> las cubre
tools/test_svg_tamano_intrinseco.py para todo el curso, y los creditos
tools/test_creditos.py; aqui solo va lo propio de esta unidad.
"""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
GENERADOR = RAIZ / "tools/gen_git.py"
ASSETS = RAIZ / "course/7_git_y_github/_assets"
UNIDAD = RAIZ / "course/7_git_y_github"
SKIN = RAIZ / "skins/fdd-eva.yaml"


def _cargar():
    assert GENERADOR.is_file(), "falta tools/gen_git.py"
    spec = importlib.util.spec_from_file_location("gen_git", GENERADOR)
    modulo = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(RAIZ / "tools"))
    try:
        spec.loader.exec_module(modulo)
    finally:
        sys.path.pop(0)
    return modulo


@pytest.fixture(scope="module", autouse=True)
def _svgs_frescos():
    subprocess.run([sys.executable, str(GENERADOR)], check=True)


def test_cada_diagrama_declarado_existe_y_lleva_prefijo():
    for nombre in _cargar().DIAGRAMAS:
        assert nombre.startswith("git-"), (
            f"{nombre}: los ids de objeto numerado son unicos en TODO el curso; "
            "sin el prefijo 'git-' pueden chocar con otra unidad"
        )
        assert (ASSETS / f"{nombre}.svg").is_file(), f"falta {nombre}.svg"


def test_no_sobran_svg_sin_generador():
    declarados = {f"{n}.svg" for n in _cargar().DIAGRAMAS}
    huerfanos = {p.name for p in ASSETS.glob("*.svg")} - declarados
    assert not huerfanos, f"SVG sin entrada en DIAGRAMAS: {sorted(huerfanos)}"


def test_cada_svg_en_disco_es_lo_que_produce_el_generador():
    for nombre, funcion in _cargar().DIAGRAMAS.items():
        assert (ASSETS / f"{nombre}.svg").read_text(encoding="utf-8") == funcion(), (
            f"{nombre}.svg no coincide con gen_git.py: no lo edites a mano, "
            "cambia la funcion y vuelve a correr el generador"
        )


def test_los_colores_salen_del_skin():
    """La paleta vive una sola vez, en svg_base, y sale de skins/fdd-eva.yaml."""
    import importlib.util as iu

    spec = iu.spec_from_file_location("svg_base", RAIZ / "tools/svg_base.py")
    base = iu.module_from_spec(spec)
    spec.loader.exec_module(base)
    tokens = yaml.safe_load(SKIN.read_text(encoding="utf-8"))["tokens"]
    paleta = set(tokens["color"].values()) | set(tokens["graph"].values())
    usados = {
        base.FONDO, base.PANEL, base.TEXTO, base.SUAVE, base.LINEA, base.ACENTO,
        base.TINTE, base.AMBAR, base.CIAN, base.VIOLETA, base.ROJO,
    }
    fuera = usados - paleta
    assert not fuera, f"colores que no estan en skins/fdd-eva.yaml: {sorted(fuera)}"


def test_cada_svg_esta_referenciado_por_alguna_pagina():
    paginas = "".join(
        p.read_text(encoding="utf-8")
        for p in sorted(UNIDAD.glob("*.md")) if p.name != "CREDITOS.md"
    )
    for nombre in _cargar().DIAGRAMAS:
        assert f"{nombre}.svg" in paginas, f"{nombre}.svg no aparece en ninguna pagina"


def test_cada_svg_tiene_aria_label_descriptiva():
    for nombre in _cargar().DIAGRAMAS:
        etiqueta = re.search(
            r'aria-label="([^"]*)"', (ASSETS / f"{nombre}.svg").read_text(encoding="utf-8")
        ).group(1)
        assert len(etiqueta) >= 80, (
            f"{nombre}.svg: aria-label demasiado corta para describir el diagrama"
        )


def test_el_diagrama_de_llaves_advierte_sobre_la_privada():
    """El error caro de esta unidad es compartir la llave privada."""
    svg = (ASSETS / "git-llaves.svg").read_text(encoding="utf-8")
    assert "nunca sale de aquí" in svg
    assert "nunca se manda" in svg


def test_el_generador_rechaza_un_nombre_desconocido():
    r = subprocess.run([sys.executable, str(GENERADOR), "git-no-existe"],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "desconocido" in r.stderr
