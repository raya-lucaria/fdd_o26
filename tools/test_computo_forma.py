"""Guarda de forma de las páginas 9+ de la unidad 11 (notas cortas, sin código).

Plan: docs/superpowers/plans/2026-10-29-clase-11-2-detalle.md, secciones B y E.
Se parametriza sobre las páginas 9_*.md … 1N_*.md que existan; si no hay
ninguna, nada falla.

FALLOS: partes por concepto en orden; definición en cada concepto; al menos
una arquitectura por página; al menos una figura, tabla o lista por página;
frases de relleno prohibidas; bloques de código; párrafos duplicados;
referencias [[id]] que no resuelven; figuras sin alt, sin SVG o sin crédito;
una página enlazada desde el índice que no existe.

AVISOS (UserWarning, no fallo): > 800 palabras de contenido; definición > 25
palabras; frases > 22 palabras; `{{m:clave}}` sin sustituir; «celda N.M»
citada que el notebook aún no trae. Con FORMA_ESTRICTA=1 los dos últimos
pasan a ser fallos.
"""
import json
import os
import re
import warnings
from collections import defaultdict
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
UNIDAD = RAIZ / "course/11_computo_y_concurrencia"
ASSETS = UNIDAD / "_assets"
CREDITOS = ASSETS / "CREDITOS.md"
NB_ARQ = RAIZ / "codigo/11_computo/arquitectura.ipynb"
NB_VIEJO = RAIZ / "codigo/11_computo/computo.ipynb"

ESTRICTO = os.environ.get("FORMA_ESTRICTA") == "1"
MAX_PALABRAS, MAX_DEFINICION, MAX_FRASE = 800, 25, 22

ESPERADAS = {"sistemas-distribuidos", "capas-de-ejecucion",
             "componer-un-servidor", "como-llegan-los-resultados"}
EXENTAS = ("si hay tiempo", "notebook", "prerrequisitos", "recordatorio", "en corto")
PARTES = ("Definición", "Figura", "Cuenta", "Ejemplo", "Arquitectura")
_PARTE = re.compile(r"^\*\*(" + "|".join(PARTES) + r")(?: \([^)]*\))?\.\*\*")
PROHIBIDAS = ("otro ángulo", "como vimos", "vale la pena notar",
              "el mismo gantt como texto")


def _numero(nombre):
    cabeza = nombre.split("_")[0]
    return int(cabeza) if cabeza.isdigit() else None


PAGINAS = sorted(p.name for p in UNIDAD.glob("*_*.md")
                 if (_numero(p.name) or 0) >= 9)
VIEJAS = sorted(p.name for p in UNIDAD.glob("*_*.md")
                if 1 <= (_numero(p.name) or 0) <= 8)


def _frontmatter(nombre):
    return (UNIDAD / nombre).read_text(encoding="utf-8").split("---", 2)[1]


def _cuerpo(nombre):
    return (UNIDAD / nombre).read_text(encoding="utf-8").split("---", 2)[2]


def _sin_codigo(texto):
    """Cuerpo sin bloques ``` (para contar y analizar prosa)."""
    salida, dentro = [], False
    for linea in texto.splitlines():
        if linea.lstrip().startswith("```"):
            dentro = not dentro
            continue
        if not dentro:
            salida.append(linea)
    return "\n".join(salida)


def _contenido(nombre):
    """Líneas de contenido: sin código, sin alt, sin líneas de directiva."""
    texto = re.sub(r"!\[[^\]]*\]\(([^)]*)\)", "", _sin_codigo(_cuerpo(nombre)))
    return [l for l in texto.splitlines() if not l.startswith(":::")]


def _avisa(mensaje):
    warnings.warn(mensaje, UserWarning, stacklevel=2)


def _palabras(texto):
    return re.findall(r"\S+", re.sub(r"[|#*_`>-]", " ", texto))


def _conceptos(nombre):
    """{titulo H2: [líneas]} de los conceptos (no exentos)."""
    secciones, actual = {}, None
    for l in _contenido(nombre):
        if l.startswith("## "):
            titulo = l[3:].strip()
            actual = None if titulo.lower().startswith(EXENTAS) else titulo
            if actual:
                secciones[actual] = []
        elif actual is not None:
            secciones[actual].append(l)
    return secciones


# ── el índice y las páginas esperadas ─────────────────────────────────────

