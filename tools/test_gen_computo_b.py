"""Guardas de tools/gen_computo_b.py: figuras de pools, recursos y arquitectura (unidad 11).

tools/test_gen_computo.py ya recorre el catálogo completo de gen_computo.py,
que incluye DIAGRAMAS_B, y comprueba allí que no sobren SVG sin generador. Aquí
va lo propio de este módulo: que se importe sin ciclo, que su catálogo llegue
de verdad a gen_computo (el import va dentro de un try que traga ImportError),
que no pise ids del catálogo base y que cada dibujo diga las cifras que las
páginas citan. Las comprobaciones de forma (aria, tamaño, fuente, colores) se
repiten sólo para estas ocho figuras, para que el fallo apunte a este archivo.
"""
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
IDS = ("cmp-roles-recursos", "cmp-ciclo-conexion", "cmp-gantt-pool",
       "cmp-pool-soltar-antes", "cmp-run-in-executor", "cmp-arq-offload",
       "cmp-arq-servidores", "cmp-arq-little")


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


def test_el_catalogo_tiene_las_ocho_figuras_del_contrato():
    assert tuple(_cargar("gen_computo_b").DIAGRAMAS_B) == IDS


def test_se_importa_sin_ciclo():
    """gen_computo importa este módulo; este módulo no debe importar gen_computo."""
    r = subprocess.run(
        [sys.executable, "-c",
         "import sys, gen_computo_b; "
         "assert 'gen_computo' not in sys.modules, 'importa gen_computo'; "
         "print(len(gen_computo_b.DIAGRAMAS_B))"],
        capture_output=True, text=True, cwd=TOOLS)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == str(len(IDS))


def test_el_catalogo_llega_a_gen_computo_sin_pisar_ids():
    base = _cargar("gen_computo")
    b = _cargar("gen_computo_b").DIAGRAMAS_B
    for nombre in IDS:
        assert nombre in base.DIAGRAMAS, (
            f"{nombre} no llegó a gen_computo.DIAGRAMAS: el import de "
            "gen_computo_b falló en silencio (lo envuelve un try/except ImportError)"
        )
        assert base.DIAGRAMAS[nombre].__name__ == b[nombre].__name__
    # update() pisaría en silencio un id repetido: se busca en el código fuente.
    fuente = (TOOLS / "gen_computo.py").read_text(encoding="utf-8")
    repetidos = set(re.findall(r'"(cmp-[\w-]+)"\s*:', fuente)) & set(b)
    assert not repetidos, f"ids repetidos en los dos catálogos: {sorted(repetidos)}"


def test_cada_svg_en_disco_es_lo_que_produce_el_generador():
    for nombre, funcion in _cargar("gen_computo_b").DIAGRAMAS_B.items():
        assert nombre.startswith("cmp-"), nombre
        assert (ASSETS / f"{nombre}.svg").is_file(), (
            f"falta {nombre}.svg: corre python3 tools/gen_computo.py {nombre}")
        assert _svg(nombre) == funcion(), (
            f"{nombre}.svg no coincide con gen_computo_b.py: no lo edites a mano, "
            "cambia la función y vuelve a correr el generador")


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
    prohibido = re.compile(
        r"[Ͱ-Ͽ]|cocin|mesero|chef|restaurante|es como|imagina", re.I)
    for nombre in IDS:
        hallado = prohibido.search(_svg(nombre))
        assert not hallado, f"{nombre}: {hallado.group(0)!r}"


