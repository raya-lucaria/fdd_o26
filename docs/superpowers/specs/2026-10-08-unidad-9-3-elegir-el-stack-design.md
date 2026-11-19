# Unidad 9 · Python — sección 9.3 Elegir el stack (diseño)

Fecha: 2026-10-08 · Estado: **aprobado en conversación; revisado por dos
agentes adversariales (pedagogía/ADHD y técnico, con versiones reales); spec
para revisión del profesor**

## 1 · Qué es y para quién

Tercera sección de la unidad **9 · Python** (`course/9_python/3_stack/`).
Se da **hoy, jueves 2026-10-08, 19:00–20:30** (`session-15`).

- **Público:** hicieron *Introduction to Python for Developers* y
  *Intermediate Python for Developers* (funciones, docstrings de sintaxis,
  `lambda`, módulos, `try/except`/`raise`, leer con pandas) y la 9.2
  (intérprete, bytecode, nombres y objetos, GIL). **Nunca vieron clases, tipos
  revisados, pruebas, Polars ni formatos.**
- **El ángulo:** escribir código ya es barato; lo caro es **decidir** el stack.
  La IA, si no se lo dices, elige **lo que más vio, que suele ser lo viejo**.
  Ejemplo vivo: **Polars 2.0 salió el 2026-10-06**; ninguna IA lo conoce.
- **Comparar es el centro.** Cada bloque es una **carrera**: las mismas
  opciones, la misma tarea, números reales en su máquina, en varios ejes
  (tiempo, memoria, corrección, notación). De cada carrera sale un **patrón**.
- **Foco con código:** Polars (con **lazy**), DuckDB, Pydantic v2,
  `dataclass`/`TypedDict`. pandas sólo para comparar y leer código ajeno. El
  resto, **sólo en tablas** (anexo «Chuleta del stack»).
- **El profesor elige en clase** qué corre y qué salta; lo demás lo leen. No
  hay presupuesto de minutos en las páginas ni celdas «de casa».
- **Fuera:** `async`/`await`, decoradores a fondo (sólo «la `@` modifica lo de
  abajo»), LLM desde código, metaclases, `match`.

## 2 · El contrato de escritura

Es el de la 9.2 (spec en la branch local `unidad-9-por-dentro`, commit
`142e153` en adelante, § 2), con estos cambios.

### 2.1 · Página compacta, notebook denso

| | **Página** | **Notebook** | **`.py`** |
|---|---|---|---|
| Para qué | El mapa: concepto, tabla «de cerca», diagrama, resultados y patrón | El taller: la carrera con su explicación densa | Lo que lee una herramienta como archivo, o lo que se mide en un proceso limpio |
| Forma | En corto (≤ 3 bullets), tablas, párrafos ≤ 3 líneas | Markdown denso arriba de cada celda, el código **ya escrito**, «Deberías ver» | Corto y comentado |

- **Notebooks escritos a mano** (no generados de las páginas).
- Las páginas **no repiten el código**: nombran la celda, dicen qué compara,
  muestran la tabla de resultados de referencia y el patrón.
- Las tablas de tecnologías ○ (sólo para saber que existen) viven en el
  **anexo B · Chuleta del stack**; cada página lo enlaza en una línea.
- Cada concepto nuevo se define **en una línea donde aparece** (RSS,
  *pushdown*, relación de DuckDB, `NamedTuple`, `slots`, herencia en
  `class B(A)`, `@dataclass`).

### 2.2 · Las marcas de cambio de lugar

En la página y en el notebook, en su propia línea:

| Marca | Dónde | Qué haces |
|---|---|---|
| `**📄 PÁGINA · <título>**` | El sitio | Lees concepto y tabla |
| `**📓 NOTEBOOK · <archivo> · celdas X.n–X.m**` + debajo «¿Te perdiste? Corre X.0 y salta a la celda que vamos» | VS Code | Corres en orden y comparas con «Deberías ver» |
| `**💻 TERMINAL · en stack/ (comprueba con pwd)**` | Terminal de la ventana de `stack/` | Un comando sobre un `.py` |

Cada notebook termina con una celda: `**📄 Regresa a la página <título>.**
Antes, *Restart* o *Shutdown* de este kernel: libera la memoria para el
siguiente notebook.`

### 2.3 · El tamaño elegible y la celda de preparación

