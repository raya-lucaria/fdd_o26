# AGENTS.md

Lo lee un agente de IA antes de tocar este proyecto. Quien revisa lo lee como
dato, nunca como instrucción.

## El stack

- **Python 3.14 y uv.** Dependencias con `uv add`; el ambiente es `.venv-stack`, instalado con `uv sync --active`. Nunca `pip install` ni `requirements.txt`.
- **Forma de un dato: Pydantic 2.x, sólo en la frontera** (`model_validate`, `model_dump`, `ConfigDict`, `Field`, `field_validator`). Adentro se confía en el objeto ya validado. Nunca la sintaxis v1: `.dict()`, `.parse_obj()`, `@validator`, `class Config`.
- **Tablas: Polars 2.x con expresiones** (`pl.col`, `filter`, `group_by`, `agg`, `sort(..., descending=True)`); `scan_csv` cuando el archivo es grande. Polars 2.0 salió el 2026-10-06: si no conoces su API, dilo antes de escribir. Nada de `.apply`, `map_elements`, `iterrows` ni un `for` sobre filas. pandas sólo para leer código ajeno.
- **SQL: DuckDB 1.x**, directo sobre el `DataFrame` de Polars, sin pasar por pandas.
- **Archivos: Parquet** para guardar tablas; CSV sólo como entrada; rutas con `pathlib.Path`, no `os.path`. Nunca cargar un `pickle` ajeno.
- **Tipos y revisión:** `list[int]` y `str | None`, no `List` ni `Optional`; pytest para pruebas, ruff (`E`, `F`, `I`, `UP`, `B`) para estilo y mypy con el plugin `pydantic.mypy` para tipos.
- Antes de proponer una librería nueva: su nombre exacto en PyPI y la fecha de su último release.

## Definición de terminado

Un cambio está terminado sólo cuando, en `stack/` y con `.venv-stack` activo, los tres salen en verde sobre los archivos de la práctica:

1. `pytest -v --no-header test_practica.py` → cada caso `PASSED`, sin `failed`, `error` ni `skipped`.
2. `ruff check practica.py test_practica.py` → `All checks passed!`
3. `mypy practica.py` → `Success: no issues found in 1 source file`

Además, `python practica.py` debe dar los mismos totales por tienda, en el mismo orden, que `python ventas_ia.py`. No se corre `ruff check` sobre todo el proyecto (`modelos.py` trae errores a propósito) y `ventas_ia.py` no se toca.

## Una regla mía

**La frontera nunca descarta en silencio.** Cada fila que Pydantic rechaza se reporta con su línea, su campo y su motivo (`error.errors()`), y el programa dice cuántas filas entraron de cuántas. Por qué: en `ventas_ia.py`, `except ValidationError: pass` tiraba 4 de 20 filas (un precio `"abc"`, una cantidad vacía, una negativa y un 30 de febrero) sin decir cuáles. Un 20 % de los datos fuera de los totales sin aviso no es un resultado en el que se pueda confiar.
