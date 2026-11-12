# Revisión de revisa_esto.py

Un error por sección. Cada uno sale de un síntoma de la salida de
`uv run revisa_esto.py`. En `Síntoma:` escribe el síntoma de la tabla de la
página «Python por dentro» (índice de la sección).

## Error 1
Síntoma: Los clientes de una región aparecen también en las siguientes regiones, aunque no hayan comprado ahí.
Línea: 25
Por qué pasa: El argumento por defecto vistos=[] se crea una sola vez al definir la función. Como la lista es mutable, conserva los clientes agregados en llamadas anteriores.
Qué le pedirías a la IA: Modifica clientes() para que cada llamada utilice una lista independiente, usando None como argumento por defecto, sin perder la eliminación de duplicados.

## Error 2
Síntoma: Se aplica un descuento del 5 % a ventas cuyo descuento original es 0 %, aunque el cero es un valor válido.
Línea: 39
Por qué pasa: La condición if not descuento interpreta 0.0 como False y lo sustituye por 0.05. Se confunde un descuento válido de cero con la ausencia de un descuento.
Qué le pedirías a la IA: Modifica la validación para distinguir entre un descuento de 0 % y un dato faltante, conservando los descuentos válidos y aplicando el valor por defecto únicamente cuando corresponda.

## Error 3
Síntoma: Algunas ventas pueden desaparecer del cálculo sin mostrar ningún mensaje cuando ocurre un error al procesarlas.
Línea: 43
Por qué pasa: El bloque except Exception captura cualquier excepción y pass la ignora completamente. Esto oculta errores y permite continuar con información incompleta.
Qué le pedirías a la IA: Sustituye el manejo genérico de excepciones por excepciones específicas, mostrando la fila problemática y el motivo del error, sin ocultar fallos inesperados.

## Error 4
Síntoma: El cálculo de puntajes con hilos tarda 0.63 segundos, mientras que sin hilos tarda 0.62 segundos, por lo que no se obtiene la aceleración prometida.
Línea: 59
Por qué pasa: ThreadPoolExecutor utiliza hilos, pero el GIL de CPython impide que varios hilos ejecuten simultáneamente código Python intensivo en CPU. Por eso no se consigue paralelismo efectivo en este cálculo.
Qué le pedirías a la IA: Evalúa si la función puntaje() está limitada por CPU y sustituye ThreadPoolExecutor por ProcessPoolExecutor cuando sea conveniente. Compara los tiempos de ejecución y considera el costo adicional de crear procesos.

## Error 5
Síntoma: La venta de Carla Ríos no aparece en los resultados y el total de ventas es menor que el registrado en contabilidad.
Línea: 37
Por qué pasa: El monto de Carla es "1,200.00" y float() no puede convertir directamente una cadena con separadores de miles. Esto genera un ValueError que posteriormente se oculta con except Exception: pass, provocando que se descarte la venta completa.
Qué le pedirías a la IA: Modifica la lectura de montos para aceptar separadores de miles, eliminando las comas antes de convertir el valor. Agrega pruebas con montos normales, montos con comas y valores inválidos para verificar que ninguna venta válida desaparezca.