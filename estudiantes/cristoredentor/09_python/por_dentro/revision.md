# Revisión de revisa_esto.py

Un error por sección. Cada uno sale de un síntoma de la salida de
`uv run revisa_esto.py`. En `Síntoma:` escribe el síntoma de la tabla de la
página «Python por dentro» (índice de la sección).

## Error 1

Síntoma: 

ValueError: could not convert string to float: '1,200.00'

Línea: 37

File "/home/cris/Documentos/ITAM/Fuentes/Github/fdd_o26/estudiantes/cristoredentor/09_python/por_dentro/revisa_esto.py", line 37, in main

Por qué pasa: 

porque tiene una coma en el registro y no lo puede transformar a float. 

Qué le pedirías a la IA:

Le pediría que añada una función que haga que en las columnas numéricas del csv quite las comas a los valores que encuentre y así permita transfomarlos a float

## Error 2

Síntoma: 

En norte salen Fátima López y Gael Muñoz, que solo compran en centro.

Línea: 25


Por qué pasa: 

La lista vistos=[] se crea una sola vez y todas las regiones usan la misma, entonces cada región se queda con los clientes de las anteriores.

Qué le pedirías a la IA:

Le pediría que la función cree una lista nueva cada vez que se llama, para que no se mezclen los clientes de distintas regiones.

## Error 3

Síntoma: 

puntaje con hilos: 1.12 s
puntaje sin hilos: 0.92 s

Línea: 59


Por qué pasa: 

Por el GIL, Python solo corre un hilo a la vez cuando hace cálculos, entonces los hilos no van más rápido aunque el comentario diga que sí.

Qué le pedirías a la IA:

Le pediría que use procesos en lugar de hilos para calcular el puntaje y que mida el tiempo para comprobar que sí es más rápido.

## Error 4

Síntoma: 

Total con IVA de norte: $325.12, pero haciendo la cuenta a mano debería dar $336.73.

Línea: 39

Por qué pasa: 

Beto Peña tiene descuento 0 y Python toma el 0 como si no hubiera descuento, entonces le pone el 5 % por defecto.

Qué le pedirías a la IA:

Le pediría que el 5 % por defecto solo se use cuando el descuento venga vacío, y que un 0 se respete como sin descuento.

## Error 5

Síntoma: 

La contabilidad NO cuadra

Línea: 76

Por qué pasa: 

El total es un float con muchos decimales y se compara con == contra un número con centavos, entonces nunca son exactamente iguales.

Qué le pedirías a la IA: 

Le pediría que use Decimal para el dinero y que redondee el total a centavos antes de compararlo con la contabilidad.
