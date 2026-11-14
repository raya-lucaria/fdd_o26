# Decisiones: de ventas_ia.py a practica.py

## Qué cambié, por qué y qué patrón

Al menos tres filas. El patrón es uno de los ocho de la página «Patrones y
el stack escrito».

| Qué cambié | Por qué | Qué patrón |
|---|---|---|
| `df.apply(lambda fila: fila["cantidad"] * fila["precio"], axis=1)` de pandas por `(pl.col("cantidad") * pl.col("precio")).sum()` dentro de `group_by("tienda").agg(...)` de Polars | `.apply` con `axis=1` es un `for` de Python escondido: llama una función por fila. La expresión de Polars multiplica la columna entera en Rust. En B.10, `.apply` fue cientos de veces más lento con el mismo resultado | Fuera del intérprete es rápido |
| `valida` regresaba `Venta(**fila).dict()` (Pydantic v1); ahora usa `Venta.model_validate(fila)` y regresa `list[Venta]`, y `total_por_tienda` recibe esos objetos sin volver a validarlos | Se valida una sola vez, en la frontera (al leer el CSV). Adentro se confía en el dato. En A.8, `model_validate` costó ~10× un `dict`: pagarlo dos veces no detecta nada nuevo | Más garantías, más costo |
| `cantidad: Optional[int]` en una tabla de pandas por `cantidad: int = Field(gt=0)` y un `pl.DataFrame` con `schema` (`Int64`, `Float64`, `String`) | En pandas un solo vacío vuelve `float64` toda la columna de enteros (B.7). Con el schema, `cantidad` sigue siendo entero, y una lista vacía da una tabla con sus columnas en vez de tronar | El tipo decide la memoria |


## Salida de pytest

Pega la salida completa de `pytest -v --no-header test_practica.py`,
corrido en `stack/`. `--no-header` quita las líneas con la ruta de tu máquina.

```text
=========================================================================================================== test session starts ===========================================================================================================
collected 3 items                                                                                                                                                                                                                         

test_practica.py::test_fila_buena_se_convierte PASSED                                                                                                                                                                               [ 33%]
test_practica.py::test_fila_sucia_se_rechaza PASSED                                                                                                                                                                                 [ 66%]
test_practica.py::test_sin_ventas_da_tabla_vacia PASSED                                                                                                                                                                             [100%]

============================================================================================================ 3 passed in 0.16s ============================================================================================================
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
