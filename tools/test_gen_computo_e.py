"""Guardas de tools/gen_computo_e.py: figuras de «Elegir el canal» (página 12, unidad 11).

tools/test_gen_computo.py recorre el catálogo completo de gen_computo.py, que
mezcla DIAGRAMAS_E. Aquí va lo propio del módulo: que llegue de verdad, que no pise
ids, la forma de las tres figuras y lo que cada dibujo dice.
"""
import html
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
TOOLS = RAIZ / "tools"
ASSETS = RAIZ / "course/11_computo_y_concurrencia/_assets"
SKIN = RAIZ / "skins/fdd-eva.yaml"
IDS = ("cmp-canales-eventos", "cmp-canales-arquitectura", "cmp-canales-decision")


def _cargar(nombre):
    spec = importlib.util.spec_from_file_location(nombre, TOOLS / f"{nombre}.py")
    modulo = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(TOOLS))
    try:
        spec.loader.exec_module(modulo)
    finally:
        sys.path.pop(0)
    return modulo


def _svg(nombre):
    return (ASSETS / f"{nombre}.svg").read_text(encoding="utf-8")


def test_el_catalogo_tiene_las_tres_figuras():
    assert tuple(_cargar("gen_computo_e").DIAGRAMAS_E) == IDS


def test_se_importa_sin_ciclo():
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys, gen_computo_e; "
         "assert 'gen_computo' not in sys.modules, 'importa gen_computo'; "
         "print(len(gen_computo_e.DIAGRAMAS_E))"],
        capture_output=True, text=True, cwd=TOOLS)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == str(len(IDS))


def test_el_catalogo_llega_a_gen_computo_sin_pisar_ids():
    base = _cargar("gen_computo")
    e = _cargar("gen_computo_e").DIAGRAMAS_E
    for nombre in IDS:
        assert nombre in base.DIAGRAMAS, f"{nombre} no llegó a gen_computo.DIAGRAMAS"
        assert base.DIAGRAMAS[nombre].__name__ == e[nombre].__name__
    for otro, nom in (("gen_computo_b", "DIAGRAMAS_B"), ("gen_computo_c", "DIAGRAMAS_C"),
                      ("gen_computo_d", "DIAGRAMAS_D")):
        if (TOOLS / f"{otro}.py").is_file():
            assert not set(getattr(_cargar(otro), nom)) & set(e), f"{otro} repite ids"


def test_cada_svg_en_disco_es_lo_que_produce_el_generador():
    for nombre, funcion in _cargar("gen_computo_e").DIAGRAMAS_E.items():
        assert (ASSETS / f"{nombre}.svg").is_file(), (
            f"falta {nombre}.svg: corre python3 tools/gen_computo.py {nombre}")
        assert _svg(nombre) == funcion(), f"{nombre}.svg no coincide: no lo edites a mano"


def test_forma_aria_tamano_fuente_y_colores():
    tokens = yaml.safe_load(SKIN.read_text(encoding="utf-8"))["tokens"]
    paleta = {c.lower() for c in
              set(tokens["color"].values()) | set(tokens["graph"].values())
              if isinstance(c, str)}
    for nombre in IDS:
        svg = _svg(nombre)
        raiz = re.search(r"<svg\b[^>]*>", svg).group(0)
        assert re.search(r'\swidth="\d+"', raiz) and re.search(r'\sheight="\d+"', raiz), nombre
        aria = re.search(r'aria-label="([^"]*)"', raiz).group(1)
        assert len(aria) >= 80, f"{nombre}: aria-label de {len(aria)} caracteres"
        tamanos = [float(t) for t in re.findall(r'font-size="([\d.]+)"', svg)]
        assert tamanos and min(tamanos) >= 16, f"{nombre}: texto de {min(tamanos)} px"
        fuera = {c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}\b", svg)} - paleta
        assert not fuera, f"{nombre}: colores fuera del skin {sorted(fuera)}"