def test_los_totales_de_los_esquemas_salen_de_los_datos():
    b = _cargar("gen_computo_b")
    olas = -(-b.POOL_N // b.POOL_K)
    assert (b.POOL_K, b.POOL_N, b.POOL_MS, olas) == (5, 20, 200, 4)
    assert "total 800 ms" in _svg("cmp-gantt-pool")
    _, retener = b._tramos_retener()
    _, soltar = b._tramos_soltar()
    assert (retener, soltar) == (2400, 1300)
    svg = _svg("cmp-pool-soltar-antes")
    for pedazo in ("total 2400 ms (esquema)", "total 1300 ms (esquema)",
                   "pool de 3 conexiones"):
        assert pedazo in svg, pedazo


def test_soltar_nunca_usa_mas_conexiones_que_el_pool():
    """En ningún instante hay más de k tramos de BD a la vez, en ningún panel."""
    b = _cargar("gen_computo_b")
    for carriles, _ in (b._tramos_retener(), b._tramos_soltar()):
        assert len(carriles) == b.SOLTAR_K
        for tramos in carriles:
            orden = sorted((ini, fin) for _, ini, fin, _ in tramos)
            for (_, fin), (ini, _) in zip(orden, orden[1:]):
                assert fin <= ini, "dos tramos solapados en la misma conexión"


def test_gantt_pool_dibuja_olas_cola_y_la_sexta():
    svg = _svg("cmp-gantt-pool")
    for pedazo in ("ola 1", "ola 4", "conexión 5", "petición 6", "espera conexión",
                   "15 esperan", "10 esperan", "5 esperan", ">p20<", "esquema"):
        assert pedazo in svg, pedazo


def test_las_trazas_de_pool_explican_por_que_y_el_total():
    pool = _svg("cmp-gantt-pool")
    for pedazo in ("espera: 5 en vuelo", "las 5 están prestadas",
                   "20 / 5 = 4 olas × 200 ms = 800 ms"):
        assert pedazo in pool, pedazo
    soltar = _svg("cmp-pool-soltar-antes")
    for pedazo in ("cola del pool", "las 3 están retenidas", "(100 + 1000 + 100) = 2400 ms",
                   "total 1300 ms"):
        assert pedazo in soltar, pedazo
    ejecutor = _svg("cmp-run-in-executor")
    for pedazo in ("en otra CPU", "latido: otra corrutina", "termina en 2020 ms"):
        assert pedazo in ejecutor, pedazo


def test_roles_y_ciclo_dicen_lo_que_la_pagina_5_promete():
    roles = _svg("cmp-roles-recursos")
    for pedazo in ("quién corre", "quién entra", "qué conexión usas", "quién ejecuta",
                   "acquire", "release", "get", "put"):
        assert pedazo in roles, pedazo
    ciclo = _svg("cmp-ciclo-conexion")
    for pedazo in ("libre", "prestada", "keep-alive", "petición 6", "cola del pool",
                   "HTTP/1.1", "HTTP/2"):
        assert pedazo in ciclo, pedazo


def test_run_in_executor_late_durante_el_calculo():
    svg = _svg("cmp-run-in-executor")
    assert "Future" in svg and "2000 ms" in svg and "100 ms" in svg
    # Los latidos: rectángulos de 6 px en el carril del loop, uno cada 100 ms.
    assert len(re.findall(r'width="6\.0"', svg)) == 25


def test_arquitectura_servidores_offload_y_little():
    serv = _svg("cmp-arq-servidores")
    for pedazo in ("hilo por conexión", "event loop", "prefork"):
        assert pedazo in serv, pedazo
    assert serv.count(">sí: ") == 3 and serv.count(">no: ") == 3
    off = _svg("cmp-arq-offload")
    for pedazo in ("run_in_executor", "min(k, P)", "pickle", "Future"):
        assert pedazo in off, pedazo
    little = _svg("cmp-arq-little")
    for pedazo in ("L = lambda · W", "160/s", "3.2 s", "3.32 s", "4.04 s", "151/s",
                   "cota"):
        assert pedazo in little, pedazo


def test_cada_figura_tiene_fila_de_creditos():
    creditos = (ASSETS / "CREDITOS.md").read_text(encoding="utf-8")
    for nombre in IDS:
        assert f"| {nombre}.svg |" in creditos, f"{nombre}.svg sin fila en CREDITOS.md"
