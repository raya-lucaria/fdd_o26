"""Guarda de la unidad 11 Cómputo y concurrencia.

Lo que protege:

- el notebook (codigo/11_computo/computo.ipynb) es el que produce
  tools/gen_notebook_computo.py desde tools/notebook_computo/, sin salidas;
- cada `**Haz (celda k.m):**` de las paginas 1–8 trae su bloque python y ese
  bloque esta literal en la celda del notebook que empieza con `# celda k.m`;
  la numeracion de cada pagina es k.1, k.2, ... sin huecos;
- ninguna celda usa `asyncio.run(` (en un notebook truena: ya hay un event
  loop) y todas compilan con `await` de nivel superior;
- lo que viaja a un proceso se importa de trabajo_computo.py (una funcion de
  celda vive en `__main__` y el hijo no la encuentra);
- servidor.py y cable.py son los mismos que los de codigo/10_apis;
- las paginas: sin marcadores `{{`, sin analogias, el codigo sólo en la
  seccion final `## Código`, las etiquetas Otro ángulo / Matemática / Ejemplo
  / Arquitectura en ese orden, la notacion de A_notacion.md, ids de
  definicion unicos y figuras que existen;
- la celda 1.1 corre contra el servidor real.

No ejecuta las celdas de 20 a 500 llamadas ni las de procesos: el profesor
pidio que la suite no devore nucleos. Lo que importa requests se omite en CI
(el job `checks` sólo instala pytest, pillow y pyyaml).
"""
import ast
import importlib.util
import json
import re
import sys
import threading
from collections import Counter
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
UNIDAD = RAIZ / "course/11_computo_y_concurrencia"
PLANTILLA = RAIZ / "codigo/11_computo"
APIS = RAIZ / "codigo/10_apis"
NOTEBOOK = PLANTILLA / "computo.ipynb"
TRABAJO = PLANTILLA / "trabajo_computo.py"
NOTACION = UNIDAD / "A_notacion.md"

def _numero(nombre):
    """Número de página de «10_capas.md» → 10 (no el primer carácter)."""
    return int(nombre.split("_")[0]) if nombre.split("_")[0].isdigit() else None


TODAS = sorted(p.name for p in UNIDAD.glob("*.md"))
# Páginas 1–8: las del notebook antiguo (Haz, código al final, etiquetas viejas).
PAGINAS = [n for n in TODAS if _numero(n) is not None and 1 <= _numero(n) <= 8]
# Páginas 9+: notas sin código; las cubre test_computo_forma.py. Aquí sólo
# ids únicos, sin analogías, sin marcadores sin sustituir y notebook nuevo.
NUEVAS = [n for n in TODAS if (_numero(n) or 0) >= 9]
NOTEBOOK_ARQ = PLANTILLA / "arquitectura.ipynb"

_HAZ = re.compile(r"^\*\*Haz \(celda (\d+)\.(\d+)[^)]*\):\*\*")

# Limites de palabra: «como sinónimos» no es «como si».
ANALOGIAS = re.compile(r"\b(imagina\w*|es como|como si|piensa en|restaurante\w*|"
                       r"cocina\w*|mesero\w*)\b", re.I)

ETIQUETAS = ("Otro ángulo", "Matemática", "Ejemplo", "Arquitectura")
_ETIQUETA = re.compile(r"^\*\*(" + "|".join(ETIQUETAS) + r")(?: \([^)]*\))?\.\*\*")

# Simbolos de la notacion: si una pagina usa uno, A_notacion.md lo define.
SIMBOLOS = {
    "τ": r"\tau", "exec": r"\operatorname{exec}", "wait": r"\operatorname{wait}",
    "ready": r"\operatorname{ready}", "blocked": r"\operatorname{blocked}",
    "ρ": r"\rho", "ExecutingAt": r"\operatorname{ExecutingAt}",
    "dur": r"\operatorname{dur}", "vida": r"\operatorname{vida}",
    "arrival": r"\operatorname{arrival}", "latencia": r"\operatorname{latencia}",
    "S(N)": "S(N)", "E(N)": "E(N)", "Little": r"L=\lambda", "⌈N/k⌉": r"\lceil",
    "T_pool": r"T_{\text{pool}}", "W_conexión": r"W_{\text{conexión}}",
}
# `S` como fraccion serial (Amdahl escribe f): 1-S, (S+..., «fracción serial S».
SERIAL_CON_S = re.compile(r"1\s*-\s*S\b(?!\()|\(\s*S\s*\+|"
                          r"fracci[oó]n serial,?\s*\$?S\b(?!\()")


