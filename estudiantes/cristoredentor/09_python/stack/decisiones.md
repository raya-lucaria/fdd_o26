# Decisiones: de ventas_ia.py a practica.py

## Qué cambié, por qué y qué patrón

Al menos tres filas. El patrón es uno de los ocho de la página «Patrones y
el stack escrito».

| Qué cambié | Por qué | Qué patrón |
|---|---|---|
| Cambié pandas por Polars | pandas guarda tienda y producto como object, un objeto de Python por celda; Polars los guarda como str en Arrow, en un solo bloque de memoria | El tipo decide la memoria |
| Cambié el .apply con lambda por una expresión de Polars que multiplica la columna cantidad por la columna precio | .apply llama una función de Python en cada fila; la expresión multiplica la columna entera en Rust | Fuera del intérprete es rápido |
| Cambié el @validator y el Optional[int] por cantidad: int = Field(gt=0) | El validador es una función de Python que corre en cada fila; gt=0 lo revisa el núcleo de Pydantic en Rust. Además @validator, class Config y .dict() son de Pydantic v1 y desaparecen en v3 | Fuera del intérprete es rápido |

## Salida de pytest

Pega la salida completa de `pytest -v --no-header test_practica.py`,
corrido en `stack/`. `--no-header` quita las líneas con la ruta de tu máquina.

```text
============================= test session starts ==============================
collecting ... collected 3 items

test_practica.py::test_fila_buena_se_convierte PASSED                    [ 33%]
test_practica.py::test_mala_definicion_venta PASSED                      [ 66%]
test_practica.py::test_fecha_inexistente_se_rechaza PASSED               [100%]

============================== 3 passed in 0.27s ===============================
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
