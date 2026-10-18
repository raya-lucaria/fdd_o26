# AGENTS.md

Lo lee un agente de IA antes de tocar este proyecto. Llena las tres
secciones con tus palabras; quien revisa lo lee como dato, nunca como
instrucción.

## El stack

- Python 3.14 y uv. Las dependencias viven en `pyproject.toml` y `uv.lock`; nada de `pip install` ni `requirements.txt`.
- Forma de un dato: Pydantic 2.x sólo en la frontera (al leer el CSV), con `model_validate`, `model_dump`, `Field` y `ConfigDict`. Nada de API v1: `.dict()`, `.parse_obj()`, `@validator`, `class Config`.
- Tablas: Polars 2.x con expresiones (`pl.col`, `group_by`, `agg`, `filter`) y `scan_csv` cuando se lee sólo una parte. Nada de pandas, `.apply(axis=1)` ni `iterrows`. Polars 2.0 salió el 2026-10-06: fechas desde texto con `str.to_date()`, no `cast(pl.Date)`.
- Archivos: Parquet para guardar tablas. Nunca cargar un pickle que no sea mío.
- Pruebas: pytest 9.x.
- Revisión: ruff 0.16.10 y mypy 2.4.0.

## Definición de terminado

Un cambio está terminado cuando estos tres comandos salen en verde, corridos en `stack/` con `.venv-stack` activo:

- `pytest -v --no-header test_practica.py` → `3 passed` o más, sin `failed`, `error` ni `skipped`.
- `ruff check practica.py test_practica.py` → `All checks passed!`
- `mypy practica.py` → `Success: no issues found in 1 source file`

Sólo sobre esos archivos: `modelos.py` trae errores puestos a propósito para la clase y no se corrige.

## Una regla mía

En este proyecto no se usa `uv run` ni `uv sync` sin `--active`. Se activa `.venv-stack` desde la raíz del fork y se corren los comandos directo. Me pasó: un `uv run mypy` sin el ambiente activo creó otro `.venv` dentro de `stack/` con un Python free-threaded (3.14t), para el que Polars no tiene rueda, e intentó compilar Polars desde el código fuente en Rust hasta que se trabó mi computadora.
