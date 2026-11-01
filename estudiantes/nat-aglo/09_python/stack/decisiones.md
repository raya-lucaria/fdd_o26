# Decisiones: de ventas_ia.py a practica.py

## Qué cambié, por qué y qué patrón

Al menos tres filas. El patrón es uno de los ocho de la página «Patrones y
el stack escrito».

| Qué cambié | Por qué | Qué patrón |
|pd.Series con índices de pandas por pl.DataFrame de Polars|pandas usa su formato propio, por lo cual cuando una libreria externa necesita
leer sus datos, ocupa reservar espacio, copiar y convertirlos para acceder a ellos. Polars guarda sus columnas usando el estandar Apache
Arrow, por tanto si otra herramienta que comparte el estandar quieren leer los datos podran hacerlo con zero-copys (leen directamente).|
Compartir vs copiar|
|df.apply(..., axis=1) por pl.col("cantidad") * pl.col("precio"|df.apply obliga al interprete de python a recorrer cada fila, construir un 
objeto pd.Series y llamar a la funcion lambda. Polars no hace la multiplicacion fila por fila, sino define una expresion abstracta y se la
entrega a su motor Rust, aprovechando vectorizacion y multihilo.| Fuera del intérprete es rápido|
|Venta(**fila) por Venta.model_validate(fila)|Comprobar que un dato sea valido requiere tiempo, CPU y memoria. La solucion: validar 
estricta y unicamente al inicio (en validar()) asegurandole al resto de las funciones la entrada de datos correctos. |Más garantías, más costo|

## Salida de pytest

Pega la salida completa de `pytest -v --no-header test_practica.py`,
corrido en `stack/`. `--no-header` quita las líneas con la ruta de tu máquina.

$ pytest -v --no-header test_practica.py
============================================================== test session starts ==============================================================
collected 3 items                                                                                                                               

test_practica.py::test_fila_buena_se_convierte PASSED                                                                                     [ 33%]
test_practica.py::test_fecha_invalida_se_rechaza PASSED                                                                                   [ 66%]
test_practica.py::test_cantidad_vacia_es_none PASSED                                                                                      [100%]

## Salida de ruff

Pega la salida de `ruff check practica.py test_practica.py`.

$ ruff check practica.py test_practica.py
All checks passed!

## Salida de mypy

Pega la salida de `mypy practica.py`.

$ mypy practica.py
Success: no issues found in 1 source file

