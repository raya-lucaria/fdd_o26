# Mi prompt

## La tarea

Un script que lea `gasolina.csv` (columnas `estado`, `fecha`, `precio`; UTF-8;
algunas filas con el precio vacío o con coma de miles) y diga el precio
promedio por estado. No escribes el script: escribes el prompt que le darías a
una IA para que lo escriba bien a la primera.

## Mi prompt

Haz un programa en Python 3.12 que se llame promedio_gasolina.py y que pueda ejecutar desde la terminal con el comando python3 promedio_gasolina.py. El programa debe leer un archivo llamado gasolina.csv que está en la misma carpeta y que contiene las columnas estado, fecha y precio, usando codificación UTF-8. Quiero que calcule el precio promedio de gasolina por cada estado, sumando los precios y dividiendo entre la cantidad de registros válidos de ese estado. El resultado debe aparecer en la terminal mostrando el nombre del estado y su precio promedio con dos decimales, ordenados alfabéticamente. Toma en cuenta que algunos precios pueden estar vacíos o tener comas para separar miles, entonces si están vacíos no los consideres para el promedio y si tienen comas convierte a números. También revisa qué pasa si hay precios que no son números, si falta el nombre del estado o si el archivo no existe, para que el programa no se cierre sin explicar qué salió mal. Si una fila tiene información incorrecta, quiero que la ignore y avise cuántas filas no se pudieron utilizar. Para verificar dame un ejemplo pequeño de gasolina.csv con algunos estados y diferentes precios, incluyendo uno vacío y otro con coma de miles, para que pueda calcular los promedios a mano y compararlos con los que imprime el programa.