Cada notebook empieza con **X.0, la celda de preparación**: idempotente
(correrla dos veces da lo mismo), importa, define `N`, genera o reusa los
datos y deja lista cualquier celda siguiente. Así el profesor puede saltar a
cualquier celda.

```python
# Elige el tamaño según tu máquina: deja UNA línea sin #.
N = 1_000_000        # por defecto: cualquier laptop
# N = 100_000        # 8 GB de RAM o menos, o si una celda tarda más de 30 s
# N = 10_000_000     # 16 GB o más; ocupa ~2 GB en disco en datos/
```

- X.0 imprime la RAM de la máquina (`os.sysconf`) y **la recomendación**
  («tienes 8 GB → te recomendamos `N = 100_000`»), sin cambiar `N` sola.
- **Las carreras de objetos Python** (A.8, A.9, el `for` y la comprehension de
  B.1, la lista de C.5) usan `N_FILAS = min(N, 200_000)`, y lo dicen.
  **`.apply` de pandas** se mide una vez sobre `min(N, 100_000)` y se
  extrapola, diciéndolo. Ninguna celda usa `%timeit` sobre algo lento.
- Con `N = 1_000_000` ninguna celda pasa de ~15 s ni de ~1 GB en la máquina
  de referencia.

### 2.4 · Cómo se mide

**En la página 0 sólo dos filas** (se dice mientras instala):

| Eje | Regla |
|---|---|
| Tiempo | Repite y quédate con el mejor; compara **cuántas veces más lento**, no segundos |
| Memoria | Hay dos: la que ve Python (`tracemalloc`) y la del proceso entero (RSS: la que el sistema le dio al proceso; `htop` la muestra en RES) |

**Cada trampa se dice en la celda donde aparece:**

| Trampa | Celda |
|---|---|
| `tracemalloc` hace todo 2–5× más lento: tiempo y memoria se miden en **pasadas separadas** | A.8 |
| `tracemalloc` no ve lo que Polars o DuckDB reservan en Rust/C++: por eso `mide.py` mide RSS en un proceso nuevo | B.3 |
| El pico de RSS se acumula en un proceso: uno nuevo por opción | B.3 |
| El `import` cuesta: `mide.py` arranca el reloj **después** del import y reporta RSS base y delta | B.3 |
| `sys.getsizeof` cuenta la cáscara, no el contenido | B.6 |
| Con datos chicos domina lo fijo: los motores empatan | B.3 |

- **`cronometra(fn, veces=3)`** (en `datos.py`) devuelve el mejor tiempo; cada
  carrera arma una tabla de Polars con `segundos` y `veces_vs_mejor`.
- **`mide.py`** se llama así, siempre:
  `subprocess.run([sys.executable, "mide.py", escenario, str(N)], capture_output=True, text=True)`.
  `sys.executable` es el Python de tu `.venv`, el de A.0. Fija
  `POLARS_MAX_THREADS` **antes** de importar Polars cuando el escenario lo pide.
- **`ru_maxrss`**: KB en Linux, bytes en macOS; `mide.py` lo normaliza.
  Windows nativo no tiene `resource`: el curso usa Linux, macOS o WSL, y
  `mide.py` lo dice si falta.

### 2.5 · Lo que se afirma de cada carrera

Medido por el revisor técnico (8 núcleos, 31 GB, versiones del § 3):

| Carrera | Estable (se afirma) | Inestable (se dice «casi empatan») |
|---|---|---|
| Motores, memoria | pandas > Polars eager > Polars lazy > DuckDB (1M y 10M) | — |
| Motores, tiempo | pandas último | Polars, lazy y DuckDB entre sí; todo a 100k |
| Escalera B.1 | Intérprete vs fuera del intérprete: **dos órdenes de magnitud** | NumPy vs Polars; `for` vs comprehension |
| Formatos C.1 | Parquet zstd < snappy < CSV < NDJSON; CSV y NDJSON pierden la fecha | — |

- La referencia se mide además con `POLARS_MAX_THREADS=4` (laptop modesta);
  sólo se afirma orden donde la brecha es ≥ 3× en las dos.
- Cada «Deberías ver» dice `N`, la máquina y: **tus números serán otros; lo
  que se mantiene es el patrón**.

## 3 · Decisiones tomadas

