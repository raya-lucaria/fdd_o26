"""Genera codigo/10_apis/apis.ipynb a partir de las paginas de la seccion 10.1.

Mismo contrato que tools/gen_notebook_por_dentro.py: por cada **Haz (celda N.M)**
de las paginas trae, en markdown, la explicacion de la pagina («Qué hace cada
línea», «Deberías ver»), y debajo la celda de codigo. Las paginas son la unica
fuente: si cambia una, se vuelve a correr este script y el notebook la sigue
(tools/test_apis_curriculum.py compara byte a byte).

El notebook nunca se edita a mano.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SECCION = RAIZ / "course/10_apis/1_apis_y_http"
DESTINO = RAIZ / "codigo/10_apis/apis.ipynb"

PAGINAS = [
    "0_index.md",
    "1_que_es_una_api.md",
    "2_el_mensaje_http.md",
    "3_metodos_y_status.md",
    "4_http_rest_y_crud.md",
]

# Titulo de cada celda en el notebook (y la lista que la guarda usa para
# comprobar que toda «celda N.M» citada en una pagina existe).
CELDAS = [
    ("0.1", "Arranque: ¿contesta el servidor?"),
    ("1.1", "El contrato del servidor"),
    ("1.2", "Función contra red"),
    ("2.1", "HTTP escrito a mano"),
    ("2.2", "HTTP a mano contra example.com"),
    ("2.3", "Lo que manda requests"),
    ("2.4", "Un body JSON"),
    ("2.5", "Un recurso, dos formatos"),
    ("2.6", "El charset que faltaba"),
    ("2.7", "La URL, parte por parte"),
    ("3.1", "Repetir cada método tres veces"),
    ("3.2", "El crawler que borra"),
    ("3.3", "Timeout"),
    ("3.4", "El cobro doble"),
    ("3.5", "Idempotency-Key"),
    ("3.6", "Galería de códigos de estado"),
    ("3.7", "El 201 que miente"),
    ("4.1", "ETag y 304"),
    ("4.2", "Sin estado"),
    ("4.3", "GitHub: el header Link (sólo el profesor)"),
    ("4.4", "Ciclo CRUD completo"),
]
TITULOS = dict(CELDAS)

_HAZ = re.compile(r"^\*\*Haz \(celda (\d+\.\d+)[^)]*\):\*\*\s*(.*)$")


def _plano(texto):
    """Wikilinks de Raya a texto: [[id|rotulo]] -> rotulo, [[id]] -> id."""
    texto = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", texto)
    return re.sub(r"\[\[([^\]]+)\]\]", r"\1", texto)


def _bloque(lineas, i):
    """Si en i empieza un bloque ```, regresa (lenguaje, contenido, fin)."""
    m = re.match(r"^```(\w*)\s*$", lineas[i])
    if not m:
        return None
    j = i + 1
    while j < len(lineas) and not lineas[j].startswith("```"):
        j += 1
    return m.group(1), "\n".join(lineas[i + 1:j]), j + 1


# De la pagina 0 sólo entra el arranque del notebook; la preparacion (git,
# uv, el servidor) se hace en la terminal y se queda en la pagina.
SECCIONES_0 = ("## Arranque del notebook",)
_FUERA = ("Sigue con", "Regresa al índice", "> [!NOTE]", "> **Si sólo recuerdas")


def _partes(pagina):
    """La pagina como lista de ("md", texto) y ("code", codigo, celda)."""
    lineas = pagina.read_text(encoding="utf-8").split("---", 2)[2].splitlines()
    solo_secciones = pagina.name == "0_index.md"
    partes, md, dentro, celda, i = [], [], not solo_secciones, None, 0
    while i < len(lineas):
        linea = lineas[i]
        if linea.startswith("## "):
            if solo_secciones:
                dentro = linea.startswith(SECCIONES_0)
            if dentro:
                md.append("#" + linea)
            i += 1
            continue
        if not dentro or linea.startswith("# ") or linea.startswith("**Página "):
            i += 1
            continue
        if linea.startswith("::: "):
            titulo = re.search(r'title="([^"]+)"', linea)
            if linea.startswith("::: figure") and titulo:
                md.append(f"*Figura en la página del curso: «{titulo.group(1)}».*")
            while i + 1 < len(lineas) and lineas[i + 1].strip() != ":::":
                i += 1
            i += 2
            continue
        if linea.startswith(_FUERA):
            i += 1
            continue
        m = _HAZ.match(linea)
        if m:
            celda = m.group(1)
        bloque = _bloque(lineas, i) if linea.startswith("```") else None
        if bloque and bloque[0] == "python" and celda:
            partes.append(("md", "\n".join(md).strip()))
            partes.append(("code", bloque[1], celda))
            md, celda, i = [], None, bloque[2]
            continue
        if bloque:
            md.append(f"```{bloque[0]}\n{bloque[1]}\n```")
            i = bloque[2]
            continue
        md.append(linea)
        i += 1
    if "\n".join(md).strip():
        partes.append(("md", "\n".join(md).strip()))
    return partes


def _encabezado(pagina):
    """Titulo y Meta: de la pagina."""
    cuerpo = pagina.read_text(encoding="utf-8").split("---", 2)[2]
    titulo = re.search(r"^# (.+)$", cuerpo, re.M).group(1)
    meta = re.search(r"^Meta: (.+)$", cuerpo, re.M)
    return titulo, (meta.group(1) if meta else "")


def _md(texto):
    lineas = texto.split("\n")
    return {"cell_type": "markdown", "metadata": {},
            "source": [l + "\n" for l in lineas[:-1]] + [lineas[-1]]}


def _codigo(texto):
    lineas = texto.split("\n")
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": [l + "\n" for l in lineas[:-1]] + [lineas[-1]]}


def notebook():
    celdas = [_md(
        "# APIs y HTTP\n\n"
        "Este notebook es la clase de la sección 10.1 completa: cada celda trae su "
        "explicación arriba y el código listo. **Antes de empezar, arranca el servidor** "
        "en una terminal aparte, dentro de esta carpeta (`uv run python servidor.py`), "
        "y déjala visible: ahí aparece cada petición que hagas.\n\n"
        "Córrelas **en orden**, una por una (Shift+Enter), y compara con «Deberías ver». "
        "La página del curso tiene lo mismo, más las tablas y los diagramas: "
        "https://rayalucaria.org/fdd_o26/apis/apis-y-http/")]
    vistas = set()
    for nombre in PAGINAS:
        pagina = SECCION / nombre
        titulo, meta = _encabezado(pagina)
        partes = _partes(pagina)
        if not any(p[0] == "code" for p in partes):
            continue
        celdas.append(_md(f"# {titulo}" + (f"\n\nMeta: {_plano(meta)}" if meta and nombre != "0_index.md" else "")))
        for parte in partes:
            if parte[0] == "md" and parte[1]:
                celdas.append(_md(_plano(parte[1])))
            elif parte[0] == "code":
                if parte[2] not in vistas:
                    celdas.append(_md(f"## {parte[2]} · {TITULOS[parte[2]]}"))
                    vistas.add(parte[2])
                celdas.append(_codigo(parte[1]))
    nb = {"cells": celdas, "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 4}
    return json.dumps(nb, ensure_ascii=False, indent=1) + "\n"


if __name__ == "__main__":
    DESTINO.write_text(notebook(), encoding="utf-8")
    print(f"escrito {DESTINO.relative_to(RAIZ)}")
    sys.exit(0)
