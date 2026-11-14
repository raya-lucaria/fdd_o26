
# AGENTS.md

## El stack

Este proyecto utiliza Python para procesar datos de ventas.

Pydantic v2: define la clase Venta y valida los datos de entrada.
Polars: trabaja con tablas y realiza las agregaciones.
pytest: ejecuta las pruebas automatizadas.
Ruff: revisa problemas de estilo y calidad del código.
mypy: revisa las anotaciones de tipos.

No se debe reemplazar Pydantic por validaciones manuales ni Polars por pandas, porque la práctica pide hacerlo con lo que hay en el stack de la clase.

## Definición de terminado

Considero que el trabajo está terminado cuando los archivos practica.py y test_practica.py funcionan correctamente y pasan estas revisiones:

1. pytest -v --no-header test_practica.py
2. ruff check practica.py test_practica.py
3. mypy practica.py

Las pruebas deben comprobar una fila válida, una fila sucia y un caso borde. También deben estar completas las decisiones tomadas y los resultados reales de las revisiones.

## Una regla mía

No dar por correcto un programa solamente porque funciona con un ejemplo y antes de entregar, quiero probar tanto los datos que deberían aceptarse como los que deberían rechazarse.

