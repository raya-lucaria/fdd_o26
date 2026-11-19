"""Guarda de la seccion 9.3 Elegir el stack (unidad 9).

Codifica el § 9 del spec
docs/superpowers/specs/2026-10-08-unidad-9-3-elegir-el-stack-design.md:
paginas cortas, celdas citadas que existen, notebooks limpios y la plantilla
codigo/09_python/stack/ tal como la prometen las paginas.

Corre con el python3 de CI (sin polars, sin uv, sin .venv): lo que necesita
esas herramientas se salta diciendo por que.
"""
import ast
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
UNIDAD = RAIZ / "course/9_python"
SECCION = UNIDAD / "3_stack"
ASSETS = UNIDAD / "_assets"
PLANTILLA = RAIZ / "codigo/09_python/stack"

NOTEBOOKS = {"A": "a_contratos.ipynb", "B": "b_tablas.ipynb", "C": "c_archivos.ipynb"}

# Tope de lineas por pagina: el largo al implementar (2026-10-08) + ~10 %.
# Si una pagina necesita crecer, sube el tope a proposito, no por inercia.
TOPE = {
    "0_index.md": 265,       # 242
    "1_contratos.md": 185,   # 169
    "2_tablas.md": 215,      # 197
    "3_archivos.md": 170,    # 154
    "4_patrones.md": 115,    # 105
    "5_A_entregas.md": 200,  # 163; 2026-10-20 +la práctica paso a paso
    "6_B_chuleta.md": 150,   # 134
}

ESCENARIOS = {"pandas", "polars", "polars-lazy", "duckdb", "polars-1-hilo",
              "lista", "generador", "scan"}
LIMITE_BYTES = 200 * 1024


def _paginas():
    return sorted(SECCION.glob("*.md"))


def _nb(letra):
    return json.loads((PLANTILLA / NOTEBOOKS[letra]).read_text(encoding="utf-8"))


def _src(celda):
    s = celda["source"]
    return "".join(s) if isinstance(s, list) else s


_TITULO = re.compile(r"^##\s+([ABC])\.(\d+)\s+·", re.M)


def _titulos(letra):
    """Numeros de celda X.n, en el orden en que aparecen sus titulos."""
    nums = []
    for c in _nb(letra)["cells"]:
        if c["cell_type"] == "markdown":
            for l, n in _TITULO.findall(_src(c)):
                assert l == letra, f"{NOTEBOOKS[letra]}: titulo {l}.{n} de otro notebook"
                nums.append(int(n))
    return nums


def _celdas_con_titulo(letra):
    """[(n, celda de codigo)]: cada celda de codigo con el X.n que la precede."""
    actual, salida = None, []
    for c in _nb(letra)["cells"]:
        if c["cell_type"] == "markdown":
            m = _TITULO.search(_src(c))
            if m:
                actual = int(m.group(2))
        elif c["cell_type"] == "code":
            salida.append((actual, c))
    return salida


# ---------------------------------------------------------------- paginas

def test_existen_las_siete_paginas():
    faltan = [p for p in TOPE if not (SECCION / p).is_file()]
    assert not faltan, f"faltan paginas de 3_stack: {faltan}"


@pytest.mark.parametrize("pagina", sorted(TOPE))
def test_cada_pagina_respeta_su_tope_de_lineas(pagina):
    ruta = SECCION / pagina
    if not ruta.is_file():
        pytest.skip(f"{pagina} aun no existe (lo reporta test_existen_las_siete_paginas)")
    n = len(ruta.read_text(encoding="utf-8").splitlines())
    assert n <= TOPE[pagina], f"{pagina}: {n} lineas > tope {TOPE[pagina]}"


def test_no_hay_paginas_sin_tope():
    sobran = [p.name for p in _paginas() if p.name not in TOPE]
    assert not sobran, f"paginas nuevas sin tope en TOPE: {sobran}"


_CITA = re.compile(
    r"(?<![\w.])([ABC])\.(\d+)(?:\s*[–-]\s*(?:([ABC])\.)?(\d+))?(?![\w])")


def _citas(texto):
    """{(letra, n)} de toda cita A.n o rango A.n–A.m / A.n–m del texto."""
    out = set()
    for l, a, l2, b in _CITA.findall(texto):
        if l2 and l2 != l:
            out |= {(l, int(a)), (l2, int(b))}
            continue
        fin = int(b) if b else int(a)
        out |= {(l, k) for k in range(int(a), fin + 1)}
    return out


def test_cada_celda_citada_en_las_paginas_existe_en_su_notebook():
    existentes = {l: set(_titulos(l)) for l in NOTEBOOKS}
    malas = []
    for p in _paginas():
        for i, linea in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for l, n in sorted(_citas(linea)):
                if n not in existentes[l]:
                    malas.append(f"{p.name}:{i} cita {l}.{n}, que no existe en {NOTEBOOKS[l]}")
    assert not malas, "\n".join(malas)


_MARCA = re.compile(r"📓\s*NOTEBOOK\s*·\s*([^·*]+?)\s*·\s*celdas?\s+([^*\n]+)")


