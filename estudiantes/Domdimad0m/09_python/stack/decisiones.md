
# Decisiones: de ventas_ia.py a practica.py

## Qué cambié, por qué y qué patrón


| Qué cambié | Por qué | Qué patrón |
|---|---|---|
| Cambié @validator por @field_validator y Config por ConfigDict. | Para utilizar las herramientas actuales de Pydantic v2 y evitar funciones obsoletas. | Migración de API |
| Reemplacé pandas por Polars y utilicé with_columns, group_by y agg. | Para calcular el total vendido por tienda utilizando el stack solicitado. | Stack explícito |
| Cambié .dict() por model_dump() y utilicé model_validate() para validar cada venta. | Para utilizar los métodos de Pydantic v2 y separar la validación del procesamiento. | Migración de API |
| Agregué tres pruebas en test_practica.py: fila válida, cantidad negativa y cantidad cero. | Para verificar que el programa acepte datos correctos y rechace cantidades inválidas. | Pruebas automatizadas |


## Salida de pytest

```text
================================================= test session starts ==================================================
collected 3 items

test_practica.py::test_fila_buena_se_convierte PASSED                                                            [ 33%]
test_practica.py::test_fila_sucia_se_rechaza PASSED                                                              [ 66%]
test_practica.py::test_cantidad_cero_se_rechaza PASSED                                                           [100%]

================================================== 3 passed in 0.20s ===================================================
```

## Salida de ruff

```text
All checks passed!
```

## Salida de mypy

```text
Success: no issues found in 1 source file
```