def _modulo(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _gen():
    return _modulo("gen_notebook_computo", RAIZ / "tools/gen_notebook_computo.py")


def _cuerpo(nombre):
    return (UNIDAD / nombre).read_text(encoding="utf-8").split("---", 2)[2]


def _haz(nombre):
    """[((k, m), bloque o None)] de una pagina: cada Haz y el ```python que le sigue."""
    lineas, haz, i = _cuerpo(nombre).splitlines(), [], 0
    while i < len(lineas):
        m = _HAZ.match(lineas[i])
        if not m:
            i += 1
            continue
        celda, bloque, i = (int(m.group(1)), int(m.group(2))), None, i + 1
        while i < len(lineas) and not _HAZ.match(lineas[i]) and not lineas[i].startswith("## "):
            if lineas[i].startswith("```python"):
                j = i + 1
                while j < len(lineas) and not lineas[j].startswith("```"):
                    j += 1
                bloque, i = "\n".join(lineas[i + 1:j]), j + 1
                break
            i += 1
        haz.append((celda, bloque))
    return haz


def _celdas_codigo():
    """[fuente] de las celdas de codigo del notebook en disco, en orden."""
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    return ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]


def _nombre(fuente):
    primera = fuente.split("\n", 1)[0].strip()
    return primera if primera.startswith("# celda ") else "celda sin rótulo"


# ── el notebook ───────────────────────────────────────────────────────────

def test_el_notebook_es_el_que_produce_su_generador():
    assert NOTEBOOK.read_text(encoding="utf-8") == _gen().notebook(), (
        "computo.ipynb no coincide con tools/gen_notebook_computo.py: no lo edites "
        "a mano, cambia tools/notebook_computo/ y vuelve a correr el generador")


def test_el_generador_es_determinista():
    gen = _gen()
    assert gen.notebook() == gen.notebook()


def test_el_parser_percent():
    texto = ('"""docstring que no entra"""\n# %% [markdown]\n# # Título\n#\n# texto\n\n'
             "# %% celda con rótulo\n# celda 1.1\nx = 1\n\n\n# %%\n\n# %% [md]\n# otro\n")
    assert _gen().celdas_de(texto) == [
        ("markdown", "# Título\n\ntexto"), ("code", "# celda 1.1\nx = 1"),
        ("markdown", "otro")]


def test_el_notebook_no_trae_salidas():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert nb["metadata"]["kernelspec"]["name"] == "python3"
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            assert c["outputs"] == [] and c["execution_count"] is None


@pytest.mark.parametrize("nombre", PAGINAS)
def test_numeracion_de_haz_consecutiva_y_de_su_pagina(nombre):
    pagina = _numero(nombre)
    numeros = [c for c, _ in _haz(nombre)]
    assert numeros == [(pagina, k) for k in range(1, len(numeros) + 1)], (
        f"{nombre}: celdas {[f'{a}.{b}' for a, b in numeros]}; deben ser "
        f"{pagina}.1, {pagina}.2, … sin huecos")


@pytest.mark.parametrize("nombre", PAGINAS)
def test_cada_haz_esta_literal_en_el_notebook(nombre):
    celdas = _celdas_codigo()
    for (k, m), bloque in _haz(nombre):
        rotulo = f"# celda {k}.{m}"
        assert bloque is not None, f"{nombre}: Haz {k}.{m} sin bloque ```python"
        # La página puede traer el rótulo o no; el notebook lo trae siempre.
        if bloque.split("\n", 1)[0].strip() == rotulo:
            bloque = bloque.split("\n", 1)[1] if "\n" in bloque else ""
        con_rotulo = [c for c in celdas if c.split("\n", 1)[0].strip() == rotulo]
        assert len(con_rotulo) == 1, (
            f"celda {k}.{m}: {len(con_rotulo)} celdas del notebook empiezan con «{rotulo}»; "
            "debe haber exactamente una")
        assert bloque.strip() in con_rotulo[0], (
            f"celda {k}.{m}: el bloque de {nombre} no está literal en la celda del notebook")


