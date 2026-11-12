# Decisiones: de ventas_ia.py a practica.py

## Qué cambié, por qué y qué patrón

Al menos tres filas. El patrón es uno de los ocho de la página «Patrones y
el stack escrito».

|| Qué cambié | Por qué | Qué patrón |
|---|---|---|
| Reemplacé el cálculo fila por fila con .apply() por expresiones de columnas en Polars. | Para evitar ejecutar una función de Python por cada fila y dejar que Polars haga el cálculo con su motor nativo. | Fuera del intérprete es rápido |
| Validé cada fila del CSV con Venta.model_validate() al entrar al programa y descarté las que no cumplen el contrato. | Para detectar los datos inválidos desde la frontera y trabajar después únicamente con ventas ya validadas. | Más garantías, más costo|
| Eliminé el procesamiento con Pandas y mantuve las operaciones de tabla en Polars. | Para no convertir los datos entre librerías sin necesidad y mantener el procesamiento en una sola herramienta. | Compartir vs copiar |

## Salida de pytest

Pega la salida completa de `pytest -v --no-header test_practica.py`,
corrido en `stack/`. `--no-header` quita las líneas con la ruta de tu máquina.

```text
tack % pytest -v --no-header test_practica.py
=========================== test session starts ===========================
collected 3 items                                                         

test_practica.py::test_fila_buena_se_convierte PASSED               [ 33%]
test_practica.py::test_fila_sucia_se_convierte PASSED               [ 66%]
test_practica.py::test_fila_borde_se_convierte PASSED               [100%]

============================ 3 passed in 0.89s ============================
```

## Salida de ruff

Pega la salida de `ruff check practica.py test_practica.py`.

```text
ruff check practica.py test_practica.py
All checks passed!
```

## Salida de mypy

Pega la salida de `mypy practica.py`.

```text
stack % mypy practica.py
Success: no issues found in 1 source file
```
