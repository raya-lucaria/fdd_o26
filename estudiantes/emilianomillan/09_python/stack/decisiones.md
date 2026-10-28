# Decisiones: de ventas_ia.py a practica.py

## Qué cambié, por qué y qué patrón

Al menos tres filas. El patrón es uno de los ocho de la página «Patrones y
el stack escrito».

| Qué cambié | Por qué | Qué patrón |
|---|---|---|
| Cambié @validator y class Config (Pydantic v1) por Field(gt=0) y ConfigDict (Pydantic v2) | La sintaxis vieja está deprecada y la regla queda en el tipo del campo | Validar en la frontera con un contrato |
| Cambié el .apply fila por fila de pandas por with_columns, group_by y sum de Polars | Polars calcula sobre columnas enteras y no fila por fila en Python | Usar el motor de tablas en vez de un ciclo en Python |
| Cambié except ValidationError: pass por un contador de filas rechazadas | El except que no hace nada escondía las filas malas; ahora se ve que son 4 | No esconder los errores |
| Cambié diccionarios con .dict() por una lista de objetos Venta con tipos | Con tipos, mypy revisa el código sin correrlo | Anotar tipos y revisar con mypy |

## Salida de pytest

Pega la salida completa de `pytest -v --no-header test_practica.py`,
corrido en `stack/`. `--no-header` quita las líneas con la ruta de tu máquina.

```text
============================= test session starts =============================
collecting ... collected 4 items

test_practica.py::test_fila_buena_se_convierte PASSED                    [ 25%]
test_practica.py::test_fila_sucia_se_rechaza PASSED                      [ 50%]
test_practica.py::test_cantidad_cero_se_rechaza PASSED                   [ 75%]
test_practica.py::test_total_por_tienda_suma_y_ordena PASSED             [100%]

============================== 4 passed in 0.52s ==============================
```

## Salida de ruff

Pega la salida de `ruff check practica.py test_practica.py`.

```text
All checks passed!
```

## Salida de mypy

Pega la salida de `mypy practica.py`.

```text
Success: no issues found in 1 source file
```