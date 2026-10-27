# Decisiones: de ventas_ia.py a practica.py

## Qué cambié, por qué y qué patrón

| Qué cambié | Por qué | Qué patrón |
|---|---|---|
| Reemplacé el cálculo fila por fila de pandas por expresiones de Polars sobre columnas. | Evita ejecutar una función de Python por cada fila y deja el trabajo tabular al motor de Polars. | Fuera del intérprete es rápido |
| Uso la clase `Venta` de Pydantic v2 para validar cada fila cuando entra desde el CSV, y después Polars realiza la agregación. | Una venta individual se valida como registro, mientras que el cálculo de totales corresponde a una operación sobre una tabla. | Fila vs columna |
| Los datos se validan una sola vez al entrar al programa con `Venta.model_validate` y no se vuelven a validar durante la agregación. | Una vez que Pydantic comprobó los datos en la frontera, repetir la validación durante el procesamiento añadiría trabajo innecesario. | Más garantías, más costo |

## Salida de pytest

```text
============================================================================= test session starts ==============================================================================
collected 3 items

test_practica.py::test_fila_buena_se_convierte PASSED                                                                                                                    [ 33%]
test_practica.py::test_fila_sucia_cantidad_invalida PASSED                                                                                                               [ 66%]
test_practica.py::test_cantidad_cero_se_rechaza PASSED                                                                                                                   [100%]

============================================================================== 3 passed in 0.10s ===============================================================================
```

## Salida de ruff

```text
All checks passed!
```

## Salida de mypy

```text
Success: no issues found in 1 source file
```