def test_paginas_enlazadas_desde_el_indice_existen():
    indice = (UNIDAD / "0_index.md").read_text(encoding="utf-8")
    existentes = {re.search(r"^id:\s*(\S+)", _frontmatter(n), re.M).group(1)
                  for n in PAGINAS}
    for id_ in ESPERADAS:
        if re.search(rf"\[\[{id_}(\|[^\]]*)?\]\]|raya:{id_}\b", indice):
            assert id_ in existentes, (
                f"0_index.md enlaza a {id_} y no hay página 9+ con ese id")


# ── conteo, forma y relleno ───────────────────────────────────────────────

@pytest.mark.parametrize("nombre", PAGINAS)
def test_palabras_de_contenido(nombre):
    n = len(_palabras("\n".join(_contenido(nombre))))
    if n > MAX_PALABRAS:
        _avisa(f"{nombre}: {n} palabras de contenido (> {MAX_PALABRAS})")


@pytest.mark.parametrize("nombre", PAGINAS)
def test_partes_por_concepto_en_orden(nombre):
    conceptos = _conceptos(nombre)
    for titulo, lineas in conceptos.items():
        vistas = [PARTES.index(m.group(1)) for l in lineas if (m := _PARTE.match(l))]
        assert vistas == sorted(vistas), (
            f"{nombre}, «{titulo}»: partes fuera de orden; el orden es "
            f"{' → '.join(PARTES)}")
        assert PARTES.index("Definición") in vistas, (
            f"{nombre}, «{titulo}»: falta **Definición.**")


@pytest.mark.parametrize("nombre", PAGINAS)
def test_arquitectura_al_menos_una(nombre):
    assert any(_PARTE.match(l) and _PARTE.match(l).group(1) == "Arquitectura"
               for l in _contenido(nombre)), f"{nombre}: falta **Arquitectura.**"


@pytest.mark.parametrize("nombre", PAGINAS)
def test_sin_frases_de_relleno(nombre):
    texto = _sin_codigo(_cuerpo(nombre)).lower()
    hallada = [f for f in PROHIBIDAS if f in texto]
    assert not hallada, f"{nombre}: {hallada}"


@pytest.mark.parametrize("nombre", PAGINAS)
def test_sin_bloques_de_codigo(nombre):
    assert "```" not in _cuerpo(nombre), (
        f"{nombre}: las notas no llevan código; cita «celda N.M»")


@pytest.mark.parametrize("nombre", PAGINAS)
def test_definiciones_y_frases_largas(nombre):
    lineas = _contenido(nombre)
    largas, i = [], 0
    while i < len(lineas):
        m = _PARTE.match(lineas[i])
        if m and m.group(1) == "Definición":
            bloque = [_PARTE.sub("", lineas[i])]
            i += 1
            while i < len(lineas) and not _PARTE.match(lineas[i]) \
                    and not lineas[i].startswith("#"):
                bloque.append(lineas[i])
                i += 1
            n = len(_palabras(" ".join(bloque)))
            if n > MAX_DEFINICION:
                largas.append(n)
        else:
            i += 1
    if largas:
        _avisa(f"{nombre}: definiciones de {largas} palabras (> {MAX_DEFINICION})")
    prosa = [l for l in lineas if l.strip() and not l.lstrip().startswith(("|", "#", "$"))]
    frases = [f for f in re.split(r"(?<=[.!?:;])\s+", re.sub(r"\$[^$]*\$", "X", " ".join(prosa)))
              if len(_palabras(f)) > MAX_FRASE]
    if frases:
        _avisa(f"{nombre}: {len(frases)} frases de más de {MAX_FRASE} palabras")


@pytest.mark.parametrize("nombre", PAGINAS)
def test_una_figura_tabla_o_lista_por_pagina(nombre):
    texto = _sin_codigo(_cuerpo(nombre))
    hay = (re.search(r"^::: figure", texto, re.M) or re.search(r"^\|.*\|\s*$", texto, re.M)
           or re.search(r"^\s*(?:[-*]|\d+\.)\s+\S", texto, re.M))
    assert hay, f"{nombre}: ni una figura, ni una tabla, ni una lista"


