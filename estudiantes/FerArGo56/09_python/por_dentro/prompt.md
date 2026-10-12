# Mi prompt
Haz un programa que lea el CSV de mi computadora con nombre gasolina.csv, el
archivo se correra adentro de un ambiente asi que solo es necesario poner
"gasolina.csv" no se necesita más ruta, las columnas del CSV son las siguientes:
`estado`, `fecha`, `precio`. USA POLARS
Entrada:
Algunas filas tiene comas en el precio y algunas
tienen cantidad vacias asi que es necesario que se esquiven esos errores con
try except, que el error no sea silencioso, que avise si la columna viene
vacia o con un elemento no valido y que use remove si trae comas. El precio
solo tendra comas para los miles por el formato. Como los resultados del
codigo pueden salir en decimales para evitar errores usar round(numero,2) para
que use solo 2 decimales.
Salida:
Lo que se busca del programa es que se haga un promedio por estado de precio
la idea es que lo imprima en la pantalla para ver los resultados de manera 
clara y legible para el humano, pon el orden de los rersultados de mayor a
 menor
Casos borde:
En caso de que un precio venga vacio no dejes que el error rompa el progrma
ni que el error sea silencioso, que se imprima el error.
Con las comas en los miles quitalas para poder convertir el valor a float con
remove
Si hay filas que no se pueden leer que se avise pero no rompa el programa hay 
que simpre salir con un promedio por estado
Normaliza los strings para que no haya errores como cdmx != CDMX,
todos los resultados en float con round(numero,2) para que no haya calculos 
erroneos. 
Requisitos:
Python = 3.14
se debe correr con uv run promedio_gasolina.py
verificacion:
Un CSV chiquito de prueba (5 o 6 filas) donde ya se sepa el promedio 
correcto
Que ese CSV incluya a propósito un precio vacío, uno con coma y una fila rota

## La tarea

Un script que lea `gasolina.csv` (columnas `estado`, `fecha`, `precio`; UTF-8;
algunas filas con el precio vacío o con coma de miles) y diga el precio
promedio por estado. No escribes el script: escribes el prompt que le darías a
una IA para que lo escriba bien a la primera.

## Mi prompt

Escríbelo aquí. Debe decir, como mínimo: la versión de Python y cómo se corre,
qué entra y qué sale, qué hacer con los casos borde, y cómo vas a verificar
que funciona.
Haz un programa que lea el CSV de mi computadora con nombre gasolina.csv, el  
archivo se correra adentro de un ambiente asi que solo es necesario poner
"gasolina.csv" no se necesita más ruta, las columnas del CSV son las siguientes:
`estado`, `fecha`, `precio`. USA POLARS
Entrada:
Algunas filas tiene comas en el precio y algunas
tienen cantidad vacias asi que es necesario que se esquiven esos errores con
try except, que el error no sea silencioso, que avise si la columna viene
vacia o con un elemento no valido y que use remove si trae comas. El precio
solo tendra comas para los miles por el formato. Como los resultados del
codigo pueden salir en decimales para evitar errores usar round(numero,2) para
que use solo 2 decimales.
Salida:
Lo que se busca del programa es que se haga un promedio por estado de precio
la idea es que lo imprima en la pantalla para ver los resultados de manera
clara y legible para el humano, pon el orden de los rersultados de mayor a 
 menor   
Casos borde:
En caso de que un precio venga vacio no dejes que el error rompa el progrma
ni que el error sea silencioso, que se imprima el error.
Con las comas en los miles quitalas para poder convertir el valor a float con 
remove
Si hay filas que no se pueden leer que se avise pero no rompa el programa hay
que simpre salir con un promedio por estado
Normaliza los strings para que no haya errores como cdmx != CDMX,
todos los resultados en float con round(numero,2) para que no haya calculos
erroneos.
Requisitos: 
Python = 3.14
se debe correr con uv run promedio_gasolina.py
verificacion:
Un CSV chiquito de prueba (5 o 6 filas) donde ya se sepa el promedio
correcto
Que ese CSV incluya a propósito un precio vacío, uno con coma y una fila rota
