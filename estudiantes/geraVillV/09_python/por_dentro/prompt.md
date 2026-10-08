# Mi prompt

## La tarea

Un script que lea `gasolina.csv` (columnas `estado`, `fecha`, `precio`; UTF-8;
algunas filas con el precio vacío o con coma de miles) y diga el precio
promedio por estado. No escribes el script: escribes el prompt que le darías a
una IA para que lo escriba bien a la primera.

## Mi prompt

Escribe un script compatible con Python 3.14 que se ejecute desde terminal con:

`python script.py gasolina.csv`

El archivo de entrada será un CSV codificado en UTF-8 con las columnas `estado`, `fecha` y `precio`. El programa debe calcular el precio promedio de gasolina por estado y mostrar los resultados ordenados alfabéticamente por estado.

El campo `precio` puede venir vacío, tener separadores de miles o contener un valor inválido. Las filas con precio vacío deben ignorarse y contarse como omitidas. Si falta alguna columna obligatoria, el archivo no existe o una fila contiene un precio inválido, muestra un mensaje claro en lugar de ocultar el error.

Para los cálculos de precios usa `Decimal` y no `float`, para evitar errores de representación en cantidades monetarias. La salida debe mostrar una línea por estado con el precio promedio redondeado a dos decimales y, al final, cuántas filas válidas y omitidas se procesaron.

Divide el programa en funciones pequeñas y usa `if __name__ == "__main__":` como punto de entrada.

Incluye pruebas que verifiquen al menos:
- un estado con varias filas;
- varios estados;
- un precio vacío;
- un precio con separador de miles;
- un precio inválido;
- y un archivo al que le falte una columna obligatoria.

Explica brevemente cómo correr el script y cómo ejecutar las pruebas.
