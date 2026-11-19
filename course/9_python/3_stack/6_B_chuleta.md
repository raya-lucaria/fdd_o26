---
id: chuleta-del-stack
title: "Chuleta del stack"
nav_title: "B. Chuleta del stack"
summary: "Todas las tecnologías de la sección en tablas: ★ las que se usan con código en clase, ○ las que sólo hay que saber que existen. Librerías y formatos por separado, y quién lee qué."
status: ready
estimated_time: 10m
tags: [cheatsheet, stack, polars, duckdb, pydantic, parquet, formatos]
prerequisites: [elegir-el-stack]
---

# Chuleta del stack

**Anexo B** · para tener abierto

★ = se usa con código en clase. ○ = sólo saber que existe, para reconocerlo en código ajeno o cuando la IA lo proponga. Versiones de referencia: las de `uv.lock` (polars 2.0.0, duckdb 1.5.6, pyarrow 25.0.1, pandas 3.0.6, pydantic 2.14.0).

**Una librería** es código que importas (`import polars`). **Un formato** es la forma en que los bytes quedan en un archivo (`.parquet`). Por eso van en tablas separadas: una librería lee varios formatos, y un formato lo leen varias librerías.

## La forma de un dato

| | Qué es | ¿Valida al correr? | ¿Lo revisa el editor o mypy? | Cuándo |
|---|---|---|---|---|
| ★ `dict` | Llaves y valores, sin forma fija | No | No | Un dato suelto, de paso |
| ★ `NamedTuple` | Tupla con nombres de campo; no se puede cambiar | No | Sí | Un registro chico que no cambia |
| ★ `TypedDict` | Un `dict` con llaves y tipos declarados: es un type hint, no una clase nueva | No | Sí | Describir un `dict` que ya existe (un JSON) |
| ★ `dataclass` | Clase cuyo `__init__` escribe el decorador `@dataclass` | No | Sí | Datos adentro de tu programa, ya validados |
| ○ attrs | La librería de la que salió `dataclass`; con validadores opcionales | Si los declaras | Sí | Código que ya la usa |
| ★ Pydantic v2 | Modelo que convierte y valida cada campo, con el núcleo en Rust | **Sí** | Sí, con su plugin de mypy | La frontera: CSV, API, configuración |
| ○ msgspec | Estructuras y lectura de JSON/MessagePack con validación, muy rápidas | Sí | Sí | Mucho JSON por segundo |
| ○ marshmallow | Esquemas que validan y serializan `dict`, sin type hints | Sí | No | Proyectos viejos (Flask) |
| ○ Pandera | Esquemas para **tablas** enteras (pandas, Polars): tipos y reglas por columna | Sí | Parcial | Validar un DataFrame, no una fila |

## Revisores de tipos

Un revisor de tipos lee tus type hints **sin correr** el código y marca dónde no cuadran.

| | Qué es | Estado |
|---|---|---|
| ★ mypy | El revisor de referencia, en Python; tiene plugin para Pydantic | El más usado: 58 % en la encuesta de tipado de Python de 2025 |
| ★ Pyright / Pylance | Pyright es de Microsoft; Pylance es la extensión de VS Code que lo usa | El que subraya en rojo en tu editor |
| ○ basedpyright | Pyright con reglas extra y funciones que en VS Code sólo trae Pylance | Para editores que no son VS Code |
| ○ ty | De Astral (los de uv y ruff), en Rust | En beta en 2026 |
| ○ Pyrefly | De Meta, en Rust | Nuevo (2025) |
| ○ Zuban | En Rust, con un modo compatible con mypy | Nuevo (2025) |

## Motores de tablas (librerías)

