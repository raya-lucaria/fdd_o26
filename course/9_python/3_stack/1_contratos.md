---
id: contratos
title: "Contratos"
nav_title: "Contratos"
summary: "Python guarda las anotaciones y no las revisa. TypedDict, dataclass y Pydantic difieren en quién revisa un dato y cuándo; validar cuesta, así que se valida una vez, en la frontera, y adentro se confía."
status: ready
estimated_time: 25m
tags: [type-hints, mypy, typeddict, dataclass, pydantic, ruff, pytest, validacion]
prerequisites: [elegir-el-stack]
---

# Contratos

**Página 1 de 4 · Elegir el stack**

Meta: saber quién revisa un dato y cuándo, cuánto cuesta esa revisión, y dónde ponerla.

**📄 PÁGINA · Contratos**

## En corto

- **Python guarda las anotaciones y no las revisa**: `precio: float` deja pasar `"abc"` hasta que algo intenta sumarlo.
- **`TypedDict` y `dataclass` los revisa sólo mypy o el editor, antes de correr; Pydantic revisa al correr, cuando crea el objeto.**
- **Valida en la frontera, confía adentro**: validar cuesta, así que se hace una vez, donde el dato entra.

Un **contrato** es lo que tu código promete sobre un dato: qué campos trae, de qué tipo, con qué reglas (`cantidad > 0`). La pregunta de esta página es quién lo hace cumplir.

## Python guarda la anotación y no la revisa

**📓 NOTEBOOK · a_contratos.ipynb · celdas A.0–A.2**

¿Te perdiste? Corre A.0 y salta a la celda que vamos.

| Celda | Qué compara | Qué sale |
|---|---|---|
| A.0 | — | Versiones, el Python de `.venv-stack`, tu RAM y el `N` recomendado |
| A.1 | `class`, herencia y `@dataclass`: lo justo para leer lo que sigue | `Punto(x=1, y=2)` |
| A.2 | `total(precios: list[float])` con números y con textos | `TypeError` **dentro** de `total`, en la línea de `sum` |

Una **anotación** (*type hint*) dice qué tipo espera una función: `list[float]`. Python la guarda en `total.__annotations__` y **no la usa**: el error sale lejos de la llamada culpable.

**💻 TERMINAL · en stack/ (comprueba con pwd)**

Celda A.3. Un **revisor de tipos** lee el archivo sin correrlo y compara cada llamada con sus anotaciones. El del curso es **mypy**; el comando y su salida están en la celda A.3.

| Quién encuentra el error | Cuándo | En qué línea |
|---|---|---|
| Python (A.2) | Al correr, si esa línea corre | La de `sum`, adentro de `total` |
| mypy (A.3) | Antes de correr | La de la llamada: `modelos.py:37` |

## Quién revisa, y cuándo

**📓 NOTEBOOK · a_contratos.ipynb · celdas A.4–A.7**

¿Te perdiste? Corre A.0 y salta a la celda que vamos.

La misma fila de un CSV, `"precio": "12.50"` (texto), entra a los tres. Los tres anotan `precio: float`.

| | `TypedDict` | `dataclass` | Pydantic v2 |
|---|---|---|---|
| El dato **es** | un `dict` común | un objeto de tu clase | un objeto de tu modelo |
| ¿Valida al correr? | No | No | **Sí**: convierte o explica por qué no |
| `"12.50"` queda como | `'12.50'`, texto | `'12.50'`, texto | `12.5`, `float` |
| `"abc"` y `-2` (A.5) | Los acepta callado | Los acepta callado | `float_parsing` y `greater_than`, con su campo |
| ¿Lo revisa el editor o mypy? | Sí | Sí | Sí, con el plugin `pydantic.mypy` |
| Costo al crear (A.8) | El de un `dict` | ~1.5–3.5× un `dict` | 5–10× un `dict` |
| Para qué | Describir un `dict` que ya existe (un JSON) | Datos adentro, ya validados | La frontera: CSV, API, configuración |

- **`TypedDict` no compite con los type hints: es uno.** Sólo lo lee mypy o el editor; al correr no existe.
- Pydantic es **laxo** por defecto: convierte `"3"` → `3`. Con `strict=True` exige el tipo exacto y `"3"` es error `int_type` (A.6).
- Pydantic v2 salió el 2023-06-30. `.dict()` y `@validator` son v1: corren, pero avisan `PydanticDeprecatedSince20` y desaparecen en v3 (A.7).