def test_cada_marca_de_notebook_nombra_un_archivo_y_celdas_reales():
    malas, vistas = [], 0
    for p in _paginas():
        for i, linea in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for archivo, celdas in _MARCA.findall(linea):
                if archivo.startswith("<"):  # la plantilla de la marca en 0_index
                    continue
                vistas += 1
                if not (PLANTILLA / archivo).is_file():
                    malas.append(f"{p.name}:{i} 📓 nombra {archivo}, que no existe")
                    continue
                letra = next((l for l, f in NOTEBOOKS.items() if f == archivo), None)
                citas = _citas(celdas)
                if not citas:
                    malas.append(f"{p.name}:{i} 📓 sin celdas legibles: {celdas!r}")
                for l, n in sorted(citas):
                    if l != letra:
                        malas.append(f"{p.name}:{i} 📓 {archivo} cita {l}.{n} de otro notebook")
                    elif n not in _titulos(l):
                        malas.append(f"{p.name}:{i} 📓 {archivo} cita {l}.{n}, que no existe")
    assert vistas, "ninguna pagina de 3_stack lleva marca 📓 NOTEBOOK"
    assert not malas, "\n".join(malas)


def test_cada_figura_py_stack_la_usa_alguna_pagina_y_tiene_credito():
    svgs = sorted(f.name for f in ASSETS.glob("py-stack-*.svg"))
    assert svgs, "no hay figuras py-stack-*.svg"
    texto = "\n".join(p.read_text(encoding="utf-8") for p in _paginas())
    creditos = (ASSETS / "CREDITOS.md").read_text(encoding="utf-8")
    gen = (RAIZ / "tools/gen_python.py").read_text(encoding="utf-8")
    sin_pagina = [s for s in svgs if f"_assets/{s}" not in texto]
    assert not sin_pagina, f"figuras que ninguna pagina de 3_stack usa: {sin_pagina}"
    for s in svgs:
        assert f"| {s} |" in creditos, f"{s} sin fila en CREDITOS.md"
        assert f'"{s[:-4]}"' in gen, f"{s} no sale de tools/gen_python.py"


# ---------------------------------------------------------------- notebooks

def test_solo_existen_los_tres_notebooks():
    nbs = sorted(p.name for p in PLANTILLA.glob("*.ipynb"))
    assert nbs == sorted(NOTEBOOKS.values()), f"notebooks en la plantilla: {nbs}"


@pytest.mark.parametrize("letra", sorted(NOTEBOOKS))
def test_celdas_en_orden_sin_huecos(letra):
    nums = _titulos(letra)
    assert nums == list(range(len(nums))), f"{NOTEBOOKS[letra]}: {nums}"


@pytest.mark.parametrize("letra", sorted(NOTEBOOKS))
def test_notebook_sin_salidas(letra):
    for i, c in enumerate(_nb(letra)["cells"]):
        if c["cell_type"] == "code":
            assert c.get("outputs") == [] and c.get("execution_count") is None, (
                f"{NOTEBOOKS[letra]}: celda {i} trae salidas o execution_count")


@pytest.mark.parametrize("letra", sorted(NOTEBOOKS))
def test_ultima_celda_regresa_a_la_pagina_con_restart(letra):
    ultima = _nb(letra)["cells"][-1]
    s = _src(ultima)
    assert ultima["cell_type"] == "markdown" and "Regresa" in s and "Restart" in s, (
        f"{NOTEBOOKS[letra]}: la ultima celda no es la de regreso con Restart")


_N = re.compile(r"^\s*(#\s*)?N\s*=\s*([\d_]+)\b", re.M)


@pytest.mark.parametrize("letra", sorted(NOTEBOOKS))
def test_celda_0_elige_n_con_una_sola_linea_activa(letra):
    cero = [c for n, c in _celdas_con_titulo(letra) if n == 0]
    assert cero, f"{NOTEBOOKS[letra]}: no hay celda de codigo bajo {letra}.0"
    lineas = _N.findall(_src(cero[0]))
    activas = [int(v) for com, v in lineas if not com]
    comentadas = sorted(int(v) for com, v in lineas if com)
    assert activas == [1_000_000], f"{letra}.0: lineas N activas {activas}"
    assert comentadas == [100_000, 10_000_000], f"{letra}.0: N comentadas {comentadas}"


@pytest.mark.parametrize("letra", sorted(NOTEBOOKS))
def test_timeit_siempre_con_una_corrida(letra):
    for n, c in _celdas_con_titulo(letra):
        for l in _src(c).splitlines():
            if "%timeit" in l:
                assert re.search(r"-n\s*1\b", l) and re.search(r"-r\s*1\b", l), (
                    f"{letra}.{n}: %timeit sin -n1 -r1: {l.strip()}")