| Decisión | Valor |
|---|---|
| Sesión | `session-15`, jueves 2026-10-08, 19:00–20:30 |
| Ruta / id | `course/9_python/3_stack/` / `elegir-el-stack` |
| Python | 3.14; `requires-python = ">=3.14"` (el lock queda más chico) |
| Carpeta / branch | `estudiantes/<login>/09_python/stack/` / `tarea-09-stack` |
| Instalación | **En clase, al inicio**: merge de `upstream/main`, copia, commit, `uv sync` (§ 5) |
| Librerías | polars `>=2.0,<3`, duckdb, pyarrow, pydantic `>=2.14,<3`, pandas `>=3`, numpy; dev: ruff, mypy, pytest, ipykernel |
| Versiones de referencia | polars 2.0.0, duckdb 1.5.6, pyarrow 25.0.1, pydantic 2.14.0, pandas 3.0.6, numpy 2.5.3, mypy 2.4.0, ruff 0.16.10, pytest 9.1.1 |
| ruff | `select = ["E", "F", "I", "UP", "B"]` explícito (ruff 0.16 cambió los defaults) |
| Revisor de tipos | **mypy** con `pydantic.mypy`; Pylance en el editor; ty y otros en la chuleta |
| Descarga de `uv sync` | **~195 MB** (53 paquetes); `.venv` ~670 MB en disco |
| Tarea | DataCamp *Software Engineering Principles in Python*, **capítulos 3 y 4** + práctica (§ 8) |
| Abre / vence | 2026-10-08 / 2026-10-15 |
| Vale / tarde / IA | 20 / `"1/dia"` / `permitida-revisada` |
| Prefijo de figuras | `py-stack-*` |

## 4 · Las páginas

| # | Archivo | Id | Qué deja | Notebook |
|---:|---|---|---|---|
| 0 | `0_index.md` | `elegir-el-stack` | Ritual, chuleta de marcas, cómo medir (2 filas), mapa del stack | — |
| 1 | `1_contratos.md` | `contratos` | Quién revisa un dato y cuándo; cuánto cuesta una garantía | `a_contratos.ipynb` |
| 2 | `2_tablas.md` | `motores-de-tablas` | Dónde se hace el trabajo; lazy; el tipo decide la memoria | `b_tablas.ipynb` |
| 3 | `3_archivos.md` | `archivos-y-memoria` | Cómo se guarda y cuánto ocupa | `c_archivos.ipynb` |
| 4 | `4_patrones.md` | `patrones-del-stack` | Los 8 patrones, cómo elegir una librería, `AGENTS.md` | — |
| A | `5_A_entregas.md` | `entregas-stack` | Tablero de la tarea | — |
| B | `6_B_chuleta.md` | `chuleta-del-stack` | Todas las tablas de tecnologías ★ y ○ | — |

### 4.0 · Página 0

- **En corto:** escribir es barato, decidir es caro · la IA elige lo viejo (Polars 2.0 tiene dos días) · hoy comparamos midiendo.
- **El ritual** (§ 5) primero: `uv sync` descarga mientras se explica lo demás.
- **Chuleta de una pantalla:** marca → dónde → qué haces → cómo sé que estoy
  bien (`pwd` termina en `09_python/stack`; arriba a la derecha del notebook
  dice `.venv`).
- **Cómo medir**, las dos filas del § 2.4.
- **Figura `py-stack-mapa`:** proyecto (uv, ruff, pytest) → contratos (tipos,
  Pydantic) → motor (Polars, DuckDB) → formato (Parquet).

### 4.1 · Página 1 · Contratos

- **En corto:** Python guarda las anotaciones y no las revisa · `TypedDict`,
  `dataclass` y Pydantic difieren en **quién revisa y cuándo** · valida en la
  frontera, confía adentro.
- **`TypedDict` no compite con los type hints: es uno.**
- Tabla de cerca: `TypedDict` · `dataclass` · Pydantic v2 (el dato es, ¿valida
  al correr?, ¿lo revisa el editor?, costo, para qué).
- **Figura `py-stack-frontera`:** afuera (CSV, API) → Pydantic → adentro
  (`dataclass`) → tu código confía.
- Tabla «**DataCamp enseña vs hoy**»: `pip` → `uv add`; `requirements.txt` +
  `setup.py` → `pyproject.toml` + `uv.lock`; `pycodestyle` → `ruff check`;
  docstrings reST/Sphinx → estilo Google + MkDocs; doctest y pytest → **igual
  hoy** (verificar contra el capítulo 4 antes de publicar).
- Resultados de A.8 y A.9 y sus patrones.