def test_ninguna_celda_usa_asyncio_run():
    paginas = [b for n in PAGINAS for _, b in _haz(n) if b]
    for codigo in _celdas_codigo() + paginas:
        assert "asyncio.run(" not in codigo, (
            f"{_nombre(codigo)}: asyncio.run truena dentro del notebook; usa await")


def test_las_celdas_compilan_con_await_de_nivel_superior():
    for codigo in _celdas_codigo():
        compile(codigo, f"<{_nombre(codigo)}>", "exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)


# ── lo que viaja a un proceso viene de trabajo_computo.py ─────────────────

def _es_pool_de_procesos(nodo):
    return (isinstance(nodo, ast.Call)
            and ast.unparse(nodo.func).split(".")[-1] == "ProcessPoolExecutor")


def _pools_de_procesos(arbol):
    """Nombres ligados a un ProcessPoolExecutor (con `with ... as p` o `p = ...`)."""
    nombres = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.withitem) and _es_pool_de_procesos(nodo.context_expr) \
                and isinstance(nodo.optional_vars, ast.Name):
            nombres.add(nodo.optional_vars.id)
        elif isinstance(nodo, ast.Assign) and _es_pool_de_procesos(nodo.value):
            nombres |= {t.id for t in nodo.targets if isinstance(t, ast.Name)}
    return nombres


def _enviadas_a_procesos(arbol, pools):
    """Lo que la celda pasa a pool.map / pool.submit / run_in_executor(pool, ...)."""
    enviadas = []
    for nodo in ast.walk(arbol):
        if not (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute)):
            continue
        dueño = nodo.func.value
        if nodo.func.attr in ("map", "submit") and nodo.args and (
                (isinstance(dueño, ast.Name) and dueño.id in pools)
                or _es_pool_de_procesos(dueño)):
            enviadas.append(nodo.args[0])
        elif nodo.func.attr == "run_in_executor" and len(nodo.args) > 1 and (
                (isinstance(nodo.args[0], ast.Name) and nodo.args[0].id in pools)
                or _es_pool_de_procesos(nodo.args[0])):
            enviadas.append(nodo.args[1])
    return enviadas


