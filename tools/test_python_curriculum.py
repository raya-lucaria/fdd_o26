"""Guarda de forma de la seccion 9.1 Ambientes (unidad 9, Python).

Las paginas se escriben contra esta guarda: lectores con ADHD, sin analogias,
labs con Haz / Deberias ver, y los labs dentro de la carpeta del alumno
(regla del curso: todo se trabaja en estudiantes/<login>/, nunca fuera del repo).
"""
import re
from pathlib import Path

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
UNIDAD = RAIZ / "course/9_python"
SECCION = UNIDAD / "1_ambientes"

ORDEN = [  # (archivo, id) en orden de lectura
    ("1_el_problema.md", "el-problema-de-los-ambientes"),
    ("2_las_piezas.md", "las-piezas-de-un-ambiente"),
    ("3_un_ambiente_por_dentro.md", "un-ambiente-por-dentro"),
    ("4_los_archivos.md", "los-archivos-del-ambiente"),
    ("5_las_herramientas.md", "las-herramientas-de-ambientes"),
    ("6_ambiente_conda_docker.md", "ambiente-conda-docker"),
    ("7_lab_uv.md", "lab-uv"),
    ("8_venv_y_pip.md", "lab-venv-y-pip"),
    ("9_vs_code.md", "ambientes-en-vs-code"),
    ("10_las_trampas.md", "trampas-de-ambientes"),
]
ANEXOS = [("11_A_cheatsheet.md", "cheatsheet-ambientes"),
          ("12_B_entregas.md", "entregas-ambientes")]
LABS = {"un-ambiente-por-dentro", "lab-uv", "lab-venv-y-pip"}
# Los labs explican cada comando (pedido del profesor): por eso su tope es mayor.
TOPE = {"las-herramientas-de-ambientes": 260, "lab-uv": 360,
        "un-ambiente-por-dentro": 230, "lab-venv-y-pip": 230,
        "entregas-ambientes": 260, "cheatsheet-ambientes": 320}
ANALOGIAS = ("imagina", "es como", "como si", "analogía", "piensa en",
             "receta", "despensa")

_FENCE = re.compile(r"^\s{0,3}(```+|~~~+)")


def _existentes(pares):
    return [(SECCION / a, i) for a, i in pares if (SECCION / a).is_file()]


LECCIONES = _existentes(ORDEN)
TODAS = LECCIONES + _existentes(ANEXOS)
IDS = [i for _, i in TODAS]
LABS_EXISTENTES = [(r, i) for r, i in LECCIONES if i in LABS]


def _front(p):
    texto = p.read_text(encoding="utf-8")
    return yaml.safe_load(texto.split("---", 2)[1]), texto.split("---", 2)[2]


def _prosa(cuerpo):
    """El cuerpo sin bloques de codigo ni code spans."""
    fuera, dentro = [], False
    for l in cuerpo.splitlines():
        if _FENCE.match(l):
            dentro = not dentro
            continue
        if not dentro:
            fuera.append(re.sub(r"`[^`\n]*`", "", l))
    return "\n".join(fuera)


def _bloques(cuerpo, lenguaje=("bash", "powershell", "text")):
    return re.findall(r"^```(?:%s)\n(.*?)^```" % "|".join(lenguaje),
                      cuerpo, flags=re.M | re.S)


def test_las_paginas_de_clase_existen():
    for a in ("1_el_problema.md", "3_un_ambiente_por_dentro.md",
              "7_lab_uv.md", "9_vs_code.md", "0_index.md"):
        assert (SECCION / a).is_file(), f"falta {a}"
    assert (UNIDAD / "0_index.md").is_file()


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_el_id_es_el_del_plan(ruta, ident):
    assert _front(ruta)[0]["id"] == ident


@pytest.mark.parametrize("ruta,ident", LECCIONES, ids=[i for _, i in LECCIONES])
def test_forma_de_leccion(ruta, ident):
    _, cuerpo = _front(ruta)
    n = int(ruta.name.split("_")[0])
    lineas = [l for l in cuerpo.splitlines() if l.strip()]
    assert f"**Página {n} de 10 · Ambientes**" in cuerpo
    assert any(l.startswith("Meta: ") for l in lineas)
    en_corto = re.split(r"\n#{2,3} ", cuerpo.split("## En corto", 1)[1], maxsplit=1)[0]
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
    if i + 1 < len(ORDEN) and not (SECCION / ORDEN[i + 1][0]).is_file():
        pytest.xfail("la siguiente pagina aun no existe")
    siguiente = ORDEN[i + 1][1] if i + 1 < len(ORDEN) else "cheatsheet-ambientes"
    assert f"Sigue con [[{siguiente}" in ruta.read_text(encoding="utf-8")


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_tope_de_lineas(ruta, ident):
    n = len(ruta.read_text(encoding="utf-8").splitlines())
    assert n <= TOPE.get(ident, 160), f"{ident}: {n} líneas"


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


@pytest.mark.parametrize("ruta,ident", LABS_EXISTENTES,
                         ids=[i for _, i in LABS_EXISTENTES])
