# AGENTS.md

## El stack
Este proyecto utiliza:
Pydantic v2 para definir la forma de cada venta, validar los datos que entran desde el CSV y convertirlos a los tipos correctos.

Polars v2 para trabajar con tablas, calcular el total de cada venta y hacer las agregaciones por tienda mediante expresiones por columnas.

csv de la biblioteca estándar de Python para leer el archivo ventas.csv.

os de la biblioteca estándar de Python para construir la ruta del archivo.

pytest para ejecutar las pruebas automatizadas de test_practica.py.

Ruff para revisar el formato y la calidad del código.

mypy para comprobar los tipos del programa.

No se debe usar Pandas para el procesamiento de las ventas ni .apply() fila por fila, porque el procesamiento de tablas se hace con Polars. Tampoco se debe usar sintaxis obsoleta de Pydantic v1, como @validator o .dict().

## Definición de terminado

Un cambio se considera terminado cuando:

pytest -v --no-header test_practica.py pasa las tres pruebas de test_practica.py: una fila válida, una fila con precio inválido y una fila con cantidad no positiva.

ruff check practica.py test_practica.py termina sin errores y muestra All checks passed!.

mypy practica.py termina sin errores de tipos.

Además, practica.py debe validar las filas con Pydantic, descartar las ventas inválidas y calcular los totales por tienda con Polars.

## Una regla mía

Validar los datos en cuanto entran al programa, para que el resto del código puede trabajar con información que ya sé que es válida y evitar repetir comprobaciones.
