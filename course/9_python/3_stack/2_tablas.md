---
id: motores-de-tablas
title: "Motores de tablas"
nav_title: "Motores de tablas"
summary: "El trabajo hecho fuera del intérprete es decenas o miles de veces más rápido. Polars lazy deja que el motor optimice el plan antes de leer, y el tipo de cada columna decide cuánta memoria ocupa. pandas, sólo para comparar."
status: ready
estimated_time: 30m
tags: [polars, lazy, duckdb, pandas, arrow, memoria, rendimiento, ia]
prerequisites: [contratos]
---

# Motores de tablas

**Página 2 de 4 · Elegir el stack**

Meta: elegir dónde se hace el trabajo sobre una tabla, leer un plan lazy de Polars y reconocer el código viejo que escribe la IA.

**📄 PÁGINA · Motores de tablas**

## En corto

- **El trabajo hecho fuera del intérprete es rápido**: una expresión de Polars le gana a un `for` por decenas de veces, y a un `.apply` por miles.
- **Lazy deja que el motor optimice**: Polars ve el plan entero y lee sólo las columnas y filas que usas.
- **El tipo decide la memoria**: la misma columna de texto ocupa de 1 MB a 57 MB, y un vacío vuelve `float` una columna de enteros en pandas.

Un **motor de tablas** es la librería que ejecuta filtros, cuentas y agrupaciones sobre una tabla entera. Todo este notebook contesta una sola pregunta: **el total vendido por tienda, sin cantidades inválidas, de mayor a menor.**

## Polars, DuckDB y pandas, de cerca

| | Polars | DuckDB | pandas |
|---|---|---|---|
| Escribes | Métodos con expresiones: `pl.col("x")` | SQL | Métodos, máscaras e índice |
| Evalúa | Eager (`read_csv`) o lazy (`scan_csv`) | Lazy: una relación, hasta `.pl()` | Eager, cada paso en el momento |
| Núcleos | Todos (Rust, fuera del GIL) | Todos (C++) | Casi siempre uno |
| ¿Más que tu RAM? | Sí, con lazy y streaming | Sí, por diseño | No: todo vive en memoria |
| Vacíos en enteros | `null`; la columna sigue entera | `NULL` | `NaN`; la columna se vuelve `float64` |
| Desde | 1.0 en 2024; **2.0 el 2026-10-06** | 1.0 en 2024 | 2008; 3.0 el 2026-01-21 |
| En este curso | **El centro** | Cuando la pregunta es SQL | Sólo para comparar y leer código ajeno |

- **Eager** ejecuta cada paso en el momento, sobre la tabla entera; **lazy** arma primero un plan con todos los pasos y lo ejecuta al final, cuando se lo pides.
- Una **expresión** de Polars describe una cuenta sobre una columna sin hacerla: `pl.col("x") * 2`. Polars la corre en Rust cuando un método (`filter`, `agg`) la usa.
- Una **relación** de DuckDB es una consulta lista, sin traer el resultado a Python; `.pl()` la ejecuta y la trae como `DataFrame` de Polars.

## Fuera del intérprete es rápido

**📓 NOTEBOOK · b_tablas.ipynb · celdas B.0–B.1**

¿Te perdiste? Corre B.0 y salta a la celda que vamos.

B.1 suma `cantidad * precio` de cinco formas. **Fuera del intérprete** quiere decir que el ciclo sobre las filas corre en código compilado (C en NumPy, Rust en Polars), y Python hace una sola llamada. El `for` y la generadora usan a lo más 200 000 filas; `.apply` se mide sobre 100 000 y se extrapola: con un millón tardaría ~8 s.

`N = 1_000_000` · Intel i7-7700HQ (4 núcleos, 8 hilos) · 31 GB, en segundos por millón de filas:

| Opción | Seg. por millón | Veces vs el mejor |
|---|---:|---:|
| NumPy | 0.0021 | 1.0 |
| Polars, expresión | 0.0036 | 1.7 |
| Expresión generadora | 0.1329 | 62.9 |
| `for` | 0.142 | 67.2 |
| pandas `.apply(axis=1)` | 8.312 | 3933.6 |

