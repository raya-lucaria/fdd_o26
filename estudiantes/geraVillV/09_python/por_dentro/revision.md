# Revisión de revisa_esto.py

Un error por sección. Cada uno sale de un síntoma de la salida de
`uv run revisa_esto.py`. En `Síntoma:` escribe el síntoma de la tabla de la
página «Python por dentro» (índice de la sección).

## Error 1

Síntoma: Los clientes de una región aparecen también en las regiones siguientes.
Línea: 25
Por qué pasa: El argumento por defecto `vistos=[]` es una lista mutable. Python crea esa lista una sola vez cuando define la función, por lo que las llamadas siguientes reutilizan la misma lista y acumulan clientes de regiones anteriores.
Qué le pedirías a la IA: No uses listas o diccionarios mutables como argumentos por defecto. Usa `None` y crea una lista nueva dentro de la función en cada llamada.

## Error 2

Síntoma: Una venta con descuento de 0 recibe un descuento de 5 % aunque cero sea un valor válido.
Línea: 39
Por qué pasa: La condición `if not descuento` trata `0.0` como falso. Entonces el programa confunde un descuento válido de cero con la ausencia de descuento y lo reemplaza por `0.05`.
Qué le pedirías a la IA: No uses una condición de verdad/falsedad para distinguir entre un valor faltante y el número cero. Valida explícitamente si el dato está vacío antes de convertirlo o usa una condición que preserve `0` como valor válido.

## Error 3

Síntoma: Algunas filas con datos incorrectos desaparecen sin mostrar ningún mensaje de error.
Línea: 43
Por qué pasa: `except Exception: pass` captura cualquier excepción y luego la ignora. Eso oculta problemas como valores que no se pueden convertir a número o columnas faltantes, y hace que el programa siga con datos incompletos sin avisar.
Qué le pedirías a la IA: No uses `except Exception: pass`. Captura únicamente las excepciones que esperas y muestra o registra qué fila falló y por qué.

## Error 4

Síntoma: El cálculo con hilos tarda más que el cálculo sin hilos.
Línea: 59
Por qué pasa: `puntaje` es una tarea intensiva de CPU y `ThreadPoolExecutor` usa hilos. En CPython, el GIL impide que varios hilos ejecuten bytecode de Python en paralelo al mismo tiempo, así que no se obtiene la aceleración esperada y además se agrega el costo de administrar los hilos.
Qué le pedirías a la IA: No uses hilos para acelerar una tarea intensiva de CPU en CPython. Usa procesos, por ejemplo `ProcessPoolExecutor`, o deja la ejecución secuencial si el trabajo es pequeño.

## Error 5

Síntoma: La conciliación indica que los totales no coinciden aunque se trate de cantidades de dinero.
Línea: 76
Por qué pasa: El programa usa `float` para los importes y después compara los totales con igualdad exacta usando `total == TOTAL_CONTABILIDAD`. Los decimales no siempre se representan exactamente en binario, así que pueden aparecer pequeñas diferencias de redondeo.
Qué le pedirías a la IA: Para cálculos de dinero usa `Decimal` en lugar de `float`, crea los valores a partir de texto y redondea de forma explícita antes de comparar.
