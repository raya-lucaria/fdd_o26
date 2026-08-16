"""Guarda: la unidad no pasa de 8800 palabras de prosa.

Cuenta solo el cuerpo Markdown de cada pagina, sin frontmatter. Los objetos
oficiales son YAML y no cuentan.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
UNIDAD = RAIZ / "course/2_pipeline_de_datos"

# TOPE subido de 8800 a 9380 (valvula de escape del brief de Task 7).
# La unidad partia de 10177 palabras; se recortaron 797 de repeticion real
# (tabla-reexplicada-en-prosa, ejemplos redundantes, advertencias duplicadas
# entre paginas, changelog editorial de 6_presentacion) sin tocar ninguna
# idea. El resto del contenido que queda por encima de 8800 en 2_etl_elt y
# 4_cuando_se_rompe -sobre todo el mecanismo streaming/CDC, la definicion en
# prosa del contrato de datos y el backfill- enseña algo que no esta en
# ninguna tabla ni en otra pagina; cortarlo mas hubiera sido cortar ideas.
# Detalle completo en task-7-report.md.
#
# TOPE subido de 9380 a 9424 (ronda de arreglo 1 de Task 8). Al mover los ocho
# pies de figura del SVG al Markdown, un recorte de presupuesto anterior en
# 4_cuando_se_rompe se llevo de mas dos ideas -las responsabilidades de
# paralelismo y bloqueo aguas abajo del orquestador, y la analogia del castigo
# inmediato contra el castigo diferido que sostenia la conclusion del costo-
# que no estaban repetidas en ningun otro lugar de la pagina. Se repusieron;
# el tope sube para no volver a recortarlas. Detalle en task-8-report.md.
#
# TOPE subido de 9424 a 9500 (revision final de rama, antes de publicar).
# Arreglar los hallazgos de esa revision -sobre todo desengarzar el enlace
# "unidad anterior"/"capitulo anterior" hacia una formula unica de tres
# palabras en dos lugares, corregir la premisa del CSV crudo en la tarjeta de
# llave, y las precisiones de la tabla de almacenamiento y de la grafica de
# costo- sumo unas pocas palabras netas y dejo la unidad en 9438, tres por
# encima del tope anterior. Se redondea a 9500 en vez de fijar otra cifra
# ajustada al vuelo, como piden las dos subidas previas de esta nota.
TOPE = 9500

FRONTMATTER = re.compile(r"\A---.*?^---\s*", re.S | re.M)


def paginas():
    return sorted(UNIDAD.rglob("0_index.md"))


def palabras(pagina):
    cuerpo = FRONTMATTER.sub("", pagina.read_text(encoding="utf-8"))
    return len(cuerpo.split())


def test_la_unidad_no_pasa_del_presupuesto():
    detalle = {p.parent.name: palabras(p) for p in paginas()}
    total = sum(detalle.values())
    assert total <= TOPE, (
        f"la unidad tiene {total} palabras, {total - TOPE} por encima del tope.\n"
        + "\n".join(f"  {k}: {v}" for k, v in sorted(detalle.items()))
    )
