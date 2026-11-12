# Revisión de revisa_esto.py

Un error por sección. Cada uno sale de un síntoma de la salida de
`uv run revisa_esto.py`. En `Síntoma:` escribe el síntoma de la tabla de la
página «Python por dentro» (índice de la sección).

## Error 1

Síntoma: Fátima sale en varias regiones.

Línea: 25

Por qué pasa: La lista se crea la primera vez que se llama la función clientes y, las siguientes veces que se llama a clientes trabaja con los datos que ya estaban en esa lista. Por eso aparece un registro en más de una región.

Qué le pedirías a la IA: Inicializar la lista con None y después añadir una validación para que, si viene None, se inicialice como una lista vacía, es decir, pedirle que no maneje listas mutables.

## Error 2

Síntoma: Mala aplicación del descuento.

Línea: 39

Por qué pasa: if not descuento está considerando un descuento válido de 0 como si no tuviera descuento y, entonces, entra al descuento por default que es de 5%.

Qué le pedirías a la IA: Cambiar if not descuento porque trata el 0 como vacío y usar una condición que permita aplicar correctamente un descuento de 0.

## Error 3

Síntoma: Los tiempos con hilos y sin hilos son similares.

Línea: 59

Por qué pasa: Se hace la comparación usando hilos esperando que sea más rápido, pero por el GIL no se puede paralelizar este tipo de cálculo de CPU.

Qué le pedirías a la IA: Como estamos haciendo cálculos y no usos de I/O, usa procesos en vez de hilos.


## Error 4
Síntoma: Hay 6 puntajes de 7 esperados por el número de personas.

Línea: 43

Por qué pasa: El registro faltante tiene una coma en el monto y no se puede convertir directamente con float(). El error entra al catch, se ignora y no se procesa ese registro, por lo que tampoco se calcula su puntaje.

Qué le pedirías a la IA: Que añada un mensajes al entrar al catch y que considere posibles separadores de miles, como una coma, al leer los montos.


## Error 5

Síntoma: Los totales no cuadran.

Línea: 37

Por qué pasa: Los datos vienen como float, cuando sabemos que para dinero se debe trabajar con Decimal. Además, esto se combina con el error de los descuentos y con el registro que se omite por el try-catch.

Qué le pedirías a la IA: Pasar el tipo Decimal en vez de float para los montos y descuentos.