- **Patrón: fuera del intérprete es rápido.** El `for` es de 20× a 70× más lento que NumPy según la corrida; `.apply`, miles de veces.
- NumPy y Polars **casi empatan**; el `for` y la generadora también: su orden cambia entre corridas. Tus números serán otros; lo que se mantiene es el patrón.

## Tres notaciones, la misma respuesta

**📓 NOTEBOOK · b_tablas.ipynb · celda B.2**

| Paso | pandas | Polars | DuckDB |
|---|---|---|---|
| Filtrar | `df[df["cantidad"] > 0]` | `.filter(pl.col("cantidad") > 0)` | `WHERE cantidad > 0` |
| La cuenta | multiplicar dos `Series` | una expresión **dentro de `.agg`** | `SUM(cantidad * precio)` |
| Agrupar | `.groupby(filas["tienda"])` | `.group_by("tienda")` | `GROUP BY tienda` |
| Ordenar | `.sort_values(ascending=False)` | `.sort("total", descending=True)` | `ORDER BY total DESC` |
| Qué regresa | `Series` con `tienda` de índice | `DataFrame`, sin índice | Una **relación** |

- El **índice** de pandas son etiquetas de fila guardadas aparte de las columnas. Polars no tiene: `tienda` es una columna más.
- B.2 comprueba que las tres dan el mismo orden y los mismos totales.

## La memoria es el eje estable

**📓 NOTEBOOK · b_tablas.ipynb · celda B.3**

B.3 corre la pregunta completa, leyendo el CSV, en un proceso nuevo por opción (`mide.py`). El **RSS** es la memoria que el sistema le dio al proceso entero; `htop` la muestra en RES. Por qué un proceso nuevo y por qué RSS y no `tracemalloc`: está en la celda.

`N = 1_000_000` · Intel i7-7700HQ (4 núcleos, 8 hilos) · 31 GB:

| Opción | Segundos | RSS pico (MB) | Base al importar (MB) |
|---|---:|---:|---:|
| pandas | 0.965 | 303.5 | 105.6 |
| Polars eager | 0.112 | 253.4 | 46.4 |
| Polars lazy | 0.071 | 146.1 | 46.5 |
| DuckDB | 0.227 | 104.4 | 54.1 |

- **Memoria: pandas > Polars eager > Polars lazy > DuckDB**, en todas las corridas, con 1 y con 10 millones de filas.
- **Tiempo, con `N = 1_000_000`: pandas es el último** (de 6× a 14×). Polars, lazy y DuckDB **casi empatan**: cambian de lugar entre corridas.
- Se compara el pico, no lo que sumó la consulta: pandas trae 105 MB sólo de importarse.

## Lazy: el plan antes que los datos

**Lazy** (`pl.scan_csv`) no lee nada: arma un **plan**, y `.collect()` lo optimiza y lo ejecuta. **Pushdown** es bajar un filtro o una selección de columnas hasta la lectura: lo que no sirve nunca llega a la memoria.

