# Revisión de revisa_esto.py

Un error por sección. Cada uno sale de un síntoma de la salida de
`uv run revisa_esto.py`. En `Síntoma:` escribe el síntoma de la tabla de la
página «Python por dentro» (índice de la sección).

## Error 1

Síntoma: Carla Rios no aparece en Norte
Línea: 36
Por qué pasa: En el CSV podemos ver que el dinero de Carla esta entre
comillas por que tiene 1,200 y como tiene una coma eso podria romper el formato
del CSV, pero esa coma hace que el valor no se cambie a float y como el 
exeption esta vacio entonces solo se lo salta
Qué le pedirías a la IA: [copy paste de la funcion], quiero que en esta funcion
también tome en cuenta los números con coma en el CSV por lo tanto en el 
except utiliza sin_coma = texto.replace(",", ""), se recibe un strin x,xxx y 
regresa un float xxxx donde las x son numeros, tambien agrega algo para que
si en caso de que alguien no ponmga un numero valido en el csv el error no 
sea silencioso y su columna digo "tipo de dato invalido" en vez de 
desapaercer

## Error 2

Síntoma: Podemos ver a Fatima Lopez y Gael Muñoz en norte cuando son de centro
Línea: 33
Por qué pasa: La lista ventas = [] se crea solo una vezx en python por lo tanto
se sobre escribe cada vez que llamas la funcion
Qué le pedirías a la IA: Mueve [copy paste de la funcion] crea la lista en la
funcion y haz el patrón típico es vistos=None y, adentro, if vistos is None:
 vistos = []

## Error 3

Síntoma: Parece ser que sin hilos y con hilos duran casi lo mismo aun que el 
comentario promete 4 veces mas rapido
Línea: 59 
Por qué pasa: Por que python tiene un GIL interno que no permite el computo
paralelo
Qué le pedirías a la IA: Borra el comentario que dice que es 4 veces más rapido

## Error 4

Síntoma: Un descuento de 0% se esta cobrando como de 0.05%
Línea: 39
Por qué pasa: tien not crea las cosas verdaderas o falsa y if not 0.0 = true
eso hace que entre al codigo y le de 0.05 de descuento
Qué le pedirías a la IA: Debes cambiar este if a que solo pase cuando en el 
CSV encuentre celdas vacias en la parte de descuento 

## Error 5

Síntoma: El calculo se da mal por los centavos
Línea:52
Por qué pasa: La computadora es lo mas exacta psoible asi que representar 
números como 1/3 le cuesa mucho y eso hace que si no redondeas las sumas salgan
mal como en este caso 
Qué le pedirías a la IA: Redondea todos los numeros vinarios que se sumen y se 
resten con round(numero, 2) para que sean solo 2 decimales