| | Qué es | Cuándo |
|---|---|---|
| ★ Polars | DataFrames en Rust; expresiones por columna, modo lazy, todos los núcleos. 2.0 salió el 2026-10-06 | La opción por omisión para tablas en Python |
| ★ DuckDB | Base de datos SQL que corre dentro de tu proceso, sin servidor; lee archivos directo | Cuando lo natural es SQL, o los datos no caben en RAM |
| ★ pandas 3.0 | El DataFrame clásico; 3.0 salió en enero de 2026 (texto como `str` por omisión) | Leer código ajeno y comparar; el que más vio la IA |
| ★ PyArrow | La librería de Arrow en Python: el formato en memoria por columnas que comparten Polars, DuckDB y pandas | Por debajo de las otras; para pasar datos sin copiar |
| ○ Narwhals | Una sola API que corre sobre pandas, Polars y otros | Escribir una librería que acepte cualquier DataFrame |
| ○ Ibis | Escribes en Python y lo traduce a SQL de muchos motores (DuckDB, BigQuery, Postgres…) | El mismo código contra varias bases |
| ○ DataFusion | Motor SQL de Apache, en Rust, sobre Arrow | Construir tu propio motor o servicio |
| ○ SQLite | Base de datos en un archivo; viene con Python (`sqlite3`) | Datos chicos que cambian fila por fila |
| ○ Dask / Modin | Reparten código de pandas en varios núcleos o máquinas | Código pandas existente que ya no cabe |
| ○ PySpark | Spark desde Python: un clúster de máquinas | Datos que no caben en una máquina |
| ○ cuDF | DataFrames en la GPU de NVIDIA, con API de pandas | Hay GPU NVIDIA y mucho dato |

## Formatos de archivo (formatos)

| | Qué guarda | ¿Conserva tipos? | Cuándo |
|---|---|---|---|
| ★ CSV | Texto, una fila por línea, separado por comas | **No**: todo es texto; la fecha y el vacío se adivinan al leer | Intercambio con humanos y con Excel |
| ★ JSON / JSONL | Texto con llaves; JSONL (o NDJSON) es un objeto JSON por línea | Parcial: no hay fecha | APIs; logs (JSONL) |
| ○ Excel (`.xlsx`) | Hojas de cálculo, en XML comprimido | Parcial | Lo que te manda otra área |
| ★ Parquet | Binario por columnas, comprimido (snappy, zstd), con esquema | **Sí** | Guardar tablas para análisis |
| ★ Arrow IPC / Feather | El formato en memoria de Arrow, escrito tal cual a disco | Sí | Pasar una tabla entre procesos rápido |
| ○ Avro | Binario por filas, con esquema | Sí | Mensajes (Kafka) |
| ○ ORC | Binario por columnas, como Parquet | Sí | Ecosistema Hadoop / Hive |
| ★ pickle | Objetos de Python serializados | Sí | **Sólo** tus propios archivos: cargar un pickle ejecuta código |

**Formatos de tabla** (encima de archivos Parquet: guardan versiones, cambios y esquema en archivos de metadatos):

| | Qué agrega | Cuándo |
|---|---|---|
| ○ Delta Lake | Transacciones, versiones («cómo estaba ayer») y borrado de filas sobre Parquet; nació en Databricks | Un datalake que se actualiza |
| ○ Apache Iceberg | Lo mismo, como estándar abierto de Apache; lo leen Spark, Trino, Snowflake, DuckDB | Un datalake que leen varios motores |

## Librería y formato a la vez

Algunos nombres son las dos cosas. Al leer código, distingue cuál de las dos es.

| Nombre | Como formato | Como librería de Python |
|---|---|---|
| Arrow | Arrow IPC / Feather (`.arrow`, `.feather`) | `pyarrow` |
| SQLite | El archivo `.db` / `.sqlite` | `sqlite3`, de la biblioteca estándar |
| DuckDB | El archivo `.duckdb` (una base entera) | `duckdb` |
| Delta | Delta Lake (carpeta con Parquet y `_delta_log/`) | `deltalake` |
| Iceberg | Apache Iceberg (Parquet + metadatos) | `pyiceberg` |
| pickle | El archivo `.pkl` | `pickle`, de la biblioteca estándar |
| JSON | El archivo `.json` / `.jsonl` | `json` (estándar) y `orjson` (más rápido, en Rust) |

