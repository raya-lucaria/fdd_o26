# Revisión de revisa_esto.py

Un error por sección. Cada uno sale de un síntoma de la salida de
`uv run revisa_esto.py`. En `Síntoma:` escribe el síntoma de la tabla de la
página «Python por dentro» (índice de la sección).

## Error 1

Síntoma: Una venta no aparece en el total, sin aviso: Carla Ríos no sale en `norte` y no hay ningún mensaje de error.
Línea: 43
Por qué pasa: el monto de Carla viene como `"1,200.00"`, con coma de miles, y `float("1,200.00")` lanza `ValueError` en la línea 37. El `except Exception: pass` de las líneas 43-44 se traga el error: la fila se descarta y el programa sigue como si nada. Python encuentra el error al correr esa línea, no antes, y un `except` vacío lo esconde (página «Qué es Python»).
Qué le pedirías a la IA: «Quita la coma de miles antes de convertir (`monto.replace(",", "")`). No uses `except Exception: pass`: atrapa sólo `ValueError` y, si una fila no se puede leer, imprime cuál fue y cuéntala, para que nunca desaparezca una venta en silencio».

## Error 2

Síntoma: La segunda región lista clientes de la primera: `norte` lista a Fátima López y Gael Muñoz, que sólo compran en `centro`.
Línea: 25
Por qué pasa: `def clientes(ventas, vistos=[])` usa una lista como argumento por defecto. Python crea esa lista una sola vez, cuando define la función, y todas las llamadas sin `vistos` comparten el mismo objeto; cada región le sigue agregando clientes a la lista de la región anterior (página «Nombres y objetos», el argumento por defecto mutable).
Qué le pedirías a la IA: «No uses objetos mutables como valor por defecto. Usa `vistos=None` y adentro `if vistos is None: vistos = []`, o crea la lista dentro de la función. Agrega una prueba que llame dos veces a `clientes` y compruebe que la segunda no trae nombres de la primera».

## Error 3

Síntoma: «Con hilos» tarda casi lo mismo que «sin hilos», aunque el comentario promete 4× más rápido (en mi corrida: 1.30 s con hilos y 1.11 s sin hilos).
Línea: 59
Por qué pasa: `puntaje` es puro cálculo en Python (un `for` de 3 millones de vueltas). Con el GIL, sólo un hilo ejecuta bytecode de Python a la vez, así que los hilos de `ThreadPoolExecutor` se turnan en lugar de correr en paralelo: no hay aceleración, y el cambio entre hilos hasta le suma tiempo. Los hilos sólo ayudan cuando el trabajo espera (red, disco) (página «El GIL»).
Qué le pedirías a la IA: «`puntaje` es trabajo de CPU: usa `ProcessPoolExecutor` en lugar de hilos, y quita el comentario de "4× más rápido" a menos que lo midas. Imprime los dos tiempos medidos y el número de procesos usados».

## Error 4

Síntoma: Un descuento de 0 se cobró como 5 %: Beto Peña tiene descuento `0` y `norte` sin Carla debería dar 104.50 + 232.23 = 336.73, pero la salida dice 325.12.
Línea: 39
Por qué pasa: `if not descuento:` trata el `0.0` como falso, igual que un dato faltante, y le pone el 5 % por defecto. Un descuento de 0 es un valor válido, no la ausencia de un valor; `bool(0.0)` es `False` (página «Lo que escribe la IA», qué cuenta como falso).
Qué le pedirías a la IA: «Distingue "no hay descuento" de "descuento 0". Aplica el 5 % por defecto sólo cuando la celda viene vacía (`fila["descuento"].strip() == ""`), y nunca cuando el valor es 0. Agrega una prueba con descuento 0».

## Error 5

Síntoma: La contabilidad está en centavos; comparar el total sin redondear con `==` falla: la última línea dice `La contabilidad NO cuadra`, y lo seguiría diciendo aunque los montos fueran los correctos.
Línea: 76
Por qué pasa: `total == TOTAL_CONTABILIDAD` compara dos `float`. Los `float` guardan los decimales en binario y casi nunca son exactos (`0.1 + 0.2 != 0.3`), así que un total con IVA casi nunca es igual, bit por bit, a un número escrito con dos decimales (página «Lo que escribe la IA», `0.1 + 0.2` y `Decimal`).
Qué le pedirías a la IA: «El dinero va en `Decimal`, construido desde el texto del CSV (`Decimal("100.10")`), o en centavos enteros. Redondea el total a centavos (`quantize(Decimal("0.01"))`) antes de compararlo con la contabilidad, y nunca compares `float` con `==`».
