# Decisiones: de ventas_ia.py a practica.py

## Qué cambié, por qué y qué patrón

| Qué cambié | Por qué | Qué patrón |
|---|---|---|
| Reemplacé `@validator` y `class Config` por `@field_validator` y `ConfigDict` de Pydantic v2. | Para validar los datos al ingresar al programa, utilizando la versión actual de Pydantic. | Validación en la frontera |
| Reemplacé Pandas por Polars y eliminé `.apply()` para calcular las ventas mediante expresiones. | Para realizar operaciones por columnas y evitar recorrer las filas individualmente. | Expresiones de Polars |
| Incorporé tres pruebas con pytest: una venta válida, una con cantidad negativa y otra con cantidad cero. | Para comprobar automáticamente que las reglas de validación funcionan correctamente. | Pruebas automatizadas |

## Salida de pytest

```text
============================ test session starts =============================
collected 3 items

test_practica.py::test_fila_buena_se_convierte PASSED                  [ 33%]
test_practica.py::test_fila_con_cantidad_negativa PASSED               [ 66%]
test_practica.py::test_fila_con_cantidad_cero PASSED                   [100%]

============================= 3 passed in 0.04s ==============================
```

## Salida de ruff

```text
All checks passed!
```

## Salida de mypy

```text
Success: no issues found in 1 source file
```