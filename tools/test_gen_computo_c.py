"""Guardas de tools/gen_computo_c.py: figuras de las páginas 9 y 10 (unidad 11).

tools/test_gen_computo.py ya recorre el catálogo completo de gen_computo.py,
que incluye DIAGRAMAS_C. Aquí va lo propio: que el módulo se importe sin ciclo,
que su catálogo llegue de verdad a gen_computo (el import va dentro de un try
que traga ImportError), que el archivo en disco sea lo que produce el
generador, la forma (aria, tamaño, fuente, colores, viewBox, sin griegas, sin
dígitos sueltos) y que cada dibujo diga las cifras que el contrato fija.
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
IDS = ("cmp-dist-relojes", "cmp-dist-tres-causas", "cmp-capas",
       "cmp-gantt-tres-planificaciones")


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
    assert tuple(_cargar("gen_computo_c").DIAGRAMAS_C) == IDS


def test_se_importa_sin_ciclo():
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys, gen_computo_c; "
         "assert 'gen_computo' not in sys.modules, 'importa gen_computo'; "
         "print(len(gen_computo_c.DIAGRAMAS_C))"],
        capture_output=True, text=True, cwd=TOOLS)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == str(len(IDS))


def test_el_catalogo_llega_a_gen_computo_sin_pisar_ids():
    base = _cargar("gen_computo")
    c = _cargar("gen_computo_c").DIAGRAMAS_C
    for nombre in IDS:
        assert nombre in base.DIAGRAMAS, f"{nombre} no llegó a gen_computo.DIAGRAMAS"
        assert base.DIAGRAMAS[nombre].__name__ == c[nombre].__name__
    fuente = (TOOLS / "gen_computo.py").read_text(encoding="utf-8")
    repetidos = set(re.findall(r'"(cmp-[\w-]+)"\s*:', fuente)) & set(c)
    assert not repetidos, f"ids repetidos en los dos catálogos: {sorted(repetidos)}"


def test_cada_svg_en_disco_es_lo_que_produce_el_generador():
    for nombre, funcion in _cargar("gen_computo_c").DIAGRAMAS_C.items():
        assert nombre.startswith("cmp-"), nombre
        assert (ASSETS / f"{nombre}.svg").is_file(), (
            f"falta {nombre}.svg: corre python3 tools/gen_computo.py {nombre}")
        assert _svg(nombre) == funcion(), (
            f"{nombre}.svg no coincide con gen_computo_c.py: no lo edites a mano")


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


def test_sin_digitos_sueltos_en_rotulos_en_negrita():
    """Un «1» solo en una barra se lee como «CPU 1»: va T1, hilo A, 100 ms."""
    for nombre in IDS:
        sueltos = re.findall(r'font-weight="600" text-anchor="middle">(\d+)</text>',
                             _svg(nombre))
        # La única excepción: la marca de B (80) resaltada sobre su eje.
        assert sueltos in ([], ["80"]), f"{nombre}: rótulos sin prefijo {sueltos}"


def test_ningun_texto_se_sale_del_viewbox():
    patron = re.compile(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*font-family="([^"]+)" '
                        r'font-size="([\d.]+)" font-weight="(\w+)" text-anchor="(\w+)">([^<]*)<')
    for nombre in IDS:
        svg = _svg(nombre)
        ancho, alto = map(float, re.search(r'viewBox="0 0 (\S+) (\S+)"', svg).groups())
        textos = patron.findall(svg)
        assert len(textos) == svg.count("<text "), f"{nombre}: texto que la guarda no lee"
        for x, y, familia, tam, peso, anclaje, s in textos:
            s = html.unescape(s)
            k = 0.6 if "mono" in familia else (0.58 if peso == "600" else 0.54)
            w = len(s) * float(tam) * k
            x0 = {"start": float(x), "middle": float(x) - w / 2, "end": float(x) - w}[anclaje]
            assert x0 >= 4 and x0 + w <= ancho - 4 and float(y) <= alto - 4, (
                f"{nombre}: {s!r} se sale del viewBox")


def test_los_relojes_hacen_la_cuenta_del_contrato():
    c = _cargar("gen_computo_c")
    assert (c.MARCA_A, c.MARCA_B, c.LATENCIA, c.DESFASE_B) == (100, 80, 20, -40)
    assert c.MARCA_B - c.MARCA_A == c.LATENCIA + c.DESFASE_B == -20
    svg = _svg("cmp-dist-relojes")
    for pedazo in ("B marca 80, A marcó 100: 80−100 = −20 ms = 20 ms − 40 ms",
                   "reloj de A (ms)", "reloj de B (ms)", "componente A", "componente B",
                   "A marca 100 ms al enviar", "B marca 80 ms al recibir",
                   "tránsito real 20 ms"):
        assert pedazo in svg, pedazo


def test_las_tres_causas_y_la_misma_observacion():
    svg = _svg("cmp-dist-tres-causas")
    for pedazo in ("1. La ida se pierde", "2. La respuesta", "3. El servidor tarda",
                   "la petición se pierde", "la respuesta se pierde", "llega tras t_max"):
        assert pedazo in svg, pedazo
    assert svg.count(">espero t_max y no sé<") == 3


def test_capas_separan_pertenencia_de_ejecucion():
    svg = _svg("cmp-capas")
    for pedazo in ("máquina", "proceso", "hilo", "tarea", "Pertenencia", "Ejecución",
                   "el sistema operativo", "asigna hilos a CPU lógicas",
                   "el runtime reparte tareas entre hilos", "planifica: el SO",
                   "planifica: el runtime", "T2 puede migrar de hilo (p. ej. en Go;", "en asyncio una tarea no cambia de hilo)"):
        assert pedazo in svg, pedazo


def test_gantt_tres_planificaciones_cuentas_y_razones():
    c = _cargar("gen_computo_c")
    assert (c.TAREAS, c.TAREA_MS) == (4, 100)
    svg = _svg("cmp-gantt-tres-planificaciones")
    assert svg.count("⌈4/1⌉·100 = 400 ms") == 2
    assert svg.count("⌈4/4⌉·100 = 100 ms") == 1
    assert 'id="rayado"' in svg and 'fill="url(#rayado)"' in svg
    assert 'stroke-dasharray="3 3"' in svg          # CPU inactiva, en contorno
    for pedazo in ("el hilo único", "espera la", "exclusión global", "(a)", "(b)", "(c)",
                   "T1 · hilo A · CPU 1", "CPU 2, 3 y 4", "T2, T3 y T4"):
        assert pedazo in svg, pedazo
    # (a) y (b): tres tareas esperan en rayado; (c): ninguna; más la leyenda.
    assert svg.count('fill="url(#rayado)"') == 3 + 3 + 1


def test_cada_figura_tiene_fila_de_creditos():
    creditos = (ASSETS / "CREDITOS.md").read_text(encoding="utf-8")
    for nombre in IDS:
        assert f"| {nombre}.svg |" in creditos, f"{nombre}.svg sin fila en CREDITOS.md"
