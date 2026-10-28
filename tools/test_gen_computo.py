"""Guardas del generador de diagramas de la unidad 11 (Computo y concurrencia).

Regenera antes de comparar: correr pytest certifica que lo comiteado coincide
con lo que el generador produce hoy. Editar un SVG a mano falla aqui.

Las convenciones de tamano de la raiz <svg> las cubre
tools/test_svg_tamano_intrinseco.py para todo el curso, y los creditos
tools/test_creditos.py; aqui va lo propio de esta seccion, mas una
comprobacion local de width/height para que el fallo apunte al generador.
"""
import html
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
GENERADOR = RAIZ / "tools/gen_computo.py"
ASSETS = RAIZ / "course/11_computo_y_concurrencia/_assets"
# Las figuras se buscan en todas las paginas de la unidad.
UNIDAD = RAIZ / "course/11_computo_y_concurrencia"
SKIN = RAIZ / "skins/fdd-eva.yaml"
GANTT = ("cmp-gantt-secuencial", "cmp-gantt-hilos", "cmp-gantt-asyncio",
         "cmp-gantt-await-en-serie", "cmp-gantt-procesos")


def _cargar():
    assert GENERADOR.is_file(), "falta tools/gen_computo.py"
    spec = importlib.util.spec_from_file_location("gen_computo", GENERADOR)
    modulo = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(RAIZ / "tools"))
    try:
        spec.loader.exec_module(modulo)
    finally:
        sys.path.pop(0)
    return modulo


def _svg(nombre):
    return (ASSETS / f"{nombre}.svg").read_text(encoding="utf-8")


def test_cada_diagrama_declarado_existe_y_lleva_prefijo():
    for nombre in _cargar().DIAGRAMAS:
        assert nombre.startswith("cmp-"), (
            f"{nombre}: los ids de objeto numerado son unicos en TODO el curso; "
            "sin el prefijo 'cmp-' pueden chocar con otra unidad"
        )
        assert (ASSETS / f"{nombre}.svg").is_file(), f"falta {nombre}.svg"


def test_no_sobran_svg_sin_generador():
    declarados = {f"{n}.svg" for n in _cargar().DIAGRAMAS}
    huerfanos = {p.name for p in ASSETS.glob("*.svg")} - declarados
    assert not huerfanos, f"SVG sin entrada en DIAGRAMAS: {sorted(huerfanos)}"


def test_cada_svg_en_disco_es_lo_que_produce_el_generador():
    for nombre, funcion in _cargar().DIAGRAMAS.items():
        assert _svg(nombre) == funcion(), (
            f"{nombre}.svg no coincide con gen_computo.py: no lo edites a mano, "
            "cambia la funcion y vuelve a correr el generador"
        )


def test_los_colores_salen_del_skin():
    """Todo color hexadecimal del SVG esta en skins/fdd-eva.yaml."""
    tokens = yaml.safe_load(SKIN.read_text(encoding="utf-8"))["tokens"]
    paleta = {c.lower() for c in
              set(tokens["color"].values()) | set(tokens["graph"].values())
              if isinstance(c, str)}
    for nombre in _cargar().DIAGRAMAS:
        usados = {c.lower() for c in re.findall(r"#[0-9a-fA-F]{6}\b", _svg(nombre))}
        fuera = usados - paleta
        assert not fuera, f"{nombre}.svg usa colores fuera del skin: {sorted(fuera)}"


def test_la_raiz_declara_width_y_height():
    for nombre in _cargar().DIAGRAMAS:
        raiz = re.search(r"<svg\b[^>]*>", _svg(nombre)).group(0)
        assert re.search(r'\swidth="\d+"', raiz) and re.search(r'\sheight="\d+"', raiz), (
            f"{nombre}.svg: sin width/height en la raiz se ve como miniatura"
        )