### 4.2 · Página 2 · Motores de tablas

- **En corto:** el trabajo fuera del intérprete es rápido · lazy deja que el
  motor optimice · el tipo decide la memoria.
- Tabla de cerca Polars · DuckDB · pandas (escribes, evalúa, núcleos, más que
  la RAM, vacíos, desde).
- Tabla de **notación** (filtrar, columna nueva, agrupar, ordenar, qué
  regresa), con código en línea corto; nunca bloques dentro de celdas.
- **Figuras** `py-stack-lazy` (justo antes de la marca de B.4) y
  `py-stack-arrow`.
- Tabla **«lo viejo que escribe la IA»** (pandas para todo, `.apply`, nombres
  de Polars de antes de 1.0, Pydantic v1, `List[int]`/`Optional`, `pip`,
  `os.path`, y «no conoce Polars 2.0»).
- Resultados de B.1, B.3, B.4 y B.7.

### 4.3 · Página 3 · Archivos y memoria

- **En corto:** Parquet guarda por columnas y conserva tipos · un formato de
  texto pierde tipos · cargar un pickle ejecuta código.
- Tabla de cerca CSV · Parquet · pickle; **figura `py-stack-generador`**.
- Resultados de C.1 y C.5.

### 4.4 · Página 4 · Patrones y el stack escrito

| Patrón | Celdas | Pregunta al revisar |
|---|---|---|
| Fuera del intérprete es rápido | B.1, A.8 (`model_construct`) | ¿Hay un `for` o un `.apply` donde cabe una expresión? |
| Fila vs columna | A.9, C.1 | ¿Valida o guarda por fila algo que es una tabla? |
| Lazy optimiza | B.4, B.5 | ¿Lee todo para quedarse con una parte? |
| El tipo decide la memoria | B.6, B.7 | ¿Textos como `object`? ¿Enteros vueltos `float`? |
| Compartir vs copiar | B.8 | ¿Convierte entre librerías sin necesidad? |
| Más garantías, más costo | A.8 | ¿Valida adentro lo que ya validó en la frontera? |
| Todo a la vez vs uno a la vez | C.5 | ¿Carga el archivo entero para recorrerlo? |
| Medir, no adivinar | todas | ¿Afirma «es más rápido» sin un número? |

- **Cómo elegir una librería, 5 preguntas:** ¿lo hace la biblioteca estándar?
  ¿release en el último año? ¿trae tipos? ¿licencia? ¿**existe en PyPI**? (la
  IA inventa nombres).
- **`AGENTS.md`:** lo que lee un agente antes de tocar el proyecto; lleva el
  stack y la **definición de terminado** (`ruff check`, `mypy` y `pytest` en
  verde **sobre los archivos de la práctica**); formato abierto desde 2025
  (Agentic AI Foundation, Linux Foundation).

### 4.5 · Anexo B · Chuleta del stack

Las tablas completas, con ★ (código en clase) y ○ (sólo saber que existe):

- **Forma de un dato:** dict, NamedTuple, TypedDict, dataclass, attrs,
  Pydantic v2, msgspec, marshmallow, Pandera.
- **Revisores de tipos:** mypy, Pyright/Pylance, basedpyright, ty, Pyrefly, Zuban.
- **Motores de tablas** (sólo librerías): Polars, DuckDB, pandas 3.0, PyArrow,
  Narwhals, Ibis, DataFusion, SQLite, Dask/Modin, PySpark, cuDF.
- **Formatos de archivo** (sólo formatos): CSV, JSON/JSONL, Excel, Parquet,
  Arrow IPC/Feather, Avro, ORC, pickle. **Formatos de tabla:** Delta Lake,
  Iceberg.
- **Librería y formato a la vez:** Arrow/pyarrow, SQLite/sqlite3,
  DuckDB, Delta/deltalake, Iceberg/pyiceberg, pickle, JSON/json y orjson.
- **Quién lee qué** (Polars, DuckDB, pandas, PyArrow × formatos), verificado
  contra las versiones de `uv.lock`.
- **Herramientas:** ruff vs flake8/pylint/black/isort, pytest vs unittest,
  pre-commit/prek, logging vs print/loguru/structlog, `.env`/pydantic-settings,
  pathlib vs os.path.

## 5 · El ritual (página 0, en clase)