::: figure {#py-stack-frontera title="Valida en la frontera, confía adentro"}
![Cuatro zonas de izquierda a derecha. Afuera: un CSV, una API y un formulario, datos en los que no confías. Una flecha entra a la frontera, donde Pydantic valida cada dato una vez. Las filas válidas pasan adentro, donde una dataclass o un TypedDict las lleva sin revisarlas de nuevo, y de ahí a tu código, que confía. Debajo de la frontera, una fila con precio igual a abc sale rechazada con ValidationError y nunca entra.](../_assets/py-stack-frontera.svg)
:::

La **frontera** es donde un dato entra a tu programa. Ahí lo valida Pydantic, una vez. Adentro viaja como `dataclass` o `TypedDict`, que no lo revisan de nuevo: ya está bien.

## Una garantía cuesta

**📓 NOTEBOOK · a_contratos.ipynb · celdas A.8–A.10**

¿Te perdiste? Corre A.0 y salta a la celda que vamos.

Seis formas de guardar las mismas 97 886 filas buenas (la mitad de `N_FILAS`, para que la celda no pase de ~10 s). El tiempo se mide **sin** `tracemalloc` (la herramienta que cuenta la memoria de Python) y la memoria en otra pasada **con** él, porque `tracemalloc` hace todo 2–5× más lento. `slots=True` guarda los atributos en lugares fijos, sin un `dict` por objeto.

`N = 1_000_000` (`N_FILAS // 2 = 100_000`) · Intel i7-7700HQ (4 núcleos, 8 hilos) · 31 GB:

| Opción | Segundos | Veces vs el mejor | MB | ¿Detecta `"abc"`? |
|---|---:|---:|---:|---|
| `dict` | 0.045 | 1.0 | 18.8 | No |
| `dataclass(slots=True)` | 0.131 | 2.9 | 7.8 | No |
| `dataclass` | 0.157 | 3.5 | 11.8 | No |
| `NamedTuple` | 0.189 | 4.2 | 10.2 | No |
| Pydantic `model_validate` | 0.426 | 9.5 | 104.9 | **Sí** |
| Pydantic `model_construct` | 0.568 | 12.6 | 99.5 | No |

- **Patrón: más garantías, más costo.** Sólo `model_validate` detecta `"abc"`, y cuesta 5–10× en tiempo (según la corrida) y ~5.6× en memoria: crea objetos nuevos (`int`, `float`, `date`) en vez de guardar los textos.
- **Patrón: fuera del intérprete es rápido.** `model_construct` no valida y es **más lento** que `model_validate` (1.3–1.8× en seis corridas): validar corre en Rust (`pydantic-core`); construir sin validar está escrito en Python.
- `slots=True`, `dataclass` y `NamedTuple` **casi empatan** en tiempo: entre corridas cambian de lugar. En memoria, `slots=True` es la más chica. Tus números serán otros; lo que se mantiene es el patrón.

## Fila por fila o por columna

Las mismas 200 000 filas, sucias: `cantidad` vacía o `≤ 0` (~1 % cada una) y `"abc"` en el precio de 1 de cada 1 000. Tres formas de encontrar las malas; el reloj mide sólo validar.

- `TypeAdapter(list[Venta])` valida una lista entera en una llamada, con el ciclo en Rust.
- En Polars, `cast(pl.Float64, strict=False)` convierte la columna entera y deja `null` (vacío) lo que no puede leer; `is_null()` y `filter` se quedan con las malas.

| Opción | Segundos | Veces vs el mejor | Filas malas | Motivos | Qué te reporta |
|---|---:|---:|---:|---:|---|
| Polars por columna | 0.059 | 1.0 | 4 299 | 0 | La fila, con `null`: `"abc"` y vacío se ven iguales |
| Pydantic fila por fila | 0.550 | 9.4 | 4 299 | 4 299 | Fila, campo y motivo; sigue con las buenas |
| `TypeAdapter(list[Venta])` | 0.558 | 9.5 | 4 299 | 4 299 | Fila, campo y motivo; **ninguna fila buena** si una falla |

- `motivos` puede ser mayor que `filas_malas`: una fila puede traer dos errores (aquí ninguna trae dos).
- **Patrón: fila vs columna.** Polars trabaja la columna entera fuera del intérprete y gana por un orden de magnitud; las dos de Pydantic **casi empatan** porque el costo está en crear un objeto Python por fila.
- Los tres encuentran las mismas filas. Lo que cambia es **qué te dicen**: para un reporte de errores, Pydantic; para filtrar millones de filas, Polars.
- **Polars 2.0** (2026-10-06) quitó `cast(pl.Date)` desde texto: ahora es `str.to_date()`. La IA te escribirá lo viejo, y el error lo dice: `It was removed in Polars 2.0`.

A.10 imprime el contrato como **JSON Schema** (`Venta.model_json_schema()`), el formato estándar que leen otras máquinas: `Field(gt=0)` se vuelve `"exclusiveMinimum": 0`.

## Lo que DataCamp enseña y lo que se usa hoy

La tarea es *Software Engineering Principles in Python* ([[entregas-stack]]). El curso es de antes de uv y de ruff; las ideas siguen, las herramientas cambiaron.

| Tema | DataCamp enseña | Hoy | Por qué |
|---|---|---|---|
| Instalar (cap. 1) | `pip install` | `uv add` | Resuelve, instala y anota en `pyproject.toml` y `uv.lock` ([[ambientes-python]]) |
| Estilo (cap. 1) | `pycodestyle` | `ruff check` | Uno solo reemplaza a `pycodestyle`, `flake8` e `isort`, y arregla con `--fix` |
| Formato | — | `ruff format` | Da formato sin discutir; `--diff` muestra sin cambiar |
| Dependencias (cap. 2) | `requirements.txt` | `pyproject.toml` + `uv.lock` | Versiones exactas de todo, también de lo indirecto |
| Empaquetar (cap. 2) | `setup.py` | `pyproject.toml` | Un archivo declarativo, sin código que se ejecuta al instalar |
| Documentar (cap. 4) | docstrings reST y Sphinx | docstrings estilo Google y MkDocs | Más fáciles de leer como texto; Sphinx sigue vivo en proyectos grandes |
| Probar (cap. 4) | `doctest` y `pytest` | **Igual hoy** | `pytest` sigue siendo el estándar |
| Tipos | — | Anotaciones + mypy | Encuentra el error de A.2 sin correr |

**💻 TERMINAL · en stack/ (comprueba con pwd)**

Celda A.11. `ruff check` reporta `F401` (un import que nadie usa) y `E711` (`== None` donde va `is None`) en `modelos.py`; `pytest` corre `test_ventas.py` y dice `3 passed`. Los comandos y la salida están en la celda A.11.

Las demás formas de un dato (attrs, msgspec, ty, pyright…) están en [[chuleta-del-stack]].

**Al revisar código de IA, busca:**

- `.dict()`, `.parse_obj(` o `@validator`: es Pydantic v1.
- `Venta.model_validate(` dentro de un `for` sobre filas que ya validaste: pagas la garantía dos veces.

**Al pedírselo a la IA, dile:**

- «Uso Pydantic 2.14 (API v2: `model_validate`, `model_dump`, `field_validator`) y Polars 2.0.»
- «Valida con Pydantic sólo donde entran los datos; adentro usa `dataclass`.»

::: problem {#py-stack-validar-adentro title="La función que valida otra vez"}
La IA te da una función `calcula_iva(venta: dict)` que empieza con `v = Venta.model_validate(venta)`. Tu programa la llama 200 000 veces, con filas que ya pasaron por `Venta` al leer el CSV. ¿Qué cambiarías?
:::

::: hint {of="py-stack-validar-adentro"}
¿En qué celda viste cuánto cuesta `model_validate` por fila, y dónde está la frontera de este programa?
:::

::: answer {of="py-stack-validar-adentro"}
- Las filas ya se validaron en la frontera: validar adentro no detecta nada nuevo.
- Y cuesta: en A.8, `model_validate` es 5–10× un `dict` en tiempo y ~5.6× en memoria.
- Arreglo: que `calcula_iva` reciba la `Venta` ya validada (`venta: Venta`) y confíe en ella.
:::

Sigue con [[motores-de-tablas]]: con el dato ya validado, la pregunta es dónde se hace el trabajo sobre la tabla entera.

> [!NOTE]
> **Si sólo recuerdas una cosa:** valida una vez, en la frontera, con Pydantic; adentro, confía.
