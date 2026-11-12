# Revisión de revisa_esto.py

Un error por sección. Cada uno sale de un síntoma de la salida de
`uv run revisa_esto.py`. En `Síntoma:` escribe el síntoma de la tabla de la
página «Python por dentro» (índice de la sección).

## Error 1

Síntoma: Una venta no aparece en el total, sin aviso (Carla Ríos no sale en norte y no hay ningún mensaje de error).
Línea: 43
Por qué pasa: En ventas.csv el monto de Carla es "1,200.00", con coma de miles, y float() no lo entiende y truena. Python se entera del error hasta que corre esa línea, y el except que no hace nada se lo traga sin avisar, así que la venta se descarta en silencio.
Qué le pedirías a la IA: Que no use un except vacío: que capture solo el error que espera (ValueError), que me avise qué fila falló y por qué, y que no siga como si nada.

## Error 2

Síntoma: La segunda región lista clientes de la primera (norte lista a Fátima López y Gael Muñoz, que solo compran en centro).
Línea: 25
Por qué pasa: El valor por defecto vistos=[] se crea una sola vez, cuando se define la función, y es el mismo objeto en cada llamada. Cada región sigue llenando la misma lista que dejó la anterior.
Qué le pedirías a la IA: Que no use listas ni diccionarios como valor por defecto: que use None y cree la lista nueva dentro de la función.

## Error 3

Síntoma: «Con hilos» tarda casi lo mismo que «sin hilos», aunque el comentario promete 4× más rápido (0.75 s contra 0.78 s).
Línea: 59
Por qué pasa: puntaje es puro cálculo, no espera nada. Por el GIL solo un hilo ejecuta código de Python a la vez, así que los hilos se turnan y no aceleran. Los hilos ayudan cuando el programa espera (red, disco), no cuando calcula.
Qué le pedirías a la IA: Que para cálculo pesado use procesos (ProcessPoolExecutor) y que mida los dos tiempos antes de decir que algo es más rápido, en vez de escribir "4× más rápido" sin comprobarlo.

## Error 4

Síntoma: Un descuento de 0 se cobró como 5 % (Beto Peña, en norte).
Línea: 39
Por qué pasa: if not descuento trata el 0 como si estuviera vacío, porque 0.0 es falso en Python. No distingue "no hay descuento" de "no me dieron el dato" y le pone 5 % a quien tiene 0.
Qué le pedirías a la IA: Que pregunte si el valor falta (is None o cadena vacía) en lugar de usar if not, y que me diga qué hace con el 0.

## Error 5

Síntoma: La última línea dice «La contabilidad NO cuadra», y la seguiría diciendo aunque los montos fueran los correctos.
Línea: 76
Por qué pasa: Los float guardan los números en binario y no representan exactos los centavos (0.1 + 0.2 no da 0.3), y además el total trae más decimales que centavos. Comparar con == casi nunca da igual. Para dinero se usa Decimal (o centavos enteros) y se compara ya redondeado a centavos.
Qué le pedirías a la IA: Que use Decimal para dinero, que redondee a centavos antes de comparar y que no use == con floats.