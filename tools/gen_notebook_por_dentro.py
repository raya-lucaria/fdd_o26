"""Genera codigo/09_python/por_dentro/por_dentro.ipynb a partir de las paginas.

El notebook es autocontenido: por cada **Haz (celda N.M)** de las paginas de
la seccion 9.2 trae, en markdown, la frase del Haz, «Qué hace cada línea» y
«Deberías ver», y debajo la celda de codigo con el codigo de la pagina. Las
paginas son la unica fuente: si cambia una, se vuelve a correr este script y
el notebook la sigue (tools/test_python_por_dentro.py compara byte a byte).

El notebook nunca se edita a mano.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SECCION = RAIZ / "course/9_python/2_por_dentro"
DESTINO = RAIZ / "codigo/09_python/por_dentro/por_dentro.ipynb"

PAGINAS = [
    "0_index.md",
    "1_que_es_python.md",
    "2_nombres_y_objetos.md",
    "3_el_gil.md",
    "4_lo_que_escribe_la_ia.md",
    "5_trabajar_con_ia.md",
]

# Titulo de cada celda en el notebook (y la lista que la guarda usa para
# comprobar que toda «celda N.M» citada en una pagina existe).
CELDAS = [
    ("0.0", "¿Dónde estoy? (la carpeta de trabajo)"),
    ("0.1", "Arranque: corre revisa_esto.py"),
    ("1.0", "Una función en 30 segundos"),
    ("1.1", "precio_final"),
    ("1.2", "Con descuento"),
    ("1.3", "Con descuento 0"),
    ("1.4", "Un except que no hace nada"),
    ("1.5", "Qué Python corre (lectura)"),
    ("1.6", "dis (lectura)"),
    ("1.7", "suma con números y con textos (lectura)"),
    ("2.1", "= no copia"),
    ("2.2", "Copiar es explícito, y de un nivel"),
    ("2.3", "La función recibe el mismo objeto"),
    ("2.4", "El argumento por defecto mutable"),
    ("3.1", "1 hilo calcula 10 s (mira htop)"),
    ("3.2", "4 hilos calculan 10 s (mira htop)"),
    ("3.3", "4 procesos calculan 10 s (mira htop)"),
    ("3.4", "4 hilos esperan"),
    ("4.1", "Qué cuenta como falso"),
    ("4.2", "edad = 0"),
    ("4.3", "0.1 + 0.2"),
    ("4.4", "Decimal"),
    ("4.5", "Comprehension (lectura)"),
    ("4.6", "zip (lectura)"),
    ("4.7", "Encoding (lectura)"),
    ("5.1", "La respuesta al prompt bueno: resume_ventas.py"),
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


# De la pagina 0 sólo entran las secciones que se hacen en el notebook; el
# ritual de git y las tablas de navegacion se quedan en la pagina.
SECCIONES_0 = ("## Dónde corre tu notebook", "## Los cinco síntomas")
_FUERA = ("Sigue con", "> [!NOTE]", "> **Si sólo recuerdas", "— Hasta aquí")


def _partes(pagina):
    """La pagina como lista de ("md", texto) y ("code", codigo, celda).

    El codigo de cada **Haz (celda N.M)** sale a una celda de codigo; todo lo
    demas (explicaciones, salidas esperadas, tablas, bloques de terminal) queda
    en markdown. Los bloques ::: (figuras, problemas) no se copian: la figura
    se nombra y se remite a la pagina.
    """
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
    if "{ruta_" in texto:
        # Una celda con un marcador sólo se corre a mano, con la ruta propia:
        # comentada, «Run All» no se detiene en ella.
        texto = ("# Sólo si la celda 0.0 no dio por_dentro: quita el # y pon tu ruta.\n"
                 + "\n".join("# " + l if l.strip() else l for l in texto.split("\n")))
    lineas = texto.split("\n")
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": [l + "\n" for l in lineas[:-1]] + [lineas[-1]]}


def notebook():
    celdas = [_md(
        "# Python por dentro\n\n"
        "Este notebook es la clase de la sección 9.2 completa: cada celda trae su "
        "explicación arriba y el código listo. Córrelas **en orden**, una por una "
        "(Shift+Enter), y compara con «Deberías ver». La página del curso tiene lo "
        "mismo, más figuras y lecturas: https://rayalucaria.org/fdd_o26/python/por-dentro/\n\n"
        "Antes de entregar: *Clear All Outputs* y guarda.")]
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
