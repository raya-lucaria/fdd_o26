"""Guarda: las ilustraciones existen, pesan poco y ningun prompt pide una persona real.

El catalogo es la unica fuente de verdad de las ilustraciones. Ninguna puede
representar a una persona real, a un rostro reconocible ni a un personaje con
derechos.
"""
import json
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "course/2_pipeline_de_datos/_assets"
CATALOGO = RAIZ / "tools/ilustraciones.json"
CREDITOS = ASSETS / "CREDITOS.md"
PAGINAS = RAIZ / "course/2_pipeline_de_datos"

# Nombres propios de personas reales que rondan el temario de la unidad, y
# personajes con derechos que un prompt podria invocar por descuido.
PROHIBIDOS = [
    "tukey", "wickham", "codd", "kimball", "inmon", "hadley",
    "musk", "bezos", "zuckerberg",
    "mickey", "pikachu", "mario", "batman", "sherlock",
]

# Terminos que delatan a una figura humana identificable en un prompt.
PROHIBIDOS_EN_PROMPT = [
    "rostro", "retrato", "cara humana", "celebridad", "famoso",
    "fotografia de una persona", "logotipo", "marca comercial",
]


def catalogo():
    return json.loads(CATALOGO.read_text(encoding="utf-8"))


def nombres():
    return list(catalogo()["ilustraciones"])


def test_catalogo_tiene_las_llaves_esperadas():
    datos = catalogo()
    assert set(datos) == {"estilo", "tamano", "ilustraciones"}
    assert datos["tamano"] == "1024x1024"
    assert datos["ilustraciones"], "el catalogo no declara ninguna ilustracion"


def test_todas_generadas():
    for nombre in nombres():
        assert (ASSETS / f"ilus-{nombre}.jpg").is_file(), f"falta ilus-{nombre}.jpg"


def test_dimensiones_y_peso():
    for nombre in nombres():
        ruta = ASSETS / f"ilus-{nombre}.jpg"
        with Image.open(ruta) as im:
            assert im.width == 1024, f"{ruta.name} mide {im.width}px de ancho"
        assert ruta.stat().st_size < 400_000, f"{ruta.name} pesa demasiado"


def test_ningun_prompt_pide_persona_real_o_personaje_protegido():
    texto = json.dumps(catalogo(), ensure_ascii=False).lower()
    for termino in PROHIBIDOS:
        assert termino not in texto, f"el catalogo menciona '{termino}'"


def test_ningun_prompt_pide_una_figura_humana_identificable():
    for nombre, prompt in catalogo()["ilustraciones"].items():
        bajo = prompt.lower()
        for termino in PROHIBIDOS_EN_PROMPT:
            assert termino not in bajo, (
                f"el prompt de '{nombre}' pide '{termino}'"
            )


def test_el_estilo_prohibe_texto_y_figuras_humanas():
    estilo = catalogo()["estilo"]
    assert estilo.rstrip().endswith(
        "Sin texto, sin letras, sin marcas de agua, sin firmas."
    ), "el estilo debe cerrar prohibiendo texto, marcas de agua y firmas"
    assert "sin figuras humanas" in estilo.lower()


def test_creditos_marcan_las_generadas():
    creditos = CREDITOS.read_text(encoding="utf-8").lower()
    for nombre in nombres():
        assert f"ilus-{nombre}.jpg" in creditos, f"ilus-{nombre}.jpg sin credito"
    assert "generada" in creditos
    assert "ninguna" in creditos and "personas reales" in creditos, (
        "el encabezado de CREDITOS.md debe decir que ninguna ilustracion "
        "representa personas reales"
    )


def test_cada_ilustracion_se_usa_en_una_pagina():
    texto = "\n".join(
        p.read_text(encoding="utf-8") for p in sorted(PAGINAS.glob("*.md"))
    )
    for nombre in nombres():
        assert f"_assets/ilus-{nombre}.jpg" in texto, (
            f"ilus-{nombre}.jpg no se usa en ninguna pagina de la unidad"
        )


def test_no_queda_png_de_ilustracion_huerfano():
    huerfanos = sorted(p.name for p in ASSETS.glob("ilus-*.png"))
    assert not huerfanos, f"PNGs de ilustracion sin reemplazar por jpg: {huerfanos}"
