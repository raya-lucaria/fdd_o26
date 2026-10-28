# Decisiones: de ventas_ia.py a practica.py

## Qué cambié, por qué y qué patrón

| Qué cambié | Por qué | Qué patrón |
|---|---|---|
| El contrato: `class Config` y `@validator("cantidad")` (Pydantic v1) → `model_config = ConfigDict(str_strip_whitespace=True)` y `cantidad: int = Field(gt=0)` (v2); `cantidad` deja de ser `Optional` | La sintaxis v1 avisa `PydanticDeprecatedSince20` y desaparece en v3 (en este proyecto pytest la vuelve error). La regla `gt=0` la revisa pydantic-core, en Rust, en lugar de una función de Python que corre una vez por fila, y queda escrita en el JSON Schema | Fuera del intérprete es rápido |
| La frontera: `Venta(**fila).dict()` con `except ValidationError: pass` → `Venta.model_validate(fila)` una sola vez; adentro viajan los objetos `Venta` ya validados, y cada fila descartada se reporta con su línea, campo y motivo | Validar cuesta 5–10× lo de un `dict` (A.8): se paga una vez, donde el dato entra, y adentro se confía. `.dict()` es v1. El `except` callado tiraba 4 de 20 filas sin decir cuáles | Más garantías, más costo |
| La suma: `df.apply(lambda fila: fila["cantidad"] * fila["precio"], axis=1)` en pandas → `(pl.col("cantidad") * pl.col("precio")).sum()` dentro de `.agg`, con `.group_by("tienda")` y `.sort("total", descending=True)` | `.apply(axis=1)` es un `for` de Python escondido que arma un objeto por fila: en B.1 fue miles de veces más lento que la expresión, que corre en Rust sobre la columna entera | Fuera del intérprete es rápido |
| La tabla: `pd.DataFrame(buenas)` con tipos adivinados → `pl.DataFrame(..., schema=ESQUEMA)` con `Date`, `String`, `Int64` y `Float64` fijos | Con `cantidad: Optional[int]`, un solo vacío vuelve `float64` toda la columna en pandas (B.7). Aquí los tipos los fija el contrato y `cantidad` sigue siendo entero | El tipo decide la memoria |

## Salida de pytest

Pega la salida completa de `pytest -v --no-header test_practica.py`,
corrido en `stack/`. `--no-header` quita las líneas con la ruta de tu máquina.

```text
============================= test session starts ==============================
collected 7 items

test_practica.py::test_fila_buena_se_convierte PASSED                    [ 14%]
test_practica.py::test_fila_sucia_se_rechaza PASSED                      [ 28%]
test_practica.py::test_caso_borde_se_rechaza[cantidad-cero] PASSED       [ 42%]
test_practica.py::test_caso_borde_se_rechaza[cantidad-vacia] PASSED      [ 57%]
test_practica.py::test_caso_borde_se_rechaza[fecha-30-de-febrero] PASSED [ 71%]
test_practica.py::test_espacios_alrededor_se_quitan PASSED               [ 85%]
test_practica.py::test_totales_iguales_a_ventas_ia PASSED                [100%]

============================== 7 passed in 0.61s ===============================
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