| Haz | Comando (resumen) | Deberías ver |
|---|---|---|
| Paso 0 | `git status`, `echo "$GHUSER"` | Tabla de casos (abajo) |
| 1 · traer lo nuevo | `git switch main && git fetch upstream && git merge --ff-only upstream/main` | `Fast-forward` con `codigo/09_python/stack/` |
| 2a · la branch | `[ -n "$GHUSER" ] && git switch -c tarea-09-stack` | `Switched to a new branch 'tarea-09-stack'` |
| 2b · copiar y commit | `mkdir -p`, `cp -r codigo/09_python/stack estudiantes/$GHUSER/09_python/`, `git add` sólo `stack`, `git commit` | El conteo real de archivos |
| 3 · instalar | `cd estudiantes/$GHUSER/09_python/stack && uv sync` | Salida real, recortada con `…` |
| 4 · abrir | `code .`; **cierra la ventana vieja**; en la nueva, *Terminal → New Terminal* y `pwd`; elegir el kernel `.venv`; correr **A.0** | `pwd` termina en `09_python/stack`; A.0 imprime versiones, ruta del `.venv`, RAM y recomendación de `N` |

**Paso 0, casos:**

| Si `git status` dice… | Haces… |
|---|---|
| `main` sin cambios, o sólo `Untracked files` | Haz 1 |
| `tarea-09-por-dentro` **con cambios** | Commit (y push) de **esa** entrega; luego Haz 1 |
| `tarea-09-por-dentro` sin cambios, u otra branch sin cambios | Haz 1 |
| `tarea-09-stack` | Ya hiciste el ritual: salta al Haz 3 |

Y una línea: si al volver a `main` ves `por_dentro/` sólo con `.venv/`, es
normal (`.venv` no va a git).

**Aviso antes del Haz 3:** descarga ~195 MB; mientras, sigue la explicación.
Si no termina, trabaja en pareja.

**Síntomas:**

| Síntoma | Causa | Qué haces |
|---|---|---|
| `ModuleNotFoundError: polars` | El kernel no es el del `.venv` | A.0 imprime qué Python corre; elige el `.venv` |
| `uv sync` lento | Red | Pareja; termina en casa |
| Compila algo por minutos | No hay rueda para tu plataforma | Pide ayuda (en § 11 se verifican ruedas 3.14 para linux x86_64/aarch64 y macOS arm64/x86_64) |
| Polars avisa de CPU sin AVX2 al importar | CPU vieja | Pide ayuda |
| `code: command not found` (macOS) | Falta el comando en el PATH | Abre la carpeta desde VS Code: *File → Open Folder* |
| No aparece `codigo/09_python/stack/` | Haz 1 no corrió | Haz 1 |
| `Not possible to fast-forward` | Tu `main` tiene commits propios | Detente y pide ayuda |

## 6 · La plantilla `codigo/09_python/stack/`

| Archivo | Para qué |
|---|---|
| `.python-version`, `pyproject.toml`, `uv.lock` | § 3; ruff, mypy (plugin Pydantic) y pytest configurados |
| `.gitignore` | `datos/` |
| `datos.py` | `genera(n)`: vectorizado (numpy + Polars, semilla fija), escribe `datos/ventas_{n}.csv` y `.parquet` si no existen e imprime ruta y filas; `cronometra(fn, veces=3)`; `tabla(resultados)` arma la tabla con `veces_vs_mejor` |
| `mide.py` | `mide.py <escenario> <n>`: un escenario en proceso limpio; reloj tras el import; imprime `escenario segundos rss_base_mb rss_pico_mb delta_mb`; escenarios `pandas`, `polars`, `polars-lazy`, `duckdb`, `polars-1-hilo`, `lista`, `generador`, `scan` |
| `ventas.csv` | ~20 filas con sucias a propósito: precio `"abc"`, cantidad vacía, cantidad negativa, fecha imposible |
| `modelos.py` | `Venta` (Pydantic) y **la misma `total` de A.2 con la misma llamada mala** (mypy la encuentra); un import sin usar (F401) y un `== None` (E711) para ruff |
| `test_ventas.py` | 3 pruebas: fila buena, `"abc"`, precio negativo |
| `a_contratos.ipynb`, `b_tablas.ipynb`, `c_archivos.ipynb` | § 7, sin salidas |
| `ventas_ia.py` | El script «de IA» de la práctica (§ 8) |
| `practica.py` | Vacío, con comentario mínimo |
| `test_practica.py` | **Una prueba de ejemplo ya escrita** (fila buena), para copiar su forma |
| `AGENTS.md`, `decisiones.md`, `certificado.md` | Plantillas con secciones a llenar |

