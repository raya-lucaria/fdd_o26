"""Guarda: los terminos que un diagrama dibuja son los que su pagina enseña.

`test_diagramas.py` solo verifica que el SVG en disco coincida con lo que
`gen_diagramas.py` produce hoy — no puede detectar que el generador dibuje
algo *distinto* de lo que la pagina dice, porque nunca compara contra la
pagina. Eso paso, sin que ninguna prueba lo viera, con dos diagramas de la
revision final de rama:

- `d-calidad` dibujaba Formato, Duplicacion e Integridad; `3_eda/0_index.md`
  enseña Completitud, Unicidad, Validez, Consistencia, Exactitud y
  Oportunidad. Integridad no esta en la pagina; Oportunidad, que sostiene el
  puente a la unidad siguiente, no estaba en el diagrama.
- `d-ciclo` dibujaba un lazo de seis etapas estrictamente hacia adelante;
  `0_index.md` enseña cuatro etapas y el argumento central de la pagina es
  que hay retornos entre ellas.

Esta prueba ata cada diagrama a una lista corta de terminos y comprueba dos
cosas: que esos terminos siguen apareciendo en el SVG que el generador
produce HOY (si esto falla, la lista de abajo quedo desactualizada frente a
un cambio en `gen_diagramas.py`, y hay que revisar cual de los dos se
equivoco) y que esos mismos terminos aparecen, literalmente, en el Markdown
de la pagina que la figura ilustra (si esto falla, la pagina cambio su
vocabulario y el diagrama se quedo atras, o al reves).

Solo se listan los diagramas donde el vinculo es limpio y comprobable por
texto: un rotulo del diagrama es, palabra por palabra o por raiz cuando el
diagrama pluraliza o la pagina declina, un termino que la pagina usa para lo
mismo. `d-dag` (nombres de un caso narrativo, no un vocabulario cerrado) y
`d-idempotencia` (dos rotulos, "idempotente"/"no idempotente", que la prueba
de vocabulario ya vigila por otro lado) quedan fuera por esa razon, no por
descuido.
"""
import importlib.util
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
UNIDAD = RAIZ / "course/2_pipeline_de_datos"


def _cargar_generador():
    spec = importlib.util.spec_from_file_location(
        "gen_diagramas", RAIZ / "tools/gen_diagramas.py"
    )
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


GEN = _cargar_generador()

# slug -> (pagina que ilustra el diagrama, [terminos o patrones de termino])
# Los patrones son case-insensitive: cubren mayuscula inicial de titulo,
# plural del diagrama y singular de la prosa con la misma expresion.
VINCULOS = {
    "d-calidad": (
        UNIDAD / "3_eda/0_index.md",
        ["Completitud", "Unicidad", "Validez", "Consistencia", "Exactitud",
         "Oportunidad"],
    ),
    "d-ciclo": (
        UNIDAD / "0_index.md",
        ["ETL / ELT", "EDA", "Entrenamiento o an[aá]lisis", "Producci[oó]n"],
    ),
    "d-schema": (
        UNIDAD / "1_el_viaje/0_index.md",
        ["Base de datos", "Data lake", "Data warehouse", "Lakehouse"],
    ),
    "d-tiempo": (
        UNIDAD / "4_cuando_se_rompe/0_index.md",
        ["Batch", "Micro-batch", "Streaming"],
    ),
    "d-tidy": (
        UNIDAD / "2_etl_elt/0_index.md",
        ["variable", "observaci[oó]n", "valor"],
    ),
    "d-etl-elt": (
        UNIDAD / "2_etl_elt/0_index.md",
        ["ETL", "ELT"],
    ),
}


@pytest.mark.parametrize("slug", sorted(VINCULOS))
def test_los_terminos_del_diagrama_aparecen_en_su_pagina(slug):
    pagina, terminos = VINCULOS[slug]
    texto_pagina = pagina.read_text(encoding="utf-8")
    faltantes = [t for t in terminos if not re.search(t, texto_pagina, re.I)]
    assert not faltantes, (
        f"{slug}: {pagina.relative_to(RAIZ)} no usa {faltantes}; el diagrama "
        f"y la pagina que ilustra deben ensenar el mismo vocabulario"
    )


@pytest.mark.parametrize("slug", sorted(VINCULOS))
def test_los_terminos_del_diagrama_aparecen_en_el_svg(slug):
    _, terminos = VINCULOS[slug]
    svg = GEN.DIAGRAMAS[slug]()
    faltantes = [t for t in terminos if not re.search(t, svg, re.I)]
    assert not faltantes, (
        f"{slug}: el SVG que produce gen_diagramas.py hoy no contiene "
        f"{faltantes} — actualiza VINCULOS en este archivo si el generador "
        f"cambio a proposito, o corrige el generador si no"
    )
