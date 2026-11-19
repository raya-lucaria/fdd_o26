---
id: patrones-del-stack
title: "Patrones y el stack escrito"
nav_title: "Patrones del stack"
summary: "Ocho patrones salen de las carreras de la clase; cada uno es una pregunta al revisar código. Cinco preguntas para elegir una librería, y AGENTS.md para dejar el stack escrito donde la IA lo lee."
status: ready
estimated_time: 15m
tags: [patrones, stack, agents-md, ia, revision-de-codigo]
prerequisites: [archivos-y-memoria]
---

# Patrones y el stack escrito

**Página 4 de 4 · Elegir el stack**

Meta: convertir cada carrera de la clase en una pregunta que haces al revisar código, y dejar tu stack escrito en `AGENTS.md`.

**📄 PÁGINA · Patrones y el stack escrito**

## En corto

- **Cada carrera dejó un patrón, y cada patrón es una pregunta al revisar.**
- **Una librería se elige con cinco preguntas**, la última es si existe: la IA inventa nombres.
- **`AGENTS.md` deja tu stack escrito** donde un agente lo lee antes de tocar el proyecto.

## Ocho patrones, ocho preguntas

| Patrón | Lo viste en | Pregunta al revisar |
|---|---|---|
| Fuera del intérprete es rápido | B.1; A.8 (`model_construct` más lento que `model_validate`) | ¿Hay un `for` o un `.apply` donde cabe una expresión? |
| Fila vs columna | A.9, C.1 | ¿Valida o guarda por fila algo que es una tabla? |
| Lazy optimiza | B.4, B.5 | ¿Lee todo para quedarse con una parte? |
| El tipo decide la memoria | B.6, B.7 | ¿Textos como `object`? ¿Enteros vueltos `float`? |
| Compartir vs copiar | B.8 | ¿Convierte entre librerías sin necesidad? |
| Más garantías, más costo | A.8 | ¿Valida adentro lo que ya validó en la frontera? |
| Todo a la vez vs uno a la vez | C.5 | ¿Carga el archivo entero para recorrerlo? |
| Medir, no adivinar | todas | ¿Afirma «es más rápido» sin un número? |

- **Fuera del intérprete** quiere decir: el trabajo lo hace código en Rust, C o C++ (Polars, NumPy, DuckDB, el núcleo de Pydantic), no un `for` de Python ([[python-por-dentro]]).
- **La frontera** es donde un dato entra a tu programa: un CSV, una API. Ahí se valida una vez ([[contratos]]).
- Los números de cada carrera están en [[contratos]], [[motores-de-tablas]] y [[archivos-y-memoria]]; aquí sólo queda la pregunta.

## Cinco preguntas para elegir una librería

Antes de agregar una librería que propone la IA, contesta en orden. Un «no» basta para buscar otra.

| # | Pregunta | Dónde la contestas |
|---:|---|---|
| 1 | ¿Lo hace ya la biblioteca estándar? (`pathlib`, `csv`, `json`, `sqlite3`) | La documentación de Python |
| 2 | ¿Tuvo un release en el último año? | La pestaña *Release history* en PyPI |
| 3 | ¿Trae tipos (*type hints*)? | En PyPI, el clasificador `Typing :: Typed`; o que mypy no se queje al importarla |
| 4 | ¿Su licencia te deja usarla? (MIT, Apache 2.0, BSD sí) | La barra lateral de PyPI |
| 5 | **¿Existe en PyPI con ese nombre exacto?** | `https://pypi.org/project/<nombre>/` |

La pregunta 5 va al final de la tabla, pero **es la que más falla**: un modelo de lenguaje inventa nombres de paquetes que suenan bien. Si alguien registra ese nombre inventado con código malicioso, `uv add` lo instala sin quejarse.

## `AGENTS.md`: el stack escrito

`AGENTS.md` es un archivo Markdown en la raíz de un proyecto que un agente de IA (Claude Code, Codex, Cursor, Copilot…) lee **antes** de tocar el código. Es un formato abierto; desde 2025 lo cuida la Agentic AI Foundation, de la Linux Foundation.

Sin él, el agente elige lo que más vio: pandas con `.apply`, Pydantic v1, `pip`. Con él, lee tu decisión en cada sesión, sin que la repitas en cada prompt.

| Sección | Qué lleva | Ejemplo |
|---|---|---|
| Stack | Librerías y versiones, y lo que **no** se usa | «Polars 2.x para tablas; nunca pandas salvo para leer código ajeno» |
| Cómo se corre | Los comandos exactos | «`uv sync`; `uv run pytest`» |
| Definición de terminado | Lo que debe estar en verde antes de decir «listo» | «`ruff check`, `mypy` y `pytest` en verde **sobre los archivos de la práctica**» |
| Reglas propias | Lo que este proyecto decidió | «Validar con Pydantic sólo en la frontera» |

- **La definición de terminado** es la lista de comandos que deben salir en verde para dar una tarea por terminada. Sin ella, «listo» significa «el agente dejó de escribir».
- Nombra **los archivos**: `ruff check` sobre todo el proyecto también revisa `modelos.py`, que trae errores plantados a propósito.
- En tu entrega llenas el `AGENTS.md` de la plantilla ([[entregas-stack]]).

**Al revisar código de IA, busca:**

- `df.apply(lambda fila: …)` o `for i, fila in df.iterrows():` sobre una tabla: un `for` de Python donde cabe una expresión de Polars.
- `pd.read_csv(...)` seguido de `df[["a", "b"]]` o de un filtro: lee todo para quedarse con una parte; `pl.scan_csv(...)` deja que el filtro baje a la lectura.

**Al pedírselo a la IA, dile:**

- «Python 3.14, Polars 2.x (salió el 2026-10-06; si no conoces su API, dilo), Pydantic v2 sólo en la frontera; nada de pandas ni `.apply`».
- «Antes de usar una librería, dime su nombre exacto en PyPI y su último release».

::: problem {#py-stack-patron title="La pregunta que falta"}
La IA te entrega esto para sumar ventas de 10 millones de filas, y dice que es «lo más rápido»:

`df = pd.read_csv("ventas.csv")` · `df["total"] = df.apply(lambda f: f["cantidad"] * f["precio"], axis=1)` · `df[df["tienda"] == "Norte"]["total"].sum()`

¿Qué dos patrones rompe, y qué tercero rompe la frase «lo más rápido»?
:::

::: hint {of="py-stack-patron"}
Recorre la columna «Pregunta al revisar»: ¿dónde corre el `lambda`? ¿Cuántas filas lee para usar las de una tienda? ¿Qué número acompaña la afirmación?
:::

::: answer {of="py-stack-patron"}
- Fuera del intérprete es rápido: `.apply` con `lambda` corre un `for` de Python fila por fila; `cantidad * precio` es una expresión de columnas.
- Lazy optimiza: lee los 10 millones de filas y todas las columnas para usar las de una tienda.
- Medir, no adivinar: «lo más rápido» no trae número.
- Arreglo: `pl.scan_csv` → `filter(tienda == "Norte")` → `select((cantidad * precio).sum())` → `collect()`, y mídelo contra la versión de pandas antes de afirmar algo.
:::

Sigue con [[entregas-stack]]: la práctica es reescribir un script con el stack viejo usando estos patrones.

> [!NOTE]
> **Si sólo recuerdas una cosa:** cada decisión del stack se defiende con un número de tu máquina, y queda escrita en `AGENTS.md`.