def test_cada_svg_tiene_aria_label_descriptiva():
    for nombre in _cargar().DIAGRAMAS:
        etiqueta = re.search(r'aria-label="([^"]*)"', _svg(nombre)).group(1)
        assert len(etiqueta) >= 80, (
            f"{nombre}.svg: aria-label demasiado corta para describir el diagrama"
        )


def test_el_texto_se_lee():
    """Nada por debajo de 13 px: en el aula se proyecta."""
    for nombre in _cargar().DIAGRAMAS:
        tamanos = [float(t) for t in re.findall(r'font-size="([\d.]+)"', _svg(nombre))]
        assert tamanos and min(tamanos) >= 13, f"{nombre}.svg: texto de {min(tamanos)} px"


def test_sin_letras_griegas_ni_cocina():
    """El material de origen usaba tau, mu y analogias de restaurante."""
    prohibido = re.compile(r"[Ͱ-Ͽ]|cocin|mesero|chef|restaurante", re.I)
    for nombre in _cargar().DIAGRAMAS:
        assert not prohibido.search(_svg(nombre)), nombre


def test_las_gantt_comparten_tareas_eje_y_leyenda():
    """Comparables a simple vista: mismas tareas, mismo eje en ms, misma leyenda."""
    modulo = _cargar()
    assert (modulo.EJECUTA_MS, modulo.ESPERA_MS) == (20, 200)
    for nombre in GANTT:
        svg = _svg(nombre)
        assert "ejecuta 20 ms, espera 200 ms la red, ejecuta 20 ms" in svg, nombre
        assert "tiempo (ms)" in svg and ">800<" in svg, nombre
        for rotulo in ("ejecuta:", "espera:", "lista:", "CPU"):
            assert rotulo in svg, f"{nombre}.svg sin {rotulo!r}"


def test_los_totales_de_las_gantt():
    """Los totales que las paginas citan salen de estos dibujos."""
    esperados = {
        "cmp-gantt-secuencial": 720, "cmp-gantt-hilos": 280,
        "cmp-gantt-asyncio": 280, "cmp-gantt-await-en-serie": 720,
        "cmp-gantt-procesos": 260, "cmp-bloqueo-del-loop": 2080,
    }
    for nombre, total in esperados.items():
        assert f"total {total} ms" in _svg(nombre), nombre


def test_procesos_dibuja_dos_cpu():
    svg = _svg("cmp-gantt-procesos")
    assert "CPU 1" in svg and "CPU 2" in svg
    # Cada fila dice en qué CPU corre y la fila de CPU nombra al proceso.
    for pedazo in ("P1 · CPU 1", "P2 · CPU 2", "P3 · CPU 1", ">P3<",
                   "CPU 1 y 2 ocupadas", "20 + 20 + 200 + 20 = 260 ms"):
        assert pedazo in svg, pedazo


TRAZAS = GANTT + ("cmp-gantt-gather", "cmp-gantt-semaforo", "cmp-bloqueo-del-loop",
                  "cmp-event-loop-ticks", "cmp-create-task")


def test_las_filas_de_cpu_nombran_tareas_no_digitos():
    """Un «1» suelto en la fila de CPU se lee como «CPU 1»: va T1, P1 o main."""
    for nombre in TRAZAS:
        sueltos = re.findall(r'font-weight="600" text-anchor="middle">(\d+)</text>', _svg(nombre))
        assert not sueltos, f"{nombre}: rótulos sin prefijo {sueltos}"


def test_cada_traza_explica_su_total():
    """Bajo la figura, una línea en ámbar hace la cuenta del total."""
    cuentas = {
        "cmp-gantt-secuencial": "3 × (20 + 200 + 20) = 720 ms",
        "cmp-gantt-hilos": "40 + 20 + 200 + 20 = 280 ms",
        "cmp-gantt-asyncio": "40 + 20 + 200 + 20 = 280 ms",
        "cmp-gantt-await-en-serie": "3 × (20 + 200 + 20) = 720 ms",
        "cmp-gantt-procesos": "20 + 20 + 200 + 20 = 260 ms",
        "cmp-gantt-gather": "50 + 20 + 200 + 20 = 290",
        "cmp-gantt-semaforo": "540 + 20 + 200 + 20 = 780 ms",
        "cmp-bloqueo-del-loop": "2040 + 20 + 20 = 2080 ms",
        "cmp-event-loop-ticks": "10 + 300 + 10 = 320 ms",
        "cmp-create-task": "20 + 100 de sleep + 10",
    }
    for nombre, cuenta in cuentas.items():
        assert cuenta in _svg(nombre), f"{nombre}: falta la cuenta {cuenta!r}"