@pytest.mark.parametrize("letra", sorted(NOTEBOOKS))
def test_mide_py_se_llama_con_sys_executable(letra):
    for n, c in _celdas_con_titulo(letra):
        s = _src(c)
        for l in s.splitlines():
            if "mide.py" in l and l.lstrip().startswith("!"):
                raise AssertionError(f"{letra}.{n}: mide.py desde la shell: {l.strip()}")
        for m in re.finditer(r"""["']mide\.py["']""", s):
            antes = s[max(0, m.start() - 40):m.start()]
            assert re.search(r"sys\.executable\s*,\s*$", antes), (
                f"{letra}.{n}: mide.py sin sys.executable justo antes")


# ---------------------------------------------------------------- plantilla

def test_mide_py_acepta_los_ocho_escenarios():
    arbol = ast.parse((PLANTILLA / "mide.py").read_text(encoding="utf-8"))
    lista = next(ast.literal_eval(n.value) for n in ast.walk(arbol)
                 if isinstance(n, ast.Assign)
                 and any(getattr(t, "id", None) == "ESCENARIOS" for t in n.targets))
    assert set(lista) == ESCENARIOS and len(lista) == 8, lista


def test_mide_py_rechaza_un_escenario_desconocido_y_lista_los_ocho():
    r = subprocess.run([sys.executable, str(PLANTILLA / "mide.py"), "nope", "10"],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode != 0
    for e in ESCENARIOS:
        assert e in r.stderr, f"el mensaje de uso no menciona {e}"


def _carga_datos(destino):
    shutil.copy(PLANTILLA / "datos.py", destino / "datos.py")
    spec = importlib.util.spec_from_file_location(f"datos_{destino.name}", destino / "datos.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_datos_genera_es_determinista_y_lleva_n_en_el_nombre(tmp_path):
    pytest.importorskip("numpy", reason="sin numpy en este python (CI): se salta")
    pytest.importorskip("polars", reason="sin polars en este python (CI): se salta")
    hechos = []
    for nombre in ("uno", "dos"):
        d = tmp_path / nombre
        d.mkdir()
        rutas = _carga_datos(d).genera(1_000)
        assert rutas["csv"].name == "ventas_1000.csv"
        assert rutas["parquet"].name == "ventas_1000.parquet"
        assert rutas["csv"].parent == d / "datos"
        hechos.append(rutas["csv"].read_bytes())
    assert hechos[0] == hechos[1], "genera(n) da CSV distintos en dos corridas"
    assert hechos[0].count(b"\n") == 1_001  # encabezado + n filas


def test_modelos_py_trae_sus_tres_errores_plantados(tmp_path):
    bin_ = PLANTILLA / ".venv/bin"
    if not (bin_ / "mypy").exists() or not (bin_ / "ruff").exists():
        pytest.skip("sin codigo/09_python/stack/.venv (uv sync): no hay mypy ni ruff")
    m = subprocess.run([str(bin_ / "mypy"), "--cache-dir", str(tmp_path / "mypy"),
                        "modelos.py"], cwd=PLANTILLA, capture_output=True, text=True,
                       timeout=180)
    fuente = (PLANTILLA / "modelos.py").read_text(encoding="utf-8").splitlines()
    linea = next(i for i, l in enumerate(fuente, 1) if re.search(r"\btotal\(\[", l))
    assert m.returncode != 0 and re.search(
        rf"modelos\.py:{linea}: error: .*\"str\".*\"float\"", m.stdout), (
        f"mypy no reporta la llamada mala a total (linea {linea}):\n{m.stdout}")
    r = subprocess.run([str(bin_ / "ruff"), "check", "--no-cache", "modelos.py"],
                       cwd=PLANTILLA, capture_output=True, text=True, timeout=60)
    assert "F401" in r.stdout and "E711" in r.stdout, f"ruff:\n{r.stdout}"


def _archivos_de_la_plantilla():
    if not shutil.which("git"):
        pytest.skip("sin git: no se puede saber que archivos se versionan")
    r = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard",
                        "--", str(PLANTILLA.relative_to(RAIZ))], cwd=RAIZ,
                       capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip(f"git ls-files fallo: {r.stderr.strip()}")
    return [RAIZ / l for l in r.stdout.splitlines() if l]


def test_plantilla_sin_archivos_grandes_ni_datos():
    archivos = _archivos_de_la_plantilla()
    assert archivos, "git no ve ningun archivo en la plantilla"
    grandes = [f"{p.relative_to(PLANTILLA)} ({p.stat().st_size // 1024} KB)"
               for p in archivos if p.exists() and p.name != "uv.lock"
               and p.stat().st_size > LIMITE_BYTES]
    assert not grandes, f"archivos > 200 KB en la plantilla: {grandes}"
    datos = [str(p.relative_to(PLANTILLA)) for p in archivos
             if p.relative_to(PLANTILLA).parts[0] == "datos"]
    assert not datos, f"archivos bajo datos/ que git versionaria: {datos}"
    nbs = sorted(p.name for p in archivos if p.suffix == ".ipynb")
    assert nbs == sorted(NOTEBOOKS.values()), f"notebooks versionables: {nbs}"


def test_gitignore_de_la_plantilla_ignora_datos():
    lineas = (PLANTILLA / ".gitignore").read_text(encoding="utf-8").split()
    assert "datos/" in lineas or "datos" in lineas
