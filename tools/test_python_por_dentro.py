"""Guarda de la seccion 9.2 Python por dentro (unidad 9).

Codifica el contrato de escritura del spec
docs/superpowers/specs/2026-10-05-unidad-9-2-python-por-dentro-design.md (§ 2)
y lo que la plantilla del alumno promete. Lectores con ADHD: sin analogias,
trio Haz / Que hace / Deberias ver, nada de codigo en celdas de tabla.
"""
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
UNIDAD = RAIZ / "course/9_python"
SECCION = UNIDAD / "2_por_dentro"
PLANTILLA = RAIZ / "codigo/09_python/por_dentro"
NOTEBOOK = PLANTILLA / "por_dentro.ipynb"


def _modulo(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_el_notebook_es_el_que_produce_su_generador():
    gen = _modulo("gen_notebook_por_dentro", RAIZ / "tools/gen_notebook_por_dentro.py")
    assert NOTEBOOK.read_text(encoding="utf-8") == gen.notebook(), (
        "por_dentro.ipynb no coincide con tools/gen_notebook_por_dentro.py: "
        "no lo edites a mano, cambia CELDAS y vuelve a correr el generador")


def test_el_notebook_de_la_plantilla_no_trae_salidas():
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            assert c["outputs"] == [] and c["execution_count"] is None


def test_el_proyecto_pide_ipykernel_y_python_313_o_mas():
    # tomllib es stdlib desde 3.11; local hay 3.10 con tomli. Igual que revisa_ficha.py.
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib
    p = tomllib.loads((PLANTILLA / "pyproject.toml").read_text(encoding="utf-8"))
    assert p["project"]["requires-python"] == ">=3.13"
    assert p["project"]["dependencies"] == []
    assert any(d.startswith("ipykernel") for d in p["dependency-groups"]["dev"])
    assert (PLANTILLA / ".python-version").read_text().strip() == "3.14"
    assert (PLANTILLA / "uv.lock").is_file()


def test_gil_py_lleva_la_guarda_y_usa_process_pool():
    src = (PLANTILLA / "gil.py").read_text(encoding="utf-8")
    assert 'if __name__ == "__main__":' in src
    assert "ProcessPoolExecutor" in src and "multiprocessing.Pool" not in src


def test_gil_py_imprime_sus_cinco_lineas():
    r = subprocess.run([sys.executable, str(PLANTILLA / "gil.py"), "--rapido"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    lineas = r.stdout.splitlines()
    assert lineas[0].startswith("Python ") and "GIL" in lineas[0]
    assert [l[:24].strip() for l in lineas[1:]] == [
        "calcula, uno tras otro", "calcula, 4 hilos",
        "calcula, 4 procesos", "espera, 4 hilos"]


ORDEN = [
    ("1_que_es_python.md", "que-es-python"),
    ("2_nombres_y_objetos.md", "nombres-y-objetos"),
    ("3_el_gil.md", "el-gil"),
    ("4_lo_que_escribe_la_ia.md", "lo-que-escribe-la-ia"),
    ("5_trabajar_con_ia.md", "trabajar-con-ia"),
]
ANEXO = ("6_A_entregas.md", "entregas-por-dentro")
TOPE = {"python-por-dentro": 380, "que-es-python": 330, "nombres-y-objetos": 240,
        "el-gil": 300, "lo-que-escribe-la-ia": 250, "trabajar-con-ia": 260,
        "entregas-por-dentro": 260}
ANALOGIAS = ("imagina", "es como", "como si", "analogía", "piensa en",
             "receta", "despensa")
_FENCE = re.compile(r"^\s{0,3}(```+|~~~+)")


def _paginas(pares):
    return [(SECCION / a, i) for a, i in pares if (SECCION / a).is_file()]


INDICE = [(SECCION / "0_index.md", "python-por-dentro")] if (SECCION / "0_index.md").is_file() else []
LECCIONES = _paginas(ORDEN)
TODAS = INDICE + LECCIONES + _paginas([ANEXO])
IDS = [i for _, i in TODAS]


def _front(p):
    t = p.read_text(encoding="utf-8")
    return yaml.safe_load(t.split("---", 2)[1]), t.split("---", 2)[2]


def _prosa(cuerpo):
    fuera, dentro = [], False
    for l in cuerpo.splitlines():
        if _FENCE.match(l):
            dentro = not dentro
            continue
        if not dentro:
            fuera.append(re.sub(r"`[^`\n]*`", "", l))
    return "\n".join(fuera)


def _bloques(cuerpo, lenguaje):
    """(contenido, texto que sigue al bloque hasta el siguiente fence)."""
    partes = re.split(r"^```(\w*)\n(.*?)^```\n", cuerpo, flags=re.M | re.S)
    salida = []
    for k in range(1, len(partes) - 2, 3):
        if partes[k] == lenguaje:
            salida.append((partes[k + 1], partes[k + 2]))
    return salida


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_el_id_es_el_del_plan(ruta, ident):
    assert _front(ruta)[0]["id"] == ident


@pytest.mark.parametrize("ruta,ident", LECCIONES, ids=[i for _, i in LECCIONES])
def test_forma_de_leccion(ruta, ident):
    _, cuerpo = _front(ruta)
    n = int(ruta.name.split("_")[0])
    lineas = [l for l in cuerpo.splitlines() if l.strip()]
    assert f"**Página {n} de 5 · Python por dentro**" in cuerpo
    assert any(l.startswith("Meta: ") for l in lineas)
    if n <= 4:
        assert re.search(r"^\*\*En `revisa_esto\.py`:\*\* esto explica (el síntoma|los síntomas) \d",
                         cuerpo, flags=re.M), f"{ident}: falta la línea del síntoma"
    en_corto = re.split(r"\n#{2,3} |\n::: ", cuerpo.split("## En corto", 1)[1], maxsplit=1)[0]
    vinetas = [l for l in en_corto.splitlines() if l.startswith("- ")]
    assert 1 <= len(vinetas) <= 3, f"{ident}: En corto con {len(vinetas)} viñetas"
    problemas = re.findall(r"^::: problem \{#(py-[a-z0-9-]+)", cuerpo, flags=re.M)
    assert len(problemas) == 1, f"{ident}: {len(problemas)} problemas"
    for k in ("hint", "answer"):
        assert f'::: {k} {{of="{problemas[0]}"}}' in cuerpo
    assert lineas[-2] == "> [!NOTE]"
    assert lineas[-1].startswith("> **Si sólo recuerdas una cosa:**")


@pytest.mark.parametrize("i", range(len(ORDEN)))
def test_el_puente_apunta_a_la_siguiente(i):
    ruta = SECCION / ORDEN[i][0]
    if not ruta.is_file():
        pytest.skip("pagina aun no escrita")
    siguiente = ORDEN[i + 1][1] if i + 1 < len(ORDEN) else ANEXO[1]
    assert f"Sigue con [[{siguiente}" in ruta.read_text(encoding="utf-8")


LECCIONES_1_A_4 = [(r, i) for r, i in LECCIONES if int(r.name.split("_")[0]) <= 4]


@pytest.mark.parametrize("ruta,ident", LECCIONES_1_A_4, ids=[i for _, i in LECCIONES_1_A_4])
def test_los_bloques_de_ia_tienen_dos_bullets_o_menos(ruta, ident):
    cuerpo = _front(ruta)[1]
    for rotulo in ("**Al revisar código de IA, busca:**", "**Al pedírselo a la IA, dile:**"):
        assert rotulo in cuerpo, f"{ident}: falta {rotulo}"
        despues = cuerpo.split(rotulo, 1)[1].lstrip("\n")
        bullets = []
        for l in despues.splitlines():
            if l.startswith("- "):
                bullets.append(l)
            elif l.strip() and not l.startswith("  "):
                break
        assert 1 <= len(bullets) <= 2, f"{ident}: {rotulo} con {len(bullets)} bullets"


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_tope_de_lineas(ruta, ident):
    n = len(ruta.read_text(encoding="utf-8").splitlines())
    assert n <= TOPE[ident], f"{ident}: {n} líneas (tope {TOPE[ident]})"


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_sin_analogias(ruta, ident):
    prosa = _prosa(_front(ruta)[1]).lower()
    for a in ANALOGIAS:
        assert a not in prosa, f"{ident}: «{a}» — sin analogías: di qué es y muéstralo"


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_sin_html_crudo_ni_dos_pesos_en_prosa(ruta, ident):
    prosa = _prosa(_front(ruta)[1])
    assert not re.search(r"<(?:div|br|iframe|details|span|img)\b", prosa, re.I)
    for l in prosa.splitlines():
        assert l.count("$") < 2, f"{ident}: dos $ en prosa: {l!r}"


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_todo_bloque_python_se_explica_y_muestra_salida(ruta, ident):
    for codigo, despues in _bloques(_front(ruta)[1], "python"):
        assert "**Qué hace cada línea:**" in despues, f"{ident}: bloque python sin explicar:\n{codigo}"
        assert "**Deberías ver:**" in despues, f"{ident}: bloque python sin salida:\n{codigo}"


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_todo_bloque_bash_se_explica(ruta, ident):
    for codigo, despues in _bloques(_front(ruta)[1], "bash"):
        assert "**Qué hace cada pieza:**" in despues, f"{ident}: bloque bash sin explicar:\n{codigo}"


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_no_hay_codigo_escondido_en_tablas(ruta, ident):
    for l in _front(ruta)[1].splitlines():
        if l.startswith("|"):
            for celda in l.split("|"):
                asignaciones = re.findall(r"`[^`]*\s=\s[^`]*`", celda)
                assert len(asignaciones) < 2, (
                    f"{ident}: celda de tabla con varias líneas de código; "
                    f"conviértela en un Haz con su bloque: {celda.strip()!r}")


def test_las_celdas_citadas_existen():
    gen = _modulo("gen_notebook_por_dentro", RAIZ / "tools/gen_notebook_por_dentro.py")
    existen = {n for n, _ in gen.CELDAS}
    for ruta, ident in LECCIONES:
        citadas = set(re.findall(r"\*\*Haz \(celda (\d+\.\d+)\):\*\*", ruta.read_text(encoding="utf-8")))
        assert citadas <= existen, f"{ident}: celdas que no están en el notebook: {sorted(citadas - existen)}"


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_rutas_del_alumno(ruta, ident):
    cuerpo = _front(ruta)[1]
    assert "~/fdd" not in cuerpo and "/home/" not in cuerpo and "fuera del repo" not in cuerpo
    assert not re.search(r"^\s*sudo\b", "\n".join(c for c, _ in _bloques(cuerpo, "bash")), re.M)


def test_el_indice_enlaza_cada_pagina_y_el_ritual_usa_la_carpeta_del_alumno():
    if not INDICE:
        pytest.skip("indice aun no escrito")
    cuerpo = _front(INDICE[0][0])[1]
    for _, ident in ORDEN + [ANEXO]:
        assert f"[[{ident}" in cuerpo, f"el índice no enlaza {ident}"
    assert "estudiantes/$GHUSER/09_python/por_dentro" in cuerpo
    assert "{tu_fork_de_la_clase}" in cuerpo
    assert '[ -n "$GHUSER" ]' in cuerpo and "--ff-only" in cuerpo


def test_ids_numerados_con_prefijo_py():
    for ruta, _ in TODAS:
        for ident in re.findall(r"^::: \w+ \{#([\w-]+)", ruta.read_text(encoding="utf-8"), flags=re.M):
            assert ident.startswith("py-"), f"{ruta.name}: {ident} sin prefijo py-"


RITUAL_9_1 = [UNIDAD / "1_ambientes/0_index.md", UNIDAD / "1_ambientes/12_B_entregas.md",
              RAIZ / "codigo/09_python/README.md"]


@pytest.mark.parametrize("ruta", RITUAL_9_1, ids=lambda p: p.name)
def test_el_ritual_de_ambientes_no_copia_por_dentro(ruta):
    t = ruta.read_text(encoding="utf-8")
    assert "cp -r codigo/09_python/. " not in t, (
        f"{ruta.name}: copiar codigo/09_python/ entero mete por_dentro/ en el PR de uv-docker")
    assert not re.search(r"git add estudiantes/\$GHUSER/09_python\s*$", t, re.M), (
        f"{ruta.name}: git add de 09_python entero sube por_dentro/ al PR de uv-docker")


def _uv_run(script):
    return subprocess.run([sys.executable, script], cwd=PLANTILLA,
                          capture_output=True, text=True, timeout=300)


def test_revisa_esto_muestra_los_cinco_sintomas():
    src = (PLANTILLA / "revisa_esto.py").read_text(encoding="utf-8")
    # los cinco errores plantados se fijan por hash: escribirlos aquí sería publicar la clave antes del 2026-10-13
    assert hashlib.sha256((PLANTILLA / "revisa_esto.py").read_bytes()).hexdigest() == "3c0db3b592b9b0deb3716747dec525a6895a9561427472802963ddc64b57c394"
    assert "NO es la salida literal de un modelo" in src
    r = _uv_run("revisa_esto.py")
    assert r.returncode in (0, 1), r.stderr
    assert "NO cuadra" in r.stdout
    assert "con hilos" in r.stdout and "sin hilos" in r.stdout
    assert "Carla Ríos" not in r.stdout


@pytest.mark.skipif(sys.version_info < (3, 12),
                    reason="la respuesta del modelo usa sintaxis 3.12+")
def test_las_respuestas_de_modelo_estan_y_corren():
    assert (PLANTILLA / "resume_ventas.py").is_file()
    r = _uv_run("resume_ventas.py")
    assert r.returncode == 0, r.stderr


def test_la_respuesta_original_no_viene_en_la_plantilla():
    # Se publica al vencer la tarea, 2026-10-13: un diff contra revisa_esto.py
    # daría las cinco líneas plantadas.
    assert not (PLANTILLA / "respuesta_original.py").exists()


def test_ningun_archivo_de_la_plantilla_dispara_el_detector_de_inyeccion():
    rf = _modulo("revisa_ficha", RAIZ / ".github/scripts/revisa_ficha.py")
    for p in PLANTILLA.iterdir():
        if p.is_file() and p.suffix in {".py", ".md", ".csv", ".ipynb", ".toml"}:
            assert not rf.frases_al_revisor(p.read_text(encoding="utf-8")), p.name


def test_trabajo_calcula_y_espera():
    """Las celdas 3.1 a 3.4 importan trabajo.py: calcula cuenta sumas por tiempo."""
    trabajo = _modulo("trabajo", PLANTILLA / "trabajo.py")
    assert trabajo.calcula(0.05) > 0
    assert trabajo.espera(0.01) == 0.01
