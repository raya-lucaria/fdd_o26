"""Guarda: ningun wikilink lleva la barra escapada.

Raya resuelve `[[id|etiqueta]]` sobre el texto crudo, antes de que Markdown
procese escapes. Escribir `[[id\\|etiqueta]]` —que es lo que uno hace por reflejo
dentro de una tabla, donde la barra si necesita escaparse— produce un id con una
barra invertida pegada y rompe el build entero con "Broken wikilink reference".

Dentro de una tabla, el wikilink va con la barra **sin** escapar: la unidad 5 lo
hace asi desde que existe y valida. La barra escapada solo hace falta dentro de
un code span, donde no hay wikilink que resolver.

Este error ya tumbo el build dos veces.
"""
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PAGINAS = sorted(RAIZ.glob("course/**/*.md"))
IDS = [str(p.relative_to(RAIZ / "course")) for p in PAGINAS]

_ESCAPADO = re.compile(r"\[\[[^\]\n]*\\\|")
_WIKILINK = re.compile(r"\[\[([^\]\n|]+)(?:\|([^\]\n]*))?\]\]")


def test_hay_paginas_que_vigilar():
    assert PAGINAS, "no se encontro ninguna pagina bajo course/"


@pytest.mark.parametrize("pagina", PAGINAS, ids=IDS)
def test_ningun_wikilink_lleva_la_barra_escapada(pagina):
    ofensas = [
        f"  linea {n}: {l.strip()[:90]}"
        for n, l in enumerate(pagina.read_text(encoding="utf-8").splitlines(), 1)
        if _ESCAPADO.search(l)
    ]
    assert not ofensas, (
        f"{pagina.name}: wikilink con la barra escapada. Raya lo resuelve sobre "
        "el texto crudo, asi que el id queda con una barra invertida pegada y "
        "el build falla. Dentro de una tabla va sin escapar:\n" + "\n".join(ofensas)
    )


@pytest.mark.parametrize("pagina", PAGINAS, ids=IDS)
def test_ningun_wikilink_queda_sin_destino(pagina):
    for destino, _ in _WIKILINK.findall(pagina.read_text(encoding="utf-8")):
        assert destino.strip(), f"{pagina.name}: wikilink sin destino"
        assert "\\" not in destino, (
            f"{pagina.name}: el destino {destino!r} trae una barra invertida"
        )
