"""Guarda: las ilustraciones existen, pesan poco y ningun prompt pide una persona real.

El catalogo es la unica fuente de verdad de las ilustraciones. Ninguna puede
representar a una persona real, a un rostro reconocible ni a un personaje con
derechos.
"""
import json
import re
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
CATALOGO = RAIZ / "tools/ilustraciones.json"
# Cada ilustracion declara su unidad en el catalogo. Antes esta guarda tenia una
# sola ruta fija, asi que una portada de otra unidad quedaba sin vigilar.
UNIDAD_POR_OMISION = "2_pipeline_de_datos"


def unidad_de(nombre):
    return catalogo().get("unidades", {}).get(nombre, UNIDAD_POR_OMISION)


def paginas_de(nombre):
    return RAIZ / "course" / unidad_de(nombre)


def assets_de(nombre):
    return paginas_de(nombre) / "_assets"


# Las dos ultimas guardas de este archivo vigilan convenciones propias de
# Pipeline de Datos, no reglas del curso, y conservan su ruta fija.
PAGINAS_PIPELINE = RAIZ / "course/2_pipeline_de_datos"
ASSETS_PIPELINE = PAGINAS_PIPELINE / "_assets"

# Nombres propios de personas reales que rondan el temario de la unidad, y
# personajes con derechos que un prompt podria invocar por descuido.
PROHIBIDOS = [
    "tukey", "wickham", "codd", "kimball", "inmon", "hadley",
    "musk", "bezos", "zuckerberg",
    "mickey", "pikachu", "mario", "batman", "sherlock",
    # Las obras de referencia estetica y sus personajes: se cita el registro
    # visual, nunca el personaje ni el titulo.
    "ghost in the shell", "kusanagi", "motoko", "batou",
    "serial experiments", "lain", "akira", "kaneda", "tetsuo",
    "frieren", "evangelion", "ayanami", "studio ghibli", "ghibli",
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
    assert set(datos) == {"estilo", "tamano", "ilustraciones", "unidades"}
    assert datos["tamano"] == "1024x1024"
    assert datos["ilustraciones"], "el catalogo no declara ninguna ilustracion"


def test_cada_ilustracion_declara_su_unidad():
    datos = catalogo()
    for nombre in nombres():
        unidad = datos["unidades"].get(nombre)
        assert unidad, f"'{nombre}' no declara unidad en el catalogo"
        assert (RAIZ / "course" / unidad).is_dir(), (
            f"'{nombre}' apunta a la unidad '{unidad}', que no existe"
        )


def test_todas_generadas():
    for nombre in nombres():
        ruta = assets_de(nombre) / f"ilus-{nombre}.jpg"
        assert ruta.is_file(), f"falta {ruta.relative_to(RAIZ)}"


def test_dimensiones_y_peso():
    for nombre in nombres():
        ruta = assets_de(nombre) / f"ilus-{nombre}.jpg"
        with Image.open(ruta) as im:
            assert im.width == 1024, f"{ruta.name} mide {im.width}px de ancho"
        assert ruta.stat().st_size < 400_000, f"{ruta.name} pesa demasiado"


def _menciona(termino, texto):
    """Coincidencia por limites de palabra: evita falsos positivos como
    'mario' dentro de 'armario' o 'lain' dentro de 'polaina'."""
    return re.search(rf"\b{re.escape(termino)}\b", texto) is not None


def test_ningun_prompt_pide_persona_real_o_personaje_protegido():
    texto = json.dumps(catalogo(), ensure_ascii=False).lower()
    for termino in PROHIBIDOS:
        assert not _menciona(termino, texto), f"el catalogo menciona '{termino}'"


def test_la_guarda_de_prohibidos_no_dispara_con_subcadenas_inocentes():
    texto = "un armario metalico y unas polainas de cuero en el taller"
    for termino in PROHIBIDOS:
        assert not _menciona(termino, texto), (
            f"'{termino}' disparo un falso positivo contra texto inocente"
        )


def test_la_guarda_de_prohibidos_si_dispara_con_una_obra_prohibida():
    texto = "una escena inspirada en ghost in the shell"
    disparo = any(_menciona(termino, texto) for termino in PROHIBIDOS)
    assert disparo, "la guarda no detecto una obra prohibida citada de verdad"


def test_ningun_prompt_pide_una_figura_humana_identificable():
    for nombre, prompt in catalogo()["ilustraciones"].items():
        bajo = prompt.lower()
        for termino in PROHIBIDOS_EN_PROMPT:
            assert termino not in bajo, (
                f"el prompt de '{nombre}' pide '{termino}'"
            )


def test_el_estilo_prohibe_texto_y_rostros_identificables():
    estilo = catalogo()["estilo"]
    assert estilo.rstrip().endswith(
        "Sin texto, sin letras, sin marcas de agua, sin firmas."
    ), "el estilo debe cerrar prohibiendo texto, marcas de agua y firmas"
    assert "sin rostros identificables" in estilo.lower()


def test_creditos_marcan_las_generadas():
    for nombre in nombres():
        creditos = (assets_de(nombre) / "CREDITOS.md").read_text(encoding="utf-8").lower()
        assert f"ilus-{nombre}.jpg" in creditos, f"ilus-{nombre}.jpg sin credito"
        assert "generada" in creditos
        assert "ninguna" in creditos and "personas reales" in creditos, (
            f"el CREDITOS.md de {unidad_de(nombre)} debe decir que ninguna "
            "ilustracion representa personas reales"
        )


def test_cada_ilustracion_se_usa_en_una_pagina():
    for nombre in nombres():
        texto = "\n".join(
            p.read_text(encoding="utf-8")
            for p in sorted(paginas_de(nombre).rglob("*.md"))
            if p.name != "CREDITOS.md"
        )
        assert f"_assets/ilus-{nombre}.jpg" in texto, (
            f"ilus-{nombre}.jpg no se usa en ninguna pagina de "
            f"{unidad_de(nombre)}"
        )


def test_no_queda_png_de_ilustracion_huerfano():
    huerfanos = sorted(p.name for p in ASSETS_PIPELINE.glob("ilus-*.png"))
    assert not huerfanos, f"PNGs de ilustracion sin reemplazar por jpg: {huerfanos}"


def test_cada_pagina_es_un_directorio_con_indice():
    sueltas = sorted(
        p.name for p in PAGINAS_PIPELINE.glob("*.md") if p.name != "0_index.md"
    )
    assert not sueltas, f"paginas sin promover a directorio: {sueltas}"
    directorios = sorted(
        d.name for d in PAGINAS_PIPELINE.iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )
    assert directorios, "la unidad no tiene ninguna pagina"
    for nombre in directorios:
        assert (PAGINAS_PIPELINE / nombre / "0_index.md").is_file(), (
            f"{nombre}/ no tiene 0_index.md"
        )
