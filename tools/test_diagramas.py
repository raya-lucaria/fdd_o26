"""Guarda: cada SVG del disco es exactamente lo que su generador produce hoy.

gen_diagramas.py es la unica fuente de verdad de los diagramas. Si alguien edita
un .svg a mano, o cambia el generador sin regenerar, esta prueba falla.
"""
import importlib.util
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent


def _cargar_generador():
    spec = importlib.util.spec_from_file_location(
        "gen_diagramas", RAIZ / "tools/gen_diagramas.py"
    )
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


GEN = _cargar_generador()
SLUGS = list(GEN.DIAGRAMAS)


def test_son_los_ocho_diagramas_esperados():
    assert SLUGS == [
        "d-dag", "d-schema", "d-etl-elt", "d-tidy",
        "d-calidad", "d-idempotencia", "d-tiempo", "d-ciclo",
    ]


@pytest.mark.parametrize("slug", SLUGS)
def test_svg_en_disco_coincide_con_su_generador(slug):
    destino = GEN.ASSETS / f"{slug}.svg"
    assert destino.is_file(), (
        f"falta {destino.name}: corre `python3 tools/gen_diagramas.py`"
    )
    esperado = GEN.DIAGRAMAS[slug]()
    actual = destino.read_text(encoding="utf-8")
    assert actual == esperado, (
        f"{destino.name} no coincide con lo que gen_diagramas.py produce hoy. "
        f"Los SVG no se editan a mano: corre `python3 tools/gen_diagramas.py`."
    )


@pytest.mark.parametrize("slug", SLUGS)
def test_generador_es_determinista(slug):
    assert GEN.DIAGRAMAS[slug]() == GEN.DIAGRAMAS[slug]()


@pytest.mark.parametrize("slug", SLUGS)
def test_svg_cumple_convenciones(slug):
    texto = (GEN.ASSETS / f"{slug}.svg").read_text(encoding="utf-8")
    raiz = texto.split(">")[0]
    assert 'viewBox="' in raiz, f"{slug}: la raiz no declara viewBox"
    # Sin width/height propios el navegador incrusta el <svg> con el tamano por
    # omision de un elemento reemplazado (~300x150 px) y se ve minusculo.
    assert "width=" in raiz and "height=" in raiz, f"{slug}: raiz sin width/height"
    assert 'role="img"' in raiz, f"{slug}: la raiz no declara role=img"
    assert "<title>" in texto, f"{slug}: sin <title> descriptivo"
    titulo = texto.split("<title>")[1].split("</title>")[0]
    assert len(titulo) > 30, f"{slug}: el <title> es demasiado escueto"
    # Fondo propio + fill explicito en todo texto: el diagrama se lee igual con
    # tema claro y con tema oscuro, sin heredar color del sitio.
    assert f'fill="{GEN.FONDO}"' in texto, f"{slug}: sin fondo propio"
    assert "<text" in texto, f"{slug}: sin texto"
    for fragmento in texto.split("<text")[1:]:
        assert "fill=" in fragmento.split(">")[0], (
            f"{slug}: hay un <text> sin fill explicito"
        )


@pytest.mark.parametrize("slug", SLUGS)
def test_svg_es_xml_bien_formado(slug):
    from xml.etree import ElementTree

    ElementTree.fromstring((GEN.ASSETS / f"{slug}.svg").read_text(encoding="utf-8"))
