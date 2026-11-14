# AGENTS.md

## El stack

- Contrato de los datos: Pydantic 2. Cada fila se valida con una clase Venta que usa model_validate, Field y ConfigDict. No usar la sintaxis de Pydantic 1: @validator, class Config ni .dict().
- Tablas: Polars 2 para sumar y agrupar. No usar pandas ni .apply fila por fila.
- Archivos: csv de la biblioteca estándar para leer y pathlib para las rutas.
- Pruebas: pytest 9.
- Revisión: ruff 0.16 para el estilo y mypy 2 para los tipos.

## Definición de terminado

Un cambio está terminado cuando estos tres comandos salen en verde, corridos en la carpeta stack sobre los archivos de la práctica:

- pytest -v --no-header test_practica.py: todas las pruebas pasan, sin fallidas, con error ni saltadas.
- ruff check practica.py test_practica.py: All checks passed!
- mypy practica.py: Success: no issues found in 1 source file

## Una regla mía

Un except que solo dice pass es mala idea. En ventas_ia.py habia uno y las filas malas desaparecian sin que me diera cuenta. Mejor contarlas y mostrar cuantas se rechazaron.