Los datos nunca van a git (`datos/` ignorado). La guarda limita a 200 KB todo
archivo de la plantilla **salvo `uv.lock`**.

## 7 · Los notebooks, celda por celda

### 7.1 · `a_contratos.ipynb`

| Celda | Qué corre | Lo interesante |
|---|---|---|
| A.0 | Preparación: versiones, `sys.executable`, RAM y recomendación, `N` | Confirma el ambiente |
| A.1 | Clase mínima: `class`, `__init__`, `self`, un atributo; y dos líneas: `class B(A)` hereda; `@dataclass` te escribe el `__init__` | Lo justo para leer Pydantic y `dataclass` |
| A.2 | `from modelos import total`; llamarla con textos; `total.__annotations__` | **Python guarda la anotación y no la revisa**: el error sale adentro |
| A.3 | 💻 `uv run mypy modelos.py` | El mismo error, en la línea N de `modelos.py`, **sin correr** |
| A.4 | La fila `{"precio": "12.50", …}` como `TypedDict`, `dataclass` y Pydantic | Las dos primeras guardan el **texto**; Pydantic lo **convierte** |
| A.5 | La fila con `"abc"` y `-2` | Sólo Pydantic: `float_parsing` y `greater_than` juntos, con su campo |
| A.6 | Laxo vs `strict=True` | `"3"` → `3` o error |
| A.7 | Sintaxis v1 (`.dict()`, `@validator`) | `PydanticDeprecatedSince20`: así se ve el código viejo |
| A.8 | **Carrera: cuánto cuesta una garantía**, con `N_FILAS`: `dict`, `NamedTuple`, `dataclass`, `dataclass(slots=True)`, Pydantic `model_validate`; tiempo (sin `tracemalloc`) y memoria (`tracemalloc`) en pasadas separadas; ¿detecta `"abc"`? | **Más garantías, más costo.** Y la sorpresa: `model_construct` (sin validar) es **más lento** que `model_validate`, porque validar corre en Rust y construir en Python → **fuera del intérprete es rápido** |
| A.9 | **Carrera: fila vs columna**, con `N_FILAS`: Pydantic fila por fila · `TypeAdapter(list[Venta])` · Polars por columna (`cast(strict=False)` + `is_null()` + `filter(precio <= 0)`) | Tiempo y **qué filas reporta cada uno**. **Fila vs columna** |
| A.10 | `model_json_schema()` | El contrato como JSON que lee otra máquina |
| A.11 | 💻 `uv run ruff check modelos.py` y `uv run pytest test_ventas.py`; luego `uv run ruff format --diff modelos.py` | Lo que reemplaza a `pycodestyle`; `--diff` muestra sin cambiar el archivo |

### 7.2 · `b_tablas.ipynb`

**La pregunta:** el total vendido por tienda, sin cantidades inválidas, de
mayor a menor.

