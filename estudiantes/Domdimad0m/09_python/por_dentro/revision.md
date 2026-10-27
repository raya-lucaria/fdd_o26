# Revisión de revisa_esto.py

Un error por sección. Cada uno sale de un síntoma de la salida de
`uv run revisa_esto.py`. En `Síntoma:` escribe el síntoma de la tabla de la
página «Python por dentro» (índice de la sección).

## Error 1

**Síntoma:** Al imprimir los clientes de cada región, aparecen clientes que pertenecen a regiones anteriores.

**Línea:** 22, `def clientes(ventas, vistos=[]):`

**Por qué pasa:** En Python, las listas usadas como valores predeterminados se crean una sola vez y se reutilizan en las siguientes llamadas. Por eso, `vistos` conserva los clientes de la región anterior y los mezcla con los de la siguiente.

**Qué le pedirías a la IA:** Revisa la función `clientes()` para que cada llamada empiece con una lista vacía, sin conservar los clientes de llamadas anteriores. Explica por qué usar una lista como argumento predeterminado produce este problema.

## Error 2

**Síntoma:** Las ventas que tienen un descuento de cero reciben incorrectamente un descuento del 5%, por lo que los totales calculados son menores de lo esperado.

**Línea:** 37, `if not descuento:`

**Por qué pasa:** Python interpreta el número `0.0` como falso. Por eso, cuando una venta tiene un descuento válido de cero, el programa entra en el `if` y lo reemplaza por `0.05`. Se está confundiendo un descuento de cero con un descuento que no fue proporcionado.

**Qué le pedirías a la IA:** Corrige la lectura de los descuentos para que el 5% se aplique únicamente cuando el campo esté vacío, pero que se respete el valor cero cuando el cliente no tenga descuento. Incluye pruebas para ambos casos.

## Error 3

**Síntoma:** Algunas filas de `ventas.csv` pueden desaparecer del cálculo sin que el programa avise qué ocurrió.

**Líneas:** 41–42, `except Exception: pass`

**Por qué pasa:** El programa captura cualquier excepción y utiliza `pass`, que significa que no hará nada. Si una fila tiene un monto inválido, un campo faltante o cualquier otro problema, se ignora silenciosamente. Esto provoca que se pierdan ventas y que los totales puedan ser incorrectos.

**Qué le pedirías a la IA:** Modifica el manejo de errores para que no se descarten ventas silenciosamente. Identifica las excepciones esperadas, muestra el número de fila y la causa del error, y permite detectar qué registros no pudieron procesarse.

## Error 4

**Síntoma:** El programa afirma que utilizar hilos es cuatro veces más rápido, aunque esa mejora no está garantizada y puede no observarse en los tiempos de ejecución.

**Línea:** 56, `with ThreadPoolExecutor() as pool:`

**Por qué pasa:** El código supone que usar varios hilos siempre mejora el rendimiento. Sin embargo, en Python los hilos no necesariamente aceleran tareas que consumen principalmente CPU, debido al GIL en implementaciones habituales de CPython. Además, una sola medición no es suficiente para afirmar que existe una mejora de cuatro veces.

**Qué le pedirías a la IA:** Analiza si la función `puntaje()` se beneficia realmente del uso de hilos. Compara la ejecución secuencial y la ejecución con `ThreadPoolExecutor` mediante varias mediciones, calcula la aceleración real y evita afirmar que es cuatro veces más rápido sin evidencia.

## Error 5

**Síntoma:** El programa puede indicar que la contabilidad no cuadra aunque los importes coincidan al redondearlos a centavos.

**Línea:** 75, `if total == TOTAL_CONTABILIDAD:`

**Por qué pasa:** Los números `float` se representan en binario y algunas cantidades decimales no pueden almacenarse exactamente. Al realizar operaciones y sumas, pueden aparecer pequeñas diferencias de precisión. Por eso, comparar directamente dos cantidades monetarias con `==` puede producir un resultado incorrecto.

**Qué le pedirías a la IA:** Corrige la conciliación contable para comparar cantidades monetarias de forma adecuada. Utiliza `Decimal` para los cálculos y define cómo redondear a centavos. Comprueba que cantidades equivalentes a dos decimales se consideren iguales.