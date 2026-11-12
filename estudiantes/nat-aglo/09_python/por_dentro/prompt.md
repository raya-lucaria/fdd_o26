# Mi prompt

## La tarea

Un script que lea `gasolina.csv` (columnas `estado`, `fecha`, `precio`; UTF-8;
algunas filas con el precio vacío o con coma de miles) y diga el precio
promedio por estado. No escribes el script: escribes el prompt que le darías a
una IA para que lo escriba bien a la primera.

## Mi prompt

Escríbelo aquí. Debe decir, como mínimo: la versión de Python y cómo se corre,
qué entra y qué sale, qué hacer con los casos borde, y cómo vas a verificar
que funciona.

Escribe un script con nombre precios-por-estado.py para Python 3.14.4; correlo con 
'uv run precios-por-estado.py' en un proyecto uv, con biblioteca estandar.
Entrada: gasolina.csv, UTF-8, con columnas estado, fecha, precio. Algunos valores 
de precio estan vacias o separan los miles con coma ("1,200.00").
Salida: por estado, calcula el precio promedio. Las filas de los  precios que no se 
pudieron leer las indicas con su motivo. Redondea a centavos los precios promedios,
igual a Decimal ("25,000.55").
Reglas: montos en Decimal, nunca Float. Las funciones no deben modificar lo que
reciben ni los valores por defecto mutables. Filas erroneas no se ignoran, se reportan.
Antes del codigo, dame la firma de la funcion o funciones con type hints y un caso
de prueba de rama por rama, incluidos: precios vacios, precios con comas separando
miles.


 