def test_cada_lista_dice_por_que():
    """El rayado solo no explica nada: cada figura nombra quién tiene el turno."""
    porque = {
        "cmp-gantt-hilos": "el hilo 1 tiene el GIL",
        "cmp-gantt-asyncio": "el loop atiende a T1",
        "cmp-gantt-procesos": "CPU 1 y 2 ocupadas",
        "cmp-gantt-gather": "el loop corre T1",
        "cmp-gantt-semaforo": "espera que T1 salga",
        "cmp-bloqueo-del-loop": "el loop calcula T3",
        "cmp-create-task": "(el loop corre main)",
    }
    for nombre, s in porque.items():
        assert s in _svg(nombre), f"{nombre}: falta {s!r}"


def test_ningun_texto_se_sale_del_viewbox():
    """Ancho estimado de cada <text> (system-ui ~0.56 em, mono 0.6 em)."""
    patron = re.compile(r'<text x="([\d.]+)" y="([\d.]+)"[^>]*font-family="([^"]+)" '
                        r'font-size="([\d.]+)" font-weight="(\w+)" text-anchor="(\w+)">([^<]*)<')
    for nombre in _cargar().DIAGRAMAS:
        svg = _svg(nombre)
        ancho, alto = map(float, re.search(r'viewBox="0 0 (\S+) (\S+)"', svg).groups())
        for x, y, familia, tam, peso, anclaje, s in patron.findall(svg):
            s = html.unescape(s)
            k = 0.6 if "mono" in familia else (0.58 if peso == "600" else 0.54)
            w = len(s) * float(tam) * k
            x0 = {"start": float(x), "middle": float(x) - w / 2, "end": float(x) - w}[anclaje]
            assert x0 >= 4 and x0 + w <= ancho - 4 and float(y) <= alto - 4, (
                f"{nombre}: {s!r} se sale del viewBox")


def test_la_lista_es_rayada_y_la_espera_contorno():
    """Convencion de A_notacion: exec relleno, wait contorno, ready rayado."""
    for nombre in GANTT + ("cmp-gantt-gather", "cmp-gantt-semaforo", "cmp-bloqueo-del-loop",
                           "cmp-create-task"):
        svg = _svg(nombre)
        assert 'id="rayado"' in svg and 'fill="url(#rayado)"' in svg, nombre
        assert 'stroke-dasharray="6 4"' in svg, f"{nombre}: la espera va en contorno"


def test_las_figuras_retiradas_no_vuelven():
    """La 2x2 concurrente x paralelo tenia una celda vacia por teorema."""
    modulo = _cargar()
    for nombre in ("cmp-matriz-2x2", "cmp-event-loop"):
        assert nombre not in modulo.DIAGRAMAS, nombre
        assert not (ASSETS / f"{nombre}.svg").exists(), nombre


def test_los_totales_de_las_figuras_nuevas():
    esperados = {"cmp-gantt-gather": 300, "cmp-gantt-semaforo": 780}
    for nombre, total in esperados.items():
        assert f"total {total} ms" in _svg(nombre), nombre