@pytest.mark.parametrize("nombre", PAGINAS)
def test_marcadores_de_medicion(nombre):
    pendientes = re.findall(r"\{\{m:[\w-]+\}\}", _cuerpo(nombre))
    if not pendientes:
        return
    msg = f"{nombre}: mediciones sin sustituir {sorted(set(pendientes))}"
    assert not ESTRICTO, msg
    _avisa(msg)


# ── duplicados ────────────────────────────────────────────────────────────

def _parrafos(nombre):
    bloques = re.split(r"\n\s*\n", _sin_codigo(_cuerpo(nombre)))
    for b in bloques:
        b = b.strip()
        if (not b or b.startswith(("#", ":::", "|", "$$")) or b.startswith("**Definición")
                or len(_palabras(b)) < 6):
            continue
        yield re.sub(r"[\W_]+", " ", b.lower()).strip()


def test_sin_parrafos_duplicados():
    vistos = defaultdict(list)
    for n in PAGINAS + VIEJAS:
        for p in _parrafos(n):
            vistos[p].append(n)
    repetidos = {p: ns for p, ns in vistos.items()
                 if len(ns) > 1 and any(n in PAGINAS for n in ns)}
    assert not repetidos, "párrafos repetidos: " + "; ".join(
        f"{p[:50]}… en {ns}" for p, ns in repetidos.items())


# ── referencias ───────────────────────────────────────────────────────────

def _ids_del_repo():
    ids = set()
    for ruta in (RAIZ / "course").rglob("*.md"):
        texto = ruta.read_text(encoding="utf-8")
        if texto.startswith("---"):
            ids |= set(re.findall(r"^id:\s*(\S+)", texto.split("---", 2)[1], re.M))
        ids |= set(re.findall(r"\{#([\w-]+)", texto))
    for ruta in (RAIZ / "course").rglob("*.y*ml"):
        ids |= set(re.findall(r"^\s*(?:-\s*)?id:\s*[\"']?([\w.-]+)",
                              ruta.read_text(encoding="utf-8"), re.M))
    return ids


@pytest.mark.parametrize("nombre", PAGINAS)
def test_wikilinks_resuelven(nombre):
    conocidos = _ids_del_repo()
    sueltos = [i for i in re.findall(r"\[\[([^\]|#]+)", _cuerpo(nombre))
               if i.strip() not in conocidos]
    assert not sueltos, f"{nombre}: [[{sueltos[0]}]] no resuelve a ningún id"


def _rotulos(ruta):
    if not ruta.is_file():
        return set()
    nb = json.loads(ruta.read_text(encoding="utf-8"))
    salida = set()
    for c in nb["cells"]:
        m = re.match(r"# celda (\d+\.\d+)", "".join(c["source"]))
        if c["cell_type"] == "code" and m:
            salida.add(m.group(1))
    return salida


@pytest.mark.parametrize("nombre", PAGINAS)
def test_celdas_citadas_existen_en_el_notebook(nombre):
    if not NB_ARQ.is_file():
        pytest.skip("arquitectura.ipynb aún no existe")
    existentes = _rotulos(NB_ARQ) | _rotulos(NB_VIEJO)
    citadas = set(re.findall(r"celdas? (\d+\.\d+)", _sin_codigo(_cuerpo(nombre))))
    faltan = sorted(citadas - existentes)
    if faltan:
        msg = f"{nombre}: celdas {faltan} sin rótulo «# celda N.M» en el notebook"
        assert not ESTRICTO, msg
        _avisa(msg)


@pytest.mark.parametrize("nombre", PAGINAS)
def test_figuras_con_alt_archivo_y_credito(nombre):
    texto = _sin_codigo(_cuerpo(nombre))
    bloques = re.findall(r"^::: figure[^\n]*\n\s*!\[([^\]]*)\]\(([^)]+)\)", texto, re.M)
    assert len(bloques) == len(re.findall(r"^::: figure", texto, re.M)), (
        f"{nombre}: una figura no trae ![alt](ruta) justo debajo")
    creditos = CREDITOS.read_text(encoding="utf-8") if CREDITOS.is_file() else ""
    for alt, ruta in bloques:
        assert alt.strip(), f"{nombre}: figura {ruta} sin alt"
        archivo = (UNIDAD / ruta).resolve()
        assert archivo.is_file(), f"{nombre}: no existe {ruta}"
        assert f"| {archivo.name} |" in creditos, (
            f"{nombre}: {archivo.name} no tiene fila en _assets/CREDITOS.md")
