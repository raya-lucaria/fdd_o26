---
id: archivos-y-memoria
title: "Archivos y memoria"
nav_title: "Archivos y memoria"
summary: "Cómo se guarda una tabla y cuánto ocupa: Parquet guarda por columnas y conserva tipos, un formato de texto los pierde, cargar un pickle ejecuta código, y un generador recorre un archivo sin cargarlo entero."
status: ready
estimated_time: 15m
tags: [parquet, csv, pickle, formatos, generador, memoria]
prerequisites: [motores-de-tablas]
---

# Archivos y memoria

**Página 3 de 4 · Elegir el stack**

Meta: elegir el formato de un archivo de datos por lo que mide en tu máquina, y recorrer un archivo grande sin cargarlo entero.

**📄 PÁGINA · Archivos y memoria**

## En corto

- **Parquet guarda por columnas y conserva los tipos**: ocupa varias veces menos que el CSV y la fecha vuelve como fecha.
- **Un formato de texto pierde los tipos**: quien lee un CSV adivina, y Polars y pandas adivinan distinto.
- **Cargar un pickle ejecuta código**: abre sólo pickles tuyos.

## Tres formatos de cerca

| | CSV | Parquet | pickle |
|---|---|---|---|
| Qué es | Texto, una fila por línea | Binario, por columnas, comprimido | El formato de Python para guardar cualquier objeto |
| ¿Guarda tipos? | No: el lector adivina | Sí | Sí |
| ¿Lee sólo unas columnas? | No: recorre cada línea | Sí | No: carga el objeto entero |
| Lo leen | Todo (Excel, R, una persona) | Polars, DuckDB, pandas, Spark, R | Sólo Python |
| Al cargarlo | Lee texto | Lee datos | **Puede ejecutar cualquier función** |
| Úsalo para | Mostrar o mandar algo chico a quien no programa | Guardar y compartir tablas | Nada que venga de otra persona |

Las demás opciones (NDJSON, Feather, Avro, Delta, Iceberg) están en [[chuleta-del-stack]].

## Parquet ocupa menos y la fecha vuelve como fecha

**📓 NOTEBOOK · c_archivos.ipynb · celdas C.0–C.2**

¿Te perdiste? Corre C.0 y salta a la celda que vamos.

C.1 escribe la misma tabla en seis formatos dentro de `datos/`, la relee entera y con sólo 2 columnas, y compara el `schema` que vuelve con el original. El `schema` es el nombre y el tipo de cada columna.

`N = 1_000_000` · Intel i7-7700HQ (4 núcleos, 8 hilos) · 31 GB. Tus números serán otros; lo que se mantiene es el patrón.

| formato | MB | escribir_s | leer_todo_s | leer_2_columnas_s | tipos_intactos |
|---|---:|---:|---:|---:|---|
| Parquet zstd | 6.0 | 0.067 | 0.011 | 0.008 | ✅ |
| Parquet snappy | 7.6 | 0.056 | 0.009 | 0.007 | ✅ |
| CSV | 32.4 | 0.138 | 0.067 | 0.043 | ❌ |
| Feather | 52.1 | 0.127 | 0.011 | 0.008 | ✅ |
| pickle | 52.1 | 0.238 | 0.081 | 0.078 | ✅ |
| NDJSON | 88.5 | 0.357 | 0.233 | 0.187 | ❌ |

NDJSON: un JSON por línea. Feather: Arrow escrito tal cual. snappy y zstd: dos compresiones de Parquet; zstd comprime más.

- **Columnas + compresión**: Parquet zstd ocupa ~5 veces menos que el CSV y ~15 veces menos que NDJSON. Ese orden se repite en cada corrida.
- Parquet y Feather leen 6–8 veces más rápido que el CSV; entre ellos **casi empatan** (su orden cambia entre corridas).
- Leer 2 columnas sólo se nota con más filas: con `N = 10_000_000`, Parquet zstd baja de 0.165 a 0.099 s y pickle no baja (0.847 → 0.907 s).
- **pickle sale bien aquí.** Su problema no es la velocidad: es C.4.

C.2 hace el viaje con dos filas: una fecha y una cantidad con un vacío.

| Se relee con | `fecha` | `cantidad` |
|---|---|---|
| CSV · Polars | `String` ❌ | `Int64` |
| CSV · pandas | `str` ❌ | `float64` ❌ |
| Parquet · Polars | `Date` | `Int64` |
| Parquet · pandas | `object` (objetos `date`) | `float64` |

- **El CSV pierde la fecha con los dos lectores.** pandas además vuelve `float64` un entero con vacío (B.7).
- Parquet llega intacto a Polars; con pandas los cambios son de pandas, que no tiene esos tipos por omisión.

**Patrón · fila vs columna:** guardar una tabla columna por columna permite comprimir cada columna y leer sólo las que pides.

