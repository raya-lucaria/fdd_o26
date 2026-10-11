# Mi prompt

## La tarea
Un script que lea `gasolina.csv` (columnas `estado`, `fecha`, `precio`; UTF-8; algunas filas con el precio vacío o con coma de miles) y calcule el precio promedio por estado.

## Mi prompt
Escribe un programa en Python 3.13 que lea un archivo CSV llamado `gasolina.csv` y calcule el precio promedio de la gasolina por estado.

Requisitos:
1. El programa debe ejecutarse desde la terminal con `python gasolina.py`.
2. Utiliza únicamente bibliotecas de la librería estándar de Python.
3. El archivo de entrada está codificado en UTF-8 y contiene las columnas `estado`, `fecha` y `precio`.
4. El precio puede contener comas como separadores de miles, por ejemplo, "1,234.50". Debes eliminarlas antes de convertir el valor a número.
5. Ignora las filas cuyo precio esté vacío, sea negativo o no pueda convertirse a número. Informa cuántas filas fueron descartadas.
6. Elimina espacios adicionales al principio y al final de los nombres de los estados.
7. Ignora las filas que no tengan un estado válido.
8. Calcula el promedio aritmético de los precios válidos para cada estado.
9. Utiliza `Decimal` para evitar problemas de precisión con cantidades monetarias.
10. Muestra los resultados en la terminal, ordenados alfabéticamente por estado, con dos decimales y el número de registros utilizados.
11. Si el archivo no existe, está vacío o no contiene las columnas requeridas, muestra un mensaje de error claro sin generar un traceback innecesario.
12. Si un estado no tiene registros válidos, no calcules un promedio para él.

Verificación:
Incluye pruebas con un CSV pequeño que contenga varios estados, precios normales, precios con separadores de miles, valores vacíos, negativos y texto inválido.

Comprueba manualmente que los promedios sean correctos y que únicamente se incluyan las observaciones válidas.

También verifica que el programa funcione cuando el archivo esté vacío, cuando falten columnas y cuando no exista.

Entrega el código completo de `gasolina.py`, explica brevemente cómo ejecutarlo y muestra ejemplos de la salida esperada.