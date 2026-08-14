"""Guarda: cada termino del catalogo se define antes de usarse y esta en el glosario.

La regla del spec es que una definicion solo puede usar vocabulario ya definido,
y que ninguna pagina puede usar un termino que se define mas adelante. El orden
de las paginas lo da el prefijo numerico del directorio.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UNIDAD = RAIZ / "course/2_pipeline_de_datos"
GLOSARIO = UNIDAD / "7_glosario/0_index.md"

# id de la definicion -> patron que delata su uso en prosa.
TERMINOS = {
    "def-tabla": r"\bfilas?\b|\bcolumnas?\b",
    "def-llave": r"\bllaves?\b",
    "def-join": r"`join`|\bjoin\b",
    "def-corrida": r"\bcorridas?\b",
    "def-esquema": r"\besquemas?\b",
    "def-formato-tabla": r"Iceberg|Delta Lake|Hudi",
    "def-particion": r"\bpartici[oó]n|\bparticionar\b",
    "def-parquet": r"\bParquet\b",
    "def-staging": r"\bstaging\b",
    "def-transaccion": r"\btransacci[oó]n|\bat[oó]mica?\b",
    "def-fuga": r"fuga de informaci[oó]n",
    "def-idempotencia": r"\bidempoten",
    "def-sistema-distribuido": r"sistema distribuido",
    "def-materializar": r"\bmaterializar\b|\bmaterializad",
}

APERTURA = re.compile(r"^::: +definition +\{#(?P<id>[A-Za-z][\w-]*)", re.M)


def paginas():
    """Las paginas de la unidad, en el orden en que las lee el alumno."""
    orden = [UNIDAD / "0_index.md"]
    orden += [
        d / "0_index.md"
        for d in sorted(UNIDAD.iterdir())
        if d.is_dir() and not d.name.startswith("_")
    ]
    return [p for p in orden if p.is_file()]


def texto(pagina):
    return pagina.read_text(encoding="utf-8")


def test_cada_termino_tiene_exactamente_una_definicion():
    encontrados = []
    for pagina in paginas():
        encontrados += APERTURA.findall(texto(pagina))
    for termino in TERMINOS:
        assert encontrados.count(termino) == 1, (
            f"{termino} aparece {encontrados.count(termino)} veces; debe ser 1"
        )


def test_ninguna_pagina_pasa_de_cuatro_definiciones():
    for pagina in paginas():
        n = len(APERTURA.findall(texto(pagina)))
        assert n <= 4, f"{pagina.parent.name} tiene {n} definiciones; el tope es 4"


def test_ningun_termino_se_usa_antes_de_definirse():
    indice_definicion = {}
    for i, pagina in enumerate(paginas()):
        for encontrado in APERTURA.findall(texto(pagina)):
            indice_definicion[encontrado] = i

    for termino, patron in TERMINOS.items():
        assert termino in indice_definicion, f"{termino} no se define en ninguna pagina"
        for i, pagina in enumerate(paginas()):
            if pagina.name == "0_index.md" and pagina.parent.name == "7_glosario":
                continue  # el glosario recapitula todo
            if re.search(patron, texto(pagina)) and i < indice_definicion[termino]:
                raise AssertionError(
                    f"{pagina.parent.name} usa '{termino}', que se define despues"
                )


def test_el_glosario_lista_todos_los_terminos():
    assert GLOSARIO.is_file(), "falta 7_glosario/0_index.md"
    cuerpo = texto(GLOSARIO)
    for termino in TERMINOS:
        assert f"@{termino}" in cuerpo, f"el glosario no referencia @{termino}"
