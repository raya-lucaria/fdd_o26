# Revisión de revisa_esto.py

Un error por sección. Cada uno sale de un síntoma de la salida de
`uv run revisa_esto.py`. En `Síntoma:` escribe el síntoma de la tabla de la
página «Python por dentro» (índice de la sección).

## Error 1

Síntoma: Una venta no aparece en el total, sin aviso
Línea: 43 y 44
Por qué pasa: Carla tiene monto en formato de string. El codigo lo resuelve con pass => lo ignora.
Qué le pedirías a la IA: (agregar lineas de error) corrije excepcion para que solo arroje ValueError o KeyError en lugar de pass. Ademas,
avisa de la fila descartada.

## Error 2

Síntoma: La segunda región lista clientes de la primera
Línea: 25
Por qué pasa: crea objeto vistos=[] una sola vez. Mas adelante, cuando empieza a almacenar a los clientes para imprimirlos por region, 
en lugar de resetear la lista usa la existente, por tanto, se acumulan. 
Qué le pedirías a la IA: (agrega funcion clientes) No uses una lista como argumento por defecto. Coloca vistos=None y, dentro de la funcion,
si vistos=None crea una nueva lista. # asi se delimita a la hora de uso por la region.

## Error 3

Síntoma: «Con hilos» tarda casi lo mismo que «sin hilos», aunque el comentario promete 4× más rápido
Línea: 59
Por qué pasa: puntaje calcula sin esperar. Python deja correr un hilo a la vez, por lo que se turnan sin trabajar en paralelo y turnarse
aumenta tiempos. 
Qué le pedirías a la IA: (58 a 65) en lugar de hilos, acelera en calculo por medio de procesos y mide los tiempos.

## Error 4

Síntoma: Un descuento de 0 se cobró como 5 %
Línea: 39
Por qué pasa: el codigo trata a un descuento=0 como si no tuviera descuento, por tanto le hace descuento del 5%. Si realmente
no hubiera descuento marcaria un error.
Qué le pedirías a la IA: (agrega lineas 36 a 44)ayudame a que el codigo distinga descuento=0 de falta de valor.

## Error 5

Síntoma: La contabilidad está en centavos; comparar el total sin redondear con == falla
Línea: 76
Por qué pasa: el total es un float que aproxima decimales en binario, y por si solo no tiene limite de lugares decimales. En cambio, 
contabilidad se delimita por centavos. Aun si coincidieran en enteros, no lo haran en decimales. Se debe comparar en centavos enteros o
redondeado.
Qué le pedirías a la IA: Maneja total (dinero) en centavos enteros o con Decimal y compara redondeando a 2 decimales.