## Quién lee qué

Probado en `.venv-stack` con las versiones de `uv.lock`. ✅ = lo lee con lo que ya instalaste. «con X» = necesita instalar X (`uv add X`). Una «extensión» de DuckDB se descarga sola la primera vez que la usas (pide red). ❌ = no lo lee directo.

| Formato | Polars | DuckDB | pandas | PyArrow |
|---|---|---|---|---|
| CSV | ✅ `read_csv`, `scan_csv` | ✅ `read_csv` | ✅ `read_csv` | ✅ `pyarrow.csv` |
| JSON (un arreglo) | ✅ `read_json` | ✅ `read_json` | ✅ `read_json` | ❌ |
| JSONL | ✅ `read_ndjson`, `scan_ndjson` | ✅ `read_json` | ✅ `read_json(lines=True)` | ✅ `pyarrow.json` |
| Excel | con `fastexcel` | extensión `excel` (`read_xlsx`) | con `openpyxl` | ❌ |
| Parquet | ✅ `read_parquet`, `scan_parquet` | ✅ | ✅ `read_parquet` (usa PyArrow) | ✅ `pyarrow.parquet` |
| Arrow IPC / Feather | ✅ `read_ipc`, `scan_ipc` | ❌ | ✅ `read_feather` | ✅ `pyarrow.feather` |
| Avro | ✅ `read_avro` | extensión `avro` | ❌ | ❌ |
| ORC | ❌ | ❌ | ✅ `read_orc` (usa PyArrow) | ✅ `pyarrow.orc` |
| pickle | ❌ | ❌ | ✅ `read_pickle` | ❌ |
| SQLite | ✅ `read_database` con una conexión de `sqlite3` | extensión `sqlite` (`sqlite_scan`) | ✅ `read_sql` con una conexión de `sqlite3` | ❌ |
| Delta Lake | con `deltalake` (`read_delta`, `scan_delta`) | extensión `delta` | ❌ | ❌ |
| Iceberg | con `pyiceberg` (`scan_iceberg`) | extensión `iceberg` | con `pyiceberg` (`read_iceberg`) | ❌ |

- Polars `read_database_uri` (con una URL `sqlite://…`) pide además `connectorx`; con una conexión de `sqlite3` no.
- «❌» en PyArrow para Delta e Iceberg: sus librerías (`deltalake`, `pyiceberg`) **regresan** tablas de Arrow.

## Herramientas del proyecto

| ★ El del curso | ○ Lo que reemplaza o compite | Qué hace |
|---|---|---|
| ★ `ruff check` | flake8, pylint, pycodestyle; isort (la regla `I`) | Encuentra errores y malas prácticas sin correr el código; con `I`, el orden de los imports |
| ★ `ruff format` | black | Da formato al código (espacios, comillas, saltos de línea) |
| ★ pytest | unittest (biblioteca estándar) | Corre pruebas: funciones `test_…` con `assert` |
| ○ pre-commit / prek | — | Corre ruff, mypy y otros antes de cada `git commit`; prek es la reimplementación en Rust de pre-commit |
| ○ `logging` (estándar) | `print`, loguru, structlog | Mensajes con nivel (INFO, ERROR) y hora, que se pueden apagar o mandar a un archivo; structlog los da como JSON |
| ○ `.env` + pydantic-settings | `os.environ` a mano | Lee la configuración (llaves, rutas) del ambiente y la valida con Pydantic |
| ★ `pathlib` | `os.path` | Rutas como objetos: `Path("datos") / "ventas.csv"`; `os.path` es lo viejo que escribe la IA |

Pydantic 2.14 salió en octubre de 2026; la API de v2 es la misma desde 2023. Lo que ves con `.dict()` o `@validator` es v1 ([[contratos]]).

> [!NOTE]
> **Si sólo recuerdas una cosa:** antes de aceptar una librería o un formato que propone la IA, búscalo en estas tablas; si es ○, pregunta por qué no la ★.
