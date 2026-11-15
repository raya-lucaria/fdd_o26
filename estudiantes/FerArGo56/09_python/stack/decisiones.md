# Decisiones: de ventas_ia.py a practica.py

## Qué cambié, por qué y qué patrón

Al menos tres filas. El patrón es uno de los ocho de la página «Patrones y
el stack escrito».

| Qué cambié | Por qué | Patrón de la clase |
|---|---|---|
| `validator` y `class Config` de Pydantic v1 → `field_validator` y `ConfigDict` de Pydantic v2 | La sintaxis v1 está deprecada y genera avisos | Validar en la frontera con Pydantic v2 |
| `df.apply(lambda ...)` fila por fila de pandas → expresión `pl.col("cantidad") * pl.col("precio")` en Polars | La expresión es vectorizada, más rápida y más legible | Polars con expresiones, sin `apply` |
| `.dict()` → `.model_dump()` y `Venta(**fila)` → `Venta.model_validate(fila)` | Es la API actual de Pydantic v2 | Validar en la frontera con Pydantic v2 |
| `os.path` → `pathlib.Path`, y `Dict`/`List`/`Optional` → `dict`/`list`/`X \| None` | Tipos nativos modernos y rutas como objetos | Stack actual de Python: pathlib y tipos nativos |
| Qué cambié | Por qué | Patrón de la clase |
|---|---|---|
| `validator` y `class Config` de Pydantic v1 → `field_validator` y `ConfigDict` de Pydantic v2 | La sintaxis v1 está deprecada y genera avisos | Validar en la frontera con Pydantic v2 |
| `df.apply(lambda ...)` fila por fila de pandas → expresión `pl.col("cantidad") * pl.col("precio")` en Polars | La expresión es vectorizada, más rápida y más legible | Polars con expresiones, sin `apply` |
| `.dict()` → `.model_dump()` y `Venta(**fila)` → `Venta.model_validate(fila)` | Es la API actual de Pydantic v2 | Validar en la frontera con Pydantic v2 |
| `os.path` → `pathlib.Path`, y `Dict`/`List`/`Optional` → `dict`/`list`/`X \| None` | Tipos nativos modernos y rutas como objetos | Stack actual de Python: pathlib y tipos nativos |


## Salida de pytest

Pega la salida completa de `pytest -v --no-header test_practica.py`,
corrido en `stack/`. `--no-header` quita las líneas con la ruta de tu máquina.

```
========================== test session starts ===========================
collected 3 items                                                        

test_practica.py::test_fila_buena_se_convierte PASSED              [ 33%]
test_practica.py::test_fila_sucia_se_rechaza PASSED                [ 66%]
test_practica.py::test_borde_espacios_y_total PASSED               [100%]

=========================== 3 passed in 0.82s ============================
```

## Salida de ruff

Pega la salida de `ruff check practica.py test_practica.py`.

```
All checks passed!
```

## Salida de mypy

Pega la salida de `mypy practica.py`.

```
Success: no issues found in 1 source file
```