def test_el_semaforo_nunca_deja_entrar_a_mas_de_k():
    """La simulacion: nunca mas de k tareas entre su primer exec y su ultimo."""
    modulo = _cargar()
    filas, _, total = modulo._simula_semaforo()
    assert len(filas) == modulo.SEM_N == 8 and modulo.SEM_K == 3
    dentro = []
    for _, tramos in filas:
        ejecuta = [t for t in tramos if t[0] == "ejecuta"]
        dentro.append((ejecuta[0][1], ejecuta[-1][2]))
        # La vida se parte sin huecos: cada tramo empieza donde acabo el anterior.
        for a, b in zip(tramos, tramos[1:]):
            assert a[2] == b[1], tramos
    for t in range(0, total, 5):
        assert sum(ini <= t < fin for ini, fin in dentro) <= 3, t
    svg = _svg("cmp-gantt-semaforo")
    for pedazo in ("espera permiso", "espera la red", "Semaphore(3)", "⌈8/3⌉", "720 ms"):
        assert pedazo in svg, pedazo
    assert "#ffc857" in svg.lower() and "#6fd8e8" in svg.lower()


def test_la_traza_del_event_loop():
    svg = _svg("cmp-event-loop-ticks")
    for pedazo in ("ejecutando", "cola de listas", "esperando", "select", "hilo del loop",
                   "tick 0", "tick 5", "dA = 300, dB = 100, dC = 200 ms",
                   "[rA, rB, rC]", ">310<", ">120<", ">230<", "320 ms"):
        assert pedazo in svg, pedazo


def test_create_task_contrasta_inerte_y_agendada():
    svg = _svg("cmp-create-task")
    for pedazo in ("c = f()", "asyncio.create_task(f())", "inerte", "never awaited",
                   "aunque nadie haga await t"):
        assert pedazo in svg, pedazo


def test_estados_e_intervalos():
    svg = _svg("cmp-estados-tarea")
    for estado in ("nueva", "lista", "ejecutando", "esperando", "terminada",
                   "ready", "exec", "wait"):
        assert estado in svg, estado
    svg = _svg("cmp-intervalos")
    for pedazo in ("[0, 240)", "[240, 480)", "t = 240", "secuencial"):
        assert pedazo in svg, pedazo


def test_conjuntos_y_matriz_asincrono():
    svg = _svg("cmp-conjuntos")
    for pedazo in ("secuencial", "concurrente", "paralelo", "Paralelo ⇒ concurrente"):
        assert pedazo in svg, pedazo
    svg = _svg("cmp-matriz-asincrono")
    for pedazo in ("bloqueante", "asíncrono", "secuencial", "hilos", "await en serie",
                   "gather", "720 ms", "280 ms"):
        assert pedazo in svg, pedazo


def test_servidor_de_la_clase_y_flujo_del_semaforo():
    svg = _svg("cmp-arq-servidor-clase")
    for pedazo in ("ThreadingHTTPServer", "1024", "un hilo por conexión", "Lock()", "accept()"):
        assert pedazo in svg, pedazo
    svg = _svg("cmp-flujo-semaforo")
    for pedazo in ("contador", "cola de espera", "k = 3", "async with sem"):
        assert pedazo in svg, pedazo


def test_amdahl_dibuja_las_tres_fracciones_seriales():
    svg = _svg("cmp-amdahl")
    for s in ("f = 0.1", "f = 0.25", "f = 0.5", ">16<", "S(N)"):
        assert s in svg, s


def test_el_arbol_termina_en_las_cinco_estrategias():
    svg = _svg("cmp-arbol-decision")
    for hoja in ("asyncio", "hilos", "vectoriza", "procesos", "secuencial", "espera"):
        assert hoja in svg, hoja


def test_el_generador_rechaza_un_nombre_desconocido():
    r = subprocess.run([sys.executable, str(GENERADOR), "cmp-no-existe"],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "desconocido" in r.stderr


def test_cada_svg_esta_referenciado_por_alguna_pagina():
    paginas = "".join(
        p.read_text(encoding="utf-8")
        for p in sorted(UNIDAD.rglob("*.md")) if p.name != "CREDITOS.md"
    )
    for nombre in _cargar().DIAGRAMAS:
        assert f"{nombre}.svg" in paginas, f"{nombre}.svg no aparece en ninguna pagina"