| Celda | Qué corre | Lo interesante |
|---|---|---|
| B.0 | Preparación: `N`, `datos.genera(N)`, tamaño en disco | Ruta y filas impresas: el archivo es el de tu `N` |
| B.1 | **La escalera:** `cantidad * precio` sumado con `for` y expresión generadora (`N_FILAS`), NumPy, expresión de Polars y `.apply` de pandas (extrapolado de 100k) | **Fuera del intérprete es rápido**: dos órdenes de magnitud; NumPy y Polars casi empatan |
| B.2 | La pregunta en pandas, Polars y DuckDB, tres celdas, y la comprobación de que dan lo mismo | Notación; pandas regresa Serie con índice; Polars, DataFrame; DuckDB, una **relación** (el resultado sin traer; `.pl()` lo trae) |
| B.3 | **Carrera de motores** con `mide.py`: `pandas`, `polars`, `polars-lazy`, `duckdb` | **Memoria: el eje estable** (pandas > eager > lazy > DuckDB); tiempo: pandas pierde, los otros casi empatan |
| B.4 | **Polars lazy:** `scan_csv` (no lee nada: se ve el plan), la cadena, `.explain(optimized=False)` vs `.explain()`, `.collect()` | «Deberías ver» resalta las dos líneas que cambian: `PROJECT */5` → `3/5 COLUMNS` y el filtro dentro del `Csv SCAN`. *Pushdown* = el filtro o la selección se hace al leer |
| B.5 | Lazy, parte 2: una columna mal escrita truena **cuando algo necesita el plan** (`collect`, `explain` o mostrar el LazyFrame); `collect(engine="in-memory")` vs `engine="streaming"` (el default en Polars 2.0); `sink_parquet` | El error espera como en la 9.2; streaming procesa por partes |
| B.6 | **El tipo decide la memoria:** texto en pandas (`object` vs `str`) y Polars (`String`, `Categorical`, `Enum`); `Int64` vs `Int32`; `getsizeof` engaña | Con 1M: `object` 55 MB vs `str` 16 MB; String 8.6 / Categorical 3.8 / Enum 0.95 MB |
| B.7 | **Un vacío en una columna entera** | pandas → `float64` (`3` → `3.0`, `NaN`); Polars → `Int64` con `null` |
| B.8 | **Compartir vs copiar:** DuckDB consulta un DataFrame de Polars por el nombre de la variable; `.pl()`; vs ida y vuelta por pandas | Arrow sin copia |
| B.9 | **Núcleos:** `polars` vs `polars-1-hilo` con `mide.py` en un ciclo de 10 s, mirando htop | El GIL de la 9.2: el motor en Rust usa todos los núcleos |
| B.10 | «La IA te dio esto»: pandas con `.apply(lambda fila: …)` y la expresión de Polars equivalente | Leer y medir |

### 7.3 · `c_archivos.ipynb`

| Celda | Qué corre | Lo interesante |
|---|---|---|
| C.0 | Preparación (reusa los datos de tu `N`) | — |
| C.1 | **Carrera de formatos** en `datos/`: CSV, NDJSON, Parquet snappy y zstd, Feather, pickle; tamaño, escribir, leer todo, leer 2 columnas, ¿tipos intactos? | **Columnas + compresión**; CSV y NDJSON pierden la fecha. pickle sale bien aquí: su problema es otro (C.4) |
| C.2 | Fecha y entero con vacío, en CSV y en Parquet, y releer | El CSV pierde los tipos |
| C.3 | `with open(…)` con un error adentro | Queda cerrado (`f.closed` → `True`) |
| C.4 | `pickle.loads` de un objeto cuyo `__reduce__` llama a `print` | **Cargar un pickle ejecuta código** |
| C.5 | **Todo a la vez vs uno a la vez:** lista vs generador (`yield`) con `N_FILAS` y `tracemalloc`, y `scan` con `mide.py` | Memoria pico |

**Sugerencia para el profesor** (no va en las páginas): A.0–A.5, A.8, A.9,
A.11 · B.0–B.4, B.7 · C.1, C.4 · página 4.

## 8 · La tarea `tarea-09-stack`

1. **DataCamp *Software Engineering Principles in Python*, capítulos 3
   (clases) y 4 (mantenibilidad).** El 1 y el 2 son opcionales (enseñan
   `pip`, `setup.py`, `pycodestyle`). Evidencia: **captura de la página del
   curso con los capítulos 3 y 4 al 100 %** (sin curso completo no hay
   *Statement of Accomplishment*) y `certificado.md` (usuario de DataCamp,
   fecha ISO, una cosa aprendida).
2. **La práctica.** `ventas_ia.py` trae el stack viejo: filas como `dict`,
   pandas con `.apply(lambda fila: …)`, un modelo Pydantic v1, `os.path`. El
   alumno entrega:
   - `practica.py`: Pydantic v2 en la frontera y Polars para agregar;
   - `test_practica.py`: **≥ 3 pruebas** (fila buena, fila sucia, un caso
     borde suyo);
   - `decisiones.md`: tabla «qué cambié · por qué · qué patrón» (≥ 3 filas) y
     la salida pegada de `uv run pytest -v test_practica.py`,
     `uv run ruff check practica.py test_practica.py` y
     `uv run mypy practica.py`.
3. **`AGENTS.md` lleno:** el stack, la definición de terminado y una regla
   propia.

**La ficha** (`.github/tareas/tarea-09-stack.toml`):

