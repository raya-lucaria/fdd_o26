# Revisión de revisa_esto.py

Un error por sección. Cada uno sale de un síntoma de la salida de
`uv run revisa_esto.py`. En `Síntoma:` escribe el síntoma de la tabla de la
página «Python por dentro» (índice de la sección).

## Error 1

Síntoma: Una venta no aparece en el total, sin aviso: Carla Ríos no sale en `norte` y no hay ningún mensaje de error.
Línea: 43
Por qué pasa: El monto de Carla viene como `"1,200.00"`, con coma de miles. El `float()` de la línea 37 no entiende la coma y lanza `ValueError`. El `except Exception: pass` de las líneas 43 y 44 atrapa ese error y no hace nada, así que la fila se descarta en silencio. Python sí detectó el error al correr; el `except` vacío lo escondió (página 1). Por eso mi conciliación da $1,388.26 contra $2,722.27: falta su venta, que con IVA es $1,322.40.
Qué le pedirías a la IA: Que no escriba `except` vacíos ni `except Exception: pass`. Que atrape sólo el error que espera (`ValueError`), que quite la coma de miles antes de convertir y que reporte con su número de línea cualquier fila que no pueda leer, en vez de saltarla callada.

## Error 2

Síntoma: La segunda región lista clientes de la primera: `norte` lista a Fátima López y Gael Muñoz, que sólo compran en `centro`.
Línea: 25
Por qué pasa: `vistos=[]` se evalúa una sola vez, cuando Python define la función, no en cada llamada. Las tres llamadas a `clientes()` comparten la misma lista. `centro` va primero en orden alfabético y deja ahí a sus clientes; `norte` los hereda, y `sur` hereda los de las dos regiones anteriores. Es el mismo objeto con otro nombre, porque `=` no copia (página 2).
Qué le pedirías a la IA: Que nunca use una lista, un diccionario o un conjunto como valor por defecto de un argumento. Que use `None` y cree la lista nueva dentro de la función, o que quite el argumento si nadie lo pasa.

## Error 3

Síntoma: «Con hilos» tarda casi lo mismo que «sin hilos», aunque el comentario promete 4× más rápido. En mi corrida, 0.67 s con hilos y 0.65 s sin hilos.
Línea: 59
Por qué pasa: `puntaje` es un cálculo puro en Python que sólo usa CPU. En CPython el GIL deja que un solo hilo ejecute bytecode a la vez, así que los hilos se turnan en vez de trabajar en paralelo. Con hilos no se gana nada, y hasta se pierde un poco por el cambio entre ellos (página 3). Los hilos ayudan cuando el trabajo espera a la red o al disco, no cuando calcula.
Qué le pedirías a la IA: Que no use hilos para cálculo puro en Python y use `ProcessPoolExecutor`, porque cada proceso tiene su propio intérprete y su propio GIL. Que mida el tiempo con y sin paralelismo antes de prometer una mejora, y que no escriba en un comentario una cifra que no midió.

## Error 4

Síntoma: Un descuento de 0 se cobró como 5 %: Beto Peña tiene descuento `0` en `norte`, y `norte` sale $325.12 cuando, aun sin Carla, debería dar $336.73.
Línea: 39
Por qué pasa: `if not descuento` pregunta si el valor es «falso», y en Python `0.0` es falso igual que un valor vacío (truthiness, página 4). El código confunde «no hay descuento» con «el descuento es cero» y le aplica 5 % a Beto: 200.20 × 0.95 × 1.16 = 220.62 en vez de 232.23. Además, un descuento vacío nunca llega a esa línea: `float("")` falla antes, en la 38, y el `except` lo esconde.
Qué le pedirías a la IA: Que no use truthiness (`if not x`) para revisar números. Que compare explícitamente contra el texto vacío o contra `None` antes de convertir, y que trate un 0 como un descuento válido de cero.

## Error 5

Síntoma: La contabilidad está en centavos; comparar el total sin redondear con `==` falla. La última línea dice `La contabilidad NO cuadra`, y lo seguiría diciendo aunque los montos fueran los correctos.
Línea: 76
Por qué pasa: Un `float` se guarda en binario y no representa exactamente la mayoría de los decimales: 0.1 + 0.2 da 0.30000000000000004. Al sumar montos con IVA esos residuos se acumulan. Además, el total real tiene más decimales que los centavos: aun con `Decimal` da 2722.270020. `==` exige que los dos números sean idénticos, y eso casi nunca pasa (página 4). Lo correcto es comparar el total redondeado a centavos.
Qué le pedirías a la IA: Que maneje el dinero con `Decimal`, creado desde el texto del archivo y no desde un `float`. Que redondee a centavos con `quantize(Decimal("0.01"))` antes de comparar, y que nunca compare montos con `==` sin redondear.