def test_los_labs_alternan_haz_y_deberias_ver(ruta, ident):
    cuerpo = _front(ruta)[1]
    assert cuerpo.count("**Haz:**") >= 3
    assert cuerpo.count("**Deberías ver:**") >= cuerpo.count("**Haz:**") - 1


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_los_labs_se_trabajan_en_la_carpeta_del_alumno(ruta, ident):
    cuerpo = _front(ruta)[1]
    assert not re.search(r"~/lab-|lab-ambientes|fuera del repo", cuerpo), (
        f"{ident}: los labs viven en estudiantes/<login>/, nunca fuera del repo")
    if ident in LABS:
        assert "estudiantes/$GHUSER/09_python/ambientes" in cuerpo, (
            f"{ident}: el lab no dice que se trabaja en tu carpeta de estudiante")


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_solo_linux_wsl2_y_macos(ruta, ident):
    """El curso se trabaja en Linux, WSL2 o macOS: nada de PowerShell."""
    cuerpo = _front(ruta)[1]
    for prohibido in ("powershell", "PowerShell", "\\Scripts", "Remove-Item", "```powershell"):
        assert prohibido not in cuerpo, f"{ident}: trae {prohibido!r}"


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_la_ruta_del_fork_es_un_marcador(ruta, ident):
    """Cada quien clono su fork en otro lado: la ruta va como {tu_fork_de_la_clase}."""
    cuerpo = _front(ruta)[1]
    assert "~/fdd/fdd_o26" not in cuerpo and "/home/ana/fdd" not in cuerpo, (
        f"{ident}: ruta del fork escrita como si fuera la de todos")


@pytest.mark.parametrize("ruta,ident", LABS_EXISTENTES,
                         ids=[i for _, i in LABS_EXISTENTES])
def test_los_labs_explican_cada_comando(ruta, ident):
    """No es copiar y pegar: cada bloque de Haz lleva su Que hace cada pieza."""
    cuerpo = _front(ruta)[1]
    assert cuerpo.count("**Qué hace cada pieza:**") >= cuerpo.count("**Haz:**") - 1, (
        f"{ident}: hay bloques de comandos sin explicar")


def test_el_lab_de_uv_dice_su_version():
    texto = (SECCION / "7_lab_uv.md").read_text(encoding="utf-8")
    assert "uv self update" in texto and "uv --version" in texto
    assert re.search(r"uv \d+\.\d+", texto), "di con qué versión se capturaron las salidas"


@pytest.mark.parametrize("ruta,ident", TODAS, ids=IDS)
def test_ningun_bloque_pide_sudo(ruta, ident):
    for b in _bloques(_front(ruta)[1]):
        assert not re.search(r"^\s*sudo\b", b, re.M), f"{ident}: sudo en un bloque"


def test_ids_numerados_con_prefijo_py():
    for ruta, ident in TODAS:
        for oid in re.findall(r"\{#([a-z0-9-]+)", ruta.read_text(encoding="utf-8")):
            assert oid.startswith("py-"), f"{ident}: {oid} sin prefijo py-"


def test_el_indice_de_la_seccion_enlaza_cada_pagina_existente():
    indice = (SECCION / "0_index.md").read_text(encoding="utf-8")
    for _, ident in TODAS:
        assert f"[[{ident}" in indice, f"el índice no enlaza {ident}"


TABLERO = SECCION / "12_B_entregas.md"


def test_el_tablero_nombra_branch_carpeta_y_fecha_de_cada_entrega():
    t = TABLERO.read_text(encoding="utf-8")
    for b, c in (("tarea-09-datacamp-python", "python/"),
                 ("tarea-09-uv-docker", "09_python/")):
        assert f"`{b}`" in t and f"`{c}" in t
    assert t.count("2026-10-06") >= 2


def test_el_tablero_de_uv_docker_menciona_platform():
    assert "--platform linux/amd64" in TABLERO.read_text(encoding="utf-8")


def test_el_tablero_dice_que_no_se_entrega_y_acabaste_cuando():
    t = TABLERO.read_text(encoding="utf-8")
    assert t.count("**Acabaste cuando**") == 2 and ".venv" in t


def test_el_tablero_no_resuelve_los_huecos_del_dockerfile():
    """El tablero dice qué va en cada hueco, nunca la instrucción."""
    t = TABLERO.read_text(encoding="utf-8")
    assert "uv sync --locked" not in t and "COPY pyproject.toml" not in t


INDICES_9 = [UNIDAD / "0_index.md", SECCION / "0_index.md"]


@pytest.mark.parametrize("ruta", [r for r, _ in TODAS] + INDICES_9,
                         ids=lambda p: f"{p.parent.name}-{p.stem}")
def test_todo_bloque_de_comandos_se_explica(ruta):
    """Pedido del profesor: que se entienda qué se escribe, cómo y por qué.
    Tras cada bloque bash viene su explicación: «Qué hace cada pieza» o las
    viñetas de cada comando."""
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lineas):
        if lineas[i].startswith("```bash"):
            inicio = i
            i += 1
            while not lineas[i].startswith("```"):
                i += 1
            siguientes = [l for l in lineas[i + 1:i + 6] if l.strip()][:2]
            assert any(l.startswith(("**Qué hace cada pieza:**", "- `", "Son las mismas piezas"))
                       for l in siguientes), (
                f"{ruta.name}:{inicio + 1}: bloque de comandos sin explicar")
        i += 1