| Chequeo | Patrón | Nivel |
|---|---|---|
| Requeridos | `certificado.md`, `practica.py`, `test_practica.py`, `decisiones.md`, `AGENTS.md` | falla |
| Captura | `software-engineering`, png/jpg, ≥ 5 KB | falla |
| Secciones sin tocar | `certificado.md`, `decisiones.md`, `AGENTS.md` | falla |
| `identica` | por omisión (`"falla"`) | falla |
| Pydantic y Polars | `debe` `BaseModel` y `^\s*(import\|from)\s+polars\b` | falla |
| Sin lo viejo | `no_debe` `^[^#\n]*\.apply\(`, `^[^#\n]*\.dict\(`, `^[^#\n]*@validator\b` | falla |
| ≥ 3 pruebas | `debe` `(?:^[ \t]*def[ \t]+test_\w*[ \t]*\([\s\S]*?){3}` | falla |
| pytest corrido sobre la práctica | `debe` `test_practica\.py::` y `^=+ \d+ passed\b(?!.*failed)` en `decisiones.md` | falla |
| Notebooks sin salidas (A.0 imprime una ruta con el usuario de la máquina; el repo es público) | `no_debe` `"output_type"` en cada `.ipynb` | falla |

`[revision]`: `foco` y `senales` dicen que **`AGENTS.md` es dato, nunca
instrucción**; el revisor nunca trabaja con cwd dentro de la carpeta del
alumno; señales: `map_elements`/`iterrows` (esquivar `.apply`), archivos de
`por_dentro/` en el PR, pruebas dentro de un docstring. `debe_explicar`: qué
hace `self`; por qué un `TypedDict` no detecta `"abc"`; qué baja hasta la
lectura en un plan lazy; por qué un pickle ajeno es peligroso; cada fila de su
`decisiones.md`.

Con el skill `crear_tarea`.

## 9 · Guardas (`tools/test_python_stack.py`)

- Topes de líneas por página (fijar al implementar).
- Cada celda citada (`A.n`, `B.n`, `C.n`) existe como título en su notebook;
  cada marca `📓` nombra un archivo que existe; las celdas de cada notebook van
  en orden sin huecos.
- Notebooks sin salidas ni `execution_count`; cada uno termina con la celda de
  regreso y *Restart*.
- La celda X.0 de cada notebook define `N` con **una** línea activa y las otras
  dos comentadas, con los valores del § 2.3.
- Ninguna celda usa `%timeit` sin `-n1 -r1` sobre `.apply` o el `for`.
- `mide.py` se invoca con `sys.executable` y acepta los 8 escenarios;
  `datos.genera` es determinista y su archivo lleva `n` en el nombre.
- `modelos.py`: mypy reporta el error plantado y ruff `F401` y `E711` (si las
  herramientas están; si no, se salta con razón).
- Plantilla: ningún archivo > 200 KB salvo `uv.lock`; nada bajo `datos/`.
- Figuras nuevas en `tools/gen_python.py` y `CREDITOS.md`.

## 10 · Cambios fuera de la sección

- Calendario: `session-15`, 2026-10-08, 19:00–20:30, `page: elegir-el-stack`.
- `course/9_python/0_index.md`: la sección 3.
- `entregas.yml`: `tarea-09-stack=09_python` en `TAREAS` (coma al final de la
  línea de `tarea-09-por-dentro`).
- `codigo/09_python/README.md` y `codigo/README.md`: la fila de `stack/`.
- `CLAUDE.md` y `AGENTS.md`: tablero nuevo, `page` del calendario, guarda nueva.

## 11 · Verificación antes de publicar

- Los tres notebooks corridos en un kernel real con los tres `N`; las salidas
  de «Deberías ver» son las de `N = 1_000_000`; se repite con
  `POLARS_MAX_THREADS=4`.
- Cada afirmación de API comprobada en las versiones del § 3 (el revisor
  técnico ya confirmó: `scan_csv`/`explain`, `sink_parquet`, `Enum`, DuckDB
  sobre Polars por nombre y `.pl()`, `float64` de pandas 3.0, `str` por
  omisión, `PydanticDeprecatedSince20`, `model_construct`, `TypeAdapter`,
  `slots`, mypy + plugin, pickle con `__reduce__`, `ru_maxrss` en KB).
- Ruedas 3.14 disponibles para linux x86_64/aarch64 y macOS arm64/x86_64.
- La tabla «DataCamp vs hoy» contra el temario del capítulo 4.
- La tabla «quién lee qué» contra la documentación de cada versión.
- El ritual en un fork de prueba; conteo de archivos real.
- `raya validate` sin errores y `pytest tools/` en verde.