::: figure {#py-stack-lazy title="Eager hace cada paso; lazy arma un plan"}
![Dos columnas. Eager, a la izquierda: cuatro pasos en orden, leer todo con 5 columnas y N filas, filtrar cantidad mayor que 0, seleccionar 3 columnas y agrupar por tienda; junto a cada paso, la tabla que materializa en memoria. Lazy, a la derecha: un plan donde nada corre todavía; el filtro y la selección de 3 columnas bajan a la lectura, pushdown, que lee sólo esas columnas y esas filas; luego agrupar por tienda, y collect corre el plan una sola vez.](../_assets/py-stack-lazy.svg)
:::

**📓 NOTEBOOK · b_tablas.ipynb · celdas B.4–B.5**

¿Te perdiste? Corre B.0 y salta a la celda que vamos.

B.4 imprime el plan dos veces: `explain(optimized=False)` (como lo escribiste) y `explain()` (el que corre). Se leen de abajo hacia arriba. Cambian dos líneas:

| Sin optimizar | Optimizado | Qué significa |
|---|---|---|
| `PROJECT */5 COLUMNS` | `PROJECT 3/5 COLUMNS` | Lee sólo `tienda`, `cantidad` y `precio` |
| `FILTER col("cantidad") > 0`, un paso aparte | `SELECTION: col("cantidad") > 0`, dentro del `Csv SCAN` | Filtra al leer: las filas inválidas nunca entran |

- **Patrón: lazy optimiza.** Por eso lazy llegó a 146 MB y eager a 253 MB en B.3, con la misma librería.
- **B.5 · el error espera:** una columna mal escrita (`"cantidda"`) no truena al armar el plan, sino cuando algo lo necesita: `collect()`, `explain()` o mostrar el `LazyFrame` en el notebook. Sale `ColumnNotFoundError`, con las columnas válidas.
- **B.5 · dos motores:** `collect(engine="in-memory")` trabaja la tabla entera; `engine="streaming"` la trabaja por partes. **En Polars 2.0, `collect()` sin argumento usa streaming**; en 1.x usaba in-memory. Con un millón de filas casi empatan en tiempo.
- **B.5 · escribir sin juntar:** `sink_parquet(ruta)` ejecuta el plan y escribe a Parquet por partes, sin armar la tabla en memoria.

## El tipo decide la memoria

**📓 NOTEBOOK · b_tablas.ipynb · celdas B.6–B.7**

B.6 guarda la columna `tienda` (8 textos distintos en un millón de filas) con cinco tipos: de 1.0 MB con `Enum` a 57.5 MB con `object` de pandas. `Categorical` y `Enum` guardan cada texto una vez y, por fila, un número; `Enum` además fija la lista de antemano. `sys.getsizeof` mide sólo el objeto de Python (48 bytes), no los buffers en Rust a los que apunta.

B.7 pone un vacío en una columna de enteros:

| Entrada | pandas | Polars |
|---|---|---|
| `[3, None, 5]` | `3.0`, `NaN`, `5.0` · `float64` | `3`, `null`, `5` · `Int64` |
| `2**53 + 1` con un vacío al lado | `9007199254740992.0`: perdió una unidad | `9007199254740993` |
| `cantidad` del CSV (~1 % vacíos) | `float64` | `Int64` |

- **Patrón: el tipo decide la memoria, y la corrección.** En pandas, un solo vacío convierte la columna entera a `float64`; arriba de 2⁵³ un entero cambia sin error.
- Polars guarda junto a cada columna una máscara de validez (un bit por fila), y la columna sigue siendo de enteros.

## Compartir, no copiar

**📓 NOTEBOOK · b_tablas.ipynb · celdas B.8–B.9**

**Arrow** es un formato estándar para guardar tablas por columnas en memoria; Polars, DuckDB y PyArrow lo usan por dentro. Quien lo entiende lee los datos del otro sin convertirlos.

::: figure {#py-stack-arrow title="Compartir la memoria o copiarla"}
![Dos paneles. Compartir: Polars, DuckDB y pandas apuntan con una flecha cada uno al mismo bloque de memoria guardado por columnas, tienda, cantidad y precio, en formato Arrow; hay una sola copia. Copiar: un DataFrame de Polars pasa por to_pandas y aparece un segundo bloque, el DataFrame de pandas, con las mismas columnas; los datos quedan dos veces en memoria.](../_assets/py-stack-arrow.svg)
:::

- **B.8:** DuckDB consulta el `DataFrame` de Polars **por el nombre de la variable** (`FROM ventas`). La misma consulta sobre el `DataFrame` de pandas es de 5× a 8× más lenta, y pasar la tabla a pandas y de regreso, sin calcular nada, cuesta de 60 % a 95 % de lo que cuesta contestar la pregunta entera. **Patrón: compartir vs copiar.**
- **B.9:** Polars con todos sus hilos contra Polars con uno (`POLARS_MAX_THREADS=1`), mirando `htop`: ~2.7× con 8 CPU lógicas. El GIL de [[el-gil]] no lo frena: su trabajo corre en Rust. La celda dura ~20 s a propósito.

## Lo viejo que escribe la IA

**📓 NOTEBOOK · b_tablas.ipynb · celda B.10**

B.10 mide el código típico de una IA: pandas con `.apply(lambda fila: …, axis=1)`. Da el mismo resultado que la expresión de Polars y es cientos de veces más lento, con 100 000 filas.

| La IA escribe | Hoy | Por qué |
|---|---|---|
| pandas para todo | Polars; DuckDB si la pregunta es SQL | B.3: más memoria y más tiempo |
| `.apply(lambda fila: …, axis=1)` | Una expresión: `pl.col(...)`, `filter`, `when/then` | B.1 y B.10: un `for` escondido |
| `df.groupby`, `with_column`, `.apply` en Polars | `group_by`, `with_columns`, `map_elements` (y mejor, una expresión) | Nombres de antes de 1.0 (2024): en 2.0 dan `AttributeError` |
| `dtype=object` para texto | `str` en pandas 3.0; `String`, `Categorical` o `Enum` en Polars | B.6 |
| `.dict()`, `@validator` | `model_dump()`, `field_validator` | Pydantic v1; ver [[contratos]] |
| `List[int]`, `Optional[str]` | `list[int]`, `str \| None` | La sintaxis nueva existe desde Python 3.9 y 3.10 |
| `pip install` | `uv add` | [[ambientes-python]] |
| `os.path.join(...)` | `pathlib.Path` | Rutas como objetos, con `/` |
| Polars 1.x | **Polars 2.0, del 2026-10-06** | **Ninguna IA lo conoce todavía**: no sabe que `collect()` ya usa streaming |

Las demás librerías de tablas (PyArrow, Narwhals, Ibis, Dask, PySpark…) están en [[chuleta-del-stack]].

**Al revisar código de IA, busca:**

- `.apply(lambda fila:` o `for _, fila in df.iterrows()`: un `for` de Python sobre la tabla.
- `pl.read_csv(...)` seguido de un `.filter(...)` o un `.select(...)`: lee todo para quedarse con una parte; con `scan_csv` el filtro baja a la lectura.

**Al pedírselo a la IA, dile:**

- «Usa Polars 2.0 con `scan_csv` y expresiones; nada de `.apply` ni `map_elements`.»
- «Muéstrame `explain()` del plan y dime qué se hace al leer.»

::: problem {#py-stack-lazy-lee-todo title="Un CSV de 8 GB en una laptop de 16"}
Un script de la IA hace `pl.read_csv("ventas.csv")`, luego `.filter(pl.col("anio") == 2025)` y `.select("tienda", "total")`. El CSV pesa 8 GB y la laptop se queda sin memoria. ¿Qué miras antes de pedir una máquina más grande?
:::

::: hint {of="py-stack-lazy-lee-todo"}
¿Qué cambiaba entre `explain(optimized=False)` y `explain()` en B.4, y quién podía hacer ese cambio?
:::

::: answer {of="py-stack-lazy-lee-todo"}
- `read_csv` es eager: lee las columnas y filas completas antes de filtrar.
- Con lazy, el filtro y la selección bajan a la lectura (pushdown): sólo entran `tienda`, `total` y las filas de 2025.
- Arreglo: `pl.scan_csv(...)` con la misma cadena y `.collect()` al final (streaming por omisión en Polars 2.0), o `.sink_parquet(...)` si el resultado tampoco cabe.
:::

Sigue con [[archivos-y-memoria]]: el CSV de esta página ocupa 32 MB y el mismo millón de filas en Parquet ocupa 6; la siguiente pregunta es cómo se guarda.

> [!NOTE]
> **Si sólo recuerdas una cosa:** pide el trabajo en expresiones, no en ciclos, y deja que el motor vea el plan entero.
