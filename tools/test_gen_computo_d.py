"""Guardas de tools/gen_computo_d.py: figuras de las páginas 11 y 12 de la unidad 11.

tools/test_gen_computo.py recorre el catálogo completo de gen_computo.py, que
mezcla DIAGRAMAS_D (el import va en un try que traga ImportError). Aquí va lo
propio del módulo: que llegue de verdad, que no pise ids, la forma de las cuatro
figuras y que cada dibujo diga las cifras del contrato.
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
IDS = ("cmp-ancla-servidor", "cmp-async-vs-def", "cmp-gantt-resultados",
       "cmp-push-webhook")


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


def test_el_catalogo_tiene_las_cuatro_figuras_del_contrato():
    assert tuple(_cargar("gen_computo_d").DIAGRAMAS_D) == IDS


def test_se_importa_sin_ciclo():
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys, gen_computo_d; "
         "assert 'gen_computo' not in sys.modules, 'importa gen_computo'; "
         "print(len(gen_computo_d.DIAGRAMAS_D))"],
        capture_output=True, text=True, cwd=TOOLS)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == str(len(IDS))


def test_el_catalogo_llega_a_gen_computo_sin_pisar_ids():
    base = _cargar("gen_computo")
    d = _cargar("gen_computo_d").DIAGRAMAS_D
    for nombre in IDS:
        assert nombre in base.DIAGRAMAS, (
            f"{nombre} no llegó a gen_computo.DIAGRAMAS: el import de gen_computo_d "
            "falló en silencio (lo envuelve un try/except ImportError)")
        assert base.DIAGRAMAS[nombre].__name__ == d[nombre].__name__
    fuente = (TOOLS / "gen_computo.py").read_text(encoding="utf-8")
    repetidos = set(re.findall(r'"(cmp-[\w-]+)"\s*:', fuente)) & set(d)
    assert not repetidos, f"ids repetidos en los dos catálogos: {sorted(repetidos)}"
    for otro in ("gen_computo_b", "gen_computo_c"):
        if (TOOLS / f"{otro}.py").is_file():
            catalogo = getattr(_cargar(otro), "DIAGRAMAS_" + otro[-1].upper())
            assert not set(catalogo) & set(d), f"{otro} repite ids de gen_computo_d"


def test_cada_svg_en_disco_es_lo_que_produce_el_generador():
    for nombre, funcion in _cargar("gen_computo_d").DIAGRAMAS_D.items():
        assert nombre.startswith("cmp-"), nombre
        assert (ASSETS / f"{nombre}.svg").is_file(), (
            f"falta {nombre}.svg: corre python3 tools/gen_computo.py {nombre}")
        assert _svg(nombre) == funcion(), (
            f"{nombre}.svg no coincide con gen_computo_d.py: no lo edites a mano")


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
        assert tamanos and min(tamanos) >= 13, f"{nombre}: texto de {min(tamanos)} px"
        fuera = {c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}\b", svg)} - paleta
        assert not fuera, f"{nombre}: colores fuera del skin {sorted(fuera)}"


def test_sin_griegas_ni_analogias():
    prohibido = re.compile(r"[Ͱ-Ͽ]|cocin|mesero|chef|restaurante|es como|imagina", re.I)
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
    """Un «3» solo no dice de qué es: va con su unidad o su nombre."""
    for nombre in IDS:
        sueltos = re.findall(r'font-weight="\w+" text-anchor="\w+">(\d+)</text>', _svg(nombre))
        # Las marcas del eje de tiempo son la excepción: llevan «tiempo (s)» al lado.
        if nombre in ("cmp-async-vs-def", "cmp-gantt-resultados"):
            assert "tiempo (s)" in _svg(nombre)
            continue
        assert not sueltos, f"{nombre}: dígitos sueltos {sueltos}"


def test_ancla_servidor_hace_la_cuenta_de_conexiones():
    d = _cargar("gen_computo_d")
    assert (d.R_REPLICAS, d.N_WORKERS, d.K_POOL) == (3, 4, 10)
    assert d.R_REPLICAS * d.N_WORKERS * d.K_POOL == 120
    svg = _svg("cmp-ancla-servidor")
    for pedazo in ("R × N × k = 3 × 4 × 10 = 120 conexiones", "97 disponibles",
                   "100 menos 3 reservadas", "pool local", "loop", "PgBouncer",
                   "población 1", "población 2", "modo transacción", "max_client_conn", "pool_mode = transaction", "balanceador", "un backend",
                   "una por"):
        assert pedazo in svg, pedazo
    assert svg.count(">pool local<") == d.N_WORKERS
    assert svg.count(">loop<") == d.N_WORKERS
    # El pool, resaltado: contorno de 3 px de ancho en el color de acento.
    assert svg.count('stroke="#7ef29d" stroke-width="3"') == d.N_WORKERS


def test_async_contra_def_sale_de_los_datos():
    d = _cargar("gen_computo_d")
    assert (d.PETICIONES, d.W_S, d.LATIDO_MS) == (12, 0.5, 10)
    assert d.PETICIONES * d.W_S == 6
    svg = _svg("cmp-async-vs-def")
    for pedazo in ("12 × 0.5 s = 6 s", "w = 0.5 s", "cada 10 ms", "latido del loop",
                   "el latido no corre en 6 s: hueco máximo ≈ 12·w",
                   "hueco máximo &lt; 0.1 s", "las 12 terminan en 0.5 s", "40 hilos",
                   "loop: hilo dormido, no atiende a nadie", "con def, el loop sigue corriendo"):
        assert pedazo in svg, pedazo
    assert "sonda" not in svg
    for i in range(1, 13):
        assert f">p{i}<" in svg, f"falta la barra p{i}"
        assert f"hilo {i}: p{i}" in svg, f"falta el hilo {i}"
    # Latido a escala: en (b) una marca cada 10 ms durante 7 s; en (a) sólo dos ráfagas de 20 ms (antes y después de los 6 s).
    marcas = len(re.findall(r'stroke-width="0.8"', svg))
    assert marcas == 700 + 2 * 2, marcas


def test_gantt_resultados_dice_cuando_se_entera_cada_uno():
    d = _cargar("gen_computo_d")
    assert (d.EVENTO_S, d.CADA_S) == (10, 3)
    consultas = [t for t in range(d.CADA_S, d.EVENTO_S + d.CADA_S, d.CADA_S)]
    assert consultas == [3, 6, 9, 12]
    assert consultas[-1] - d.EVENTO_S == 2
    svg = _svg("cmp-gantt-resultados")
    for pedazo in ("evento: 10 s", "consulta cada 3 s", "demora de 2 s", "trae el resultado",
                   "consulta 4", "no hay petición pendiente (con keep-alive el socket puede seguir abierto)", "consulta pendiente", "respuesta abierta",
                   "responde en 10 s", "el evento llega en 10 s", "4 consultas, 3 sin novedades",
                   "80 consultas", "60 vuelven sin novedades", "casi 0 s de demora"):
        assert pedazo in svg, pedazo
    # Rótulos <text>: tres consultas, el resumen del polling y la cuenta de 20 clientes.
    assert len(re.findall(r">[^<]*sin novedades[^<]*</text>", svg)) == 5


def test_push_webhook_marca_quien_inicia_y_que_queda_abierto():
    svg = _svg("cmp-push-webhook")
    for pedazo in ("inicia: el cliente", "inicia: el emisor", "GET /eventos", "GET con Upgrade",
                   "101: cambia de protocolo", "POST /evento", "200 OK",
                   "mensaje (cliente envía)", "mensaje (servidor envía)",
                   "evento (servidor envía)", "queda abierto:",
                   "una respuesta HTTP larga", "una conexión, en", "los dos sentidos",
                   "no deja petición pendiente", "una URL"):
        assert pedazo in svg, pedazo
    assert svg.count("inicia: el cliente") == 2 and svg.count("inicia: el emisor") == 1


def test_cada_figura_tiene_fila_de_creditos():
    creditos = (ASSETS / "CREDITOS.md").read_text(encoding="utf-8")
    for nombre in IDS:
        assert f"| {nombre}.svg |" in creditos, f"{nombre}.svg sin fila en CREDITOS.md"