def test_lo_que_va_a_un_proceso_se_importa_de_trabajo_computo():
    trabajo = _modulo("trabajo_computo", TRABAJO)
    # El notebook corre en orden: lo importado en una celda sirve en las siguientes.
    pools, importadas, revisadas = set(), set(), 0
    for codigo in _celdas_codigo():
        celda = _nombre(codigo)
        arbol = compile(codigo, celda, "exec",
                        flags=ast.PyCF_ONLY_AST | ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
        pools |= _pools_de_procesos(arbol)
        importadas |= {a.asname or a.name for n in ast.walk(arbol)
                      if isinstance(n, ast.ImportFrom) and n.module == "trabajo_computo"
                      for a in n.names}
        definidas = {n.name for n in ast.walk(arbol)
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        # La celda del PicklingError manda una lambda a propósito (junto con
        # partial y una función de módulo) para mostrar cuál viaja: queda exenta.
        if "PicklingError" in codigo:
            continue
        for arg in _enviadas_a_procesos(arbol, pools):
            if isinstance(arg, ast.Lambda) and "pickl" in codigo.lower():
                continue                    # la lambda que muestra que no viaja
            if (isinstance(arg, ast.Attribute) and isinstance(arg.value, ast.Name)
                    and arg.value.id == "trabajo_computo"):
                nombre = arg.attr
            else:
                assert isinstance(arg, ast.Name), (
                    f"{celda}: a un proceso sólo viaja una función con nombre de "
                    f"trabajo_computo.py, no {ast.unparse(arg)}")
                assert arg.id not in definidas, (
                    f"{celda}: {arg.id} se define en la celda; un proceso hijo no la "
                    "encuentra. Va en trabajo_computo.py")
                assert arg.id in importadas, (
                    f"{celda}: {arg.id} debe importarse de trabajo_computo")
                nombre = arg.id
            assert callable(getattr(trabajo, nombre, None)), (
                f"trabajo_computo.py no define {nombre}")
            revisadas += 1
    assert revisadas >= 2, "ninguna celda manda calcula a un proceso: ¿cambió el parser?"


def test_trabajo_computo_solo_usa_la_libreria_estandar():
    arbol = ast.parse(TRABAJO.read_text(encoding="utf-8"))
    modulos = {a.name.split(".")[0] for n in ast.walk(arbol) if isinstance(n, ast.Import)
               for a in n.names}
    modulos |= {n.module.split(".")[0] for n in ast.walk(arbol)
                if isinstance(n, ast.ImportFrom) and n.module}
    assert modulos <= set(sys.stdlib_module_names), modulos - set(sys.stdlib_module_names)
    assert callable(_modulo("trabajo_computo", TRABAJO).calcula)


# ── la plantilla del alumno ───────────────────────────────────────────────

@pytest.mark.parametrize("archivo", ["servidor.py", "cable.py"])
def test_servidor_y_cable_son_los_de_10_apis(archivo):
    assert (PLANTILLA / archivo).read_bytes() == (APIS / archivo).read_bytes(), (
        f"codigo/11_computo/{archivo} y codigo/10_apis/{archivo} deben ser idénticos")


def test_el_proyecto_pide_sus_dependencias():
    texto = (PLANTILLA / "pyproject.toml").read_text(encoding="utf-8")
    try:
        import tomllib                      # 3.11+
        deps = tomllib.loads(texto)["project"]["dependencies"]
    except ModuleNotFoundError:             # 3.10: basta la lista entre corchetes
        lista = re.search(r"^dependencies\s*=\s*\[(.*?)\]", texto, re.M | re.S).group(1)
        deps = re.findall(r'"([^"]+)"', lista)
    for paquete in ("requests", "httpx", "numpy", "matplotlib"):
        assert any(re.match(rf"{paquete}\b", d) for d in deps), f"falta {paquete}"
    assert (PLANTILLA / "uv.lock").is_file()


# ── las paginas ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("nombre", TODAS)
def test_sin_marcadores_de_plantilla(nombre):
    cuerpo = _cuerpo(nombre)
    if nombre in NUEVAS:                    # {{m:clave}} lo vigila test_computo_forma
        cuerpo = re.sub(r"\{\{m:[\w-]+\}\}", "", cuerpo)
    assert "{{" not in cuerpo, f"{nombre}: quedó un marcador «{{{{»"


@pytest.mark.parametrize("nombre", TODAS)
def test_sin_analogias(nombre):
    hallado = ANALOGIAS.search(_cuerpo(nombre))
    assert not hallado, f"{nombre}: «{hallado.group(0)}»"


def test_la_regex_de_analogias_no_dispara_con_como_sinonimos():
    assert not ANALOGIAS.search("se usan como sinónimos")
    assert ANALOGIAS.search("es como si fuera") and ANALOGIAS.search("Imagina un")


@pytest.mark.parametrize("nombre", PAGINAS)
def test_codigo_solo_al_final(nombre):
    lineas = _cuerpo(nombre).splitlines()
    codigo = [i for i, l in enumerate(lineas) if l.strip() == "## Código"]
    python = [i for i, l in enumerate(lineas) if l.startswith("```python")]
    if not python:
        return
    assert codigo, f"{nombre}: tiene bloques python y no tiene sección «## Código»"
    antes = [i + 1 for i in python if i < codigo[0]]
    assert not antes, (f"{nombre}: bloque ```python antes de «## Código» "
                       f"(renglones {antes} del cuerpo)")


@pytest.mark.parametrize("nombre", PAGINAS)
def test_etiquetas_en_orden(nombre):
    seccion, ultima = "(inicio)", -1
    for linea in _cuerpo(nombre).splitlines():
        if linea.startswith("## "):
            seccion, ultima = linea, -1
            continue
        m = _ETIQUETA.match(linea)
        if not m:
            continue
        orden = ETIQUETAS.index(m.group(1))
        assert orden >= ultima, (
            f"{nombre}, «{seccion}»: **{m.group(1)}.** va después de "
            f"**{ETIQUETAS[ultima]}.**; el orden es {' / '.join(ETIQUETAS)}")
        ultima = orden


def test_la_regex_de_etiquetas():
    assert _ETIQUETA.match("**Ejemplo (medición real).** Las 20")
    assert _ETIQUETA.match("**Otro ángulo.**") and not _ETIQUETA.match("**Haz (celda 1.1):**")


def test_notacion_define_los_simbolos_que_usan_las_paginas():
    assert NOTACION.is_file(), "falta A_notacion.md"
    notacion = _cuerpo(NOTACION.name)
    paginas = "\n".join(_cuerpo(n) for n in PAGINAS)
    faltan = [s for s, lit in SIMBOLOS.items() if lit in paginas and lit not in notacion]
    assert not faltan, f"las páginas usan símbolos que A_notacion.md no define: {faltan}"


@pytest.mark.parametrize("nombre", PAGINAS + ["A_notacion.md"])
def test_notacion_sin_S_serial_ni_D_pool(nombre):
    cuerpo = _cuerpo(nombre)
    hallado = SERIAL_CON_S.search(cuerpo)
    assert not hallado, (f"{nombre}: «{hallado.group(0)}»: la fracción serial se "
                         "escribe f; S es speedup")
    assert "D_pool" not in cuerpo, f"{nombre}: «D_pool» no es notación de la unidad"


def test_la_regex_de_S_serial():
    assert SERIAL_CON_S.search(r"S(N)=1/(S+(1-S)/N)")
    assert SERIAL_CON_S.search("la fracción serial $S$")
    assert not SERIAL_CON_S.search(r"$S(N)=\frac{1}{f+(1-f)/N}$ y $E(N)=S(N)/N$")


def test_ids_de_definicion_unicos():
    ids = [i for n in TODAS for i in re.findall(r"\{#(cmp-def-[\w-]+)", _cuerpo(n))]
    repetidos = [i for i, c in Counter(ids).items() if c > 1]
    assert not repetidos, f"ids de definición repetidos: {repetidos}"


@pytest.mark.parametrize("nombre", TODAS)
def test_figuras_referenciadas_existen(nombre):
    figuras = re.findall(r"_assets/(cmp-[\w-]+\.svg)", _cuerpo(nombre))
    faltan = [f for f in figuras if not (UNIDAD / "_assets" / f).is_file()]
    assert not faltan, f"{nombre}: figuras que no existen en _assets/: {faltan}"


@pytest.mark.parametrize("nombre", NUEVAS)
def test_paginas_nuevas_sin_bloques_de_codigo(nombre):
    assert "```" not in _cuerpo(nombre), f"{nombre}: las páginas 9+ no llevan código"


def test_ids_de_pagina_y_de_objeto_unicos_en_la_unidad():
    ids = []
    for n in TODAS:
        texto = (UNIDAD / n).read_text(encoding="utf-8")
        ids += re.findall(r"^id:\s*(\S+)", texto.split("---", 2)[1], re.M)
        ids += re.findall(r"\{#([\w-]+)", texto)
    repetidos = [i for i, c in Counter(ids).items() if c > 1]
    assert not repetidos, f"ids repetidos en la unidad: {repetidos}"


@pytest.mark.parametrize("nombre", TODAS)
def test_wikilinks_de_la_unidad_resuelven(nombre):
    conocidos = ids_del_repo()
    sueltos = [i for i in re.findall(r"\[\[([^\]|#]+)", _cuerpo(nombre))
               if i.strip() not in conocidos]
    assert not sueltos, f"{nombre}: [[{sueltos[0]}]] no es el id de ninguna página"


def ids_del_repo():
    ids = set()
    for ruta in (RAIZ / "course").rglob("*"):
        if ruta.suffix == ".md":
            texto = ruta.read_text(encoding="utf-8")
            ids |= set(re.findall(r"^id:\s*(\S+)", texto.split("---", 2)[1]
                                  if texto.startswith("---") else "", re.M))
            ids |= set(re.findall(r"\{#([\w-]+)", texto))
        elif ruta.suffix in (".yaml", ".yml"):
            ids |= set(re.findall(r"^\s*(?:-\s*)?id:\s*[\"']?([\w.-]+)",
                                  ruta.read_text(encoding="utf-8"), re.M))
    return ids


# ── el notebook nuevo (arquitectura.ipynb), si ya existe ──────────────────

hay_arq = pytest.mark.skipif(not NOTEBOOK_ARQ.is_file(),
                             reason="arquitectura.ipynb aún no existe")


@hay_arq
def test_arquitectura_sin_salidas_y_kernel_python3():
    nb = json.loads(NOTEBOOK_ARQ.read_text(encoding="utf-8"))
    assert nb["metadata"]["kernelspec"]["name"] == "python3"
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            assert c["outputs"] == [] and c["execution_count"] is None


@hay_arq
def test_arquitectura_rotulos_unicos_y_en_orden():
    nb = json.loads(NOTEBOOK_ARQ.read_text(encoding="utf-8"))
    rotulos = []
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        m = re.match(r"# celda (\d+)\.(\d+)\s*$", "".join(c["source"]).split("\n", 1)[0])
        assert m, f"celda de código sin rótulo «# celda N.M»: {''.join(c['source'])[:40]!r}"
        rotulos.append((int(m.group(1)), int(m.group(2))))
    assert rotulos, "arquitectura.ipynb no tiene celdas de código"
    assert len(set(rotulos)) == len(rotulos), "rótulos repetidos"
    assert rotulos == sorted(rotulos), f"rótulos fuera de orden: {rotulos}"


@hay_arq
def test_arquitectura_es_lo_que_produce_su_generador():
    gen = RAIZ / "tools/gen_notebook_arquitectura.py"
    if not gen.is_file():
        pytest.skip("aún no existe tools/gen_notebook_arquitectura.py")
    modulo = _modulo("gen_notebook_arquitectura", gen)
    if not hasattr(modulo, "notebook"):
        pytest.skip("el generador no expone notebook()")
    assert NOTEBOOK_ARQ.read_text(encoding="utf-8") == modulo.notebook()


# ── la celda 1.1, contra el servidor real ─────────────────────────────────

@pytest.fixture
def servidor(monkeypatch):
    pytest.importorskip("requests", reason="CI instala sólo pytest, pillow y pyyaml")
    monkeypatch.setenv("FDD_SILENCIO", "1")
    mod = _modulo("servidor_computo", PLANTILLA / "servidor.py")
    assert mod.SILENCIO, "FDD_SILENCIO=1 no apaga la radiografía"
    mod.reiniciar()
    srv = mod.Servidor(("127.0.0.1", 0), mod.Ventas)   # la misma clase que __main__
    assert srv.request_queue_size >= 1024
    hilo = threading.Thread(target=srv.serve_forever, daemon=True)
    hilo.start()
    url = f"http://127.0.0.1:{srv.server_address[1]}"
    cable = _modulo("cable", PLANTILLA / "cable.py")
    cable.URL = url
    monkeypatch.setitem(sys.modules, "cable", cable)
    yield url
    srv.shutdown()
    srv.server_close()


def test_celda_1_1_corre_contra_el_servidor(servidor, capsys):
    """1.1: una llamada con ?lento=0.2 y un bucle de 3 M; ~0.6 s, un núcleo."""
    codigo = dict(_haz("1_donde_pasa_el_tiempo.md"))[(1, 1)]
    exec(compile(codigo, "<celda 1.1>", "exec"), {"__name__": "__celda__"})
    salida = capsys.readouterr().out
    assert "llamada ?lento=0.2" in salida and "bucle puro de Python" in salida
    reloj = float(re.search(r"llamada \?lento=0\.2\s+reloj\s+([\d.]+) s", salida).group(1))
    assert reloj >= 0.2, "la llamada debió esperar los 0.2 s que pidió"