## `with` cierra el archivo aunque haya un error

**📓 NOTEBOOK · c_archivos.ipynb · celda C.3**

`with open(ruta, "w", encoding="utf-8") as f:` abre el archivo y lo nombra `f`; al salir del bloque, por el final o **por un error**, Python lo cierra. Cerrar es lo que garantiza que lo escrito llegó al disco.

En C.3 un `raise` a la mitad del bloque provoca un error, y aun así `f.closed` da `True` y la línea está en el archivo.

## Cargar un pickle ejecuta código

**📓 NOTEBOOK · c_archivos.ipynb · celda C.4**

`__reduce__` es el método que pickle llama al guardar un objeto para saber cómo reconstruirlo: regresa una función y sus argumentos. Al cargar, `pickle.loads` **llama a esa función**.

En C.4 la función es `print`, a propósito inofensiva. Al cargar aparece `Esto lo ejecutó pickle.loads, no tu código.` sin que ninguna línea lo imprima.

- Un pickle ajeno puede traer `os.system` con cualquier comando, y corre **antes** de que veas los datos.
- Pasa igual con todo lo que usa pickle por dentro, como `pd.read_pickle`.

## Un generador recorre el archivo sin cargarlo

**📓 NOTEBOOK · c_archivos.ipynb · celda C.5**

Un **generador** es una función con `yield`: entrega un valor, se pausa y sigue cuando le piden el siguiente. En memoria vive un valor a la vez.

::: figure {#py-stack-generador title="Todo a la vez o uno a la vez"}
![Dos carriles. Arriba, lista: la comprehension convierte las doce líneas del archivo antes de que sum empiece, y la memoria crece con el archivo. Abajo, generador: yield entrega un precio, sum lo suma y pide el siguiente, mientras el resto sigue en el archivo; la memoria queda fija.](../_assets/py-stack-generador.svg)
:::

C.5 suma la columna `precio` de tres maneras. Primero con `N_FILAS = 200_000` dentro del kernel; luego el archivo entero, una opción por proceso con `mide.py`. El **RSS** es la memoria que el sistema le dio al proceso entero; `delta_mb`, lo que sumó la tarea.

| Opción | segundos (`N_FILAS`) | pico `tracemalloc` MB | segundos (`N`) | `delta_mb` (`N`) | `delta_mb` (10 millones) |
|---|---:|---:|---:|---:|---:|
| lista | 0.106 | 16.83 | 0.462 | 93.9 | 937.7 |
| generador | 0.098 | 0.17 | 0.389 | 0.1 | 0.1 |
| `scan` de Polars | — | — | 0.043 | 77.2 | 506.4 |

- **La memoria de la lista crece con el archivo; la del generador, no.** En tiempo, lista y generador casi empatan.
- **`scan` es ~10 veces más rápido, pero no es «uno a la vez»**: lee bloques grandes en varios hilos y su memoria también crece.

**Patrón · todo a la vez vs uno a la vez:** si el archivo no cabe en memoria, recórrelo por partes.

**Al revisar código de IA, busca:**

- `pickle.load(` o `pd.read_pickle(` sobre un archivo que llegó de otra persona o de internet.
- `f.readlines()` sobre un archivo grande, o `df.to_csv(` para guardar una tabla que tu programa vuelve a leer.

**Al pedírselo a la IA, dile:**

- «Guarda las tablas en Parquet, no en CSV ni pickle; al releer, comprueba el `schema`».
- «Recorre el archivo con un generador o con `pl.scan_csv`; no lo cargues entero».

::: problem {#py-stack-pickle title="La tabla que manda un compañero"}
Un compañero te manda `ventas_limpias.pkl` por correo, y la IA te propone abrirlo con `df = pd.read_pickle("ventas_limpias.pkl")`. Quieres la tabla con sus fechas como fechas. ¿Qué riesgo corres al correr esa línea y qué formato le pides en su lugar?
:::

::: hint {of="py-stack-pickle"}
En C.4, ¿en qué momento apareció el mensaje: al guardar, al cargar o al usar el objeto?
:::

::: answer {of="py-stack-pickle"}
- `pd.read_pickle` usa pickle: al cargar, llama a la función que el archivo nombre. El código corre antes de que veas un solo dato.
- Que venga de alguien conocido no basta: el archivo pudo cambiar en el camino o en su máquina.
- Arreglo: pídele la tabla en Parquet (`df.write_parquet(...)`): guarda datos y tipos, no instrucciones, y la fecha vuelve como `Date`.
:::

Sigue con [[patrones-del-stack]]: junta los patrones de las tres carreras en preguntas para revisar código.

> [!NOTE]
> **Si sólo recuerdas una cosa:** guarda tablas en Parquet y abre sólo pickles tuyos.