def test_sin_griegas_ni_analogias():
    prohibido = re.compile(r"[\u0370-\u03ff]|cocin|mesero|chef|restaurante|es como|imagina", re.I)
    for nombre in IDS:
        hallado = prohibido.search(_svg(nombre))
        assert not hallado, f"{nombre}: {hallado.group(0)!r}"


def test_ningun_texto_se_sale_del_viewbox():
    patron = re.compile(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*font-family="([^"]+)" '
                        r'font-size="([\d.]+)" font-weight="(\w+)" text-anchor="(\w+)">([^<]*)<')
    for nombre in IDS:
        svg = _svg(nombre)
        ancho, alto = map(float, re.search(r'viewBox="0 0 (\S+) (\S+)"', svg).groups())
        for x, y, familia, tam, peso, anclaje, s in patron.findall(svg):
            s = html.unescape(s)
            k = 0.6 if "mono" in familia else (0.58 if peso == "600" else 0.54)
            w = len(s) * float(tam) * k
            x0 = {"start": float(x), "middle": float(x) - w / 2, "end": float(x) - w}[anclaje]
            assert x0 >= 4 and x0 + w <= ancho - 4 and float(y) <= alto - 4, (
                f"{nombre}: {s!r} se sale del viewBox")


def test_ningun_rotulo_es_un_digito_suelto():
    for nombre in IDS:
        sueltos = re.findall(r'font-weight="\w+" text-anchor="\w+">(\d+)</text>', _svg(nombre))
        assert not sueltos, f"{nombre}: dígitos sueltos {sueltos}"


def test_eventos_dice_los_mismos_tres_eventos_en_los_cinco_canales():
    e = _cargar("gen_computo_e")
    assert (e.EVENTOS_S, e.EJE_MAX, e.CADA_S) == ((2, 5, 9), 12, 3)
    consultas = list(range(e.CADA_S, e.EJE_MAX + 1, e.CADA_S))
    demoras = [next(c for c in consultas if c >= ev) - ev for ev in e.EVENTOS_S]
    assert demoras == [1, 1, 0]
    svg = _svg("cmp-canales-eventos")
    for pedazo in ("Los cinco canales para los mismos tres eventos", "pregunta cada 3 s",
                   "una consulta pendiente", "una conexión abierta</",
                   "una conexión abierta, dos sentidos", "el cliente envía",
                   "tres llamadas, nada abierto entre ellas", "sin novedades",
                   ">1 s<", ">0 s<", "evento del servidor"):
        assert pedazo in svg, pedazo
    for canal in ("polling", "long polling", "SSE", "WebSocket", "webhook"):
        assert f">{canal}<" in svg, canal
    for marca in ("0 s", "3 s", "6 s", "9 s", "12 s"):
        assert f">{marca}<" in svg, marca


def test_arquitectura_dice_que_retiene_el_servidor():
    svg = _svg("cmp-canales-arquitectura")
    for pedazo in ("Quién conecta con quién y qué retiene el servidor", "navegadores",
                   "balanceador", "tercero", "tu endpoint", "cola", "trabajador",
                   "polling / long polling: el cliente pregunta al servidor",
                   "cada cliente deja UNA conexión abierta en un servidor",
                   "memoria + un hilo o una tarea por sesión",
                   "el mismo aviso puede llegar dos veces", "retiene"):
        assert pedazo in svg, pedazo
    assert svg.count(">servidor de aplicación<") == 2


def test_decision_llega_a_las_seis_hojas():
    svg = _svg("cmp-canales-decision")
    for pedazo in ("¿Qué canal uso? Tres preguntas", "¿Quién tiene que empezar?",
                   "¿Importa la demora?", ">WebSocket<", ">SSE<", ">webhook<",
                   ">long polling<"):
        assert pedazo in svg, pedazo
    assert svg.count(">polling<") == 2


def test_cada_figura_tiene_fila_de_creditos():
    creditos = (ASSETS / "CREDITOS.md").read_text(encoding="utf-8")
    for nombre in IDS:
        assert f"| {nombre}.svg |" in creditos, f"{nombre}.svg sin fila en CREDITOS.md"
