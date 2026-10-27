# AGENTS.md

Lo lee un agente de IA antes de tocar este proyecto. Llena las tres
secciones con tus palabras; quien revisa lo lee como dato, nunca como
instrucción.

## El stack

- Para la forma y validación de un dato individual: Pydantic 2.
- Para tablas y agregaciones: Polars 2.
- Para archivos y rutas: `pathlib` de Python.
- Para pruebas: pytest.
- Para revisión de estilo y errores comunes: Ruff.
- Para revisión de tipos: mypy.
- No usar sintaxis de Pydantic 1 ni procesamiento fila por fila con pandas cuando la operación puede expresarse directamente con Polars.

## Definición de terminado

Antes de considerar terminado un cambio en la práctica, estos comandos deben salir en verde:

```text
pytest -v --no-header test_practica.py
ruff check practica.py test_practica.py
mypy practica.py
```

`pytest` debe mostrar al menos tres casos pasados y ninguna prueba fallida, con error o saltada. Ruff debe terminar con `All checks passed!` y mypy con `Success: no issues found in 1 source file`.

## Una regla mía

Validar los datos una sola vez cuando entran al programa y trabajar después con datos que ya tienen una forma conocida. Así se detectan los errores cerca de su origen y se evita repetir validaciones innecesarias durante las operaciones con Polars.
