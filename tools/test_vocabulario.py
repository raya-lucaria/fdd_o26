"""Guarda: cada termino del catalogo se define antes de usarse y esta en el glosario.

La regla del spec es que una definicion solo puede usar vocabulario ya definido,
y que ninguna pagina puede usar un termino que se define mas adelante. El orden
de las paginas lo da el prefijo numerico del directorio.

Ronda de arreglo 1: la comprobacion "no se usa antes de definirse" opera en dos
niveles.

- Entre paginas: si una pagina anterior (indice menor) a la que define el
  termino lo usa en cualquier parte, es una falla — sin excepciones. Esto no
  cambio respecto a la primera version de la guarda.
- Dentro de la misma pagina que define el termino: cualquier linea de prosa
  ANTES de la caja `::: definition` que lo usa tambien es una falla, porque el
  lector la lee antes de llegar a la definicion. Aqui hay tres exenciones,
  porque no son prosa que se lea en orden:
    (a) el frontmatter (YAML entre los `---`) — es metadato para la
        maquinaria del sitio, nadie lo lee como texto corrido;
    (b) la seccion `## En corto` — es un resumen que adelanta vocabulario por
        diseno, para que el lector sepa que viene antes de leer los detalles;
    (c) las filas de tabla (lineas que empiezan por `|`) — se consultan por
        columna, no se leen en orden, y sus "Ejemplos" son ilustrativos, no
        prosa que ensena el termino.
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


def _lineas_exentas(lineas):
    """Numeros de linea (0-index) exentos de la comprobacion intra-pagina.

    Ver las tres exenciones documentadas en el docstring del modulo:
    frontmatter, seccion "## En corto" y filas de tabla.
    """
    exentas = set()

    # (a) Frontmatter: del primer "---" al siguiente "---", ambos incluidos.
    if lineas and lineas[0].strip() == "---":
        for i in range(1, len(lineas)):
            if lineas[i].strip() == "---":
                exentas.update(range(0, i + 1))
                break

    # (b) Seccion "## En corto": del encabezado al siguiente "## " (exclusivo).
    inicio_en_corto = None
    for i, linea in enumerate(lineas):
        if linea.strip() == "## En corto":
            inicio_en_corto = i
            break
    if inicio_en_corto is not None:
        fin_en_corto = len(lineas)
        for i in range(inicio_en_corto + 1, len(lineas)):
            if lineas[i].startswith("## "):
                fin_en_corto = i
                break
        exentas.update(range(inicio_en_corto, fin_en_corto))

    # (c) Filas de tabla: cualquier linea que empiece por "|".
    for i, linea in enumerate(lineas):
        if linea.lstrip().startswith("|"):
            exentas.add(i)

    return exentas


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
    todas = paginas()
    indice_definicion = {}
    linea_definicion = {}
    for i, pagina in enumerate(todas):
        contenido = texto(pagina)
        for m in APERTURA.finditer(contenido):
            termino = m.group("id")
            indice_definicion[termino] = i
            linea_definicion[termino] = contenido.count("\n", 0, m.start())

    for termino, patron in TERMINOS.items():
        assert termino in indice_definicion, f"{termino} no se define en ninguna pagina"
        i_definicion = indice_definicion[termino]
        pagina_definicion = todas[i_definicion]

        # Entre paginas: ninguna pagina anterior a la que define el termino
        # puede usarlo en ningun lugar. Sin exenciones.
        for i, pagina in enumerate(todas):
            if pagina.name == "0_index.md" and pagina.parent.name == "7_glosario":
                continue  # el glosario recapitula todo
            if i >= i_definicion:
                continue
            if re.search(patron, texto(pagina), re.I):
                raise AssertionError(
                    f"{pagina.parent.name} usa '{termino}', que se define despues"
                )

        # Dentro de la pagina que lo define: ninguna linea de prosa antes de
        # la caja puede usarlo, salvo las exentas (frontmatter, En corto,
        # filas de tabla).
        lineas = texto(pagina_definicion).splitlines()
        exentas = _lineas_exentas(lineas)
        limite = linea_definicion[termino]
        for num in range(limite):
            if num in exentas:
                continue
            if re.search(patron, lineas[num], re.I):
                raise AssertionError(
                    f"{pagina_definicion.parent.name}:{num + 1} usa '{termino}' "
                    f"en prosa antes de su propia caja de definicion "
                    f"(linea {limite + 1})"
                )


def test_el_glosario_lista_todos_los_terminos():
    assert GLOSARIO.is_file(), "falta 7_glosario/0_index.md"
    cuerpo = texto(GLOSARIO)
    for termino in TERMINOS:
        assert f"@{termino}" in cuerpo, f"el glosario no referencia @{termino}"


CONTENIDO = [
    "0_index", "1_el_viaje", "2_etl_elt", "3_eda",
    "4_cuando_se_rompe", "5_posiciones",
]


def soporte(nombre):
    if nombre == "0_index":
        return UNIDAD / "_official"
    return UNIDAD / nombre / "_official"


def test_cada_pagina_de_contenido_tiene_dos_tarjetas_y_dos_preguntas():
    import yaml

    for nombre in CONTENIDO:
        base = soporte(nombre)
        tarjetas = sorted((base / "cards").glob("*.yaml")) if (base / "cards").is_dir() else []
        assert len(tarjetas) == 2, f"{nombre}: {len(tarjetas)} tarjetas, deben ser 2"

        quizzes = sorted((base / "quizzes").glob("*.yaml")) if (base / "quizzes").is_dir() else []
        assert len(quizzes) == 1, f"{nombre}: {len(quizzes)} quizzes, debe ser 1"
        preguntas = yaml.safe_load(quizzes[0].read_text(encoding="utf-8"))
        n = len(preguntas["content"]["questions"])
        assert n == 2, f"{nombre}: el quiz tiene {n} preguntas, deben ser 2"


def test_ninguna_pregunta_tiene_dos_opciones_correctas():
    import yaml

    for ruta in UNIDAD.rglob("_official/quizzes/*.yaml"):
        datos = yaml.safe_load(ruta.read_text(encoding="utf-8"))
        for pregunta in datos["content"]["questions"]:
            correctas = [o for o in pregunta["options"] if o.get("correct")]
            assert len(correctas) == 1, (
                f"{ruta.name}/{pregunta['id']}: {len(correctas)} opciones correctas"
            )
