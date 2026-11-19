# Decisiones: de ventas_ia.py a practica.py

## Qué cambié, por qué y qué patrón

Al menos tres filas. El patrón es uno de los ocho de la página «Patrones y
el stack escrito».

| Qué cambié | Por qué | Qué patrón |
|---|---|---|
| `df.apply(lambda fila: fila["cantidad"] * fila["precio"], axis=1)` por `(pl.col("cantidad") * pl.col("precio")).sum()` dentro de `group_by("tienda").agg(...)` | El `.apply` corre un `for` de Python fila por fila; la expresión de Polars multiplica y suma columnas completas en Rust | Fuera del intérprete es rápido |
| `Venta(**fila).dict()` → `pd.DataFrame(...)` por `pl.DataFrame([v.model_dump() ...], schema=ESQUEMA)` directo | Ya no paso por pandas sólo para sumar: los datos validados van de Pydantic a una sola tabla de Polars | Compartir vs copiar |
| `cantidad: Optional[int]` por `cantidad: int = Field(gt=0)` (y `precio` con `gt=0`) | Con `Optional`, la fila sin cantidad entraba como `None` y en pandas la columna de enteros se volvía `float` con `NaN`; ahora esa fila no entra y la columna es `Int64` | El tipo decide la memoria |
| `class Config` y `@validator` (Pydantic v1) por `model_config = ConfigDict(...)` y `Field(gt=0)` (v2), validando cada fila una sola vez al leer el CSV | La sintaxis v1 está deprecada (en este proyecto es error en las pruebas), y la regla queda declarada en el contrato; después de la frontera ya no se vuelve a validar | Más garantías, más costo |

## Salida de pytest

Pega la salida completa de `pytest -v --no-header test_practica.py`,
corrido en `stack/`. `--no-header` quita las líneas con la ruta de tu máquina.

```text
```

## Salida de ruff

Pega la salida de `ruff check practica.py test_practica.py`.

```text
```

## Salida de mypy

Pega la salida de `mypy practica.py`.

```text
```
