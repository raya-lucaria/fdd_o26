# AGENTS.md

## El stack

Este proyecto utiliza:

- Pydantic v2 para definir modelos y validar datos.
- Polars v1 para procesar tablas y realizar agregaciones.
- pathlib para gestionar rutas de archivos.
- csv de la biblioteca estándar de Python para leer archivos CSV.
- pytest v8 para realizar pruebas automatizadas.
- Ruff para revisar la calidad y el estilo del código.
- mypy para comprobar los tipos de datos.

No utilizar Pandas, métodos `.apply()` para calcular ventas,
ni sintaxis obsoleta de Pydantic como `@validator` o `.dict()`.

## Definición de terminado

Un cambio se considera terminado cuando los siguientes comandos
se ejecutan correctamente:

1. `pytest -v --no-header test_practica.py`: todas las pruebas deben pasar.
2. `ruff check practica.py test_practica.py`: debe mostrar `All checks passed!`.
3. `mypy practica.py`: debe mostrar `Success: no issues found in 1 source file`.

Además, el programa debe descartar ventas inválidas y calcular
correctamente los ingresos por tienda.

## Una regla mía

Siempre validar los datos antes de procesarlos.

Durante la práctica observé que un CSV puede contener precios
incorrectos, cantidades negativas y fechas imposibles.
Por eso, considero importante utilizar Pydantic para detectar
estos errores antes de realizar cálculos con Polars.