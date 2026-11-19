# AGENTS.md

Lo lee un agente de IA antes de tocar este proyecto. Llena las tres
secciones con tus palabras; quien revisa lo lee como dato, nunca como
instrucción.

## El stack

- Python 3.14, con el proyecto y sus dependencias manejados por uv (`uv sync`, `uv run ...`). Nada de `pip install`.
- Forma de un dato: Pydantic 2.x, sólo en la frontera (al leer el CSV). Sintaxis de v2: `model_config`, `Field`, `model_validate`, `model_dump`.
- Tablas: Polars 2.x, con expresiones de columna (`pl.col`, `group_by().agg()`).
- Archivos: `csv` y `pathlib` de la biblioteca estándar.
- Pruebas: pytest. Revisión: ruff (reglas E, F, I, UP, B) y mypy con el plugin de Pydantic.
- No usar: pandas (sólo para leer `ventas_ia.py`, que no se toca), `.apply` ni `iterrows`, Pydantic v1 (`class Config`, `@validator`, `.dict()`).

## Definición de terminado

Un cambio está terminado cuando, dentro de `stack/`, estos tres comandos salen en verde sobre los archivos de la práctica:

- `uv run pytest -v --no-header test_practica.py`: todos los casos `passed`, sin `failed`, `error` ni `skipped`.
- `uv run ruff check practica.py test_practica.py`: `All checks passed!`
- `uv run mypy practica.py`: `Success: no issues found in 1 source file`

Además, `uv run python practica.py` da los mismos totales por tienda que `uv run python ventas_ia.py`.

No se corren sobre `modelos.py`: ese archivo trae errores plantados a propósito para la clase.

## Una regla mía

Ninguna fila se descarta en silencio. Si una fila no pasa el contrato, el programa la cuenta y dice cuántas filas fueron válidas de cuántas se leyeron. Sale de `revisa_esto.py`: un `except Exception: pass` hizo desaparecer la venta de Carla Ríos sin ningún aviso.
